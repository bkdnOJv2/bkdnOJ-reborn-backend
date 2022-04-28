from django.utils.translation import gettext_lazy as _
# from bkdnoj import settings
import bkdnoj


from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator

from django_extensions.db.models import TimeStampedModel

from organization.models import Organization
from helpers.fileupload import path_and_rename_test_zip
from submission.models import SubmissionSourceAccess

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

  source = models.CharField(max_length=2048,
    help_text=_("Sources of the problem. For example: "
                "Codeforces Div.2 Round #123 - Problem D."
    ),
    blank=True, default=""
  )
  time_limit = models.FloatField(default=1.0,
    help_text=_("The time limit for this problem, in seconds. "
                "Fractional seconds (e.g. 1.5) are supported."
    ),
    validators=[MinValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                MaxValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)]
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
    raise NotImplemented
  
  def is_editable_by(self, user):
    raise NotImplemented
  
  def is_accessible_by(self, user):
    raise NotImplemented

  @classmethod
  def get_visible_problems(cls, user):
    raise NotImplemented
  
  @classmethod
  def get_public_problems(cls):
    raise NotImplemented

  @classmethod
  def get_editable_problems(cls, user):
    raise NotImplemented

  def get_absolute_url(self):
    return reverse('problem_detail', args=(self.shortname,))

  def __str__(self):
    return f'prob[{self.shortname}]'

class ProblemTestDataProfile(TimeStampedModel):
  problem = models.OneToOneField(Problem,
    primary_key=True,
    on_delete=models.CASCADE,
    to_field='shortname',
    related_name='test_profile',
  )
  uploader = models.ForeignKey(User, null=True, 
    on_delete=models.SET_NULL,
  )
  zip_url = models.FileField(
    upload_to=path_and_rename_test_zip,
    null=True, blank=True
  )


class ProblemTestCase(models.Model):
  """
    Model for each test case of a problem
  """
  test_profile = models.ForeignKey(ProblemTestDataProfile,
    null=False,
    on_delete=models.CASCADE,
  )
  rel_input_file_url = models.CharField(max_length=500,
    null=False
  )
  rel_answer_file_url = models.CharField(max_length=500,
    null=False
  )
  order = models.IntegerField()
  points = models.FloatField(default=0.0)

  def swap_order(self, test_case):
    self.order, test_case.order = test_case.order, self.order

  def save(self, *args, **kwargs):
    if self.order == None:
      self.order = self.id
    super(ProblemTestCase, self).save(*args, **kwargs)



class Language(models.Model):
  """
  Model of Programming Language, for each problem
  """
  key = models.CharField(max_length=6, verbose_name=_('short identifier'),
    help_text=_('The identifier for this language; the same as its executor id for judges.'),
    unique=True
  )
  name = models.CharField(max_length=20, verbose_name=_('long name'),
    help_text=_('Longer name for the language, e.g. "Python 2" or "C++11".')
  )
  short_name = models.CharField(max_length=10, verbose_name=_('short name'),
    help_text=_('More readable, but short, name to display publicly; e.g. "PY2" or '
                '"C++11". If left blank, it will default to the '
                'short identifier.'
    ),
    null=True, blank=True
  )

  common_name = models.CharField(max_length=10, verbose_name=_('common name'),
    help_text=_('Common name for the language. For example, the common name for C++03, '
                'C++11, and C++14 would be "C++"')
  )
  ace = models.CharField(max_length=20, verbose_name=_('ace mode name'),
    help_text=_('Language ID for Ace.js editor highlighting, appended to "mode-" to determine '
                'the Ace JavaScript file to use, e.g., "python".')
  )
  pygments = models.CharField(max_length=20, verbose_name=_('pygments name'),
    help_text=_('Language ID for Pygments highlighting in source windows.')
  )
  template = models.TextField(verbose_name=_('code template'),
    help_text=_('Code template to display in submission editor.'),
    blank=True,
  )
  info = models.CharField(max_length=50, verbose_name=_('runtime info override'), blank=True,
    help_text=_("Do not set this unless you know what you're doing! It will override the "
                "usually more specific, judge-provided runtime info!"),
  )
  description = models.TextField(verbose_name=_('language description'),
    help_text=_("Use this field to inform users of quirks with your environment, "
                "additional restrictions, etc."),
    blank=True
  )
  extension = models.CharField(max_length=10, verbose_name=_('extension'),
    help_text=_('The extension of source files, e.g., "py" or "cpp".')
  )

  def runtime_versions(self):
    runtimes = OrderedDict()
    # There be dragons here if two judges specify different priorities
    for runtime in self.runtimeversion_set.all():
      id = runtime.name
      if id not in runtimes:
        runtimes[id] = set()
      if not runtime.version:  # empty str == error determining version on judge side
        continue
      runtimes[id].add(runtime.version)

    lang_versions = []
    for id, version_list in runtimes.items():
      lang_versions.append((id, sorted(version_list, key=lambda a: tuple(map(int, a.split('.'))))))
    return lang_versions

  @classmethod
  def get_common_name_map(cls):
    result = cache.get('lang:cn_map')
    if result is not None:
      return result
    result = defaultdict(set)
    for id, cn in Language.objects.values_list('id', 'common_name'):
      result[cn].add(id)
    result = {id: cns for id, cns in result.items() if len(cns) > 1}
    cache.set('lang:cn_map', result, 86400)
    return result

  @cached_property
  def short_display_name(self):
    return self.short_name or self.key

  def __str__(self):
    return self.name

  @cached_property
  def display_name(self):
    if self.info:
      return '%s (%s)' % (self.name, self.info)
    else:
      return self.name

  @classmethod
  def get_python3(cls):
    # We really need a default language, and this app is in Python 3
    return Language.objects.get_or_create(key='PY3', defaults={'name': 'Python 3'})[0]

  def get_absolute_url(self):
    return reverse('runtime_list') + '#' + self.key

  @classmethod
  def get_default_language(cls):
    try:
      return Language.objects.get(key=settings.DEFAULT_USER_LANGUAGE)
    except Language.DoesNotExist:
      return cls.get_python3()

  @classmethod
  def get_default_language_pk(cls):
    return cls.get_default_language().pk

  class Meta:
    ordering = ['key']
    verbose_name = _('language')
    verbose_name_plural = _('languages')

class LanguageLimit(models.Model):
    problem = models.ForeignKey(Problem, verbose_name=_('problem'), 
      related_name='language_limits', on_delete=models.CASCADE)
    
    language = models.ForeignKey(Language, 
      verbose_name=_('language'), on_delete=models.CASCADE)

    time_limit = models.FloatField(verbose_name=_('time limit'),
      validators=[MinValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MIN_TIME_LIMIT),
                  MaxValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MAX_TIME_LIMIT)]
    )
    memory_limit = models.IntegerField(verbose_name=_('memory limit'),
      validators=[MinValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT),
                  MaxValueValidator(bkdnoj.settings.BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT)]
    )

    class Meta:
        unique_together = ('problem', 'language')
        verbose_name = _('language-specific resource limit')
        verbose_name_plural = _('language-specific resource limits')