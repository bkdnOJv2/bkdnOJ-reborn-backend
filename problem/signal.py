from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import os
import logging
logger = logging.getLogger(__name__)

from problem.models import Problem, ProblemTestProfile, TestCase

@receiver(post_save, sender=Problem)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProblemTestProfile.objects.create(problem=instance)

@receiver(pre_delete, sender=ProblemTestProfile)
def delete_test_zip(sender, instance, **kwargs):
    if instance.zipfile:
        logger.info("ProblemTestProfile pre_delete signal caught, deleting zip file")
        instance.zipfile.delete(save=False)
