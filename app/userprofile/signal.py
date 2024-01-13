# pylint: skip-file
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model
User = get_user_model()

from userprofile.models import UserProfile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, email=instance.email, username_display_override=instance.username)
