from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
User = get_user_model()

from userprofile.models import UserProfile as Profile

from judger.utils.float_compare import float_compare_equal

from helpers.fileupload import \
  path_and_rename_org_avatar, DEFAULT_ORG_AVATAR_URL


class Organization(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('organization title'))
    slug = models.SlugField(
      max_length=128, verbose_name=_('organization slug'),
      help_text=_('Organization name shown in URL'))
    short_name = models.CharField(
      max_length=20, verbose_name=_('short name'),
      help_text=_('Displayed beside user name during contests'))
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
    logo_override_image = models.CharField(
      verbose_name=_('Logo override image'), default='', max_length=150,
      blank=True,
      help_text=_('This image will replace the default site logo for users '
                  'viewing the organization.'))
    performance_points = models.FloatField(default=0)
    member_count = models.IntegerField(default=0)

    _pp_table = [pow(settings.VNOJ_ORG_PP_STEP, i) for i in range(settings.VNOJ_ORG_PP_ENTRIES)]

    def calculate_points(self, table=_pp_table):
        data = self.members.get_queryset().order_by('-performance_points') \
                   .values_list('performance_points', flat=True).filter(performance_points__gt=0)
        pp = settings.VNOJ_ORG_PP_SCALE * sum(ratio * pp for ratio, pp in zip(table, data))
        if not float_compare_equal(self.performance_points, pp):
            self.performance_points = pp
            self.save(update_fields=['performance_points'])
        return pp

    def on_user_changes(self):
        self.calculate_points()
        member_count = self.members.count()
        if self.member_count != member_count:
            self.member_count = member_count
            self.save(update_fields=['member_count'])

    @cached_property
    def admins_list(self):
        return self.admins.all()

    def is_admin(self, user):
        return user in self.admins_list

    def __contains__(self, item):
        if item is None:
            return False
        if isinstance(item, int):
            return self.members.filter(id=item).exists()
        elif isinstance(item, Profile):
            return self.members.filter(id=item.id).exists()
        else:
            raise TypeError('Organization membership test must be Profile or primany key')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organization_home', args=(self.id, self.slug))

    def get_users_url(self):
        return reverse('organization_users', args=(self.id, self.slug))

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
