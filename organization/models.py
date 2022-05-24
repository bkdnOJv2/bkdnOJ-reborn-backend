from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()
from django_extensions.db.models import TimeStampedModel

from helpers.fileupload import \
  path_and_rename_org_avatar, DEFAULT_ORG_AVATAR_URL

class Organization(TimeStampedModel):
  shortname = models.SlugField(
    max_length=256,
    # null=False, blank=False, unique=True, db_index=True, 
    primary_key=True,
  )
  name = models.CharField(max_length=256, null=False, blank=False)
  description = models.TextField(null=False, blank=False)

  org_image = models.ImageField(upload_to=path_and_rename_org_avatar,
    default=DEFAULT_ORG_AVATAR_URL,
  )

  members = models.ManyToManyField('userprofile.UserProfile', through='OrgMembership')

  @property
  def memberships(self):
    org_memberships = OrgMembership.objects.filter(org=self.shortname)
    return org_memberships
  
  class Meta:
    verbose_name = _('Organization')
    verbose_name_plural = _('Organizations')

    default_permissions = (
      'view', 'add', 'delete',
      #'change', 
    )

    permissions = [
      ("change_own_org", _("Can change their own organizations and its' members")),
      ("change_all_org", _("Can change all organizations and its' members")),
    ]

  admin_list = ['shortname', 'name']

  def __str__(self):
    return f'{self.shortname}'
  
  def get_absolute_url(self):
    return reverse("organization-detail", 
      kwargs={"shortname": self.shortname})


class OrgMembership(TimeStampedModel):
  user = models.ForeignKey('userprofile.UserProfile', on_delete=models.CASCADE)
  org = models.ForeignKey(Organization, on_delete=models.CASCADE)

  class MembershipType(models.TextChoices):
    MEMBER = 'MMB', _('Member')
    MANAGER = 'MNG', _('Manager')
    OWNER = 'OWN', _('Owner')

  role = models.CharField(max_length=8,
    choices=MembershipType.choices, default=MembershipType.MEMBER)

  @property
  def role_label(self) -> MembershipType:
    return self.MembershipType(self.role).label

  ranking = models.BigIntegerField(default=0)

  class Meta:
    unique_together = ['user', 'org']
    verbose_name = _('Organization-User Relationship')
    verbose_name_plural = _('Organization-User Relationships')


  admin_list = ['__str__', 'user', 'org', 'role', 'ranking']

  def __str__(self):
    return f'user [{self.user.owner.username}] - org [{self.org.shortname}]'
