import hashlib
import hmac

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from userprofile.models import UserProfile
from judger.judgeapi import abort_submission, judge_submission
from judger.models.runtime import Language
from judger.utils.unicode import utf8bytes

__all__ = ['SUBMISSION_RESULT', 'Submission', 'SubmissionSource', 'SubmissionTestCase']

SUBMISSION_RESULT = (
  ('AC', _('Accepted')),
  ('WA', _('Wrong Answer')),
  ('TLE', _('Time Limit Exceeded')),
  ('MLE', _('Memory Limit Exceeded')),
  ('OLE', _('Output Limit Exceeded')),
  ('IR', _('Invalid Return')),
  ('RTE', _('Runtime Error')),
  ('CE', _('Compile Error')),
  ('IE', _('Internal Error')),
  ('SC', _('Short circuit')),
  ('AB', _('Aborted')),
)

class SubmissionSourceAccess(models.TextChoices):
  FOLLOW = 'FOLLOW', _("Follow bkdnOJ's setting."),
  ALWAYS = 'ALWAYS', _("Users can see all submissions"),
  SOLVED = 'SOLVED', _(
    "Users can see their own, and others if they have solved that problem"
  ),
  ONLY_OWN = 'ONLY_OWN', _('Users can only see their own submissions.'),
  HIDDEN = 'HIDDEN', _('Submissions will never be visible.'),

class Submission(models.Model):
  STATUS = (
    ('QU', _('Queued')),
    ('P', _('Processing')),
    ('G', _('Grading')),
    ('D', _('Completed')),
    ('IE', _('Internal Error')),
    ('CE', _('Compile Error')),
    ('AB', _('Aborted')),
  )
  IN_PROGRESS_GRADING_STATUS = ('QU', 'P', 'G')
  RESULT = SUBMISSION_RESULT
  USER_DISPLAY_CODES = {
    'AC': _('Accepted'),
    'WA': _('Wrong Answer'),
    'SC': 'Short Circuited',
    'TLE': _('Time Limit Exceeded'),
    'MLE': _('Memory Limit Exceeded'),
    'OLE': _('Output Limit Exceeded'),
    'IR': _('Invalid Return'),
    'RTE': _('Runtime Error'),
    'CE': _('Compile Error'),
    'IE': _('Internal Error (judging server error)'),
    'QU': _('Queued'),
    'P': _('Processing'),
    'G': _('Grading'),
    'D': _('Completed'),
    'AB': _('Aborted'),
  }

  user = models.ForeignKey(
    UserProfile, verbose_name=_('user_profile'), on_delete=models.CASCADE
  )
  problem = models.ForeignKey(
    'problem.Problem', verbose_name=_('problem'), on_delete=models.CASCADE
  )
  date = models.DateTimeField(
    verbose_name=_('submission time'), auto_now_add=True, db_index=True
  )
  time = models.FloatField(
    verbose_name=_('execution time'), null=True, db_index=True
  )
  memory = models.FloatField(
    verbose_name=_('memory usage'), null=True
  )
  points = models.FloatField(
    verbose_name=_('points granted'), null=True, db_index=True
  )
  language = models.ForeignKey(
    Language, verbose_name=_('submission language'), on_delete=models.CASCADE
  )
  status = models.CharField(
    verbose_name=_('status'), max_length=2, choices=STATUS, default='QU', db_index=True
  )
  result = models.CharField(
    verbose_name=_('result'), max_length=3, choices=SUBMISSION_RESULT,
    default=None, null=True, blank=True, db_index=True
  )
  error = models.TextField(
    verbose_name=_('compile errors'), null=True, blank=True
  )
  current_testcase = models.IntegerField(default=0)
  batch = models.BooleanField(verbose_name=_('batched cases'), default=False)
  case_points = models.FloatField(verbose_name=_('test case points'), default=0)
  case_total = models.FloatField(verbose_name=_('test case total points'), default=0)
  judged_on = models.ForeignKey(
    'judger.Judge', verbose_name=_('judged on'), null=True, blank=True,
    on_delete=models.SET_NULL)
  judged_date = models.DateTimeField(
    verbose_name=_('submission judge time'), default=None, null=True)
  rejudged_date = models.DateTimeField(
    verbose_name=_('last rejudge date by admin'), null=True, blank=True)
  is_pretested = models.BooleanField(
    verbose_name=_('was ran on pretests only'), default=False)
  contest_object = models.ForeignKey(
    'compete.Contest', verbose_name=_('contest'), null=True, blank=True,
    on_delete=models.SET_NULL, related_name='+')
  locked_after = models.DateTimeField(
    verbose_name=_('submission lock'), null=True, blank=True)

  @classmethod
  def result_class_from_code(cls, result, case_points, case_total):
    if result == 'AC':
      if case_points == case_total:
        return 'AC'
      return '_AC'
    return result

  @property
  def result_class(self):
    # This exists to save all these conditionals from being executed (slowly) in each row.jade template
    if self.status in ('IE', 'CE'):
      return self.status
    return Submission.result_class_from_code(self.result, self.case_points, self.case_total)

  @property
  def memory_bytes(self):
    return self.memory * 1024 if self.memory is not None else 0

  @property
  def short_status(self):
    return self.result or self.status

  @property
  def long_status(self):
    return Submission.USER_DISPLAY_CODES.get(self.short_status, '')

  @cached_property
  def is_locked(self):
    return self.locked_after is not None and self.locked_after < timezone.now()

  def is_frozen_to(self, user):
    """
    Submission is_frozen when:
      - Sub is in contest
      - User who is viewing doesn't have see_detail permission
      - Contest has enable_frozen on AND
          submission time is after frozen_time
    """
    if self.contest_object is None or not self.contest_object.enable_frozen:
      return False

    if self.user.owner == user or self.can_see_detail(user):
      return False

    if self.date < self.contest_object.frozen_time:
      return False
    return True

  def judge(self, *args, rejudge=False, force_judge=False, rejudge_user=None, **kwargs):
    if force_judge or not self.is_locked:
      judged_succeeded = judge_submission(self, *args, rejudge=rejudge, **kwargs)

  judge.alters_data = True

  def abort(self):
    abort_submission(self)

  abort.alters_data = True

  def can_see_detail(self, user):
    if not user.is_authenticated:
      return False

    profile = user.profile
    source_visibility = self.problem.submission_visibility_mode

    ## Overwrite FOLLOW because we haven't set up this yet
    if source_visibility == SubmissionSourceAccess.FOLLOW:
        source_visibility = SubmissionSourceAccess.ONLY_OWN

    if self.problem.is_editable_by(user):
      return True

    if not self.problem.is_accessible_by(user):
      return False

    # If user is an author or curator of the contest the
    # submission was made in, or they can see in-contest subs
    contest = self.contest_object
    if contest is not None:
      from organization.models import Organization
      if (user.profile.id in contest.editor_ids or
        (contest.published and contest.is_organization_private and Organization.exists_pair_of_ancestor_descendant(
          user.profile.admin_of.all(), contest.organizations.all()
        ))
      ):
          return True

    if user.has_perm('submission.view_all_submission') or user.is_superuser:
      return True
    elif source_visibility == SubmissionSourceAccess.HIDDEN:
      return False
    elif self.user_id == profile.id: # Themself
      return True
    elif source_visibility == SubmissionSourceAccess.ALWAYS:
      return True
    elif source_visibility == SubmissionSourceAccess.SOLVED and \
        self.problem.submission_set.filter(user_id=profile.id, result='AC').exists():
      return True

    return False

  def update_contest(self):
    try:
      contest = self.contest
    except AttributeError:
      return

    contest_problem = contest.problem
    contest.points = round(self.case_points / self.case_total * contest_problem.points
                 if self.case_total > 0 else 0, 3)
    if not contest_problem.partial and contest.points != contest_problem.points:
      contest.points = 0
    contest.save()
    contest.participation.recompute_results()
    contest_problem.expensive_recompute_stats()

  update_contest.alters_data = True

  @property
  def is_graded(self):
    return self.status not in ('QU', 'P', 'G')

  @cached_property
  def contest_key(self):
    if hasattr(self, 'contest'):
      return self.contest_object.key

  def __str__(self):
    return 'Submission %d of %s by %s' % (self.id, self.problem, self.user.owner.username)

  def get_absolute_url(self):
    return reverse('submission_status', args=(self.id,))

  @cached_property
  def contest_or_none(self):
    try:
      return self.contest
    except ObjectDoesNotExist:
      return None

  @classmethod
  def get_id_secret(cls, sub_id):
    return (hmac.new(utf8bytes(settings.EVENT_DAEMON_SUBMISSION_KEY), b'%d' % sub_id, hashlib.sha512)
          .hexdigest()[:16] + '%08x' % sub_id)

  @cached_property
  def id_secret(self):
    return self.get_id_secret(self.id)

  class Meta:
    ordering = ['-id']
    permissions = (
      ('abort_any_submission', _('Abort any submission')),
      ('rejudge_submission', _('Rejudge the submission')),
      ('rejudge_submission_lot', _('Rejudge a lot of submissions')),
      ('spam_submission', _('Submit without limit')),
      ('view_all_submission', _('View all submission')),
      ('resubmit_other', _("Resubmit others' submission")),
      ('lock_submission', _('Change lock status of submission')),
    )
    verbose_name = _('submission')
    verbose_name_plural = _('submissions')


