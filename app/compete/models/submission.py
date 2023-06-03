from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import CASCADE, SET_NULL, Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _

from problem.models import Problem
from submission.models import Submission

from .problem import ContestProblem
from .participation import ContestParticipation

__all__ = ['ContestSubmission']

class ContestSubmission(models.Model):
    submission = models.OneToOneField(Submission,
        verbose_name=_('submission'), related_name='contest', on_delete=CASCADE)
    problem = models.ForeignKey(ContestProblem,
        verbose_name=_('problem'), on_delete=CASCADE,
        related_name='submissions', related_query_name='submission')
    participation = models.ForeignKey(ContestParticipation,
        verbose_name=_('participation'), on_delete=CASCADE,
        related_name='submissions', related_query_name='submission')
    points = models.FloatField(default=0.0, verbose_name=_('points'))
    is_pretest = models.BooleanField(
        verbose_name=_('is pretested'),
        help_text=_('Whether this submission was ran only on pretests.'),
        default=False)

    class Meta:
        verbose_name = _('contest submission')
        verbose_name_plural = _('contest submissions')
        ordering = ['-id']

