from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _

from compete.models import Contest

from judger.utils.celery import Progress

import logging
logger = logging.getLogger('judger.tasks')

__all__ = ('recompute_standing')

@shared_task(bind=True)
def recompute_standing(self, contest_id):
  contest = Contest.objects.get(id=contest_id)
  users = contest.users.filter(virtual=0, is_disqualified=False)
  logger.info("Job: Recomputing standing for contest %s.." % contest.key)

  recompute = 0
  with Progress(self, users.count()) as p:
    for user in users:
      user.recompute_results()
      recompute += 1
      if recompute % 10 == 0:
        p.done = recompute
    contest.clear_scoreboard_cache()

  logger.info("Job: Recomputing stats for ContestProblem(s) %s.." % contest.key)
  for p in contest.contest_problems.all():
    p.expensive_recompute_stats(force_update=True)

  logger.info("Finished: Recomputing standing for contest %s." % contest.key)
  return recompute


@shared_task(bind=True)
def rescore_problem(self, problem_id, publicy_changed=False):
  raise NotImplementedError
