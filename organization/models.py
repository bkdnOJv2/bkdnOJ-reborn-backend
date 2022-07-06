from queue import Queue
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.validators import MinLengthValidator

from treebeard.mp_tree import MP_Node

from .exceptions import OrganizationTooDeepError

from userprofile.models import UserProfile as Profile
from judger.utils.float_compare import float_compare_equal

from helpers.fileupload import \
  path_and_rename_org_avatar, DEFAULT_ORG_AVATAR_URL


ORGANIZATION_CACHE_DURATION = 30*60 # 30 mins

class Organization(MP_Node):
  # treebeard fields
  node_order_by = ['short_name']

  # model fields
  slug = models.SlugField(
    validators=[MinLengthValidator(3)],
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

  # Use to validate caches
  modified = models.DateTimeField(verbose_name=_('modified date'), null=True, auto_now=True)

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

  """
    Recalculate member count of this org
  """
  @classmethod
  def reupdate_tree_member_count(cls, root, wrapTransaction=True):
    if wrapTransaction:
      with transaction.atomic():
        mbcount = cls.reupdate_tree_member_count(root, False)
        return mbcount
    ##
    mbcount = root.members.count()
    for child in root.get_children().all():
      mbcount += cls.reupdate_tree_member_count(child, False)
    root.member_count = mbcount
    root.save(update_fields=['member_count'])
    return mbcount

  """
    Update member_count based on deltas
  """
  def on_user_changes(self):
    member_count = self.members.count()
    old_member_count = self._old_member_count
    delta = member_count - old_member_count
    if delta != 0:
      ## Update recursively to all parent orgs
      traversal = self
      with transaction.atomic():
        while True:
          traversal.member_count += delta
          traversal.save(update_fields=['member_count'])
          if traversal.is_root():
            break
          traversal = traversal.get_parent()
    return member_count

  def add_members(self, qs):
    self._old_member_count = self.members.count()
    self.members.add(*qs)
    self.save()
    self.on_user_changes()

  def remove_members(self, qs):
    self._old_member_count = self.members.count()
    self.members.remove(*qs)
    self.save()
    self.on_user_changes()

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
    delta = self.member_count
    with transaction.atomic():
      # Remove tree from parent
      if not self.is_root():
        traversal = self.get_parent()
        while True:
          traversal.member_count -= delta
          traversal.save(update_fields=['member_count'])
          if traversal.is_root():
            break
          traversal = traversal.get_parent()
      # Move the tree
      self.move(target, 'sorted-child')
      # Update the new parent tree
      traversal = target
      while True:
        traversal.member_count += delta
        traversal.save(update_fields=['member_count'])
        if traversal.is_root():
          break
        traversal = traversal.get_parent()
    # End transaction

  def become_root(self):
    if not self.is_root():
      with transaction.atomic():
        delta = -self.member_count
        if delta != 0 and not self.is_root():
          traversal = self.get_parent()
          while True:
            traversal.member_count += delta
            traversal.save(update_fields=['member_count'])
            if traversal.is_root():
              break
            traversal = traversal.get_parent()
        ## Move
        root = self.get_root()
        self.move(root, 'sorted-sibling')

  #### ==================================== Model Method
  def add_child(self, **kwargs):
    if self.get_depth() >= settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
      raise OrganizationTooDeepError()
    return super().add_child(**kwargs)

  def move(self, target, pos=None):
    if self == target:
      raise ValueError("Node and Parent node must be different.")
    if type(pos) == str:
      if pos.endswith('child'): # Attempts to add child to target
        if target.get_depth() >= settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
          raise OrganizationTooDeepError()
      else: # Attempts to add siblings to target
        if target.get_depth() > settings.BKDNOJ_ORG_TREE_MAX_DEPTH:
          raise OrganizationTooDeepError()
    super().move(target, pos)


  def delete(self):
    delta = -self.members.count()
    if delta != 0:
      ## Update recursively to all parent orgs
      traversal = self
      with transaction.atomic():
        while True:
          traversal.member_count += delta
          traversal.save(update_fields=['member_count'])
          if traversal.is_root():
            break
          traversal = traversal.get_parent()
    super().delete()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._old_member_count = self.member_count

  def clean(self):
    if len(self.slug) < 3:
      raise ValidationError("Slug must be longer than 2 characters")
    return True

  #### =================================
  """
    Given a Tree, and two list of nodes A and B, check if exists
    a pair of node (a, b) that a is an ancestor of b.
    Complexity: O(a + settings.BKDNOJ_ORG_TREE_MAX_DEPTH * b)
  """
  @classmethod
  def exists_pair_of_ancestor_descendant(cls, ancestors, descendants):
      ### Implementation 1:
      ancestor_ids = set(ancestors.values_list('id', flat=True))

      for descendant in descendants:
        # trvs = descendant
        # while True:
        #   if trvs.id in ancestor_ids: return True
        #   if trvs.is_root(): break
        #   trvs = trvs.get_parent()

        if descendant.id in ancestor_ids:
          return True
        path = list(descendant.get_ancestors().values_list('id', flat=True))
        for node_id in path:
          if node_id in ancestor_ids:
            return True
      return False

      ### Implementation 2
      # q1 = Q()
      # for org in descendants.only('id').all():#order_by('depth').all():
      #     q1 |= Q(id=org.id)
      #     q1 |= Q(id__in=org.get_ancestors())

      # q2 = Q()
      # for org in ancestors.only('id').all():#order_by('depth').all():
      #     q2 |= Q(id=org.id)
      #     q2 |= Q(id__in=org.get_descendants())

      # orgs = Organization.objects.only('id').all()
      # return (orgs.filter(q1) & orgs.filter(q2)).exists()

  def is_accessible_by(self, user):
    if not self.is_unlisted:
      return True # And their parents too! Which is what I am going to enforce.

    if not user.is_authenticated:
      return False

    # Unlisted, and User is logged-in
    if user.is_superuser: # or user.has_perm('organization.see_all_organizations'):
      return True

    ## Check for member-ship
    ## For every org that this person is in, check if this org is a sub_org of `self`
    for descen_org in user.profile.organizations.all():
      if self==descen_org or descen_org.is_descendant_of(self):
        return True

    ## Check for admin-ship
    ## For every org that this person is an admin of, check if this org is a sub_org of `self`
    for ances_org in user.profile.admin_of.all():
      if self==ances_org or self.is_descendant_of(ances_org):
        return True

    return False

  def is_editable_by(self, user):
    if not user.is_authenticated:
      return False
    if user.is_superuser: # or user.has_perm('organization.edit_all_organizations'):
      return True
    ## Check for admin-ship
    ## For every org that this person is an admin of, check if this org is a sub_org of `self`
    for ances_org in user.profile.admin_of.all():
      if self==ances_org or self.is_descendant_of(ances_org):
        return True
    return False

  @classmethod
  def get_public_root_organizations(cls):
    return cls.get_root_nodes().filter(is_unlisted=False)

  @classmethod
  def get_visible_root_organizations(cls, user):
    if not user.is_authenticated:
      return cls.get_public_root_organizations()

    if user.has_perm("organization.see_all_organization") or user.has_perm("organization.edit_all_organization"):
      return cls.get_root_nodes().all()

    return Organization.objects.filter(Q(id__in=user.profile.admin_of.all()) | Q(id__in=user.profile.organizations.all())).distinct()

  @classmethod
  def get_visible_organizations(cls, user):
    if not user.is_authenticated:
      return Organization.get_visible_root_organizations(user)

    if user.has_perm("organization.see_all_organizations"):
      return Organization.objects.all()

    # ids = set()

    # for org in cls.get_visible_root_organizations(user):
    #   q = Queue()
    #   q.put(org)
    #   while not q.empty():
    #     top = q.get()
    #     ids.add(top.id)
    #     for child in top.get_children():
    #       if not child.id in ids:
    #         q.put(child)

    return Organization.objects.filter(Q(id__in=user.profile.member_of_org_with_ids)
              | Q(id__in=user.profile.admin_of_org_with_ids) )

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

  @cached_property
  def _now(self):
    return timezone.now()

  # def get_absolute_url(self):
  #   return reverse('organization_home', args=(self.id, self.slug))

  # def get_users_url(self):
  #   return reverse('organization_users', args=(self.id, self.slug))

  @cached_property
  def cache_key(self):
    return f"{self.__class__.__name__}-{self.id}"

  def set_cache(self, data):
    cache_val = {
      'data': data,
      'cached_at': self.modified,
    }
    cache.set(
      self.cache_key, cache_val, ORGANIZATION_CACHE_DURATION
    )

  def get_cache(self):
    cache_dict = cache.get(self.cache_key)
    if cache_dict is None:
      return None

    if cache_dict.get('cached_at') and cache_dict.get('cached_at') == self.modified:
      return cache_dict.get('data')
    return None

  def save(self, *args, **kwargs):
    if not kwargs.get('update_modified_only'):
      self.slug = self.slug.upper()
      self.clean()
    else:
      kwargs.pop('update_modified_only')

    self.modified = self._now

    res = super().save(*args, **kwargs)
    if not self.is_root():
      kwargs['update_modified_only'] = True
      self.get_parent().save(*args, **kwargs)
    return res


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
