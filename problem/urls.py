from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProblemListView, ProblemDetailView, \
    ProblemTestDataProfileListView, ProblemTestDataProfileDetailView

urlpatterns = [
    path('problem/', 
        ProblemListView.as_view(), 
        name='problem-list'
    ),
    path('problem/<str:shortname>/', 
        ProblemDetailView.as_view(), 
        name='problem-detail',
    ),
    path('problem-test-profile/', 
        ProblemTestDataProfileListView.as_view(), 
        name='problem-test-profile-list',
    ),
    path('problem-test-profile/<str:problem>/', 
        ProblemTestDataProfileDetailView.as_view(), 
        name='problem-test-profile-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)