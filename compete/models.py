from django.utils.translation import gettext_lazy as _
from django.db import models
from django_extensions.db.models import TimeStampedModel

class Contest(TimeStampedModel):
    class Meta:
        ordering = []
        verbose_name = _("Contest")
        verbose_name_plural = _("Contests")