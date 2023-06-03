from django.conf import settings
from django.utils.translation import gettext_lazy as _

__all__ = [
  'OrganizationTooDeepError',
]

class OrganizationTooDeepError(Exception):
  def __init__(self):
    super().__init__(_(
      "Cannot add sub org. Organization tree has reached maximum depth "+
      f"allowed (> {settings.BKDNOJ_ORG_TREE_MAX_DEPTH}).")
    )
