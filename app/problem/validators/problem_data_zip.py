from django.conf import settings
VALID_IN_EXT = settings.BKDNOJ_PROBLEM_DATA_IN_FILE_EXT 
VALID_ANS_EXT = settings.BKDNOJ_PROBLEM_DATA_ANS_FILE_EXT 

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from django.core.validators import ValidationError
from zipfile import BadZipFile, ZipFile

import logging
logger = logging.getLogger(__name__)

import os

@deconstructible
class ProblemDataZipFileValidator(object):
  error_messages = {
   'no_matching_ans_files': 
      "These input files doesn't have corresponding answer files: %(no_match_ans)s",
    
   'no_matching_in_files': 
      "These answer files doesn't have corresponding input files: %(no_match_in)s",
    
   'duplicated_file_prefix': "These input (or answer) files have the same prefix when "
      "we strip their extension. bkdnOJ uses their prefix to separate different input "
      "(or answer) files from each other. "
      "Please change their name or put them into separate folders: %(dup_files)s"
  }

  def __init__(self):
    pass

  @staticmethod
  def check_duplicate_prefix(arr, file_list):
    dup_files = []
    dup_start = 0
    for fidx in range(1, len(arr)):
      if arr[fidx-1][0] != arr[fidx][0]:
        if dup_start+1 < fidx:
          dups = []
          for i in range(dup_start, fidx):
            dups.append(file_list[ arr[i][1] ])
          dup_files.append( str(dups) )
        dup_start = fidx

    if len(dup_files) > 0:
      raise ValidationError(
        self.error_messages['duplicated_file_prefix'], 'duplicated_file_prefix', {
          'dup_files': str(dup_files),
        }
      )

  def __call__(self, data):
    file_list = ZipFile(data).namelist()
    in_files, ans_files = [], []
    for idx, file in enumerate(file_list):
      base_name, ext_name = os.path.splitext(file)
      if ext_name in VALID_IN_EXT:
        in_files.append( (base_name, idx) )
      elif ext_name in VALID_ANS_EXT:
        ans_files.append( (base_name, idx) )
    
    in_files.sort()
    ProblemDataZipFileValidator.check_duplicate_prefix(in_files, file_list)
    ans_files.sort()
    ProblemDataZipFileValidator.check_duplicate_prefix(ans_files, file_list)

    in_idx = ans_idx = 0
    no_match_ans, no_match_in = [], []
    while in_idx < len(in_files) and ans_idx < len(ans_files):
      if in_files[in_idx][0] > ans_files[ans_idx][0]:
        no_match_in.append(file_list[ ans_files[ans_idx][1] ])
        ans_idx += 1
      elif in_files[in_idx][0] < ans_files[ans_idx][0]:
        no_match_ans.append(file_list[ in_files[in_idx][1] ])
        in_idx += 1
      else:
        in_idx += 1
        ans_idx += 1
    
    while in_idx < len(in_files):
      no_match_ans.append(file_list[ in_files[in_idx][1] ])
      in_idx += 1
    
    while ans_idx < len(ans_files):
      no_match_in.append(file_list[ ans_files[ans_idx][1] ])
      ans_idx += 1
    
    if len(no_match_ans) > 0:
      raise ValidationError(
        self.error_messages['no_matching_ans_files'], 'no_matching_ans_files', 
        {'no_match_ans': no_match_ans},
      )
    
    if len(no_match_in) > 0:
      raise ValidationError(
        self.error_messages['no_matching_in_files'], 'no_matching_in_files',
        {'no_match_in': no_match_in},
      )

problem_data_zip_validator = ProblemDataZipFileValidator()