from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig

class CompeteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compete'
    verbose_name = _("Competition")
    verbose_name_plural = _("Competitions")
