from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProblemListView, ProblemDetailView, \
    ProblemTestDataProfileListView, ProblemTestDataProfileDetailView, \
    ProblemSubmitView, problem_data_file

urlpatterns = [
    path('problem/', 
        ProblemListView.as_view(), 
        name='problem-list'
    ),
    path('problem/<str:shortname>/', 
        ProblemDetailView.as_view(), 
        name='problem-detail',
    ),
    path('problem/<str:shortname>/submit', 
        ProblemSubmitView.as_view(), 
        name='problem-submit',
    ),
    path('problem/<str:problem>/data/', 
        ProblemTestDataProfileDetailView.as_view(), 
        name='problem-data-detail',
    ),
    path('problem/test_data/<str:shortname>/<path:path>', 
        problem_data_file, name='problem_data_file'
    ),

    path('problem-data/', 
        ProblemTestDataProfileListView.as_view(), 
        name='problem-data-list',
    ),
    path('problem-data/<str:problem>/', 
        ProblemTestDataProfileDetailView.as_view(), 
        name='problem-data-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)