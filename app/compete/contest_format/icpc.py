from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Max
# from django.template.defaultfilters import floatformat
# from django.urls import reverse
# from django.utils.html import format_html
# from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.translation import gettext as ungettext

from .default import DefaultContestFormat
from .registry import register_contest_format
from helpers.timezone import from_database_time
# from helpers.timedelta import nice_repr


@register_contest_format('icpc')
class ICPCContestFormat(DefaultContestFormat):
    name = gettext_lazy('ICPC')
    config_defaults = {'penalty': 20}
    config_validators = {'penalty': lambda x: x >= 0}
    """
        penalty: Number of penalty minutes each incorrect submission adds. Defaults to 20.
    """

    @classmethod
    def validate(cls, config):
        if config is None:
            return

        if not isinstance(config, dict):
            raise ValidationError(
                'ICPC-styled contest expects no config or dict as config')

        for key, value in config.items():
            if key not in cls.config_defaults:
                raise ValidationError('unknown config key "%s"' % key)
            if not isinstance(value, type(cls.config_defaults[key])):
                raise ValidationError('invalid type for config key "%s"' % key)
            if not cls.config_validators[key](value):
                raise ValidationError(
                    'invalid value "%s" for config key "%s"' % (value, key))

    def __init__(self, contest, config):
        self.config = self.config_defaults.copy()
        self.config.update(config or {})
        self.contest = contest

    def update_participation(self, participation):
        cumtime = 0
        last = 0
        penalty = 0
        score = 0

        format_data = {}

        frozen_cumtime = 0
        frozen_last = 0
        frozen_penalty = 0
        frozen_score = 0
        frozen_time = participation.contest.frozen_time

        frozen_format_data = {}

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT MAX(cs.points) as points, (
                    SELECT MIN(csub.date)
                        FROM compete_contestsubmission ccs LEFT OUTER JOIN
                             submission_submission csub ON (csub.id = ccs.submission_id)
                        WHERE ccs.problem_id = cp.id
                            AND ccs.participation_id = %s AND ccs.points = MAX(cs.points)
                ) AS time, cp.id AS prob
                FROM compete_contestproblem cp INNER JOIN
                     compete_contestsubmission cs ON
                        (cs.problem_id = cp.id AND cs.participation_id = %s)
                     LEFT OUTER JOIN
                     submission_submission sub ON (sub.id = cs.submission_id)
                GROUP BY cp.id
            """, (participation.id, participation.id))

            for points, time, prob in cursor.fetchall():
                time = from_database_time(time)
                dt_seconds = (time - participation.start).total_seconds()
                dt = int(dt_seconds // 60)
                # Frozen and sub_time after frozen
                is_frozen_sub = (
                    participation.is_frozen and time >= frozen_time)

                sub_time = dt_seconds

                frozen_sub_time = sub_time
                frozen_points = 0
                frozen_tries = 0
                _tries = None

                # Compute penalty
                if self.config['penalty']:
                    # An IE can have a submission result of 'None'
                    subs = participation.submissions.exclude(submission__result__isnull=True) \
                                                    .exclude(submission__result__in=['IE', 'CE']) \
                                                    .filter(problem_id=prob)

                    if points:  # Acceptted
                        # Submissions after the first AC does not count toward number of tries
                        tries = subs.filter(submission__date__lte=time).count()
                        _tries = tries
                        penalty += (tries - 1) * self.config['penalty']

                        if not is_frozen_sub:  # AC BEFORE FROZEN
                            # frozen_XX == XX
                            frozen_penalty += (tries - 1) * \
                                self.config['penalty']
                            frozen_tries = tries
                            # frozen_sub_time = sub_time # Already set
                        else:
                            # AC_AFTER FROZEN
                            # Tries should be number of attempts
                            tries = subs.count()
                            if tries > 0:
                                frozen_tries = subs.filter(
                                    submission__date__lt=frozen_time).count()

                                # We should always display latest sub time to hide the fact that this participant
                                # has solved this problem if they were to sub more after AC
                                frozen_sub_time = subs.aggregate(
                                    time=Max('submission__date'))['time']
                                frozen_sub_time = from_database_time(
                                    frozen_sub_time)
                                # number of minutes from start to last submission
                                frozen_sub_time = (
                                    frozen_sub_time - participation.start).total_seconds()
                    else:
                        # Not acceptted in anyway, points == frozen_points == 0
                        tries = subs.count()
                        if tries > 0:
                            frozen_tries = subs.filter(
                                submission__date__lt=frozen_time).count()

                            sub_time = subs.aggregate(
                                time=Max('submission__date'))['time']
                            sub_time = from_database_time(sub_time)
                            # sub_time = int((sub_time - participation.start).total_seconds() // 60)
                            sub_time = sub_time - participation.start
                            sub_time = sub_time.total_seconds()
                            frozen_sub_time = sub_time
                        else:
                            is_frozen_sub = False
                else:
                    tries = 0

                if points:
                    cumtime += dt
                    last = max(last, dt)
                    score += points

                    if not is_frozen_sub:
                        frozen_points = points
                        frozen_cumtime += dt
                        frozen_last = max(frozen_last, dt)
                        frozen_score += points

                format_data[str(prob)] = {
                    'sub_time': sub_time,  # Submission time
                    'points': points,  # AC or Not
                    'tries': _tries if _tries is not None else tries,  # Tries
                }
                frozen_format_data[str(prob)] = {
                    'sub_time': frozen_sub_time,
                    'points': frozen_points,  # AC or Not before Frozen
                    'tries': frozen_tries,  # Tries

                    'tries_after_frozen': tries-frozen_tries,  # Tries before frozen
                    # 'is_frozen': is_frozen_sub, ## If participant submit after frozen
                }

        participation.cumtime = cumtime + penalty
        participation.score = round(score, self.contest.points_precision)
        participation.tiebreaker = last  # field is sorted from least to greatest
        participation.format_data = format_data

        participation.frozen_cumtime = frozen_cumtime + frozen_penalty
        participation.frozen_score = round(
            frozen_score, self.contest.points_precision)
        participation.frozen_tiebreaker = frozen_last
        participation.frozen_format_data = frozen_format_data
        participation.frozen_time = frozen_time

        participation.save()

    def display_user_problem(self, participation, contest_problem):
        raise NotImplementedError

    def get_label_for_problem(self, index):
        index += 1
        ret = ''
        while index > 0:
            ret += chr((index - 1) % 26 + 65)
            index = (index - 1) // 26
        return ret[::-1]

    # def get_short_form_display(self):
    #     yield _('The maximum score submission for each problem will be used.')

    #     penalty = self.config['penalty']
    #     if penalty:
    #         yield ungettext(
    #             'Each submission before the first maximum score '
    #                 'submission will incur a **penalty of %d minute**.',
    #             'Each submission before the first maximum score '
    #                 'submission will incur a **penalty of %d minutes**.',
    #             penalty,
    #         ) % penalty
    #     else:
    #         yield _('Ties will be broken by the sum of the last score '
    #                 'altering submission time on problems with a non-zero '
    #                 'score, followed by the time of the last score altering submission.')

    #         if self.contest.enable_frozen:
    #             yield ungettext(
    #                 'The scoreboard will be frozen after ',
    #                 str(self.contest.frozen_time),
    #             )
