from django.conf import settings
from django.utils.translation import gettext as _
from django.db import transaction, IntegrityError
from rest_framework import views, permissions, generics, viewsets, response, status

from problem.serializers import ProblemBriefSerializer, ProblemSerializer, \
  ProblemTestProfileSerializer
from problem.models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
  SubmissionBasicSerializer

import logging
logger = logging.getLogger(__name__)

class ProblemListView(generics.ListCreateAPIView):
  """ 
    Return a list of Problems 
  """
  queryset = Problem.objects.all()
  serializer_class = ProblemBriefSerializer
  permission_classes = []

class ProblemDetailView(generics.RetrieveUpdateDestroyAPIView):
  """ 
    Return detailed view of the requested problem
  """
  queryset = Problem.objects.all()
  serializer_class = ProblemSerializer 
  permission_classes = []
  lookup_field = 'shortname'


class ProblemSubmitView(generics.CreateAPIView):
  """ 
    Return the requested Problem's view to submit submissions.
  """
  queryset = Problem.objects.all()
  serializer_class = SubmissionSubmitSerializer
  lookup_field = 'shortname'
  permission_classes = [permissions.IsAuthenticated]
  
  def create(self, request, *args, **kwargs):
    if (
      not self.request.user.has_perm('submission.spam_submission') 
      and Submission
        .objects.filter(user=self.request.user.profile, rejudged_date__isnull=True)
        .exclude(status__in=['D', 'IE', 'CE', 'AB']).count() >= settings.BKDNOJ_SUBMISSION_LIMIT
    ):
      return response.Response(
        _('You have reached maximum pending submissions allowed. '
          'Please wait until your previous submissions finish grading.'),
        status=status.HTTP_429_TOO_MANY_REQUESTS,
      )

    prob = self.get_object()

    sub = SubmissionSubmitSerializer(data=request.data)
    if not sub.is_valid():
      return response.Response(sub.errors, status=status.HTTP_400_BAD_REQUEST)
    
    sub_obj = sub.save(problem=prob, user=request.user.profile)
    sub_obj.judge()
    return response.Response(
      SubmissionBasicSerializer(sub_obj, context={'request':request}).data,
      status=status.HTTP_200_OK,
    )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from helpers.string_process import ustrip

import io, os
from ast import literal_eval
from zipfile import BadZipfile, ZipFile

encoding = 'utf-8-sig'
__prob_attrib_2_confkey = {
  'shortname': ['code', 'codename', 'probid'],
  'title': ['name', 'title', 'problem', 'code', 'codename'],
  'time_limit': ['time_limit', 'timelimit', 'time', 'tl'],
  'memory_limit': ['memory_limit', 'memorylimit', 'mem_limit', 'memlimit', 'memory', 'mem', 'ml'],
  'points': ['points', 'pts'],
  'short_circuit': ['skip_non_ac', 'short_circuit'],
  'partial': ['allow_partial', 'partial'],
}

@api_view(['POST'])
def create_problem_from_archive(request):
  archive = request.FILES.get('archive')
  if archive == None:
    return Response({'detail': "No zip file with key can be found."},
      status=status.HTTP_400_BAD_REQUEST)

  config_file = None
  problem_config = {}

  with ZipFile(archive, 'r') as zfile:
    for filename in zfile.namelist():
      _, fileext = os.path.splitext(filename)
      if fileext in settings.BKDNOJ_PROBLEM_ACCEPTABLE_CONFIG_EXT:
        # print(f"Reading file '{filename}':")
        if config_file != None:
          return Response({
            "detail": f"Found multiple config files ['{config_file}', '{filename}']. Please provide only 1 config file."
          }, status=status.HTTP_400_BAD_REQUEST)

        config_file = filename
        with zfile.open(config_file) as file:
          line_row = 0
          for line in io.TextIOWrapper(file, encoding):
            line_row += 1

            line = ustrip(line)
            if len(line) == 0 or line.startswith(';'): # comment or empty line
              continue

            tokens = line.split('=')
            if len(tokens) != 2:
              return Response({
                "detail": f"Invalid format while reading File '{config_file}', "+
                          f"Line {line_row}: '{line}'."
              }, status=status.HTTP_400_BAD_REQUEST)
            
            # The value might be a string enclosed in Ascii quotes
            parsed_key = ustrip(tokens[0])
            parsed_val = ustrip(tokens[1])
            # If starts or end with a quote, attempt to parse it
            if parsed_val[0] in "'\"" or parsed_val[-1] in "'\"":
              # attempt to avoid crashing ast compiler by limiting the len 
              if len(parsed_val) > 65536: 
                return Response({
                  "detail": f"Key '{parsed_key}' has value's length too long (>65536)."
                }, status=status.HTTP_400_BAD_REQUEST)

              try:
                parsed_val = literal_eval(parsed_val)
              except Exception as err:
                return Response({
                  "detail": f"Cannot parse value for key {parsed_key} ({err})"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            problem_config[parsed_key] = ustrip(parsed_val)
   
  # Collect into a dict
  data = {}
  conf_key_set = set(problem_config.keys())
  for attrib, keylist in __prob_attrib_2_confkey.items():
    for key in keylist:
      if key in conf_key_set: 
        data[attrib] = problem_config[key]
        break
    
  # Include additional data that config file might not have
  data['authors'] = [request.user]
      
  # Validatin
  context={'request':request}
  seri = ProblemSerializer(data=data, context=context)
  if not seri.is_valid():
    return Response({
      "detail": "Invalid problem attributes after parsing.",
      "errors": seri.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

  # Creating problem object
  try:
    with transaction.atomic():
      prob = seri.save()
      test_profile, _ = ProblemTestProfile.objects.get_or_create(problem=prob)
      test_profile.set_zipfile( archive )
      test_profile.generate_test_cases()
      test_profile.update_pdf_within_zip()
      test_profile.save()
      return Response(seri.data, 
        status=status.HTTP_201_CREATED)
  except IntegrityError as intergrity_err:
    return Response({
      "detail": intergrity_err,
    }, status=status.HTTP_400_BAD_REQUEST)
