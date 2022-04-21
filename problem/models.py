from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django_extensions.db.models import TimeStampedModel

from organization.models import Organization
from runtime.models import Language

class Problem(TimeStampedModel):
  # -------------- Problem General Info
  shortname = models.SlugField(max_length=128, primary_key=True,
    help_text=_("This field is used to separate different problems from each other, "
              "similar to `problem code'. Only letters [A-Z], numbers [0-9], "
              "underscores (_) or hyphens (-) allowed. Max length is 128 characters. "
              "e.g. BIGNUM-PRIME, MAZE-3,... "
    ),
  )
  title = models.CharField(max_length=256,
    help_text=_("Title for problem"),
  )
  content = models.TextField(
    help_text=_("Problem's statement"),
  )

  source = models.CharField(max_length=2048,
    help_text=_("Sources of the problem. For example: "
                "Codeforces Div.2 Round #123 - Problem D."
    ),
  )
  time_limit = models.FloatField(default=1.0,
    help_text=_("The time limit for this problem, in seconds. "
                "Fractional seconds (e.g. 1.5) are supported."
    ),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)]
  )
  memory_limit = models.PositiveIntegerField(default=256*1024,
    help_text=_("The memory limit for this problem, in kilobytes "
                "(e.g. 64mb = 65536 kilobytes)."
    ),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT)]
  )

  # -------------- Problem Judging Info
  allowed_language = models.ManyToMany(Language,
    help_text=_('List of allowed submission languages.')
  )

  # -------------- Privacy
  authors = models.ManyToMany(User,
    help_text=_("These users may view, edit the problem, and will be listed as Authors "
              "on the Problem Detail page."
    ),
  )
  collaborators = models.ManyToMany(User,
    help_text=_("These users may view, edit the problem, but won't be listed as Authors "
              "on the Problem Detail page."
    ),
  )
  reviewers = models.ManyToMany(User,
    help_text=_("These users may only view and make submissions to the problem"),
  )

  is_published = models.BooleanField(null=False, default=False,
    help_text=_("If this option was False, only users added above "
              "(authors, collab,...) may see the problem. If this "
              "option was True, this problem is public (anyone can see and submit)."
    ),
  )
  is_privated_to_orgs = models.BooleanField(null=False, default=False,
    help_text=_("If this option was True, and problem is published, only added "
              "organizations may see and submit to the problem. "
    ),
  )
  shared_orgs = models.ManyToManyField(Organization)

  class SubmissionVisibilityType(models.TextChoices):
    DEFAULT = 'DEFAULT', _('Follow default setting.'),
    ALWAYS = 'ALWAYS', _('Always visible'),
    SOLVED = 'SOLVED', _('Visible if problem solved'),
    ONLY_OWN = 'ONLY_OWN', _('Only own submissions'),
    HIDDEN = 'HIDDEN', _('Submissions will never be shown'),

  submission_visibility_mode = models.CharField(max_length=16,
    choices=SubmissionVisibilityType.choices, default=SubmissionVisibilityType.DEFAULT,
    help_text=_("Determine if users can view submissions for this problem. This is for "
                "public problems only. For problems within certain contests, please set "
                "the contest's own submission visibility setting."
    ),
  )

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
  def __str__(self):
    return f'prob[{self.shortname}]'
