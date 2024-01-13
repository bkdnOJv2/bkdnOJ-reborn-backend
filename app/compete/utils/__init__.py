# pylint: skip-file
from django.core.cache import cache
from django.db.models import Case, Count, ExpressionWrapper, F, Max, When
from django.db.models.fields import FloatField
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_noop

from userprofile.models import UserProfile
from compete.models import Contest, ContestParticipation
from problem.models import Problem
from submission.models import Submission

CACHE_DURATION = 5 * 60 * 60 # 5 hours 

def key_contest_completed_ids(participation):
    return 'contest_completed:%d' % participation.id

def contest_completed_ids(participation: ContestParticipation):
    key = key_contest_completed_ids(participation)
    result = cache.get(key)
    if result is None:
        result = set(
          participation.submissions.filter(submission__result='AC', points=F('problem__points'))
          .values_list('problem__problem__id', flat=True).distinct()
        )
        cache.set(key, result, CACHE_DURATION)
    return result

def key_contest_attempted_ids(participation):
    return 'contest_attempted:%d' % participation.id

def contest_attempted_ids(participation: ContestParticipation):
    key = key_contest_attempted_ids(participation)
    result = cache.get(key)
    if result is None:
        result = {
          id: points
          for id, max_points, points in (participation.submissions
                                          .values_list('problem__problem__id', 'problem__points')
                                          .annotate(points=Max('points'))
                                          .filter(points__lt=F('problem__points')))
        }
        cache.set(key, result, CACHE_DURATION)
    return result

def key_contest_registered_ids(contest):
    return 'contest_registered:%d' % contest.id

def contest_registered_ids(contest):
    key = key_contest_registered_ids(contest)
    result = cache.get(key)
    if result is None:
        from userprofile.models import UserProfile
        result = set( 
            UserProfile.objects.filter(id__in=\
                contest.users.filter(virtual__in=[ContestParticipation.LIVE, ContestParticipation.SPECTATE])\
                .values_list('user_id', flat=True)
            ).values_list('id', flat=True)
        )
        cache.set(key, result, CACHE_DURATION)
    return result