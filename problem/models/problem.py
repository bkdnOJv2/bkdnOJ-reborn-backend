from django.utils.translation import gettext_lazy as _
# from bkdnoj import settings
import bkdnoj

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator, \
    FileExtensionValidator

from django_extensions.db.models import TimeStampedModel

from organization.models import Organization
from helpers.problem_data import problem_pdf_storage, problem_directory_pdf

from submission.models import SubmissionSourceAccess
from .problem_test_data import ProblemTestProfile, \
  problem_directory_file

from judger.models import Language

class Problem(TimeStampedModel):
  # -------------- Problem General Info
  shortname = models.SlugField(
    max_length=128,
    null=False, blank=False, unique=True, db_index=True,
    help_text=_("This field is used to separate different problems from each other, "
              "similar to `problem code'. Only letters [A-Z], numbers [0-9], "
              "underscores (_) or hyphens (-) allowed. Max length is 128 characters. "
              "e.g. BIGNUM-PRIME, MAZE-3,... "
    ),
  )
  title = models.CharField(max_length=256,
    help_text=_("Title for problem"),
    blank=True, default="",
  )
  content = models.TextField(
    help_text=_("Problem's statement"),
    blank=True, default="",
  )
  pdf = models.FileField(
    storage=problem_pdf_storage,
    upload_to=problem_directory_pdf,
    null=True, blank=True, default=None,
    validators=[FileExtensionValidator(['pdf'])],
  )

  source = models.CharField(max_length=2048,
    help_text=_("Sources of the problem. For example: "
                "Codeforces Div.2 Round #123 - Problem D."
    ),
    blank=True, default="",
  )
  time_limit = models.FloatField(default=1.0,
    help_text=_("The time limit for this problem, in seconds. "
                "Fractional seconds (e.g. 1.5) are supported."
    ),
    validators=[MinValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                MaxValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)],
  )
  memory_limit = models.PositiveIntegerField(default=256*1024,
    help_text=_("The memory limit for this problem, in kilobytes "
                "(e.g. 64mb = 65536 kilobytes)."
    ),
    validators=[MinValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT),
                MaxValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT)]
  )

  # -------------- Problem Judging Info
  allowed_languages = models.ManyToManyField(Language,
    help_text=_('List of allowed submission languages.'),
    blank=True, default=[],
  )

  # -------------- Privacy
  authors = models.ManyToManyField(User,
    related_name="authored_problem_set",
    help_text=_("These users may view, edit the problem, and will be listed as Authors "
              "on the Problem Detail page."
    ),
    blank=True, default=[],
  )
  collaborators = models.ManyToManyField(User,
    related_name="collaborated_problem_set",
    help_text=_("These users may view, edit the problem, but won't be listed as Authors "
              "on the Problem Detail page."
    ),
    blank=True, default=[],
  )
  reviewers = models.ManyToManyField(User,
    related_name="reviewed_problem_set",
    help_text=_("These users may only view and make submissions to the problem"),
    blank=True, default=[],
  )

  is_published = models.BooleanField(null=False, default=False,
    help_text=_("If this option was False, only users added above "
              "(authors, collab,...) may see the problem. If this "
              "option was True, this problem is public (anyone can see and submit)."
    ),
  )
  published_at = models.DateTimeField(null=True)

  is_privated_to_orgs = models.BooleanField(null=False, default=False,
    help_text=_("If this option was True, and problem is published, only added "
              "organizations may see and submit to the problem. "
    ),
  )
  organizations = models.ManyToManyField(
    Organization, blank=True, default=[],
  )

  submission_visibility_mode = models.CharField(max_length=16,
    choices=SubmissionSourceAccess.choices, default=SubmissionSourceAccess.FOLLOW,
    help_text=_("Determine if users can view submissions for this problem. This is for "
                "public problems only. For problems within certain contests, please set "
                "the contest's own submission visibility setting."
    ),
  )

  points = models.FloatField(verbose_name=_('points'),
    help_text=_('Points awarded for problem completion. '
                "Points are displayed with a 'p' suffix if partial."),
    default=100,
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_PROBLEM_POINTS)],
  )
  partial = models.BooleanField(verbose_name=_('allows partial points'), default=False)
  short_circuit = models.BooleanField(verbose_name=_('short circuit'), default=False)

  # -------------- TODO: Problem Statistics Info
  solved_count = models.PositiveIntegerField(default=0,
    help_text=_("Number of users who has solved this problem"),
  )
  attempted_count = models.PositiveIntegerField(default=0,
    help_text=_("Number of users who has attempted this problem"),
  )

  # -------------- TODO: Problem Clarification Info

  # -------------- TODO: Problem TestCase Info

  # -------------- Methods
  def __init__(self, *args, **kwargs):
    super(Problem, self).__init__(*args, **kwargs)
    self.__original_shortname = self.shortname

  def languages_list(self):
    return self.allowed_languages. \
      values_list('common_name', flat=True).distinct().order_by('common_name')
  
  def is_editor(self, user):
    raise NotImplementedError
  
  def is_editable_by(self, user):
    return True
    raise NotImplementedError
  
  def is_accessible_by(self, user):
    raise NotImplementedError

  @classmethod
  def get_visible_problems(cls, user):
    raise NotImplementedError
  
  @classmethod
  def get_public_problems(cls):
    raise NotImplementedError

  @classmethod
  def get_editable_problems(cls, user):
    raise NotImplementedError

  def get_absolute_url(self):
    return reverse('problem_detail', args=(self.shortname,))

  class Meta:
    ordering = ['-created']
    verbose_name = _("Problem")
    verbose_name_plural = _("Problems")


  def __str__(self):
    return f'{self.shortname}'