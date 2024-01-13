# pylint: skip-file
from django.core.cache import cache
from django.db.models import Case, Count, ExpressionWrapper, F, Max, When
from django.db.models.fields import FloatField
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_noop

from userprofile.models import UserProfile
from problem.models import Problem
from submission.models import Submission

CACHE_DURATION = 5 * 60 * 60 # 5 hours 

def key_user_completed_ids(profile: UserProfile):
  return 'user_completed:%d' % profile.id

def user_completed_ids(profile: UserProfile):
  key = key_user_completed_ids(profile)
  result = cache.get(key)
  if result is None:
    result = set( Submission.objects.filter(user=profile, result='AC', points=F('problem__points'))
                  .values_list('problem_id', flat=True).distinct()
            )
    cache.set(key, result, CACHE_DURATION)
  return result

def key_user_attempted_ids(profile: UserProfile):
  return 'user_attempted:%d' % profile.id

def user_attempted_ids(profile: UserProfile):
  key = key_user_attempted_ids(profile)
  result = cache.get(key)
  if result is None:
    result = {
      id: points for id, max_points, points in (
          Submission.objects.filter(user=profile).values_list('problem__id', 'problem__points')
            .annotate(points=Max('points')).filter(points__lt=F('problem__points'))
        )
    }
    cache.set(key, result, CACHE_DURATION)
  return result
