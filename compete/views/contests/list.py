from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Case, Count, F, FloatField, IntegerField, Max, Min, Q, Sum, Value, When
from django.db import IntegrityError
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError

import django_filters

from rest_framework import views, permissions, generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.serializers import DateTimeField
from rest_framework.serializers import Serializer

from operator import attrgetter, itemgetter
from organization.models import Organization
from organization.serializers import OrganizationBasicSerializer

from problem.serializers import ProblemSerializer
from userprofile.models import UserProfile as Profile

from compete.serializers import *
from compete.models import Contest, ContestProblem, ContestSubmission, ContestParticipation, Rating
from compete.exceptions import *
from compete.tasks import recompute_standing

from helpers.custom_pagination import Page100Pagination, Page10Pagination

import logging
logger = logging.getLogger(__name__)

__all__ = [
    ### Contest View
    'PastContestListView', 'AllContestListView', 'ContestListView', 
]

class AllContestListView(generics.ListAPIView):
    """
        Return a List of all Contests
    """
    serializer_class = PastContestBriefSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^key', '@name']
    filterset_fields = ['enable_frozen', 'is_rated', 'is_visible', 'format_name']
    ordering_fields = ['start_time', 'end_time']
    ordering = ['-end_time']

    def get_queryset(self):
        user = self.request.user
        org = self.request.query_params.get('org', None)
        if org:
            org = Organization.objects.filter(slug=org).first()

            if org and org.id in user.profile.member_of_org_with_ids:
                if self.request.query_params.get('recursive'):
                    return Contest.get_org_visible_contests(org, True)
                return Contest.get_org_visible_contests(org)
            else:
                return Contest.objects.none()

        return Contest.get_visible_contests(user)

class PastContestListView(generics.ListAPIView):
    """
        Return a List of all Past Contests
    """
    serializer_class = PastContestBriefSerializer
    permission_classes = []

    def get_queryset(self):
        qs = None
        user = self.request.user

        org = self.request.query_params.get('org', None)
        if org:
            org = Organization.objects.filter(slug=org).first()

            if org and org.id in user.profile.member_of_org_with_ids:
                if self.request.query_params.get('recursive'):
                    qs = Contest.get_org_visible_contests(org, True)
                else:
                    qs = Contest.get_org_visible_contests(org)
            else:
                qs = Contest.objects.none()
        else:
            qs = Contest.get_visible_contests(user)

        qs = qs.filter(end_time__lt=timezone.now()).order_by('-end_time')
        return qs

class ContestListView(generics.ListCreateAPIView):
    """
        Return a List of present, active, future contest
    """
    serializer_class = ContestBriefSerializer
    permission_classes = []

    @cached_property
    def _now(self):
        return timezone.now()

    def _get_queryset(self):
        qs = None
        user = self.request.user

        org = self.request.query_params.get('org', None)
        if org:
            org = Organization.objects.filter(slug=org).first()

            if org and org.id in user.profile.member_of_org_with_ids:
                if self.request.query_params.get('recursive'):
                    qs = Contest.get_org_visible_contests(org, True)
                else:
                    qs = Contest.get_org_visible_contests(org)
            else:
                qs = Contest.objects.none()
        else:
            qs = Contest.get_visible_contests(user)

        return qs.prefetch_related('tags', 'organizations', 'authors', 'collaborators', 'reviewers')

    def get_queryset(self):
        return self._get_queryset().order_by('key').filter(end_time__lt=self._now)

    def get(self, request):
        present, active, future = [], [], []
        finished = set()
        for contest in self._get_queryset().exclude(end_time__lt=self._now):
            if contest.start_time > self._now:
                future.append(contest)
            else:
                present.append(contest)

        if self.request.user.is_authenticated:
            for participation in ContestParticipation.objects.filter(virtual=0, #LIVE
                    user=self.request.user.profile, contest_id__in=present) \
                    .select_related('contest') \
                    .prefetch_related('contest__authors', 'contest__collaborators', 'contest__reviewers') \
                    .annotate(key=F('contest__key')):
                if participation.ended:
                    finished.add(participation.contest)
                else:
                    active.append(participation.contest)
                    present.remove(participation.contest)

        active.sort(key=attrgetter('end_time', 'key'))
        present.sort(key=attrgetter('end_time', 'key'))
        future.sort(key=attrgetter('start_time'))
        context={'request': request}
        return Response({
            'active': ContestBriefSerializer(active, many=True, context=context).data,
            'present': ContestBriefSerializer(present, many=True, context=context).data,
            'future': ContestBriefSerializer(future, many=True, context=context).data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied()

        data = request.data.copy()
        data['authors'] = [{'username': request.user.username}]

        seri = ContestBriefSerializer(data=data, context={'request':request})
        if not seri.is_valid():
            return Response({ 'detail': seri.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        try:
            seri.save()
        except Exception as excp:
            return Response({
                'errors': str(excp),
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(seri.data, status=status.HTTP_201_CREATED)

