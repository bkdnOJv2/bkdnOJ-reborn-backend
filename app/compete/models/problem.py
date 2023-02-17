from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import CASCADE
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _

from problem.models import Problem

from .contest import *
from .rating import *

__all__ = [
    'ContestProblem',
    'MinValueOrNoneValidator',
]


class MinValueOrNoneValidator(MinValueValidator):
    def compare(self, a, b):
        return a is not None and b is not None and super().compare(a, b)


class ContestProblem(models.Model):
    problem = models.ForeignKey(Problem,
                                verbose_name=_('problem'), related_name='contests', on_delete=CASCADE)
    contest = models.ForeignKey(Contest,
                                verbose_name=_('contest'), related_name='contest_problems', on_delete=CASCADE)
    points = models.IntegerField(verbose_name=_('points'))
    partial = models.BooleanField(default=True, verbose_name=_('partial'))
    is_pretested = models.BooleanField(
        default=False, verbose_name=_('is pretested'))

    order = models.PositiveIntegerField(
        db_index=True, verbose_name=_('order'))

    output_prefix_override = models.IntegerField(
        verbose_name=_('output prefix length override'),
        default=0, null=True, blank=True)
    max_submissions = models.IntegerField(
        validators=[MinValueOrNoneValidator(1, _('Why include a problem you '
                                                 "can't submit to?"))],
        help_text=_('Maximum number of submissions for this problem, '
                    'or leave blank for no limit.'),
        default=None, null=True, blank=True,
    )

    solved_count = models.PositiveIntegerField(default=0,
                                               help_text=_(
                                                   "Number of users who has solved this problem"),
                                               )
    attempted_count = models.PositiveIntegerField(default=0,
                                                  help_text=_(
                                                      "Number of users who has attempted this problem"),
                                                  )
    frozen_solved_count = models.PositiveIntegerField(default=0,
                                                      help_text=_(
                                                          "Number of users who has solved this problem before frozen time"),
                                                      )
    frozen_attempted_count = models.PositiveIntegerField(default=0,
                                                         help_text=_(
                                                             "Number of users who has attempted this problem before frozen time"),
                                                         )
    modified = models.DateTimeField(verbose_name=_(
        'modified date'), null=True, auto_now=True)

    @cached_property
    def label(self):
        return self.contest.get_label_for_problem(self.order)

    def expensive_recompute_stats(self, force_update=False):
        contest = self.contest
        liveparts = contest.users.filter(
            virtual=0).values_list('user_id', flat=True)
        queryset = self.submissions.prefetch_related('submission', 'submission_user').\
            filter(submission__user__in=liveparts)

        totals = queryset.values_list('submission__user').distinct().count()
        # ContestSubmission.points >= ContestProblem.points AND result = 'AC'
        solves = queryset.filter(points__gte=self.points, submission__result='AC').\
            values_list('submission__user').distinct().count()
        self.attempted_count = totals
        self.solved_count = solves

        should_refresh = force_update or (
            not (contest.modified < self.modified))
        if should_refresh:
            queryset = queryset.filter(
                submission__date__lt=contest.frozen_time)
            self.frozen_attempted_count = queryset.values_list(
                'submission__user').distinct().count()
            self.frozen_solved_count = queryset.filter(
                points__gte=self.points,
                submission__result='AC',
            ).values_list('submission__user').distinct().count()
        else:
            if not contest.is_frozen_time:
                self.frozen_attempted_count = totals
                self.frozen_solved_count = solves

        self.save()

    def clean(self):
        if self.order is None or int(self.order) < 0:
            raise ValidationError(_("'order' must be a positive integer"))

    def save(self, *args, **kwargs):
        self.clean()
        rs = super().save(args, kwargs)
        self.contest.clear_scoreboard_cache()
        return rs

    @cached_property
    def _now(self):
        return timezone.now()

    def __str__(self):
        return f"Problem {self.problem.shortname} in Contest {self.contest.key}"

    class Meta:
        unique_together = ('problem', 'contest')
        verbose_name = _('contest problem')
        verbose_name_plural = _('contest problems')
        ordering = ('order',)
