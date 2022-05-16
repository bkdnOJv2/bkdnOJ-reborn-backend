from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProblemListView, ProblemDetailView, \
    ProblemTestProfileListView, ProblemTestProfileDetailView, \
    ProblemSubmitView, \
    TestCaseListView, TestCaseDetailView, \
    problem_pdf_file, problem_data_file 

urlpatterns = [
    path('problem/', 
        ProblemListView.as_view(), 
        name='problem-list'
    ),
    path('problem/<str:shortname>/', 
        ProblemDetailView.as_view(), 
        name='problem-detail',
    ),
    path('problem/<str:shortname>/submit/', 
        ProblemSubmitView.as_view(), 
        name='problem-submit',
    ),
    path('problem/<str:problem>/data/', 
        ProblemTestProfileDetailView.as_view(), 
        name='problem-data-detail',
    ),
    # TestCase Views
    path('problem/<str:problem>/data/test/', 
        TestCaseListView.as_view(), 
        name='problemtestcase-list',
    ),
    path('problem/<str:problem>/data/test/<int:pk>/', 
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