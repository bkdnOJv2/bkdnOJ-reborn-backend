# pylint: skip-file
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _

from problem.models import Problem
from userprofile.models import UserProfile as Profile
from submission.models import Submission
from judger.utils.celery import Progress

import logging
logger = logging.getLogger('judger.tasks')

__all__ = ('apply_submission_filter', 'rejudge_problem_filter', 'rescore_problem')

def apply_submission_filter(queryset, id_range, languages, results):
    if id_range:
        start, end = id_range
        queryset = queryset.filter(id__gte=start, id__lte=end)
    if languages:
        queryset = queryset.filter(language_id__in=languages)
    if results:
        queryset = queryset.filter(result__in=results)
    queryset = queryset.exclude(locked_after__lt=timezone.now()) \
                       .exclude(status__in=Submission.IN_PROGRESS_GRADING_STATUS)
    return queryset


@shared_task(bind=True)
def rejudge_problem_filter(self, problem_id, id_range=None, languages=None, results=None, user_id=None):
  queryset = Submission.objects.filter(problem_id=problem_id)
  queryset = apply_submission_filter(queryset, id_range=id_range, languages=languages, results=results)
  user = User.objects.get(id=user_id)
  logger.info("Job: Rejudge job acknowledged.")

  rejudged = 0
  with Progress(self, queryset.count()) as p:
    for submission in queryset.reverse().iterator(): # Reverse because I want earliest sub to be judged first
      submission.judge(rejudge=True, batch_rejudge=True, rejudge_user=user.profile)
      rejudged += 1
      if rejudged % 10 == 0:
        p.done = rejudged
  logger.info("Job: Rejudge job finished.")
  return rejudged


@shared_task(bind=True)
def rescore_problem(self, problem_id, publicy_changed=False):
  raise NotImplementedError
