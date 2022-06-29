from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('problem/',
        ProblemListView.as_view(),
        name='problem-list'
    ),
    path('problem-from-archive',
        create_problem_from_archive,
        name='problem-from-archive'
    ),

    path('problem/<str:shortname>/',
        ProblemDetailView.as_view(),
        name='problem-detail',
    ),
    path('problem/<int:pk>/',
        ProblemDetailView.as_view(),
        name='problem-detail',
    ),

    path('problem/<str:shortname>/submit/',
        ProblemSubmitView.as_view(),
        name='problem-submit',
    ),
    path('problem/<str:shortname>/rejudge/',
        ProblemRejudgeView.as_view(),
        name='problem-rejudge',
    ),

    path('problem/<str:problem>/data/',
        ProblemTestProfileDetailView.as_view(),
        name='problem-data-detail',
    ),
    # TestCase Views
    path('problem/<str:shortname>/data/test/',
        TestCaseListView.as_view(),
        name='problemtestcase-list',
    ),
    path('problem/<str:shortname>/data/test/<int:pk>/',
        TestCaseDetailView.as_view(),
        name='problemtestcase-detail',
    ),

    path('problem/problem_data/<str:shortname>/<path:path>',
        problem_data_file, name='problem_data_file'
    ),
    path('problem/problem_pdf/<str:shortname>/<path:path>',
        problem_pdf_file, name='problem_pdf_file'
    ),

    path('problem-test-profile/',
        ProblemTestProfileListView.as_view(),
        name='problemtestprofile-list',
    ),
    path('problem-test-profile/<str:problem>/',
        ProblemTestProfileDetailView.as_view(),
        name='problemtestprofile-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
