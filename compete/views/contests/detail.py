from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Case, Count, F, FloatField, IntegerField, Max, Min, Q, Sum, Value, When
from django.db import IntegrityError
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError
from django.core.cache import cache

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
from compete.ratings import rate_contest
from compete.exceptions import *
from compete.tasks import recompute_standing

from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, SubmissionBasicSerializer

from userprofile.models import UserProfile as Profile
from userprofile.serializers import UserProfileBasicSerializer as ProfileSerializer


from helpers.custom_pagination import Page100Pagination, Page50Pagination, Page10Pagination

import logging
logger = logging.getLogger(__name__)

__all__ = [
    ### Contest info
    'ContestDetailView',

    # Problems within Contest
    'ContestProblemListView', 'ContestProblemDetailView',

    ### Submissions within Contest
    'ContestSubmissionListView',

    'ContestProblemSubmissionListView', 'ContestProblemSubmissionDetailView',

    ### Participants within Contest
    'ContestParticipationListView', 'ContestParticipationDetailView',
    'ContestParticipantListView',
]

class ContestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Contest.objects.none()
    lookup_field = 'key'
    serializer_class = ContestDetailSerializer
    permission_classes = []

    def get_object(self, *a):
        contest = get_object_or_404(
            Contest.objects.prefetch_related(
                'problems', 'contest_problems', 'contest_problems__problem',
                'authors', 'authors__user',
                'collaborators', 'collaborators__user',
                'reviewers', 'reviewers__user',
                'private_contestants', 'private_contestants__user',
                'organizations',
            ),
            key=self.kwargs['key']
        )
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            # if not contest.started:
            #     raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    def put(self, *args, **kwargs):
        return self.patch(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        contest = self.get_object()
        try:
            return super().patch(request, *args, **kwargs)
        except ValidationError as e:
            return Response({
                'general': e,
            }, status=status.HTTP_400_BAD_REQUEST)


class ContestProblemListView(generics.ListCreateAPIView):
    """
        Problems within contests view
    """
    serializer_class = ContestProblemBriefSerializer
    pagination_class = Page100Pagination
    lookup_field = 'shortname'

    def get_object(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    def get_queryset(self):
        contest = self.get_object()
        return contest.contest_problems.filter()

    NON_ASSOCIATE_FIELDS = ('order', 'points', 'partial',)# 'is_pretested', 'max_submissions')
    def create(self, request, *args, **kwargs):
        contest = self.get_object()
        cproblems = contest.contest_problems # Manager
        visproblems = Problem.get_visible_problems(request.user)

        contest_problem_ids = set()
        for rowidx, problem_kw in enumerate(request.data):
            try:
                cpf = cproblems.filter(problem__shortname=problem_kw['shortname'])
                if cpf.exists():
                    cpf = cpf.first()
                else:
                    p = visproblems.get(shortname=problem_kw['shortname'])
                    cpf = ContestProblem(contest=contest, problem=p)
                for k, v in problem_kw.items():
                    if k in ContestProblemListView.NON_ASSOCIATE_FIELDS:
                        setattr(cpf, k, v)
            except Problem.DoesNotExist:
                return Response({ 'detail': _(f"Row {rowidx}: Problem '{problem_kw['shortname']}' "
                                    "does not exist or you do not have permission to it.")},
                    status=status.HTTP_400_BAD_REQUEST)
            except KeyError as ke:
                return Response({ 'detail': _(f"Row {rowidx}: Expecting key='{ke.args[0]}'")},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                cpf.save()
            except Exception as excp:
                return Response({
                    'detail': _(f"Row {rowidx} has the following errors:"),
                    'errors': str(excp),
                }, status=status.HTTP_400_BAD_REQUEST)
            contest_problem_ids.add(cpf.id)

        cproblems.exclude(id__in=contest_problem_ids).delete()

        # Schedule recomputing job after editting Contest Problems list
        from compete.tasks import recompute_standing
        async_status = recompute_standing.delay(contest.id)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ContestProblemDetailView(generics.RetrieveAPIView):
    """
        Certain Problem within Contest view
    """
    pagination_class = None

    def get_serializer_class(self):
        return ContestProblemSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    def get_object(self):
        p = get_object_or_404(ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname'])
        return p

    # def get(self, request, key, shortname):
    #     p = self.get_object()
    #     return Response(
    #         self.get_serializer_class()(p, context={'request': request}).data
    #     )


class ContestSubmissionListView(generics.ListAPIView):
    """
        All Submissions within contest view
    """
    serializer_class = ContestSubmissionSerializer
    pagination_class = Page10Pagination

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    @cached_property
    def contest(self):
        return self.get_contest()

    def get_queryset(self):
        contest = self.contest

        cps = ContestProblem.objects.filter(contest=contest).all()
        css = ContestSubmission.objects.select_related(
                'participation', 'participation__contest', 'problem', 'submission'
            ).filter(problem__in=cps)

        ## Visible subs
        if not contest.is_testable_by(self.request.user):
            css = css.filter(participation__virtual=ContestParticipation.LIVE)

        ## Query params
        username = self.request.query_params.get('user')
        if username is not None:
            css = css.filter(participation__user__user__username=username)

        prob_shortname = self.request.query_params.get('problem')
        if prob_shortname is not None:
            css = css.filter(problem__problem__shortname=prob_shortname)
        return css


    def get_serializer_context(self):
        should_freeze_result = self.contest.is_frozen
        # and not self.contest.can_see_full_scoreboard(request.user)
        context = {
            'request': self.request,
            'should_freeze_result': should_freeze_result,
        }
        return context

    def get(self, request, key):
        css = self.get_queryset()
        page = self.paginate_queryset(css)
        data = ContestSubmissionSerializer(page,
                context=self.get_serializer_context(), many=True).data
        return self.get_paginated_response(data)

## SHOULD NOT USE
class ContestProblemSubmissionListView(generics.ListAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise ContestNotAccessible
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise ContestNotStarted
        return contest

    def get_queryset(self):
        raise NotImplementedError
        cp = get_object_or_404( ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname']
        )
        queryset = ContestSubmission.objects.filter(problem=cp)
        if not queryset.exists():
            raise Http404
        return queryset

## SHOULD NOT USE
class ContestProblemSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Certain Submission within Contest view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise ContestNotAccessible
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise ContestNotStarted
        return contest

    def get_queryset(self):
        raise NotImplementedError
        cp = get_object_or_404( ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname']
        )
        queryset = ContestSubmission.objects.filter(problem=cp)
        return queryset

    def get(self, *args, **kwargs):
        p = get_object_or_404(self.get_queryset(), id=self.kwargs['id'])
        ## TODO raise PermissionDenied see_detail
        return Response(
            ContestSubmissionSerializer(p).data,
            status=status.HTTP_200_OK,
        )


class ContestParticipationListView(generics.ListAPIView):
    """
        ADMIN ONLY:
        Participations List View for Contest `key`
    """
    serializer_class = ContestParticipationSerializer
    permission_classes = [permissions.IsAdminUser]

    """
        Staff that has access to Contest can see list of Participations
    """
    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404()
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users

        username = self.request.query_params.get('user')
        if username is not None:
            queryset = queryset.filter(user__user__username=username)

        virtual = self.request.query_params.get('virtual')
        if virtual is not None:
            if virtual == 'LIVE':
                queryset = queryset.filter(virtual=0)
            elif virtual == 'SPECTATE':
                queryset = queryset.filter(virtual=-1)
            elif virtual == 'VIRTUAL':
                queryset = queryset.filter(virtual__gt=0)
            else:
                raise Http404()

        is_disqualified = self.request.query_params.get('is_disqualified')
        if is_disqualified is not None:
            queryset = queryset.filter(is_disqualified=is_disqualified)

        return queryset.all()


class ContestParticipationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestParticipationDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method
        if method == 'GET':
            if not contest.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not contest.is_editable_by(self.request.user):
                raise PermissionDenied()
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users.all()
        return queryset


class ContestParticipantListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    pagination_class = Page50Pagination

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404()
        return contest
    
    @cached_property
    def contest(self):
        return self.get_contest()
    
    def get_queryset(self):
        queryset = Profile.objects.select_related('user').filter(
            id__in=self.contest.users.filter(virtual=0).values_list('user__id', flat=True))
        return queryset
        
    def get(self, request, key):
        if request.query_params.get('view_full', False) not in ['true', '1']: 
            view_full = '0'
        else:
            view_full = '1'

        # Cache is 
        if view_full == '1':
            contest = self.contest
            # cache_duration = c.scoreboard_cache_duration
            cache_duration = max( int( (contest.end_time - contest.start_time).total_seconds() ), 300 ) ## Extra 5 mins
            cache_disabled = (cache_duration == 0)
            cache_key = contest.participants_cache_key
            cache.delete(cache_key)
            data = None

            if cache_disabled or cache.get(cache_key) == None:
                data = self.get_serializer_class()(self.get_queryset(), many=True, context={'request': request}).data
                if not cache_disabled:
                    cache.set(cache_key, data, cache_duration)
            else:
                data = cache.get(cache_key)

            return Response(data, status=status.HTTP_200_OK)
        else:
            data = self.paginate_queryset(self.get_queryset())
            data = self.get_serializer_class()(data, many=True, context={'request': request}).data,
            return self.get_paginated_response(data)
            
