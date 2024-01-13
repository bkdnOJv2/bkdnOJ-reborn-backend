# pylint: skip-file
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import shutil
import os
import logging
logger = logging.getLogger(__name__)

from compete.models import Contest, ContestProblem, ContestParticipation

# @receiver(post_save, sender=Problem)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         ProblemTestProfile.objects.get_or_create(problem=instance)
#         # Work around because there is no way admin can change this yet
#         # TODO: Add view to change allowed_languages
#         instance.allowed_languages.add(*Language.objects.all())
#         instance.save()