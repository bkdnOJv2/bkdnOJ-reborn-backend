import io, os
from ast import literal_eval
from zipfile import BadZipfile, ZipFile

from django.shortcuts import get_object_or_404

from django.core.exceptions import PermissionDenied
from django.core.validators import ValidationError

from django.http import Http404
from django.conf import settings
from django.utils.translation import gettext as _
from django.db import transaction, IntegrityError
from rest_framework import views, permissions, generics, viewsets, response, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException
import django_filters.rest_framework

from problem.validators import problem_data_zip_validator
from problem.serializers import ProblemBriefSerializer, ProblemSerializer, \
  ProblemTestProfileSerializer
from problem.models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
  SubmissionBasicSerializer
from organization.models import Organization

from helpers.string_process import ustrip

__all__ = [
  'ProblemListView', 'ProblemDetailView',
  'ProblemSubmitView', 'ProblemRejudgeView', 'create_problem_from_archive'
]

import logging
logger = logging.getLogger(__name__)

class ProblemListView(generics.ListCreateAPIView):
  """
    Return a list of Problems
  """
  serializer_class = ProblemBriefSerializer
  permission_classes = []
  lookup_field = 'shortname'
  filter_backends = [
    django_filters.rest_framework.DjangoFilterBackend,
    filters.SearchFilter,
    filters.OrderingFilter,
  ]
  search_fields = ['^shortname', '@title']
  filterset_fields = ['is_public', 'is_organization_private', 'partial', 'short_circuit']
  ordering_fields = ['modified', 'created', 'points']
  ordering = ['-created']

  def check_perms(self, request):
      if request.method == 'GET':
          pass
      else:
          if not request.user.is_staff:
              raise PermissionDenied
      return True

  def get_queryset(self):
      user = self.request.user
      if not user.is_authenticated:
        return Problem.get_public_problems()

      return Problem.get_visible_problems(user)

      org = self.request.query_params.get('org', None)
      if org:
        org = Organization.objects.filter(slug=org).first()
        if org and org.id in user.profile.member_of_org_with_ids:
          return Problem.get_org_visible_problems(org)
        else:
          return Problem.objects.none()
      else:
        # return Problem.get_visible_problems(user)
        return Problem.get_public_problems()

  def post(self, request):
      self.check_perms(request)
      try:
          rs = super().post(request)
          return rs
      except IntegrityError as ie:
          return Response({ 'detail': str(ie) },
            status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
          return Response({ 'detail': str(e) },
            status=status.HTTP_400_BAD_REQUEST)


class ProblemDetailView(generics.RetrieveUpdateDestroyAPIView):
  """
    Return detailed view of the requested problem
  """
  serializer_class = ProblemSerializer
  permission_classes = []
  lookup_field = 'shortname'

  def get_object(self):
      method = self.request.method
      p = get_object_or_404(Problem, shortname=self.kwargs['shortname'])
      if method == 'GET':
          if not p.is_accessible_by(self.request.user):
              raise Http404()
      else:
          if not p.is_editable_by(self.request.user):
              raise PermissionDenied
      return p

  def get_serializer_context(self):
    return {
      'request': self.request,
    }

  def put(self, *args):
    return self.patch(*args)

  def patch(self, request, shortname):
    p = self.get_object()
    data = request.data
    if data.get('pdf'):
      p.pdf = data['pdf']
      p.save()
      return Response(self.serializer_class(p, context=self.get_serializer_context()).data, status=status.HTTP_200_OK)
    else:
      return super().patch(request, shortname)


class ProblemSubmitView(generics.CreateAPIView):
  """
    Return the requested Problem's view to submit submissions.
  """
  serializer_class = SubmissionSubmitSerializer
  lookup_field = 'shortname'
  permission_classes = [permissions.IsAuthenticated]

  def get_object(self):
      p = get_object_or_404(Problem, shortname=self.kwargs['shortname'])
      if not p.is_accessible_by(self.request.user):
          raise Http404()
      return p

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

from judger.tasks.submission import rejudge_problem_filter, apply_submission_filter

class ProblemRejudgeView(views.APIView):
  """
    Rejudge all submissions of a Problem, including in contest
  """
  serializer_class = SubmissionSubmitSerializer
  lookup_field = 'shortname'
  permission_classes = [permissions.IsAdminUser]

  def get_object(self):
    p = get_object_or_404(Problem, shortname=self.kwargs['shortname'])
    if not p.is_editable_by(self.request.user):
      raise PermissionDenied
    return p

  def get_sub_id_range(self, request):
    data = request.data
    if data == {}:
      data = request.GET
    if data.get('use_range', 'off') == 'on':
      try:
        start = int(data.get('start'))
        end = int(data.get('end'))
        return (start, end)
      except (KeyError, ValueError, TypeError):
        pass
    return None

  def get(self, request, shortname):
    problem = self.get_object()
    queryset = problem.submission_set
    if not queryset.exists():
        return Response({
            'detail': 'There are no submission to rejudge.'
        }, status=status.HTTP_400_BAD_REQUEST)

    id_range = self.get_sub_id_range(request)
    if id_range is None:
      id_range = (queryset.last().id, queryset.first().id)

    queryset = apply_submission_filter(queryset, id_range, None, None)
    ##
    cnt = queryset.count()
    return Response({
      'count': cnt,
      'msg': f"This will rejudge {cnt} submission(s).",
    })

  def post(self, request, shortname):
    problem = self.get_object()
    queryset = problem.submission_set
    if not queryset.exists():
        return Response({
            'detail': 'There are no submission to rejudge.'
        }, status=status.HTTP_400_BAD_REQUEST)

    id_range = self.get_sub_id_range(request)
    if id_range is None:
      id_range = (queryset.last().id, queryset.first().id)

    queryset = apply_submission_filter(queryset, id_range, None, None)

    ## ---
    async_status = rejudge_problem_filter.delay(
      problem.id, id_range, user_id=request.user.id)

    return Response({}, status=status.HTTP_204_NO_CONTENT)

CONF_TOK_LEN = settings.BKDNOJ_PROBLEM_CONFIG_TOKEN_LENGTH
encoding = 'utf-8-sig'
__prob_attrib_2_confkey = {
  'shortname': ['shortname', 'code', 'codename', 'probid',],
  'title': ['name', 'title', 'problem', 'code', 'codename'],
  'time_limit': ['time_limit', 'timelimit', 'time', 'tl'],
  'memory_limit': ['memory_limit', 'memorylimit', 'mem_limit', 'memlimit', 'memory', 'mem', 'ml'],
  'points': ['points', 'pts'],

  'short_circuit': ['short_circuit', 'skip_non_ac', 'icpc'],
  'partial': ['partial', 'allow_partial', 'ioi'],

  'is_public': ['is_public', 'public', ]
}

@api_view(['POST'])
def create_problem_from_archive(request):
  archive = request.FILES.get('archive')
  if archive == None:
    return Response({'detail': "No zip file with key can be found."},
      status=status.HTTP_400_BAD_REQUEST)

  config_file = None
  problem_config = {}

  try:
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

              eqlpos = line.find('=')
              if eqlpos < 0:
                return Response({
                  "detail": f"Invalid format. File '{config_file}', "+
                            f"Line {line_row}: `{line}` not following 'KEY=VALUE' format."
                }, status=status.HTTP_400_BAD_REQUEST)

              # String unicode whitespaces
              parsed_key = ustrip(line[:eqlpos])
              parsed_val = ustrip(line[eqlpos+1:])

              # Check the length to make sure notempty or too long
              if len(parsed_key) == 0 or len(parsed_key) > CONF_TOK_LEN:
                return Response({
                  "detail": f"File '{config_file}', line {line_row}: Key is empty or too long. (>{CONF_TOK_LEN})"
                }, status=status.HTTP_400_BAD_REQUEST)

              if len(parsed_val) == 0 or len(parsed_val) > CONF_TOK_LEN:
                return Response({
                  "detail": f"File '{config_file}', line {line_row}: Value is empty or too long. (>{CONF_TOK_LEN})"
                }, status=status.HTTP_400_BAD_REQUEST)

              # The value might be a string enclosed in Ascii quotes
              # If starts or end with a quote, attempt to parse it
              if parsed_val[0] in "'\"" or parsed_val[-1] in "'\"":
                # because we have checked the length, this wont crash the ast compiler
                try:
                  parsed_val = literal_eval(parsed_val)
                except Exception as err:
                  return Response({
                    "detail": f"Cannot parse value for key {parsed_key} ({err})"
                  }, status=status.HTTP_400_BAD_REQUEST)

              problem_config[parsed_key] = ustrip(parsed_val)
  except BadZipfile:
    return Response({
      "detail": "Provided file is not a valid .zip file.",
    }, status=status.HTTP_400_BAD_REQUEST)

  # Collect into a dict
  data = {}
  conf_key_set = set(problem_config.keys())
  for attrib, keylist in __prob_attrib_2_confkey.items():
    for key in keylist:
      if key in conf_key_set:
        data[attrib] = problem_config[key]
        break

  # Include additional data that config file might not have
  data['authors'] = [{'username':request.user.username}]

  # Validating Problem settings
  context={'request':request}
  seri = ProblemSerializer(data=data, context=context)
  if not seri.is_valid():
    return Response({
      "detail": "Invalid problem attributes after parsing.",
      "errors": seri.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

  # Validating archive testdata
  try:
    problem_data_zip_validator(archive)
  except ValidationError as ve:
    return Response({
      "detail": "Invalid test cases.",
      "errors": ve,
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
      return Response(seri.data, status=status.HTTP_201_CREATED)
  except IntegrityError as intergrity_err:
    return Response({
      'detail': "Error while creating problem/populating data",
      'errors': [str(intergrity_err)],
    }, status=status.HTTP_400_BAD_REQUEST)
