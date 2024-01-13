# pylint: skip-file
from django.core.exceptions import ValidationError

from django.core.cache import cache
from django.db import models, transaction
from django.db.models import CASCADE, SET_NULL, Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _
from jsonfield import JSONField

from helpers.custom_pagination import Page10Pagination

from problem.models import Problem
from userprofile.models import UserProfile as Profile
from submission.models import Submission

from .contest import *
from .rating import *

__all__ = ['ContestParticipation']


class ContestParticipation(models.Model):
    LIVE = 0
    SPECTATE = -1

    contest = models.ForeignKey(Contest,
        verbose_name=_('associated contest'), related_name='users', on_delete=CASCADE)
    user = models.ForeignKey(Profile,
        verbose_name=_('user'), related_name='contest_history', on_delete=CASCADE)
    real_start = models.DateTimeField(
        verbose_name=_('start time'), default=timezone.now, db_column='start')

    score = models.FloatField(
        verbose_name=_('score'), default=0, db_index=True)
    cumtime = models.PositiveIntegerField(
        verbose_name=_('cumulative time'), default=0)
    tiebreaker = models.FloatField(
        verbose_name=_('tie-breaking field'), default=0.0)
    format_data = JSONField(
        verbose_name=_('contest format specific data'), null=True, blank=True)

    frozen_time = models.DateTimeField(
        verbose_name=_("frozen time"),
        help_text=_("time when frozen data was last written"),
        blank=True, null=True,
    )
    frozen_score = models.FloatField(
        verbose_name=_('frozen score'), default=0, db_index=True)
    frozen_cumtime = models.PositiveIntegerField(
        verbose_name=_('frozen cumulative time'), default=0)
    frozen_tiebreaker = models.FloatField(
        verbose_name=_('frozen tie-breaking field'), default=0.0)
    frozen_format_data = JSONField(
        verbose_name=_('contest format specific data'), null=True, blank=True)

    is_disqualified = models.BooleanField(
        verbose_name=_('is disqualified'), default=False,
        help_text=_('Whether this participation is disqualified.'))

    virtual = models.IntegerField(
        verbose_name=_('virtual participation id'), default=LIVE,
        help_text=_('0 means non-virtual, otherwise the n-th virtual participation.'))

    modified = models.DateTimeField(verbose_name=_('modified date'), null=True, auto_now=True)

    organization = models.ForeignKey(
        'organization.Organization', verbose_name=_('organization'),
        blank=True, null=True, on_delete=models.SET_NULL,
    )

    def recompute_results(self):
        with transaction.atomic():
            self.contest.format.update_participation(self)
            if self.is_disqualified:
                self.score = self.frozen_score = -9999
                self.cumtime = self.frozen_cumtime = 0
                self.tiebreaker = self.frozen_tiebreaker = 0
                self.save(update_fields=['score', 'cumtime', 'tiebreaker', 'frozen_score', 'frozen_cumtime', 'frozen_tiebreaker'])
    recompute_results.alters_data = True

    def set_disqualified(self, disqualified):
        self.is_disqualified = disqualified
        self.recompute_results()
        if self.contest.is_rated and self.contest.ratings.exists():
            self.contest.rate()
        if self.is_disqualified:
            if self.user.current_contest == self:
                self.user.remove_contest()
            self.contest.banned_users.add(self.user)
        else:
            self.contest.banned_users.remove(self.user)
    set_disqualified.alters_data = True

    @property
    def live(self):
        return self.virtual == self.LIVE

    @property
    def spectate(self):
        return self.virtual == self.SPECTATE

    @cached_property
    def start(self):
        contest = self.contest
        return contest.start_time if contest.time_limit is None and (self.live or self.spectate) else self.real_start

    @property
    def end_time(self):
        contest = self.contest
        if self.spectate:
            return contest.end_time
        if self.virtual:
            if contest.time_limit:
                return self.real_start + contest.time_limit
            else:
                return self.real_start + (contest.end_time - contest.start_time)
        return contest.end_time if contest.time_limit is None else \
            min(self.real_start + contest.time_limit, contest.end_time)

    @cached_property
    def _now(self):
        # This ensures that all methods talk about the same now.
        return timezone.now()

    @property
    def ended(self):
        return self.end_time is not None and self.end_time < self._now

    @property
    def time_remaining(self):
        end = self.end_time
        if end is not None and end >= self._now:
            return end - self._now

    @property
    def is_frozen(self):
        return self.contest.is_frozen

    # ========================== Cache helpers

    # ========================== Others
    def save(self, *args, **kwargs):
        self.modified = self._now
        return super().save(*args, **kwargs);

    def __str__(self):
        if self.spectate:
            return _('%s spectating in %s') % (self.user.username, self.contest.name)
        if self.virtual:
            return _('%s in %s, v%d') % (self.user.username, self.contest.name, self.virtual)
        return _('%s in %s') % (self.user.username, self.contest.name)

    class Meta:
        verbose_name = _('contest participation')
        verbose_name_plural = _('contest participations')
        unique_together = ('contest', 'user', 'virtual')
        ordering = ['-id']
