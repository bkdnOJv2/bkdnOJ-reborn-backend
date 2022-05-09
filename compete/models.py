from django.utils.translation import gettext_lazy as _
from django.db import models
from django_extensions.db.models import TimeStampedModel

class Contest(TimeStampedModel):
    class Meta:
        ordering = []
        verbose_name = _("contest")
        verbose_name_plural = _("contests")

        permissions = [
            ("virtual_participate", _("Can virtual participate contests")),
        ]