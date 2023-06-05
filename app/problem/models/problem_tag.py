from django.db import models
from django_extensions.db.models import TimeStampedModel
from .problem import Problem
import logging

logger = logging.getLogger(__name__)


class ProblemTag(TimeStampedModel):
    name = models.CharField(
        max_length=128,
        null=False,
        unique=True,
        db_index=True,
        help_text=("Name of this Problem Tag. Eg: 'dp', 'math', 'binary-search',..."),
    )
    descriptions = models.TextField(
        help_text=("Description of tag"),
        blank=True,
        default="",
    )
    tagged_problems = models.ManyToManyField(
        Problem,
        help_text=("Problems those carry this tag"),
        blank=True,
        default=[],
        related_name="tags",
    )

    def __str__(self):
        return f"{self.name}"
