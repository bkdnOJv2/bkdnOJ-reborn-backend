# pylint: skip-file
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _

from submission.models import Submission

from judger.utils.celery import Progress

import logging
logger = logging.getLogger('judger.tasks')

__all__ = ('recompute_standing')

@shared_task(bind=True)
def mass_rejudge(self, sub_ids, rejudge_user_id):
  subs = Submission.objects.filter(id__in=sub_ids)
  user = User.objects.get(id=rejudge_user_id)
  logger.info(f"Job: Mass rejudging {len(sub_ids)} submission(s)..")

  rejudged = 0
  with Progress(self, len(sub_ids)) as p:
    for sub in subs.reverse().iterator(): # Reverse because I want earliest sub to be judged first
      sub.judge(rejudge=True, batch_rejudge=True, rejudge_user=user.profile)
      rejudged += 1
      if rejudged % 10 == 0:
        p.done = rejudged
  logger.info("Job: Rejudge job finished.")
  return rejudged
