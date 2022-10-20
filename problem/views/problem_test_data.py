from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework import views, permissions, generics, viewsets, response, status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser

from problem.serializers import ProblemSerializer, ProblemTestProfileSerializer
from problem.models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
    SubmissionBasicSerializer

from helpers.problem_data import problem_pdf_storage
from judger.utils.unicode import utf8text
from judger.highlight_code import highlight_code

import logging
logger = logging.getLogger(__name__)

import json
from zipfile import BadZipFile

class ProblemTestProfileListView(generics.ListAPIView):
    """
        Return a List of Problem Test Profiles
    """
    queryset = ProblemTestProfile.objects.none()
    serializer_class = ProblemTestProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class ProblemTestProfileDetailView(generics.RetrieveUpdateAPIView):
    """
        Return a Detailed view of the requested Problem Test Profiles
    """
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestProfileSerializer
    lookup_field = 'problem'
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, problem=''):
        method = self.request.method
        if method == 'GET':
            problem = get_object_or_404(Problem, shortname=self.kwargs['problem'])
            if problem.is_accessible_by(self.request.user):
                probprofile, _ = ProblemTestProfile.objects.get_or_create(problem=problem)
                return probprofile
            raise PermissionDenied
        else:
            problem = get_object_or_404(Problem, shortname=self.kwargs['problem'])
            if problem.is_editable_by(self.request.user):
                probprofile, _ = ProblemTestProfile.objects.get_or_create(problem=problem)
                return probprofile
            raise PermissionDenied

    def get(self, request, problem, *args, **kwargs):
        probprofile = self.get_object(problem)
        return response.Response(
            ProblemTestProfileSerializer(probprofile, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, *args, **kwargs):
        return self.put(*args, **kwargs)

    @parser_classes([MultiPartParser])
    def put(self, request, problem, *args, **kwargs):
        FILE_FIELDS = ('zipfile', 'generator', 'custom_checker')
        obj = self.get_object(problem)
        data = request.data.copy()
        data.pop('problem', None)

        is_zipfile_changed = False

        for k, v in data.items():
            # k is file key but the file is empty
            if (k in FILE_FIELDS) and not v: continue
            if k == 'custom_checker' and v:
                obj.custom_checker = v
            if k == 'generator' and v:
                obj.generator = v
            elif k == 'zipfile' and v:
                is_zipfile_changed = True
                obj.set_zipfile(v)
            elif k == 'custom_checker_remove' and v == 'true':
                if obj.custom_checker: obj.custom_checker.delete(save=False)
            elif k == 'zipfile_remove' and v == 'true':
                if obj.zipfile:
                    is_zipfile_changed = True
                    obj.zipfile.delete(save=False)
            elif k == 'generator_remove' and v == 'true':
                if obj.generator: obj.generator.delete(save=False)
            else:
                setattr(obj, k, v)

        try:
            obj.save()
        except ValidationError as ve:
            return response.Response({
                'errors': {'error': ve},
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj.update_pdf_within_zip()
            if is_zipfile_changed:
                obj.generate_test_cases()
            else:
                obj.update_test_cases()
            # obj will be saved because both ended with ProblemDataCompile.gen
            # and it calls obj.save
        except BadZipFile as bzfe:
            return response.Response({
                'details': 'BadZipFile: your Archive is corrupted or is not a valid zipfile'
            }, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(
            ProblemTestProfileSerializer(obj, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from problem.models import problem_data_storage
import os
from django.conf import settings

def add_file_response(request, response, url_path, file_path, file_object=None):
    if url_path is not None and request.META.get('SERVER_SOFTWARE', '').startswith('nginx/'):
        response['X-Accel-Redirect'] = url_path
    else:
        if file_object is None:
            with open(file_path, 'rb') as f:
                response.content = f.read()
        else:
            with file_object.open(file_path, 'rb') as f:
                response.content = f.read()

def __problem_x_file(request, shortname, path, url_path, storage, content_type='application/octet-stream', perm_type='access'):
    problem_code = shortname
    problem = get_object_or_404(Problem, shortname=problem_code)

    from compete.models import Contest
    ckey = request.GET.get('contest', None)
    contest = Contest.objects.filter(key=ckey)

    if perm_type == 'edit':
        if not problem.is_editable_by(request.user):
            raise Http404()
    else:
        if not problem.is_accessible_by(request.user, contest=contest.first()):
            raise Http404()

    problem_dir = storage.path(problem_code)
    if os.path.commonpath(
        (storage.path(os.path.join(problem_code, path)), problem_dir)
    ) != problem_dir:
        raise Http404()

    response = HttpResponse()
    try:
        add_file_response(request, response, url_path, os.path.join(problem_code, path), storage)
    except IOError:
        raise Http404()

    response['Content-Type'] = content_type
    return response

# api_view decorator has auth middleware to set request.user
@api_view(['GET'])
def problem_data_file(request, shortname, path):
    if hasattr(settings, 'BKDNOJ_PROBLEM_DATA_INTERNAL'):
        url_path = '%s/%s/%s' % (settings.BKDNOJ_PROBLEM_DATA_INTERNAL, shortname, path)
    else:
        url_path = None
    return __problem_x_file(request, shortname, path, url_path, problem_data_storage, 'application/octet-stream', 'edit')

# api_view decorator has auth middleware to set request.user
@api_view(['GET'])
def problem_pdf_file(request, shortname, path):
    return __problem_x_file(request, shortname, path, None, problem_pdf_storage, 'application/pdf')
