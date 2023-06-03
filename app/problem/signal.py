from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import shutil
import os
import logging
logger = logging.getLogger(__name__)

from problem.models import Problem, ProblemTestProfile, TestCase
from judger.models import Language
from helpers.problem_data import ProblemDataCompiler

@receiver(post_save, sender=Problem)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProblemTestProfile.objects.get_or_create(problem=instance)
        # Work around because there is no way admin can change this yet
        # TODO: Add view to change allowed_languages
        instance.allowed_languages.add(*Language.objects.all())
        instance.save()

@receiver(pre_delete, sender=Problem)
def delete_test_zip(sender, instance, **kwargs):
    logger.info("Problem pre_delete signal caught, deleting problem_pdf")
    instance.delete_pdf()

@receiver(pre_delete, sender=ProblemTestProfile)
def delete_test_zip(sender, instance, **kwargs):
    logger.info("ProblemTestProfile pre_delete signal caught, deleting problem_data")
    instance.delete_data()
