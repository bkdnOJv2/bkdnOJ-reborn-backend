import errno
from django.utils.translation import gettext_lazy as _

import shutil
from django.conf import settings
from django.db import models
from django.db.models import CASCADE, F, Q, QuerySet, SET_NULL
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator, \
    FileExtensionValidator, MinLengthValidator

from django_extensions.db.models import TimeStampedModel

from userprofile.models import UserProfile as Profile
from organization.models import Organization
from helpers.problem_data import problem_pdf_storage, problem_directory_pdf

from submission.models import SubmissionSourceAccess
from .problem_test_data import ProblemTestProfile, \
  problem_directory_file

from judger.models import Language

import logging
logger = logging.getLogger(__name__)

class Problem(TimeStampedModel):
  # -------------- Problem General Info
  shortname = models.SlugField(
    max_length=128, validators=[MinLengthValidator(4)],
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
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)],
  )
  memory_limit = models.PositiveIntegerField(default=256*1024,
    help_text=_("The memory limit for this problem, in kilobytes "
                "(e.g. 64mb = 65536 kilobytes)."
    ),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT)]
  )

  # -------------- Problem Judging Info
  allowed_languages = models.ManyToManyField(Language,
    help_text=_('List of allowed submission languages.'),
    blank=True, default=[],
  )

  # -------------- Privacy
  authors = models.ManyToManyField(Profile,
    related_name="authored_problems",
    help_text=_("These users may view, edit the problem, and will be listed as Authors "
              "on the Problem Detail page."
    ),
    blank=True, default=[],
  )
  collaborators = models.ManyToManyField(Profile,
    related_name="collaborated_problems",
    help_text=_("These users may view, edit the problem, but won't be listed as Authors "
              "on the Problem Detail page."
    ),
    blank=True, default=[],
  )
  reviewers = models.ManyToManyField(Profile,
    related_name="reviewed_problems",
    help_text=_("These users may only view and make submissions to the problem"),
    blank=True, default=[],
  )

  banned_users = models.ManyToManyField(Profile,
    verbose_name=_('personae non gratae'), blank=True,
    help_text=_('Bans the selected users from submitting to this problem.')
  )

  is_public = models.BooleanField(
    verbose_name=_("publicly visible"), db_index=True, default=False,
    help_text=_("If this option was False, only users added above "
              "(authors, collab,...) may see the problem. If this "
              "option was True, this problem is public (anyone can see and submit)."
    ),
  )
  date = models.DateTimeField(auto_now_add=True, null=True, blank=True, db_index=True,
    help_text=_("Publish date of problem"),
  )

  is_organization_private = models.BooleanField(default=False,
    help_text=_("If private only added, organizations may see "
                "and submit to the problem."),
  )
  organizations = models.ManyToManyField(
    Organization, blank=True, default=[],
    verbose_name=_('organizations'),
  )

  submission_visibility_mode = models.CharField(max_length=16,
    choices=SubmissionSourceAccess.choices, default=SubmissionSourceAccess.ONLY_OWN,
    help_text=_("Determine if users can view submissions for this problem. This is for "
                "public problems only. For problems within certain contests, please set "
                "the contest's own submission visibility setting."),
  )

  points = models.FloatField(
    verbose_name=_('points'), default=100,
    help_text=_("Points awarded for problem completion. "
                "Points are displayed with a 'p' suffix if partial."),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_PROBLEM_POINTS)],
  )
  partial = models.BooleanField(
    verbose_name=_('allow earning partial points'), default=False,
    help_text=_("Allow solvers to earn points for each testcase they did right.")
  )
  short_circuit = models.BooleanField(
    verbose_name=_('stop on unacceptted testcase'), default=False,
    help_text=_("Stop grading as soon as there is one not acceptted testcase."),
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
  def __init__(self, *args, **kwargs):
    super(Problem, self).__init__(*args, **kwargs)
    self.__original_shortname = self.shortname

  def languages_list(self):
    return self.allowed_languages. \
      values_list('common_name', flat=True).distinct().order_by('common_name')

  def is_editor(self, user):
    return (self.authors.filter(id=user.profile.id) |
        self.collaborators.filter(id=user.profile.id)).exists()

  def is_tester(self, user):
    return self.reviewers.filter(id=user.profile.id).eixsts()

  def is_editable_by(self, user):
      if not user.is_authenticated: return False
      if user.is_superuser: return True

      # if not user.has_perm('problem.edit_own_problem'): return False
      # if user.has_perm('problem.edit_all_problem'): return True

      if user.profile.id in self.editor_ids:
          return True

      ## If Problem is shared among organizations
      ## Check if exists an organization that User is admin of.
      if self.is_organization_private:
        if Organization.exists_pair_of_ancestor_descendant(user.profile.admin_of.all(), self.organizations.all()):
          return True
      return False

  def is_accessible_by(self, user, contest=None):
    if user.is_superuser: #or user.has_perm("problem.see_all_problems"):
        return True

    # Belong in a public contest
    if self.contest_set.filter(published=True, is_visible=True).exists():
        return True

    # Given contest, if user still have participation in that contest
    if contest != None and user.is_authenticated:
        if contest.is_accessible_by(user):
            return True
        # if contest.is_editable_by(user):
        #     return True

        # from compete.models import ContestParticipation
        # cps = ContestParticipation.objects.filter(contest=contest, user=user.profile).all()
        # for cp in reversed(cps):
        #     if not cp.ended:
        #         return True

    if self.is_public:
        # Problem is not private to an organization.
        if not self.is_organization_private:
            return True

        # If the user can see all organization private problems.
        if user.has_perm('problem.see_organization_privated_problems'):
            return True

        # Check if exists one organization this problem was shared that the user is a member of
        if user.is_authenticated:
            if Organization.exists_pair_of_ancestor_descendant(self.organizations.all(), user.profile.organizations.all()):
              return True

    if not user.is_authenticated: return False
    if user.has_perm('problem.see_private_problems'): return True

    if self.reviewers.filter(id=user.profile.id).exists():
        return True

    ## The below line works, but has some redundant checks, we will manually do some checks
    # if self.is_editable_by(user) or user.profile.id in self.editor_ids:
    ## ================= is_editable_by BEGIN
    if user.has_perm('problem.edit_all_problem'): return True
    if user.profile.id in self.editor_ids: return True
    # If Problem is shared among organizations
    # Check if exists an organization that User is admin of.
    if self.is_organization_private:
      if Organization.exists_pair_of_ancestor_descendant(user.profile.admin_of.all(), self.organizations.all()):
        return True
    ## ================= is_editable_by END
    return False

  @classmethod
  def get_public_problems(cls):
    return cls.objects.filter(is_public=True, is_organization_private=False).defer('content')

  @classmethod
  def get_visible_problems(cls, user):
    if not user.is_authenticated:
        return cls.get_public_problems()

    if user.has_perm('problem.see_all_problems'): # user.is_superuser also included.
        return cls.objects.defer('content').all()

    queryset = cls.objects.defer('content')
    # edit_own_problem = user.has_perm('problem.edit_own_problem')
    # edit_public_problem = edit_own_problem and user.has_perm('problem.edit_public_problem')
    # edit_all_problem = edit_own_problem and user.has_perm('problem.edit_all_problem')

    # if not (user.has_perm('problem.see_private_problem') or edit_all_problem):
    ## << Tab

    member_org_ids = user.profile.member_of_org_with_ids
    admin_org_ids = user.profile.admin_of_org_with_ids
    q = (
      Q(is_public=True) & (
        Q(is_organization_private=False) |
        Q(is_organization_private=True, organizations__id__in=member_org_ids) |
        Q(is_organization_private=True, organizations__id__in=admin_org_ids)
      )
    )

    ## Special access
    q |= Q(authors=user.profile)
    q |= Q(collaborators=user.profile)
    q |= Q(reviewers=user.profile)

    queryset = queryset.filter(q)
    return queryset.distinct()

  @classmethod
  def get_editable_problems(cls, user):
      if not user.is_authenticated: return cls.objects.none()
      if user.has_perm('problem.edit_all_problem'): return cls.objects.all() # user.is_superuser included

      q = Q(authors=user.profile) | Q(collaborators=user.profile)
      q |= Q(is_public=True, is_organization_private=True, organizations__id__in=user.profile.admin_of_org_with_ids)

      return cls.objects.filter(q)

  def delete_pdf(self):
    shutil.rmtree(problem_pdf_storage.path(self.shortname), ignore_errors=True)

  def update_stats(self):
    queryset = self.submission_set.select_related('user')
    solves = queryset.filter(points__gte=self.points, result='AC').order_by('user').\
              values('user').distinct().count()
    total = queryset.order_by('user').values('user').distinct().count()

    self.solved_count = solves
    self.attempted_count = total
    self.save()
  update_stats.alters_data = True

  @cached_property
  def author_ids(self):
    return Problem.authors.through.objects.filter(problem=self).\
            values_list('userprofile_id', flat=True)

  @cached_property
  def editor_ids(self):
    return self.author_ids.union(
        Problem.collaborators.through.objects.filter(problem=self).\
        values_list('userprofile_id', flat=True))

  @cached_property
  def tester_ids(self):
    return Problem.reviewers.through.objects.filter(problem=self).\
            values_list('userprofile_id', flat=True)

  @cached_property
  def usable_common_names(self):
    return set(self.usable_languages.values_list('common_name', flat=True))

  def save(self, *args, **kwargs):
    self.shortname = self.shortname.upper()
    super().save(*args, **kwargs)
    if self.shortname != self.__original_shortname:
        original = self.__original_shortname
        try:
            problem_data = self.test_profile
        except AttributeError:
            pass
        else:
            problem_data._update_code(original, self.shortname)
            try:
              problem_pdf_storage.rename(original, self.shortname)
            except OSError as e:
              if e.errno != errno.ENOENT:
                raise
            if self.pdf:
              self.pdf.name = problem_directory_pdf(
                self, self.pdf.name)
            ## Change instance var to avoid recursion
            self.__original_shortname = self.shortname
            self.save(update_fields=['pdf'])

  class Meta:
    ordering = ['-created']
    verbose_name = _("Problem")
    verbose_name_plural = _("Problems")

    # permissions = (
    #   ('clone', _("Can clone/copy all problems")),
    # )

  def __str__(self):
    return f'{self.shortname}'


class LanguageLimit(models.Model):
  problem = models.ForeignKey(Problem,
    verbose_name=_('problem'), related_name='language_limits', on_delete=models.CASCADE)
  language = models.ForeignKey(Language,
    verbose_name=_('language'), on_delete=models.CASCADE)
  time_limit = models.FloatField(verbose_name=_('time limit'),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)])
  memory_limit = models.IntegerField(verbose_name=_('memory limit'),
    validators=[MinValueValidator(settings.BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT)])

  class Meta:
    unique_together = ('problem', 'language')
    verbose_name = _('Language-specific resource limit')
    verbose_name_plural = _('Language-specific resource limits')
