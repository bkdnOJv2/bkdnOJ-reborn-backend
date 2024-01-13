# pylint: skip-file
from celery import shared_task
from django.conf import settings # TAG_PREDICTOR_ADDRESS, TAG_PREDICTOR_MAX_SUBMISSIONS
from problem.models import Problem, ProblemTag
from judger.utils.celery import Progress

import requests

import logging
logger = logging.getLogger('problem.tasks')

__all__ = ('tag_problem')

def __get_predict_api_url():
  endpoint = f"http://{settings.TAG_PREDICTOR_ADDRESS}/predict"
  return endpoint


@shared_task(bind=True)
def tag_problem(self, problem_id):
  problem = Problem.objects.get(id=problem_id)

  submissions = problem.submission_set.filter(result='AC')
  if settings.TAG_PREDICTOR_LANGS_COMMON_NAME:
    submissions = submissions.filter(language__common_name__in=settings.TAG_PREDICTOR_LANGS_COMMON_NAME)

  if not submissions.exists():
    logger.info("No Accepted C++ source code found")
    return None

  logger.info("Tagging problem %s.." % problem.shortname)
  submission_ids = submissions.values_list('id', flat=True)
  if settings.TAG_PREDICTOR_MAX_SUBMISSIONS < len(submission_ids):
    import random
    submission_ids = random.sample(submission_ids, settings.TAG_PREDICTOR_MAX_SUBMISSIONS)
  
  try:
    source_codes = list(submissions.filter(id__in=submission_ids).values_list('source__source', flat=True))
    tags_with_probs = {}
    with Progress(self, len(source_codes)) as p:
      for source in source_codes:
        r = requests.post(
          __get_predict_api_url(), 
          json={'text': source})
        prediction = r.json()

        for tag in prediction:
          new_prob = tags_with_probs.get(tag, 0.0) + prediction[tag]
          tags_with_probs[tag] = new_prob
    
    # Averages results
    # Choose only tags that's above thresh hold. Creates them if not exists.
    subs_count = len(submission_ids)
    tags_to_be_added = []

    for tag in tags_with_probs:
      tags_with_probs[tag] /= subs_count
      if tags_with_probs[tag] >= settings.TAG_PREDICTOR_ACCEPT_THRESHOLD:
        tags_to_be_added.append(ProblemTag.objects.get_or_create(name=tag)[0].id)
    
    problem.tags.set(tags_to_be_added)
    problem.save()

  except requests.exceptions.InvalidSchema:
    logger.error("Tag Predictor server could not be reached")
  except ValueError as e:
    logger.error("Unexpected response, err=", e)
  except TypeError as e:
    logger.error("Unexpected response, err=", e)
  
  logger.info("Job: Done Tagging Problem %s, %s" % (problem.shortname, tags_with_probs))
  return None
