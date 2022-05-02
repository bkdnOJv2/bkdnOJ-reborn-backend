from rest_framework import views, permissions, generics, viewsets, response, status

from problem.serializers import ProblemSerializer, ProblemTestProfileSerializer
from problem.models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
    SubmissionURLSerializer

import logging
logger = logging.getLogger(__name__)

import json

class ProblemTestProfileListView(generics.ListAPIView):
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestProfileSerializer

class ProblemTestProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestProfileSerializer
    lookup_field = 'problem'

    def get(self, request, *args, **kwargs):
        problem = self.kwargs.get('problem')
        try:
            problem = Problem.objects.get(shortname=problem)
        except Problem.DoesNotExist:
            return response.Response('Cannot find such problem.',
                status=status.HTTP_404_NOT_FOUND,
            )
        probprofile, probprofile_created = ProblemTestProfile.objects.get_or_create(problem=problem)
        return response.Response(
            ProblemTestProfileSerializer(probprofile, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
    def patch(self, *args, **kwargs):
        return self.put(*args, **kwargs)
    
    def put(self, request, problem, *args, **kwargs):
        FILE_FIELDS = ('zipfile', 'generator')
        obj = self.get_object()

        for k, v in request.data.items():
            # k is file key but the file is empty
            if (k in FILE_FIELDS) and not v:
                continue
            if k == 'zipfile' and v:
                obj.set_zipfile(v)
                continue
            if k == 'zipfile_remove' and v == True:
                if obj.zipfile:
                    obj.delete_zipfile(save=False)
                continue
            if k == 'generator_remove' and v == True:
                if obj.generator:
                    obj.generator.delete(save=False)
                continue
            setattr(obj, k, v)
        obj.save()
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

def problem_data_file(request, shortname, path):
    logger.warn(shortname)
    problem = shortname
    object = get_object_or_404(Problem, shortname=problem)
    if not object.is_editable_by(request.user):
        raise Http404()

    problem_dir = problem_data_storage.path(problem)
    logger.warn('Problem dir: %s', problem_dir)

    if os.path.commonpath(
        (problem_data_storage.path(os.path.join(problem, path)), problem_dir)
    ) != problem_dir:
        raise Http404()

    response = HttpResponse()

    if hasattr(settings, 'DMOJ_PROBLEM_DATA_INTERNAL'):
        url_path = '%s/%s/%s' % (settings.DMOJ_PROBLEM_DATA_INTERNAL, problem, path)
    else:
        url_path = None

    try:
        add_file_response(request, response, url_path, os.path.join(problem, path), problem_data_storage)
    except IOError:
        raise Http404()

    response['Content-Type'] = 'application/octet-stream'
    return response

def problem_init_view(request, problem):
    problem = get_object_or_404(Problem, shortname=problem)
    if not problem.is_editable_by(request.user):
        raise Http404()

    try:
        with problem_data_storage.open(os.path.join(problem.shortname, 'init.yml'), 'rb') as f:
            data = utf8text(f.read()).rstrip('\n')
    except IOError:
        raise Http404()

    return render(request, 'problem/yaml.html', {
        'raw_source': data, 'highlighted_source': highlight_code(data, 'yaml'),
        'title': _('Generated init.yml for %s') % problem.name,
        'content_title': mark_safe(escape(_('Generated init.yml for %s')) % (
            format_html('<a href="{1}">{0}</a>', problem.name,
                        reverse('problem_detail', args=[problem.shortname])))),
    })