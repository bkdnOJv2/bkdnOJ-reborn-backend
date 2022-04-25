from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Problem, ProblemTestDataProfile

@receiver(post_save, sender=Problem)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ProblemTestDataProfile.objects.create(problem=instance)