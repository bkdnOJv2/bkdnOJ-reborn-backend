from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
User = get_user_model()

from treebeard.mp_tree import MP_Node

from .exceptions import OrganizationTooDeepError

from userprofile.models import UserProfile as Profile
from judger.utils.float_compare import float_compare_equal

from helpers.fileupload import \
  path_and_rename_org_avatar, DEFAULT_ORG_AVATAR_URL


class Organization(MP_Node):
  # treebeard fields
  node_order_by = ['short_name']

  # model fields
  slug = models.SlugField(
    max_length=128, verbose_name=_('organization slug'),
    help_text=_('Organization name shown in URL and also will be used for searching.'),
    unique=True,
  )
  short_name = models.CharField(
    max_length=64, verbose_name=_('short name'),
    help_text=_('To identify each org from their sibling orbs. Also is displayed beside user name during contests.'),
  )
  name = models.CharField(max_length=128, verbose_name=_('organization name'))

  about = models.TextField(
    verbose_name=_('organization description'))

  admins = models.ManyToManyField('userprofile.UserProfile',
    verbose_name=_('administrators'), related_name='admin_of',
    help_text=_('Those who can edit this organization'))

  creation_date = models.DateTimeField(verbose_name=_('creation date'), auto_now_add=True)

  is_open = models.BooleanField(
    verbose_name=_('is open organization?'),
    help_text=_('Allow joining organization'), default=True)
  is_unlisted = models.BooleanField(verbose_name=_('is unlisted organization?'),
    help_text=_('Organization will not be listed'), default=True)

  slots = models.IntegerField(
    verbose_name=_('maximum size'), null=True, blank=True,
    help_text=_('Maximum amount of users in this organization, '
          'only applicable to private organizations'))
  access_code = models.CharField(
    max_length=7, help_text=_('Student access code'),
    verbose_name=_('access code'), null=True, blank=True)
  logo_url = models.CharField(
    verbose_name=_('logo url'), default='', max_length=256,
    blank=True,
    help_text=_('Link to organization logo.'))
  performance_points = models.FloatField(default=0)
  member_count = models.IntegerField(default=0)

  _pp_table = [pow(settings.VNOJ_ORG_PP_STEP, i) for i in range(settings.VNOJ_ORG_PP_ENTRIES)]

  def calculate_points(self, table=_pp_table):
    raise NotImplementedError
    # data = self.members.get_queryset().order_by('-performance_points') \
    #      .values_list('performance_points', flat=True).filter(performance_points__gt=0)
    # pp = settings.VNOJ_ORG_PP_SCALE * sum(ratio * pp for ratio, pp in zip(table, data))
    # if not float_compare_equal(self.performance_points, pp):
    #   self.performance_points = pp
    #   self.save(update_fields=['performance_points'])
    # return pp

  def on_user_changes(self):
    member_count = self.members.count()
    delta = member_count - self.member_count
    if delta != 0:
      ## Update recursively to all parent orgs
      traversal = self
      with transaction.atomic():
        while True:
          traversal.member_count += delta
          self.save(update_fields=['member_count'])
          if traversal.is_root():
            break
          traversal = traversal.get_parent()
    return member_count


  #### ==================================== Ancestors/Descendants helpers
  def is_suborg_of(self, org):
    return self.is_descendant_of(org)


  #### ==================================== Admin Helper
  @cached_property
  def direct_admins_list(self):
    return self.admins.all()

  @cached_property
  def admins_list(self):
    admins, trv = None, self
    while True:
      if admins is None:
        admins = trv.direct_admins_list
      else:
        admins |= trv.direct_admins_list
      if trv.is_root():
        break
      trv = trv.get_parent()
    return admins

  def is_direct_admin(self, user):
    return user in self.admins_list

  def is_admin(self, user):
    trv = self
    while True:
      if trv.is_direct_admin(user):
        return True
      if trv.is_root():
        break
      trv = trv.get_parent()
    return False

  #### ==================================== Tree moving helper Method
  def become_child_of(self, target):
    self.move(target, 'sorted-child')

  def become_root(self):
    if not self.is_root():
      root = self.get_root()
      self.move(root, 'sorted-sibling')

  #### ==================================== Model Method
  def add_child(self, *args, **kwargs):
    if self.get_depth() >= settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
      raise OrganizationTooDeepError()
    return super().add_child(*args, **kwargs)

  def move(self, target, pos=None):
    if type(pos) == str:
      if pos.endswith('child'): # Attempts to add child to target
        if target.get_depth() >= settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
          raise OrganizationTooDeepError()
      else: # Attempts to add siblings to target
        if target.get_depth() > settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
          raise OrganizationTooDeepError()
    super().move(target, pos)


  def save(self, *args, **kwargs):
    self.slug = self.slug.upper()
    return super().save(*args, **kwargs)

  def __contains__(self, item):
    if item is None:
      return False
    if isinstance(item, int):
      return self.members.filter(id=item).exists()
    elif isinstance(item, Profile):
      return self.members.filter(id=item.id).exists()
    else:
      raise TypeError('Organization membership test must be Profile or primary key')

  def __str__(self):
    return self.short_name

  # def get_absolute_url(self):
  #   return reverse('organization_home', args=(self.id, self.slug))

  # def get_users_url(self):
  #   return reverse('organization_users', args=(self.id, self.slug))

  class Meta:
    ordering = ['name']
    permissions = (
      ('organization_admin', _('Administer organizations')),
      ('edit_all_organization', _('Edit all organizations')),
      ('change_open_organization', _('Change is_open field')),
      ('spam_organization', _('Create organization without limit')),
    )
    verbose_name = _('organization')
    verbose_name_plural = _('organizations')


class OrganizationRequest(models.Model):
  user = models.ForeignKey('userprofile.UserProfile',
    verbose_name=_('user'), related_name='requests', on_delete=models.CASCADE)
  organization = models.ForeignKey(Organization,
    verbose_name=_('organization'), related_name='requests', on_delete=models.CASCADE)
  time = models.DateTimeField(verbose_name=_('request time'), auto_now_add=True)
  state = models.CharField(max_length=1, verbose_name=_('state'), choices=(
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
  ))
  reason = models.TextField(verbose_name=_('reason'))

  class Meta:
    verbose_name = _('organization join request')
    verbose_name_plural = _('organization join requests')
