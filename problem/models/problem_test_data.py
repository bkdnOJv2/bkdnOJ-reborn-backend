import errno
from django.core.validators import FileExtensionValidator
from django.db import models, IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
User = get_user_model()

from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile

from django_extensions.db.models import TimeStampedModel

from organization.models import Organization
from helpers.problem_data import problem_directory_pdf
from submission.models import SubmissionSourceAccess
from judger.models import Language

from problem.validators import problem_data_zip_validator

from helpers.problem_data import ProblemDataCompiler, \
  problem_data_storage, problem_pdf_storage

import shutil
import zipfile
import logging
logger = logging.getLogger(__name__)

CHECKERS = (
  ('standard', _('Standard')),
  ('floats', _('Floats')),
  ('floatsabs', _('Floats (absolute)')),
  ('floatsrel', _('Floats (relative)')),
  ('rstripped', _('Non-trailing spaces')),
  ('sorted', _('Unordered')),
  ('identical', _('Byte identical')),
  ('linecount', _('Line-by-line')),

  ('custom-py3', _("Custom checker (Py3)")),
)

from zipfile import BadZipfile, ZipFile
import os
def _problem_directory_file(shortname, filename):
  return os.path.join(shortname, os.path.basename(filename))

def problem_directory_file(data, filename):
  return _problem_directory_file(data.problem.shortname, filename)

class ProblemTestProfile(TimeStampedModel):
  problem = models.OneToOneField(
    'problem.Problem',
    #primary_key=True,
    on_delete=models.CASCADE,
    #to_field='shortname',
    related_name='test_profile',
  )
  zipfile = models.FileField(
    storage=problem_data_storage,
    upload_to=problem_directory_file,
    null=True, blank=True,
    validators=[problem_data_zip_validator],
  )
  generator = models.FileField(
    verbose_name=_('generator file'),
    storage=problem_data_storage, null=True, blank=True,
    upload_to=problem_directory_file)
  output_prefix = models.IntegerField(
    verbose_name=_('output prefix length'),
    blank=True, null=True,
    validators=[MinValueValidator(0),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_OUTPUT_PREFIX)],
    )
  output_limit = models.IntegerField(
    verbose_name=_('output limit length'),
    blank=True, null=True,
    validators=[MinValueValidator(0),
                MaxValueValidator(settings.BKDNOJ_PROBLEM_MAX_OUTPUT_LIMIT)],
  )
  feedback = models.TextField(
    verbose_name=_('init.yml generation feedback'), blank=True)
  checker = models.CharField(
    max_length=10, verbose_name=_('checker'), choices=CHECKERS, blank=True)
  checker_args = models.TextField(
    verbose_name=_('checker arguments'), blank=True,
    help_text=_('checker arguments as a JSON object'))

  custom_checker = models.FileField(
    verbose_name=_("Custom checker script/code"),
    storage=problem_data_storage,
    upload_to=problem_directory_file,
    null=True, blank=True,
    validators=[FileExtensionValidator(allowed_extensions=["py"])],
  )

  _original_zipfile = None
  _zipfile_changed = False
  _signal_caught = False

  def __init__(self, *args, **kwargs):
    super(ProblemTestProfile, self).__init__(*args, **kwargs)
    self._original_zipfile = self.zipfile

  def set_zipfile(self, zipf, *args, **kwargs):
    self._original_zipfile.delete(save=False)

    # setting new zipfile, doesnt need to delete old zip
    # because the save() method will be call later and clean this up
    self.zipfile = zipf

    # save so the zipfile is fully uploaded
    # otherwise the zip will not exist
    self.save(update_fields=['zipfile'])
    self._zipfile_changed = True
    # statement.pdf

  def delete_data(self, *args, **kwargs):
    # self.zipfile.delete(kwargs.get('save', True))
    # self.cases.all().delete()
    shutil.rmtree(problem_data_storage.path(self.problem.shortname), 
      ignore_errors=True)
  
  def update_test_cases(self):
      self.cases.update(
        output_prefix=self.output_prefix, output_limit=self.output_limit,
        checker=self.checker, checker_args=self.checker_args
      )
      ProblemDataCompiler.generate(
        self.problem, self, self.cases.order_by('order'), self.valid_files
      )

  def generate_test_cases(self):
    if self._zipfile_changed:
      testcase_to_be_created = []
      case_pairs = self.valid_pairs_of_cases
      for in_file, ans_file in case_pairs:
          testcase_to_be_created.append(
              TestCase(test_profile=self,
                  order=len(testcase_to_be_created),
                  input_file=in_file,
                  output_file=ans_file,
                  generator_args=self.generator_args,
                  points=1,
                  is_pretest=False,
                  output_prefix=self.output_prefix,
                  output_limit=self.output_limit,
                  checker=self.checker,
                  checker_args=self.checker_args,
              )
          )

      with transaction.atomic():
        self.cases.all().delete()
        TestCase.objects.bulk_create(testcase_to_be_created)

      ProblemDataCompiler.generate(
        self.problem, self, self.cases.order_by('order'), self.valid_files
      )
      return True
    return False

  def update_pdf_within_zip(self):
    pdf_file = self.valid_statement_pdf
    if not pdf_file:
      return False
    with zipfile.ZipFile(self.zipfile.path, 'r') as zfile:
      pdf_data = zfile.read(pdf_file)

      self.problem.pdf = problem_pdf_storage.save(
        problem_directory_pdf(self.problem, None),
        ContentFile(pdf_data)
      )
      self.problem.save(update_fields=['pdf'])

  def __str__(self):
    return 'Problem Test Profile %s' % (self.problem)

  def get_absolute_url(self):
    return reverse('problemtestprofile_detail', args=(self.problem,))

  def save(self, *args, **kwargs):
    obj = super(ProblemTestProfile, self).save(*args, **kwargs)
    # Don't call ProblemDataCompiler.generate() it causes infinite recursion
    return obj

  @cached_property
  def valid_statement_pdf(self):
    if self.zipfile:
      file_list = ZipFile(self.zipfile.path).namelist()
      for file in file_list:
        fpath, frel = os.path.split(file)
        if frel in settings.BKDNOJ_PROBLEM_ACCEPTABLE_STATEMENT_PDF:
          return file
    return None

  """
    Return a tuple(in_files, ans_files), in_files and ans_files are
    both list of valid in/ans files in the archive.
  """
  @cached_property
  def valid_in_ans_files(self):
    in_files = []
    ans_files = []
    try:
      if self.zipfile:
        file_list = ZipFile(self.zipfile.path).namelist()
        for file in file_list:
          base_name, ext_name = os.path.splitext(file)
          if ext_name in settings.BKDNOJ_PROBLEM_DATA_IN_FILE_EXT:
            in_files.append(file)
          elif ext_name in settings.BKDNOJ_PROBLEM_DATA_ANS_FILE_EXT:
            ans_files.append(file)
        in_files.sort()
        ans_files.sort()
        return in_files, ans_files
    except BadZipfile:
      return [], []
    return [], []

  @cached_property
  def valid_files(self):
    inf, ansf = self.valid_in_ans_files
    return inf + ansf

  @cached_property
  def valid_pairs_of_cases(self):
    return list(zip(
      *self.valid_in_ans_files
    ))

  def _update_code(self, original, new):
    try:
      problem_data_storage.rename(original, new)
    except OSError as e:
      if e.errno != errno.ENOENT:
        raise

    if self.zipfile:
      self.zipfile.name = _problem_directory_file(new, self.zipfile.name)
    if self.generator:
      self.generator.name = _problem_directory_file(new, self.generator.name)
    if self.custom_checker:
      self.custom_checker.name = _problem_directory_file(
          new, self.custom_checker.name
      )
    self.save()

  class Meta:
    verbose_name = _('problem data profile')
    verbose_name_plural = _('problem data profiles')


class TestCase(models.Model):
  """
    Model for each test case of a problem
  """
  test_profile = models.ForeignKey(
    ProblemTestProfile,
    null=False,
    on_delete=models.CASCADE,
    related_name='cases',
    db_index=True,
  )
  order = models.IntegerField(
    verbose_name=_('case position'), null=True)
  type = models.CharField(max_length=1, verbose_name=_('case type'),
    choices=(('C', _('Normal case')),
              ('S', _('Batch start')),
              ('E', _('Batch end'))),
    default='C')
  input_file = models.CharField(max_length=100,
    verbose_name=_('input file name'), blank=True)
  output_file = models.CharField(max_length=100,
    verbose_name=_('output file name'), blank=True)
  generator_args = models.TextField(
    verbose_name=_('generator arguments'), blank=True)
  points = models.IntegerField(verbose_name=_('point value'),
    blank=True, null=True)
  is_pretest = models.BooleanField(
    verbose_name=_('case is pretest?'))
  output_prefix = models.IntegerField(
    verbose_name=_('output prefix length'),
    blank=True, null=True, default=settings.BKDNOJ_DEFAULT_SUBMISSION_OUTPUT_PREFIX,
  )
  output_limit = models.IntegerField(
    verbose_name=_('output limit length'),
    blank=True, null=True, default=settings.BKDNOJ_DEFAULT_SUBMISSION_OUTPUT_LIMIT,
  )
  checker = models.CharField(
    max_length=10, verbose_name=_('checker'), choices=CHECKERS, blank=True)
  checker_args = models.TextField(
    verbose_name=_('checker arguments'), blank=True,
    help_text=_('checker arguments as a JSON object'))

  def swap_order(self, test_case):
    self.order, test_case.order = test_case.order, self.order

  def save(self, *args, **kwargs):
    super(TestCase, self).save(*args, **kwargs)

  class Meta:
    ordering = ['test_profile']
    verbose_name = _('Test case')
    verbose_name_plural = _('Test cases')
