from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import os
import logging
logger = logging.getLogger(__name__)

from problem.models import Problem, ProblemTestProfile, TestCase
from helpers.problem_data import ProblemDataCompiler

@receiver(post_save, sender=Problem)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProblemTestProfile.objects.create(problem=instance)

@receiver(pre_delete, sender=ProblemTestProfile)
def delete_test_zip(sender, instance, **kwargs):
    if instance.zipfile:
        logger.info("ProblemTestProfile pre_delete signal caught, deleting zip file")
        instance.zipfile.delete(save=False)

# # Moved into views
# @receiver(post_save, sender=ProblemTestProfile)
# def compile_problem_data_yml(sender, instance, created, **kwargs):
#     if instance._signal_caught != True:
#         instance._zipfile_change = True
#         instance._signal_caught = True
#         instance.save()
#         instance.generate_test_cases()
#         instance.update_pdf_within_zip()
#         instance.save()
