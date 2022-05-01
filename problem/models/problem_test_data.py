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

from helpers.problem_data import ProblemDataStorage
problem_data_storage = ProblemDataStorage()

CHECKERS = (
  ('standard', _('Standard')),
  ('floats', _('Floats')),
  ('floatsabs', _('Floats (absolute)')),
  ('floatsrel', _('Floats (relative)')),
  ('rstripped', _('Non-trailing spaces')),
  ('sorted', _('Unordered')),
  ('identical', _('Byte identical')),
  ('linecount', _('Line-by-line')),
)

import os
def _problem_directory_file(shortname, filename):
  return os.path.join(shortname, os.path.basename(filename))

def problem_directory_file(data, filename):
  return _problem_directory_file(data.problem.shortname, filename)

class ProblemTestProfile(TimeStampedModel):
  problem = models.OneToOneField(
    'problem.Problem',
    primary_key=True,
    on_delete=models.CASCADE,
    to_field='shortname',
    related_name='test_profile',
  )
  zipfile = models.FileField(
    storage=problem_data_storage,
    upload_to=problem_directory_file,
    null=True, blank=True,
  )
  generator = models.FileField(
    verbose_name=_('generator file'), 
    storage=problem_data_storage, null=True, blank=True,
    upload_to=problem_directory_file)
  output_prefix = models.IntegerField(
    verbose_name=_('output prefix length'), 
    blank=True, null=True)
  output_limit = models.IntegerField(
    verbose_name=_('output limit length'), 
    blank=True, null=True)
  feedback = models.TextField(
    verbose_name=_('init.yml generation feedback'), blank=True)
  checker = models.CharField(
    max_length=10, verbose_name=_('checker'), choices=CHECKERS, blank=True)
  checker_args = models.TextField(
    verbose_name=_('checker arguments'), blank=True,
    help_text=_('checker arguments as a JSON object'))

  __original_zipfile = None

  def __init__(self, *args, **kwargs):
    super(ProblemTestProfile, self).__init__(*args, **kwargs)
    self.__original_zipfile = self.zipfile

class TestCase(models.Model):
  """
    Model for each test case of a problem
  """
  test_profile = models.ForeignKey(
    ProblemTestProfile,
    null=False,
    on_delete=models.CASCADE,
    related_name='cases',
  )
  order = models.IntegerField(verbose_name=_('case position'))
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
    blank=True, null=True)
  output_limit = models.IntegerField(
    verbose_name=_('output limit length'), 
    blank=True, null=True)
  checker = models.CharField(
    max_length=10, verbose_name=_('checker'), choices=CHECKERS, blank=True)
  checker_args = models.TextField(
    verbose_name=_('checker arguments'), blank=True,
    help_text=_('checker arguments as a JSON object'))

  def swap_order(self, test_case):
    self.order, test_case.order = test_case.order, self.order

  def save(self, *args, **kwargs):
    if self.order == None:
      self.order = self.id
    super(ProblemTestCase, self).save(*args, **kwargs)
