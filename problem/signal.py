from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import os
import logging
logger = logging.getLogger(__name__)

from problem.models import Problem, ProblemTestProfile

@receiver(post_save, sender=Problem)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProblemTestProfile.objects.create(problem=instance)

@receiver(pre_delete, sender=ProblemTestProfile)
def delete_test_zip(sender, instance, **kwargs):
    if instance.zip_url:
        logger.info("ProblemTestProfile pre_delete signal caught, deleting zip file")
        if os.path.isfile(instance.zip_url.path):
            os.remove(instance.zip_url.path)
            logger.info("OK: Deleted")
        else:
            logger.info("Zip file doesn't exist")

# @receiver(post_save, sender=ProblemTestDataProfile)
# def prepare_save(sender, instance, **kwargs):
#     if instance.zip_url: