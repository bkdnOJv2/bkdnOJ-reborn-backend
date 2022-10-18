from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models import Max, Min, OuterRef, Subquery, Count
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy

from .default import DefaultContestFormat
from .registry import register_contest_format
from helpers.timedelta import nice_repr
from helpers.timezone import from_database_time


@register_contest_format('ioi')
class LegacyIOIContestFormat(DefaultContestFormat):
    name = gettext_lazy('IOI')
    config_defaults = {'cumtime': True}
    """
        cumtime: Specify True if time penalties are to be computed. Defaults to True.
    """
    # Max score, Min time
    # Cumtime calculates by minutes

    @classmethod
    def validate(cls, config):
        if config is None:
            return

        if not isinstance(config, dict):
            raise ValidationError('IOI-styled contest expects no config or dict as config')

        for key, value in config.items():
            if key not in cls.config_defaults:
                raise ValidationError('unknown config key "%s"' % key)
            if not isinstance(value, type(cls.config_defaults[key])):
                raise ValidationError('invalid type for config key "%s"' % key)

    def __init__(self, contest, config):
        self.config = self.config_defaults.copy()
        self.config.update(config or {})
        self.contest = contest

    def __update_data(self, participation, save=False):
        cumtime = 0
        score = 0
        format_data = {}

        ## Calculate not frozen first ------------
        queryset = (participation.submissions.values('problem_id')
            .filter(points=Subquery(
                participation.submissions.filter(problem_id=OuterRef('problem_id'))
                                        .order_by('-points').values('points')[:1]))
            .annotate(time=Min('submission__date'))
            .values_list('problem_id', 'time', 'points'))
        for problem_id, time, points in queryset:
            time = from_database_time(time)

            if self.config['cumtime']:
                dt = int((time - participation.start).total_seconds() // 60)
                if points:
                    cumtime += dt
            else:
                dt = 0

            format_data[str(problem_id)] = {
                'points': points, 'sub_time': dt,
            }
            score += points
        participation.cumtime = max(cumtime, 0)
        participation.score = round(score, self.contest.points_precision)
        participation.tiebreaker = 0
        participation.format_data = format_data
        if save:
            participation.save()

    def __update_frozen_data(self, participation, save=False):
        frozen_cumtime = 0
        frozen_score = 0
        frozen_format_data = {}
        frozen_time = participation.contest.frozen_time

        frozen_queryset = (participation.submissions.values('problem_id')
            .filter(points=Subquery(
                participation.submissions.filter(submission__date__lt=frozen_time)
                                        .filter(problem_id=OuterRef('problem_id'))
                                        .order_by('-points').values('points')[:1])
            ).annotate(time=Min('submission__date'))
            .values_list('problem_id', 'time', 'points'))

        for problem_id, time, points in frozen_queryset:
            frozen_time = from_database_time(time)
            frozen_points = points
            # print(points)

            if self.config['cumtime']:
                dt = int((frozen_time - participation.start).total_seconds() // 60)
                if frozen_points:
                    frozen_cumtime += dt
            else:
                dt = 0

            frozen_format_data[str(problem_id)] = {
                'points': frozen_points, 'sub_time': dt,
            }
            frozen_score += frozen_points

        # We need another query to count the number of tries after frozen this participant has
        # In addiction, the above loop may not be ran because user might never submit
        # before frozen. So, we assign points 0 to them.
        for problem_id, sub_time, tries_after_frozen in participation.submissions.exclude(submission__result__isnull=True) \
                .exclude(submission__result__in=['IE', 'CE']) \
                .filter(submission__date__gte=frozen_time)\
                .values('problem_id').annotate(tries_after_frozen=Count('id'), sub_time=Max('submission__date'))\
                .values_list('problem_id', 'sub_time', 'tries_after_frozen'):
            ff = frozen_format_data.get(str(problem_id), {})
            ff['tries_after_frozen'] = tries_after_frozen
            points_before = ff.get('points', 0)
            if points_before == 0:
                dt = int((sub_time - participation.start).total_seconds() // 60)
                ff['sub_time'] = dt
                ff['points'] = 0

            frozen_format_data[str(problem_id)] = ff

        participation.frozen_cumtime = max(frozen_cumtime, 0)
        participation.frozen_score = round(frozen_score, self.contest.points_precision)
        participation.frozen_tiebreaker = 0
        participation.frozen_format_data = frozen_format_data
        if save:
            participation.save()

    def update_participation(self, participation):
        self.__update_data(participation, save=False)
        self.__update_frozen_data(participation, save=False)
        participation.save()

    def display_user_problem(self, participation, contest_problem):
        raise NotImplementedError

    def display_participation_result(self, participation):
        raise NotImplementedError

    def get_short_form_display(self):
        yield _('The maximum score submission for each problem will be used.')

        if self.config['cumtime']:
            yield _('Ties will be broken by the sum of the last score altering submission time on problems with a '
                    'non-zero score.')
        else:
            yield _('Ties by score will **not** be broken.')
