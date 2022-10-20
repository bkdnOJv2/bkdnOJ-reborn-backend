from functools import lru_cache

from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, \
    RegexValidator, MinLengthValidator

from django.core.cache import cache
from django.db import models, transaction
from django.db.models import CASCADE, SET_NULL, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _
from jsonfield import JSONField

from helpers.custom_pagination import Page10Pagination

from problem.models import Problem
from organization.models import Organization
from userprofile.models import UserProfile as Profile
from submission.models import Submission
from compete.ratings import rate_contest
from compete import contest_format

__all__ = ['Contest', 'ContestTag']

from .rating import Rating

class MinValueOrNoneValidator(MinValueValidator):
    def compare(self, a, b):
        return a is not None and b is not None and super().compare(a, b)


class ContestTag(models.Model):
    color_validator = RegexValidator('^#(?:[A-Fa-f0-9]{3}){1,2}$', _('Invalid colour.'))

    name = models.CharField(
        max_length=20, verbose_name=_('tag name'),
        unique=True, db_index=True, #unique implies db_index=True
        validators=[RegexValidator(r'^[a-z-]+$',
                    message=_('Lowercase letters and hyphens only.'))
                    ]
    )
    color = models.CharField(max_length=7, verbose_name=_('tag colour'), validators=[color_validator])
    description = models.TextField(verbose_name=_('tag description'), blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contest_tag', args=[self.name])

    @property
    def text_color(self, cache={}):
        if self.color not in cache:
            if len(self.color) == 4:
                r, g, b = [ord(bytes.fromhex(i * 2)) for i in self.color[1:]]
            else:
                r, g, b = [i for i in bytes.fromhex(self.color[1:])]
            cache[self.color] = '#000' if 299 * r + 587 * g + 144 * b > 140000 else '#fff'
        return cache[self.color]

    class Meta:
        verbose_name = _('contest tag')
        verbose_name_plural = _('contest tags')


class Contest(models.Model):
    SCOREBOARD_VISIBLE = 'V'
    SCOREBOARD_AFTER_CONTEST = 'C'
    SCOREBOARD_AFTER_PARTICIPATION = 'P'
    SCOREBOARD_VISIBILITY = (
        (SCOREBOARD_VISIBLE, _('Visible')),
        (SCOREBOARD_AFTER_CONTEST, _('Hidden for duration of contest')),
        (SCOREBOARD_AFTER_PARTICIPATION, _('Hidden for duration of participation')),
    )
    # ---------------------
    key = models.CharField(max_length=20, verbose_name=_('contest identifier'),
        unique=True, db_index=True, #unique implies db_index=True
        validators=[
            RegexValidator('^[a-z][a-z0-9\-_]+$',
               _('Contest identifier must starts with a letter, contains only letters (lowercase), digits, and dashes.')),
            MinLengthValidator(4),
        ]
    )
    name = models.CharField(max_length=100, verbose_name=_('contest name'), db_index=True)

    description = models.TextField(verbose_name=_('description'), blank=True)
    problems = models.ManyToManyField(Problem, verbose_name=_('problems'), through='ContestProblem')

    start_time = models.DateTimeField(verbose_name=_('start time'), db_index=True)
    end_time = models.DateTimeField(verbose_name=_('end time'), db_index=True)
    time_limit = models.DurationField(verbose_name=_('time limit'), blank=True, null=True)

    locked_after = models.DateTimeField(
        verbose_name=_('contest lock'), null=True, blank=True,
        help_text=_('Prevent submissions from this contest '
                    'from being rejudged after this date.'))

    ## Visibility/Accessibility
    authors = models.ManyToManyField(Profile, help_text=_('These users will be able to edit the contest.'),
                                     related_name='authors+')
    collaborators = models.ManyToManyField(Profile,
        help_text=_('These users will be able to edit the contest, '
                    'but will not be listed as authors.'),
        related_name='collaborators+', blank=True)
    reviewers = models.ManyToManyField(Profile,
        help_text=_('These users will be able to view the contest, '
                    'but not edit it.'),
        blank=True, related_name='reviewers+')


    published = models.BooleanField(
        verbose_name=_('contest published'), default=False,
        help_text=_('Allow users beside authors, collaborators, reviewers to see the contest'),
    )

    is_visible = models.BooleanField(
        verbose_name=_('publicly visible'), default=False,
        help_text=_('Allow contest data to be viewed by anyone'),
    )

    ## Private contestants/organizations
    is_private = models.BooleanField(
        verbose_name=_('private to specific users'), default=False
    )
    private_contestants = models.ManyToManyField(Profile,
        blank=True, verbose_name=_('private contestants'),
        help_text=_('If private, only these users may register to the contest'),
        related_name='private_contestants+'
    )

    is_organization_private = models.BooleanField(
        verbose_name=_('private to organizations'), default=False)
    organizations = models.ManyToManyField(Organization,
        blank=True, verbose_name=_('organizations'),
        help_text=_('If private, only these organizations may register to the contest')
    )

    banned_users = models.ManyToManyField(Profile,
        verbose_name=_('Banned users'), blank=True,
        help_text=_('Bans the selected users from joining this contest.'))

    ## Scoreboard
    scoreboard_cache_duration = models.PositiveIntegerField(
        verbose_name=_('scoreboard cache timeout'),
        default=0,
        help_text=_('How long (seconds) should scoreboard will be cached. '
                    'Set to 0 to disable')
    )

    view_contest_scoreboard = models.ManyToManyField(
        Profile,
        verbose_name=_('view contest scoreboard'), blank=True,
        related_name='view_contest_scoreboard',
        help_text=_('These users will be able to view the scoreboard.')
    )

    scoreboard_visibility = models.CharField(
        verbose_name=_('scoreboard visibility'), default=SCOREBOARD_VISIBLE,
        max_length=1, choices=SCOREBOARD_VISIBILITY,
        help_text=_('Scoreboard visibility through the duration of the contest')
    )

    ## Freezing
    enable_frozen = models.BooleanField(
        verbose_name=_("enable contest freezing"),
        help_text=_("Enable scoreboard/submission freezing, "
            "stop showing actual results after 'frozen_time'."),
        default=True, db_index=True,
    )
    frozen_time = models.DateTimeField(
        verbose_name=_("freeze after"),
        help_text=_("Timestamp to freeze results, if 'enable_frozen' is True"),
        blank=True, null=True,
    )

    use_clarifications = models.BooleanField(
        verbose_name=_('Allow clarification request'),
        help_text=_('Allow participants to use the clarification system.'),
        default=False,
    )

    ## Rating
    is_rated = models.BooleanField(
        verbose_name=_('contest rated'), help_text=_('Whether this contest can be rated.'),
        default=False
    )
    rating_floor = models.IntegerField(
        verbose_name=('rating floor'), help_text=_('Rating floor for contest'),
        null=True, blank=True)

    rating_ceiling = models.IntegerField(
        verbose_name=('rating ceiling'), help_text=_('Rating ceiling for contest'),
        null=True, blank=True)
    rate_all = models.BooleanField(
        verbose_name=_('rate all'), help_text=_('Rate all users who joined.'), default=False
    )
    rate_exclude = models.ManyToManyField(
        Profile, verbose_name=_('exclude from ratings'), blank=True,
        related_name='rate_exclude+'
    )

    hide_problem_tags = models.BooleanField(
        verbose_name=_('hide problem tags'),
        help_text=_('Whether problem tags should be hidden by default.'),
        default=False)

    hide_problem_authors = models.BooleanField(
        verbose_name=_('hide problem authors'),
        help_text=_('Whether problem authors should be hidden by default.'),
        default=False)

    run_pretests_only = models.BooleanField(
        verbose_name=_('run pretests only'),
        default=False,
        help_text=_('Whether judges should grade pretests only, versus all '
                    'testcases. Commonly set during a contest, then unset '
                    'prior to rejudging user submissions when the contest ends.'),
    )

    show_short_display = models.BooleanField(
        verbose_name=_('show short form settings display'),
        help_text=_('Whether to show a section containing contest settings '
                    'on the contest page or not.'),
        default=False)

    # og_image = models.CharField(verbose_name=_('OpenGraph image'), default='', max_length=150, blank=True)
    # logo_override_image = models.CharField(
    #     verbose_name=_('Logo override image'), default='', max_length=150, blank=True,
    #     help_text=_('This image will replace the default site logo for users '
    #                 'inside the contest.')
    # )

    tags = models.ManyToManyField(ContestTag,
        verbose_name=_('contest tags'), blank=True, related_name='contests'
    )

    # summary = models.TextField(blank=True, verbose_name=_('contest summary'),
    #                            help_text=_('Plain-text, shown in meta description tag, e.g. for social media.'))

    access_code = models.CharField(
        verbose_name=_('access code'), blank=True, default='', max_length=255,
        help_text=_('An optional code to prompt contestants before they are allowed '
                    'to join the contest. Leave it blank to disable.'))

    format_name = models.CharField(
        verbose_name=_('contest format'), default='icpc', max_length=32,
        choices=contest_format.choices(), help_text=_('The contest format module to use.')
    )
    format_config = JSONField(
        verbose_name=_('contest format configuration'), null=True, blank=True,
        help_text=_('A JSON object to serve as the configuration for the chosen contest format '
                    'module. Leave empty to use None. Exact format depends on the contest format '
                    'selected.')
    )
    user_count = models.IntegerField(verbose_name=_('the amount of live participants'), default=0)

    points_precision = models.IntegerField(
        verbose_name=_('precision points'), default=3,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text=_('Number of digits to round points to.'))

    modified = models.DateTimeField(verbose_name=_('modified date'), null=True, auto_now=True)
    standing_date = models.DateTimeField(verbose_name=_('standing date'), null=True, auto_now_add=True)
    standing_outdated_reason = models.CharField(verbose_name=_('standing outdated reason'),
        max_length=255, blank=True, default='', help_text=_('reason for why Standing is outdated'))

    STANDING_RELATED_FIELDS = ['frozen_time', 'format_name', 'points_precision', 'format_config', 'banned_users']
    def __init__(self, *args, **kwargs):
        super(Contest, self).__init__(*args, **kwargs)

        ## BUG: `getattr`` cause a recursion with 'format_config' and 'banned_users', might be mutability issue
        # for field in Contest.STANDING_RELATED_FIELDS:
        #     setattr(self, f"__{field}", getattr(self, field, None))

    @cached_property
    def format_class(self):
        return contest_format.formats[self.format_name]

    @cached_property
    def format(self):
        return self.format_class(self, self.format_config)

    @cached_property
    def get_label_for_problem(self):
        return self.format.get_label_for_problem

    @cached_property
    def author_ids(self):
        return Contest.authors.through.objects.filter(contest=self).\
                values_list('userprofile_id', flat=True)

    @cached_property
    def editor_ids(self):
        return self.author_ids.union(
            Contest.collaborators.through.objects.filter(contest=self).\
            values_list('userprofile_id', flat=True)
        )

    @cached_property
    def tester_ids(self):
        return Contest.reviewers.through.objects.filter(contest=self).\
                values_list('userprofile_id', flat=True)

    @cached_property
    def can_join(self):
        return self.start_time <= self._now

    """
        Check scoreboard visibility mode and contest is ended or not
    """
    @cached_property
    def show_scoreboard(self):
        # if not self.can_join:
        #     return False
        if (self.scoreboard_visibility in \
                (self.SCOREBOARD_AFTER_CONTEST, self.SCOREBOARD_AFTER_PARTICIPATION) and
                not self.ended):
            return False
        return True

    """
        Check if user can see the normal scoreboard
    """
    def can_see_scoreboard(self, user):
        if self.can_see_full_scoreboard(user):
            return True
        return self.show_scoreboard

    """
        See full scoreboard means: Seeing pass the frozen, or hidden scoreboard
    """
    def can_see_full_scoreboard(self, user):
        if not self.published:
            return False

        ## Scoreboard is private, or frozen then only added users can see, check for them
        if not self.show_scoreboard or self.is_frozen:
            if not user.is_authenticated:
                return False

            ### TODO check for perms
            ## Only reveal hidden scoreboard to editors
            if user.is_superuser or user.profile.id in self.editor_ids:
                return True

            ## Admin of orgs
            if self.is_organization_private and \
                Organization.exists_pair_of_ancestor_descendant(user.profile.admin_of.all(), self.organizations.all()):
                    return True

            ## And added individuals
            # if self.view_contest_scoreboard.filter(user__id=user.profile.id).exists():
            #     return True

            return False
        return True

    @property
    def contest_window_length(self):
        return self.end_time - self.start_time

    @cached_property
    def _now(self):
        # This ensures that all methods talk about the same now.
        return timezone.now()

    @property
    def time_before_start(self):
        if self.start_time >= self._now:
            return self.start_time - self._now
        else:
            return None

    @property
    def time_before_end(self):
        if self.end_time >= self._now:
            return self.end_time - self._now
        else:
            return None

    @cached_property
    def ended(self):
        return self.end_time < self._now

    @cached_property
    def started(self):
        return self.start_time <= self._now

    @cached_property
    def is_frozen_time(self):
        return self.frozen_time <= self._now

    @cached_property
    def is_frozen(self):
        return self.enable_frozen and self.is_frozen_time

    def set_standing_outdated_reason(self, reasons):
        Contest.objects.filter(id=self.id).update(standing_outdated_reason=(', '.join(reasons))[:255])

    def append_standing_outdated_reason(self, new_reasons):
        reasons = self.standing_outdated_reason.split(', ')
        reasons += new_reasons
        reasons = [rs for rs in reasons if rs.strip() != '']
        self.set_standing_outdated_reason(reasons)

    # def get_absolute_url(self):
    #    return reverse('contest_view', args=(self.key,))
    def recompute_standing(self):
        # Schedule recomputing job after editting Contest Problems list
        from compete.tasks import recompute_standing
        async_status = recompute_standing.delay(self.id)
        Contest.objects.filter(id=self.id).update(standing_date=self.modified, standing_outdated_reason='')
        self.clear_cache()

    def update_user_count(self):
        self.user_count = self.users.filter(virtual=0).count()
        self.save()

    update_user_count.alters_data = True

    class Inaccessible(Exception):
        pass

    class PrivateContest(Exception):
        pass

    """
        User can edit Contest details
    """
    def is_editable_by(self, user): # TODO: we should figure out how to cache and invalidate cache this
        if not user.is_authenticated:
            return False

        # If the user can edit all contests
        if user.is_superuser or user.has_perm('compete.edit_all_contest'):
            return True

        # If the user is a contest organizer or curator
        if user.profile.id in self.editor_ids:
            return True

        if self.published and self.is_organization_private and Organization.exists_pair_of_ancestor_descendant(
            user.profile.admin_of.all(), self.organizations.all()
        ):
            return True
        return False

    """
        User can test Contest
    """
    def is_testable_by(self, user): # TODO: we should figure out how to cache and invalidate cache this
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.profile.id in self.tester_ids:
            return True
        return self.is_editable_by(user)

    """
        Check if user can access contest in general
    """
    def is_accessible_by(self, user): # TODO: we should figure out how to cache and invalidate cache this
        # Unauthenticated users can only see visible, non-private contests
        if not user.is_authenticated:
            if self.published and self.is_visible:
                return True
            return False

        if self.is_testable_by(user):
            return True

        if not self.published:
            return False

        if self.is_visible:
            return True

        if self.is_organization_private and Organization.exists_pair_of_ancestor_descendant(
                self.organizations.all(), user.profile.organizations.all()):
            return True

        if self.is_private and self.private_contestants.filter(user__id=user.profile.id).exists():
            return True

        return False
    
    """
        Check is user can access contest after it started
    """
    def is_accessible_at_start_time_by(self, user):
        return self.started and self.is_accessible_by(user)

    """
        Check if user is currently participating the contest (virtual or live)
    """
    def is_in_contest(self, user):
        # Check if user still have parts in the contest
        # We checks this because later we have to take care of Virtual Participations

        # Because Participations are in `date` order, and we only allow 1 participation
        # that is not ended per user/contest. So, we only need to check the last Part.
        if user.is_authenticated:
            if self.banned_users.filter(id=user.profile.id).exists():
                return False

            participation = self.users.filter(user=user.profile).last()
            if participation and not participation.ended: return True
        return False

    """
        Check if user is has already completed participating in the contest
    """
    def has_completed_contest(self, user):
        if user.is_authenticated:
            participation = self.users.filter(user=user.profile).last()
            if participation and participation.ended: return True
        return False


    def is_registerable_by(self, user):
        if not user.is_authenticated:
            return None

        if user.is_superuser or user.has_perm('contest.see_private_contest') or user.has_perm('contest.edit_all_contest'):
            return 'SPECTATE'

        if user.profile.id in self.editor_ids:
            return 'SPECTATE'

        if user.profile.id in self.tester_ids:
            return 'SPECTATE'

        if not self.published:
            return None

        if self.banned_users.filter(id=user.profile.id).exists():
            return None

        if self.is_visible and (not self.is_private) and (not self.is_organization_private):
            return 'LIVE'

        if self.is_organization_private and Organization.exists_pair_of_ancestor_descendant(
                self.organizations.all(), user.profile.organizations.all()):
            return 'LIVE'

        if self.is_private and self.private_contestants.filter(user__id=user.profile.id).exists():
            return 'LIVE'

        return None

    @classmethod
    def get_public_contests(cls):
        return cls.objects.filter(published=True, is_visible=True).defer('description').distinct()

    @classmethod
    def get_visible_contests(cls, user):
        if not user.is_authenticated:
            return cls.get_public_contests()

        queryset = cls.objects.only('key', 'name', 'format_name', 'is_rated', 'published', 'is_visible',
                    'is_private', 'is_organization_private', 'start_time', 'end_time', 'time_limit',
                    'enable_frozen', 'frozen_time', 'user_count').filter()

        if not (user.has_perm('compete.see_private_contest') or user.has_perm('compete.edit_all_contest')): # superuser included
            q=Q(published=True) & (
                Q(is_visible=True) |
                Q(is_private=True, private_contestants=user.profile) |
                Q(is_organization_private=True, organizations__in=user.profile.member_of_org_with_ids)
            )

            q |= Q(authors=user.profile)
            q |= Q(collaborators=user.profile)
            q |= Q(reviewers=user.profile)

            queryset = queryset.filter(q)
        return queryset.distinct()

    @classmethod
    def get_org_visible_contests(cls, org, recursive=False):
        queryset = cls.objects.only('key', 'name', 'format_name', 'is_rated', 'published', 'is_visible',
                    'is_private', 'is_organization_private', 'start_time', 'end_time', 'time_limit',
                    'enable_frozen', 'frozen_time', 'user_count').filter()

        if recursive:
            q = (
                Q(published=True, is_organization_private=True) & (
                    Q(organizations__id=org.id) | Q(organizations__id__in=org.get_ancestors().values_list('id', flat=True))
                )
            )
        else:
            q = Q(published=True, is_organization_private=True) & Q(organizations__id=org.id)

        return queryset.filter(q).distinct()

    def rate(self):
        with transaction.atomic():
            Rating.objects.filter(contest__end_time__range=(self.end_time, self._now)).delete()
            for contest in Contest.objects.filter(
                is_rated=True, end_time__range=(self.end_time, self._now),
            ).order_by('end_time'):
                rate_contest(contest)

    def renumerate_problems(self):
        numbering = 0
        problems = self.contest_problems.all()
        for prob in problems:
            prob.order = numbering
            prob.save(update_fields=['order'])
            numbering += 1

    ## Clear scoreboard cache
    def clear_scoreboard_cache(self):
        keys = []
        for view_mode in ['full', 'froze']:
            cache_key = f"contest-{self.key}-scoreboard-{view_mode}"
            keys.append(cache_key)
        cache.delete_many(keys)

    ## cache_keys
    @property
    def participants_cache_key(self):
        cache_key = f"contest-{self.key}-participants-full"
        return cache_key

    def clear_cache(self):
        keys = [self.participants_cache_key]
        for view_mode in ['full', 'froze']:
            cache_key = f"contest-{self.key}-scoreboard-{view_mode}"
            keys.append(cache_key)
        cache.delete_many(keys)

    ## Django model methods
    def clean(self):
        if self.time_limit != None and self.time_limit.total_seconds() < 0:
            raise ValidationError(
                _("time_limit cannot be negative"),
                code='invalid')

        # Django will complain if you didn't fill in start_time or end_time, so we don't have to.
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                _("Contest cannot have `end_time` <= `start_time`."),
                code='invalid')
        self.format_class.validate(self.format_config)

        if self.frozen_time is None:
            _frozen_after = self.end_time - timedelta(hours=1)
            if _frozen_after <= self.start_time:
                delta = self.end_time - self.start_time
                _frozen_after = self.start_time + delta/3*2
            self.frozen_time = _frozen_after

        try:
            # a contest should have at least one problem, with contest problem index 0
            # so test it to see if the script returns a valid label.
            label = self.get_label_for_problem(0)
        except Exception as e:
            raise ValidationError('Contest problem label script: %s' % e)
        else:
            if not isinstance(label, str):
                raise ValidationError('Contest problem label script: script should return a string.')

    def save(self, *args, **kwargs):
        self.clean()
        cont = super().save(*args, **kwargs)
        self.clear_scoreboard_cache()
        return cont

    def __str__(self):
        return self.name

    class Meta:
        # permissions = (
        #     ('see_private_contest', _('See private contests')),
        #     ('edit_own_contest', _('Edit own contests')),
        #     ('edit_all_contest', _('Edit all contests')),
        #     ('clone_contest', _('Clone contest')),
        #     ('moss_contest', _('MOSS contest')),
        #     ('contest_rating', _('Rate contests')),
        #     ('contest_access_code', _('Contest access codes')),
        #     ('create_private_contest', _('Create private contests')),
        #     ('change_contest_visibility', _('Change contest visibility')),
        #     ('contest_problem_label', _('Edit contest problem label script')),
        #     ('lock_contest', _('Change lock status of contest')),
        # )
        verbose_name = _('contest')
        verbose_name_plural = _('contests')
        ordering = ['-id']

