import operator
from functools import reduce
from queue import Queue

from django.contrib.auth import get_user_model
User = get_user_model()

from django.conf import settings
from django.db import models
from django.db.models import Max, F
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.core.cache import cache
from django_extensions.db.models import TimeStampedModel
from django.db.models import Q

from bkdnoj.choices import TIMEZONE, ACE_THEMES

from helpers.get_cached_tree import get_cached_trees
from helpers.fileupload import \
    path_and_rename_avatar, DEFAULT_AVATAR_URL

from judger.models import Language
from judger.utils.float_compare import float_compare_equal


PROFILE_ORG_IDS_CACHE_TIMEOUT = 2 * 60 * 60 # 2 hours

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    first_name = models.CharField(
        max_length=50, verbose_name=_('first name'), blank=True
    )
    last_name = models.CharField(
        max_length=50, verbose_name=_('first name'), blank=True
    )
    email = models.EmailField(
        max_length=256, verbose_name=_('email'), blank=True
    )

    about = models.TextField(verbose_name=_("self-description"),
        null=True, blank=True)
    timezone = models.CharField(
        max_length=50, verbose_name=_('location'), choices=TIMEZONE,
        default=settings.DEFAULT_USER_TIME_ZONE)
    language = models.ForeignKey(Language,
        verbose_name=_('preferred language'), on_delete=models.SET_DEFAULT,
        default=Language.get_default_language_pk)

    points = models.FloatField(default=0, db_index=True)
    performance_points = models.FloatField(default=0, db_index=True)
    problem_count = models.IntegerField(default=0, db_index=True)

    ace_theme = models.CharField(max_length=30, choices=ACE_THEMES, default='github')
    last_access = models.DateTimeField(verbose_name=_('last access time'), default=now)
    ip = models.GenericIPAddressField(verbose_name=_('last IP'), blank=True, null=True)

    # organizations = SortedManyToManyField(Organization,
    organizations = models.ManyToManyField('organization.Organization',
        verbose_name=_('organization'), blank=True,
        related_name='members', related_query_name='member'
    )
    display_organization = models.ForeignKey('organization.Organization',
        verbose_name=_('display organization'),
        null=True, blank=True, default=None,
        related_name='representative_members', related_query_name='representative_member',
        on_delete=models.SET_NULL,
    )

    display_rank = models.CharField(
        max_length=10, default='user', verbose_name=_('display rank'),
        choices=settings.BKDNOJ_DISPLAY_RANKS)
    mute = models.BooleanField(
        verbose_name=_('comment mute'), help_text=_('Some users are at their best when silent.'),
        default=False)
    is_unlisted = models.BooleanField(
        verbose_name=_('unlisted user'), help_text=_('User will not be ranked.'),
        default=False)
    ban_reason = models.TextField(
        null=True, blank=True,
        help_text=_('Show to banned user in login page.'))

    rating = models.IntegerField(null=True, default=None)
    current_contest = models.OneToOneField('compete.ContestParticipation',
        verbose_name=_('current contest'),
        null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    notes = models.TextField(
        verbose_name=_('internal notes'), null=True, blank=True,
        help_text=_('Notes for administrators regarding this user.'))
    username_display_override = models.CharField(
        max_length=100, blank=True, verbose_name=_('display name override'),
        help_text=_('name displayed in place of username'))

    avatar = models.ImageField( upload_to=path_and_rename_avatar, default=DEFAULT_AVATAR_URL )

    @cached_property
    def organization(self):
        return self.display_organization

    @property
    def owner(self):
        return self.user
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @cached_property
    def username(self):
        return self.username_display_override or self.user.username

    @cached_property
    def display_name(self):
        return self.username_display_override or self.username

    @cached_property
    def has_any_solves(self):
        return self.submission_set.filter(points=F('problem__points')).exists()

    _pp_table = [pow(settings.DMOJ_PP_STEP, i) for i in range(settings.DMOJ_PP_ENTRIES)]

    def calculate_points(self, table=_pp_table):
        from problem.models import Problem
        public_problems = Problem.get_public_problems()
        data = (
            public_problems.filter(submission__user=self, submission__points__isnull=False)
                           .annotate(max_points=Max('submission__points')).order_by('-max_points')
                           .values_list('max_points', flat=True).filter(max_points__gt=0)
        )
        extradata = (
            public_problems.filter(submission__user=self, submission__result='AC').values('id').distinct().count()
        )
        bonus_function = settings.DMOJ_PP_BONUS_FUNCTION
        points = sum(data)
        problems = len(data)
        pp = sum(x * y for x, y in zip(table, data)) + bonus_function(extradata)
        if not float_compare_equal(self.points, points) or \
           problems != self.problem_count or \
           not float_compare_equal(self.performance_points, pp):
            self.points = points
            self.problem_count = problems
            self.performance_points = pp
            self.save(update_fields=['points', 'problem_count', 'performance_points'])
            for org in self.organizations.get_queryset():
                org.calculate_points()
        return points
    calculate_points.alters_data = True

    def ban_user(self, reason):
        self.ban_reason = reason
        self.display_rank = 'banned'
        self.is_unlisted = True
        self.save(update_fields=['ban_reason', 'display_rank', 'is_unlisted'])

        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
    ban_user.alters_data = True

    def set_image_to_default(self):
        self.avatar.delete(save=False) # delete old image file
        self.avatar = DEFAULT_AVATAR_URL
        self.save()


    @property
    def __cache_key_member_of_org_with_ids(self):
        return f"{self.__class__.__name__}-{self.id}-member-org-ids"

    """
        Return a SET of ID of organizations that this profile is a member of
    """
    @cached_property
    def member_of_org_with_ids(self):
        from organization.models import Organization

        q = None
        for org in self.organizations.all():#order_by('depth').all():
            if q is None: q = Q(id=org.id) 
            else: q |= Q(id=org.id)
            q |= Q(id__in=org.get_ancestors())

        for org in self.admin_of.all():#order_by('depth').all():
            if q is None: q = Q(id=org.id)
            else: q |= Q(id=org.id)
            q |= Q(id__in=org.get_descendants())
        
        if q is None:
            return set()

        data = set( Organization.objects.only('id').filter(q).distinct().values_list('id', flat=True) )
        return data

    """
        Experimental implementation for member_of_org_with_ids in attempt to improve speed
        Approaches:
        1. Look into django-mptt, and modify https://github.com/django-treebeard/django-treebeard/blob/master/treebeard/ns_tree.py into QuerySet.get_descendants()
        2. (In used) Basically my implementation, but do it at DB by calling get_descendents() and chaining Q objects together
            2.a Improved by cache the whole tree in memory, avoding N+1 problem.
    """
    @cached_property
    def __EXPERIMENTAL_member_of_org_with_ids(self):
        if data is None:
            from organization.models import Organization

            q = Q()
            for org in self.organizations.all():#order_by('depth').all():
                q |= Q(id=org.id)
                q |= Q(id__in=org.get_ancestors())

            for org in self.admin_of.all():#order_by('depth').all():
                q |= Q(id=org.id)
                q |= Q(id__in=org.get_descendants())

            data = set( Organization.objects.only('id').filter(q).distinct().values_list('id', flat=True) )
            cache.set(self.__cache_key_member_of_org_with_ids, data, PROFILE_ORG_IDS_CACHE_TIMEOUT)
        return data

    @property
    def __cache_key_admin_of_org_with_ids(self):
        return f"{self.__class__.__name__}-{self.id}-admin-org-ids"

    """
        Return a SET of ID of organizations that this profile is an admin of
    """
    @cached_property
    def admin_of_org_with_ids(self):
        # data = cache.get(self.__cache_key_admin_of_org_with_ids)
        from organization.models import Organization

        q = Q()
        for org in self.admin_of.all():#order_by('depth').all():
            q |= Q(id=org.id)
            q |= Q(id__in=org.get_descendants())

        data = set( Organization.objects.only('id').filter(q).distinct().values_list('id', flat=True) )
        return data
    
    """ Using cache, but doesn't improve much """
    def __EXPERIMENTAL_admin_of_org_with_ids(self):
        if self.admin_of.count() == 0:
            return set()

        data = cache.get(self.__cache_key_admin_of_org_with_ids)
        if data is None:
            from organization.models import Organization

            q = Q()
            for org in self.admin_of.all():#order_by('depth').all():
                q |= Q(id=org.id)
                q |= Q(id__in=org.get_descendants())

            data = set( Organization.objects.only('id').filter(q).distinct().values_list('id', flat=True) )
            cache.set(self.__cache_key_admin_of_org_with_ids, data, PROFILE_ORG_IDS_CACHE_TIMEOUT)
        return data

    def __invalidate_cache(self):
        cache.delete(self.__cache_key_admin_of_org_with_ids)
        cache.delete(self.__cache_key_member_of_org_with_ids)

    def __str__(self):
        name = f"{self.first_name} {self.last_name}"
        if not name.strip():
            name = "no name given"
        return f"@{self.owner.username} ({name})"

    class Meta:
        ordering = ['id']
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

        default_permissions = (
            'view', 'change', #'add', 'delete'
        )
        permissions = (
            # (, _()),
        )


class Badge(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('badge name'))
    mini = models.URLField(verbose_name=_('mini badge URL'), blank=True)
    full_size = models.URLField(verbose_name=_('full size badge URL'), blank=True)

    def __str__(self):
        return f"Badge {self.name}"
