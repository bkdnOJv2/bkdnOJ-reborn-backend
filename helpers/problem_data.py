import json
import os
import re

import yaml
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils.translation import gettext as _

import logging
logger = logging.getLogger(__name__)

if os.altsep:
  def split_path_first(path, repath=re.compile('[%s]' % re.escape(os.sep + os.altsep))):
    return repath.split(path, 1)
else:
  def split_path_first(path):
    return path.split(os.sep, 1)

class ProblemDataStorage(FileSystemStorage):
  def __init__(self):
    super(ProblemDataStorage, self).__init__(settings.BKDNOJ_PROBLEM_DATA_ROOT)

  def url(self, name):
    path = split_path_first(name)
    if len(path) != 2:
      return ''
      #raise ValueError('This file is not accessible via a URL.')
    return reverse('problem_data_file', args=path)

  def _save(self, name, content):
    if self.exists(name):
      self.delete(name)
    return super(ProblemDataStorage, self)._save(name, content)

  def get_available_name(self, name, max_length=None):
    return name

  def rename(self, old, new):
    return os.rename(self.path(old), self.path(new))


class ProblemDataError(Exception):
  def __init__(self, message):
    super(ProblemDataError, self).__init__(message)
    self.message = message


class ProblemDataCompiler(object):
  def __init__(self, problem, data, cases, files):
    self.problem = problem
    self.data = data
    self.cases = cases
    self.files = files

    self.generator = data.generator

  def make_init(self):
    cases = []
    batch = None

    def end_batch():
      if not batch['batched']:
        raise ProblemDataError(_('Empty batches not allowed.'))
      cases.append(batch)

    def make_checker(case):

      def get_lang_from_checker_name(checker_name):
        from judger.models.runtime import Language
        pos = checker_name.find('-')
        if pos < 0:
            raise ValidationError("Invalid Checker: Checker name must have format '<checker_type>-<lang_key>'")
        lang_name = checker_name[pos+1:]
        lang = Language.objects.filter(key=lang_name)
        if lang is None:
            raise ValidationError(f"Invalid Checker: Lang key '{lang_name}' does not exist")
        return lang_name

      checker_name = self.data.checker
      ## Custom Checker
      if checker_name.startswith("custom"):
        try:
          #custom_checker_path = split_path_first(self.data.custom_checker.name)
          if checker_name.endswith("PY3"):
            custom_checker_basename = os.path.basename(self.data.custom_checker.name)
            return custom_checker_basename

          else:
            lang = get_lang_from_checker_name(checker_name)

            chkargs = {
                'files': os.path.basename(self.data.custom_checker.name),
                'lang': lang,
                'type': 'testlib',
            }
            if self.data.checker_args:
                chkargsdict = json.loads(self.data.checker_args)
                for k, v in chkargsdict.items():
                    chkargs[k] = v
            self.data.checker_args = json.dumps(chkargs)
            self.data.save(update_fields=['checker_args'])
            return {
                'name': 'bridged',
                'args': json.loads(self.data.checker_args),
            }
        except OSError:
          raise ProblemDataError(
            _("How did the custom checker path get corrupted?")
          )

      ## Custom Interactive Checker
      if checker_name.startswith("interactive"):
        try:
          lang = get_lang_from_checker_name(checker_name)

          chkargs = {
              'files': os.path.basename(self.data.custom_checker.name),
              'lang': lang,
              'type': 'testlib',
          }
          if self.data.checker_args:
              chkargsdict = json.loads(self.data.checker_args)
              for k, v in chkargsdict.items():
                  chkargs[k] = v
          self.data.checker_args = json.dumps(chkargs)
          self.data.save(update_fields=['checker_args'])
          return json.loads(self.data.checker_args)
        except OSError:
          raise ProblemDataError(
            _("How did the interactive checker path get corrupted?")
          )

      if case.checker_args:
        return {
          'name': case.checker,
          'args': json.loads(case.checker_args),
        }
      return case.checker

    def assign_checker(yaml_dict, case=None):
      name = 'checker'
      if self.data.checker.startswith('interactive'):
        name = 'interactive'
        yaml_dict['unbuffered'] = True
      yaml_dict[name] = make_checker(case)

    # ---------------------------------------------------------

    for i, case in enumerate(self.cases, 1):
      if case.type == 'C':
        data = {}
        if batch:
          case.points = None
          case.is_pretest = batch['is_pretest']
        else:
          if case.points is None:
            raise ProblemDataError(_('Points must be defined for non-batch case #%d.') % i)
          data['is_pretest'] = case.is_pretest

        if not self.generator:

          if case.input_file not in self.files:
            raise ProblemDataError(_('Input file for case %d does not exist: %s') %
                         (i, case.input_file))
          if case.output_file not in self.files:
            raise ProblemDataError(_('Output file for case %d does not exist: %s') %
                         (i, case.output_file))

        if case.input_file:
          data['in'] = case.input_file
        if case.output_file:
          data['out'] = case.output_file
        if case.points is not None:
          data['points'] = case.points
        if case.generator_args:
          data['generator_args'] = case.generator_args.splitlines()
        if case.output_limit is not None:
          data['output_limit_length'] = case.output_limit
        if case.output_prefix is not None:
          data['output_prefix_length'] = case.output_prefix
        if case.checker:
          assign_checker(data, case)
        else:
          case.checker_args = ''
        case.save(update_fields=('checker_args', 'is_pretest'))
        (batch['batched'] if batch else cases).append(data)
      elif case.type == 'S':
        if batch:
          end_batch()
        if case.points is None:
          raise ProblemDataError(_('Batch start case #%d requires points.') % i)
        batch = {
          'points': case.points,
          'batched': [],
          'is_pretest': case.is_pretest,
        }
        if case.generator_args:
          batch['generator_args'] = case.generator_args.splitlines()
        if case.output_limit is not None:
          batch['output_limit_length'] = case.output_limit
        if case.output_prefix is not None:
          batch['output_prefix_length'] = case.output_prefix
        if case.checker:
          assign_checker(batch, case)
        else:
          case.checker_args = ''
        case.input_file = ''
        case.output_file = ''
        case.save(update_fields=('checker_args', 'input_file', 'output_file'))
      elif case.type == 'E':
        if not batch:
          raise ProblemDataError(_('Attempt to end batch outside of one in case #%d') % i)
        case.is_pretest = batch['is_pretest']
        case.input_file = ''
        case.output_file = ''
        case.generator_args = ''
        case.checker = ''
        case.checker_args = ''
        case.save()
        end_batch()
        batch = None
    if batch:
      end_batch()

    init = {}

    if self.data.zipfile:
      zippath = split_path_first(self.data.zipfile.name)
      if len(zippath) != 2:
        raise ProblemDataError(_('How did you corrupt the zip path?'))
      init['archive'] = zippath[1]

    if self.generator:
      generator_path = split_path_first(self.generator.name)
      if len(generator_path) != 2:
        raise ProblemDataError(_('How did you corrupt the generator path?'))
      init['generator'] = generator_path[1]

    pretests = [case for case in cases if case['is_pretest']]
    for case in cases:
      del case['is_pretest']
    if pretests:
      init['pretest_test_cases'] = pretests
    if cases:
      init['test_cases'] = cases
    if self.data.output_limit is not None:
      init['output_limit_length'] = int(self.data.output_limit)
    if self.data.output_prefix is not None:
      init['output_prefix_length'] = int(self.data.output_prefix)
    if self.data.checker:
      assign_checker(init, self.data)
    else:
      self.data.checker_args = ''
    return init

  def compile(self):
    from problem.models import problem_data_storage

    yml_file = '%s/init.yml' % self.problem.shortname
    try:
      init = self.make_init()
      init['wall_time_factor'] = 1
      if init:
        init = yaml.safe_dump(init)
    except ProblemDataError as e:
      self.data.feedback = e.message
      self.data.save()
      problem_data_storage.delete(yml_file)
    else:
      self.data.feedback = ''
      self.data.save()
      if init:
        problem_data_storage.save(yml_file, ContentFile(init))
      else:
        # Don't write empty init.yml since we should be looking in manually managed
        # judge-server#670 will not update cache on empty init.yml,
        # but will do so if there is no init.yml, so we delete the init.yml
        problem_data_storage.delete(yml_file)

  @classmethod
  def generate(cls, *args, **kwargs):
    self = cls(*args, **kwargs)
    self.compile()


class ProblemPDFStorage(FileSystemStorage):
  def __init__(self):
    super(ProblemPDFStorage, self).__init__(settings.BKDNOJ_PROBLEM_PDF_ROOT)

  def url(self, name):
    path = split_path_first(name)
    if len(path) != 2:
      raise ValueError('This file is not accessible via a URL.')
    return reverse('problem_pdf_file', args=path)

  def _save(self, name, content):
    if self.exists(name):
      self.delete(name)
    return super(ProblemPDFStorage, self)._save(name, content)

  def get_available_name(self, name, max_length=None):
    return name

  def rename(self, old, new):
    return os.rename(self.path(old), self.path(new))


problem_data_storage = ProblemDataStorage()
problem_pdf_storage = ProblemPDFStorage()

def problem_directory_pdf(prob, filename):
  return os.path.join(prob.shortname,
                      settings.BKDNOJ_PROBLEM_STATEMENT_PDF_FILENAME)
