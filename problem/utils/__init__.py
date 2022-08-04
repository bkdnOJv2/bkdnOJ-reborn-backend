from django.core.cache import cache
from django.db.models import Case, Count, ExpressionWrapper, F, Max, When
from django.db.models.fields import FloatField
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_noop

from userprofile.models import UserProfile
from problem.models import Problem
from submission.models import Submission

CACHE_DURATION = 86400

def user_completed_ids(profile: UserProfile):
  key = 'user_completed:%d' % profile.id
  result = cache.get(key)
  if result is None:
    result = set( Submission.objects.filter(user=profile, result='AC', points=F('problem__points'))
                  .values_list('problem_id', flat=True).distinct()
            )
    cache.set(key, result, CACHE_DURATION)
  return result


def user_attempted_ids(profile: UserProfile):
  key = 'user_attempted:%d' % profile.id
  result = cache.get(key)
  if result is None:
    # result = {
    #   id: {
    #     'achieved_points': points,
    #     'max_points': max_points,
    #   } for id, max_points, points in (
    #       Submission.objects.filter(user=profile).values_list('problem__id', 'problem__points')
    #         .annotate(points=Max('points')).filter(points__lt=F('problem__points'))
    #     )
    # }
    result = {
      id: points for id, max_points, points in (
          Submission.objects.filter(user=profile).values_list('problem__id', 'problem__points')
            .annotate(points=Max('points')).filter(points__lt=F('problem__points'))
        )
    }
    cache.set(key, result, CACHE_DURATION)
  return result
