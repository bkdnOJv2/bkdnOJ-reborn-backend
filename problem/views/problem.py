from django.conf import settings
from django.utils.translation import gettext as _
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

import io
from zipfile import BadZipfile, ZipFile

encoding = 'utf-8-sig'
config_to_problem_mapping = {
  'shortname': ['code', 'codename', 'probid'],
  'title': ['name', 'title', 'problem', 'code', 'codename'],
  'time_limit': ['time_limit', 'timelimit', 'time', 'tl'],
  'memory_limit': ['memory_limit', 'memorylimit', 'mem_limit', 'memlimit', 'memory', 'mem', 'ml'],
  'points': ['points', 'pts'],
  'short_circuit': ['icpc', 'ioi', 'mode'],
  'partial': ['icpc', 'ioi', 'mode'],
}

@api_view(['POST'])
def create_problem_from_archive(request):
  archive = request.FILES['archive']

  config_file = None
  problem_config = {}

  with ZipFile(archive, 'r') as zfile:
    for filename in zfile.namelist():
      if filename[-3:] == 'ini':
        print(f"Reading file '{filename}':")
        if config_file != None:
          return Response({
            "detail": f"Found multiple config files ['{config_file}', '{filename}']."
          }, status=status.HTTP_400_BAD_REQUEST)

        config_file = filename
        with zfile.open(config_file) as file:
          line_row = 0
          for line in io.TextIOWrapper(file, encoding):
            line_row += 1

            line = ustrip(line)
            print(ord(line[0]), ord(line[1]))
            if len(line) == 0 or line.startswith(';'): # comment or empty line
              continue

            tokens = line.split('=')
            if len(tokens) != 2:
              return Response({
                "detail": f"Invalid format while reading File '{config_file}', "+
                          f"Line {line_row}: '{line}'."
              }, status=status.HTTP_400_BAD_REQUEST)
            problem_config[ustrip(tokens[0])] = ustrip(tokens[1])
  print(problem_config)

  return Response({"detail": "Received file"})