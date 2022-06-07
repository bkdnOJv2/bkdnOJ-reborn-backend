from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from rest_framework import views, permissions, generics, viewsets, response, status

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

class ProblemTestProfileListView(generics.ListAPIView):
    """
        Return a List of Problem Test Profiles
    """
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestProfileSerializer

class ProblemTestProfileDetailView(generics.RetrieveUpdateAPIView):
    """
        Return a Detailed view of the requested Problem Test Profiles
    """
    queryset = ProblemTestProfile.objects.all()
    serializer_class = ProblemTestProfileSerializer
    lookup_field = 'problem'

    def get(self, request, *args, **kwargs):
        problem = get_object_or_404(Problem, shortname=self.kwargs['problem'])
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
            if k == 'generator' and v:
                obj.generator = v
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

        # # # Currently not in-use
        # # output_prefix and output_length wasn't updated yet
        # obj.save(update_fields=['output_limit', 'output_prefix'])
        obj.generate_test_cases()
        obj.update_pdf_within_zip()
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

def __problem_x_file(request, shortname, path, url_path, storage, content_type='application/octet-stream'):
    problem = shortname
    obj = get_object_or_404(Problem, shortname=problem)
    if not obj.is_accessible_by(request.user):
        raise Http404()

    problem_dir = storage.path(problem)
    if os.path.commonpath(
        (storage.path(os.path.join(problem, path)), problem_dir)
    ) != problem_dir:
        raise Http404()

    response = HttpResponse()
    try:
        add_file_response(request, response, url_path, os.path.join(problem, path), storage)
    except IOError:
        raise Http404()

    response['Content-Type'] = content_type
    return response


def problem_data_file(request, shortname, path):
    if hasattr(settings, 'BKDNOJ_PROBLEM_DATA_INTERNAL'):
        url_path = '%s/%s/%s' % (settings.BKDNOJ_PROBLEM_DATA_INTERNAL, shortname, path)
    else:
        url_path = None
    return __problem_x_file(request, shortname, path, url_path, problem_data_storage, 'application/octet-stream')


def problem_pdf_file(request, shortname, path):
    return __problem_x_file(request, shortname, path, None, problem_pdf_storage, 'application/pdf')

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