class SubmissionSource(models.Model):
  submission = models.OneToOneField(
    Submission, on_delete=models.CASCADE, verbose_name=_('associated submission'),
    related_name='source')
  source = models.TextField(verbose_name=_('source code'), max_length=65536)

  def __str__(self):
    return 'Source of %s' % self.submission

  class Meta:
    verbose_name = _('submission source')
    verbose_name_plural = _('submission sources')


class SubmissionTestCase(models.Model):
  RESULT = SUBMISSION_RESULT

  submission = models.ForeignKey(Submission, verbose_name=_('associated submission'),
                   related_name='test_cases', on_delete=models.CASCADE)
  case = models.IntegerField(verbose_name=_('test case ID'))
  status = models.CharField(max_length=3, verbose_name=_('status flag'), choices=SUBMISSION_RESULT)
  time = models.FloatField(verbose_name=_('execution time'), null=True)
  memory = models.FloatField(verbose_name=_('memory usage'), null=True)
  points = models.FloatField(verbose_name=_('points granted'), null=True)
  total = models.FloatField(verbose_name=_('points possible'), null=True)
  batch = models.IntegerField(verbose_name=_('batch number'), null=True)
  feedback = models.CharField(max_length=50, verbose_name=_('judging feedback'), blank=True)
  extended_feedback = models.TextField(verbose_name=_('extended judging feedback'), blank=True)
  output = models.TextField(verbose_name=_('program output'), blank=True)

  @property
  def long_status(self):
    return Submission.USER_DISPLAY_CODES.get(self.status, '')

  class Meta:
    unique_together = ('submission', 'case')
    verbose_name = _('submission test case')
    verbose_name_plural = _('submission test cases')
