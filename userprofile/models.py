from django.contrib.auth import get_user_model
User = get_user_model()

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.timezone import now
from django_extensions.db.models import TimeStampedModel

from bkdnoj.choices import TIMEZONE, ACE_THEMES
from helpers.fileupload import \
    path_and_rename_avatar, DEFAULT_AVATAR_URL
from judger.models import Language

class UserProfile(TimeStampedModel):
    owner = models.OneToOneField(User,
        on_delete=models.CASCADE, primary_key=True,
        related_name='profile',
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
        related_name='members', related_query_name='member')
    display_rank = models.CharField(
        max_length=10, default='user', verbose_name=_('display rank'),
        choices=(   ('user', _('Normal User')),
                    ('setter', _('Problem Setter')),
                    ('admin', _('Admin')))
    )
    mute = models.BooleanField(
        verbose_name=_('comment mute'), help_text=_('Some users are at their best when silent.'),
        default=False
    )
    is_unlisted = models.BooleanField(
        verbose_name=_('unlisted user'), help_text=_('User will not be ranked.'),
        default=False)
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

    @property
    def user(self):
        return self.owner # For compatibility with DMOJ

    @property
    def first_name(self):
        return self.owner.first_name

    @property
    def last_name(self):
        return self.owner.last_name

    @cached_property
    def organization(self):
        # We do this to take advantage of prefetch_related
        orgs = self.organizations.all()
        return orgs[0] if orgs else None

    @cached_property
    def username(self):
        return self.user.username

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
        entries = min(len(data), len(table))
        pp = sum(map(mul, table[:entries], data[:entries])) + bonus_function(extradata)
        if self.points != points or problems != self.problem_count or self.performance_points != pp:
            self.points = points
            self.problem_count = problems
            self.performance_points = pp
            self.save(update_fields=['points', 'problem_count', 'performance_points'])
        return points

    calculate_points.alters_data = True

    def remove_contest(self):
        self.current_contest = None
        self.save()
    remove_contest.alters_data = True

    def update_contest(self):
        contest = self.current_contest
        if contest is not None and (contest.ended or not contest.contest.is_accessible_by(self.user)):
            self.remove_contest()
    update_contest.alters_data = True

    def set_image_to_default(self):
        self.avatar.delete(save=False) # delete old image file
        self.avatar = DEFAULT_AVATAR_URL
        self.save()

    def __str__(self):
        name = f"{self.first_name} {self.last_name}"
        if not name.strip():
            name = "no name given"
        return f"@{self.owner.username} ({name})"

    class Meta:
        ordering = ['owner']
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

        default_permissions = ( 
            'view', 'change', #'add', 'delete'
        )
        permissions = (
            # (, _()),
        )

