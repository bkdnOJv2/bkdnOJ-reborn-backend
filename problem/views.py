from rest_framework import views, permissions, generics, viewsets, response, status

from .serializers import ProblemSerializer, ProblemTestDataProfileSerializer
from .models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
    SubmissionURLSerializer

import logging
logger = logging.getLogger(__name__)

import json

# Create your views here.
class ProblemListView(generics.ListCreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = []

class ProblemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer #ProblemDetailSerializer
    permission_classes = []
    lookup_field = 'shortname'

class ProblemSubmitView(generics.CreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = SubmissionSubmitSerializer
    lookup_field = 'shortname'
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        prob = self.get_object()

        sub = SubmissionSubmitSerializer(data=request.data)
        if not sub.is_valid():
            return response.Response(sub.errors, status=status.HTTP_400_BAD_REQUEST)
        sub_obj = sub.save(problem=prob, user=request.user.profile)

        return response.Response(
            SubmissionURLSerializer(sub_obj, context={'request':request}).data,
            status=status.HTTP_200_OK
        )

class ProblemTestDataProfileListView(generics.ListAPIView):
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer

class ProblemTestDataProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer
    lookup_field = 'problem'
    
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
