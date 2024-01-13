# pylint: skip-file
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

from helpers.custom_pagination import Page100Pagination, Page10Pagination

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'contest_standing_view',
]

# from collections import defaultdict, namedtuple
from django.core.cache import cache

from django.utils import timezone
from judger.utils.ranker import ranker

@api_view(['GET'])
def contest_standing_view(request, key):
    # now = timezone.now()
    # logger.info('Received request')

    user = request.user
    contest = get_object_or_404(Contest, key=key)

    if not contest.started:
        if not contest.is_editable_by(user):
            raise ContestNotStarted

    if not contest.is_accessible_by(user):
        return Response({
            'detail': "Contest is not public to view."
        }, status=status.HTTP_403_FORBIDDEN)


    cache_duration = contest.scoreboard_cache_duration
    cache_disabled = (cache_duration == 0)

    ## TODO: Scoreboard visibility
    can_break_ice = (contest.is_frozen and contest.can_see_full_scoreboard(user))
    if contest.is_frozen and \
        ((not can_break_ice) or (not (request.GET.get('view_full')=='1'))):
            scoreboard_view_mode = 'froze'
            scoreboard_serializer = ContestStandingFrozenSerializer
    else:
        scoreboard_view_mode = 'full'
        scoreboard_serializer = ContestStandingSerializer

    # logger.info("Done permission checking -- %.4fs" % (timezone.now()-now).total_seconds())
    # now = timezone.now()

    cache_key = f"contest-{contest.key}-scoreboard-{scoreboard_view_mode}"

    if cache_disabled or cache.get(cache_key) == None:
        cprobs = contest.contest_problems.prefetch_related('problem').all()
        problem_data = [{
            'id': p.id,
            'label': p.label,
            'shortname': p.problem.shortname,
            'points': p.points,
            'partial': p.partial,
        } for p in cprobs]

        # logger.info("Done serializing problems -- %.4fs" % (timezone.now()-now).total_seconds())
        # now = timezone.now()

        corgs = Organization.objects.filter(id__in=contest.users\
                    .annotate(org=F('organization'))\
                    .exclude(org=None)\
                    .values_list('org', flat=True).order_by('org').distinct())
        org_data = OrganizationBasicSerializer(corgs, many=True).data

        # logger.info("Done serializing orgs -- %.4fs" % (timezone.now()-now).total_seconds())
        # now = timezone.now()

        if scoreboard_view_mode == 'froze':
            queryset = contest.users.select_related('user', 'user__user').filter(virtual=ContestParticipation.LIVE).\
                order_by('-frozen_score', 'frozen_cumtime', 'frozen_tiebreaker',
                        'user__id').all()
            ranker_key = itemgetter('frozen_score', 'frozen_cumtime', 'frozen_tiebreaker')
        else:
            queryset = contest.users.select_related('user', 'user__user').filter(virtual=ContestParticipation.LIVE).\
                order_by('-score', 'cumtime', 'tiebreaker', 'user__id').all()
            ranker_key = itemgetter('score', 'cumtime', 'tiebreaker')
        
        results = scoreboard_serializer(queryset, many=True, context={'request': request}).data

        is_frozen = (scoreboard_view_mode == 'froze')
        dat = {
            'organizations': org_data,
            'problems': problem_data,
            'results': results,
            'is_frozen': is_frozen,
            'is_frozen_enabled': contest.enable_frozen,
            'frozen_time': DateTimeField().to_representation(contest.frozen_time),
            'scoreboard_cache_duration': contest.scoreboard_cache_duration,
        }
        if not cache_disabled:
            cache.set(cache_key, dat, cache_duration)
    else:
        # logger.info("Fetch from cache")
        dat = cache.get(cache_key)

    # logger.info("Done serializing data -- %.4fs" % (timezone.now()-now).total_seconds())
    # now = timezone.now()

    if can_break_ice:
        dat['can_break_ice'] = True
    return Response(dat, status=status.HTTP_200_OK)
