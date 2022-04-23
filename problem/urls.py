from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProblemListView, ProblemDetailView

urlpatterns = [
    path('problem/', 
        ProblemListView.as_view(), 
        name='problem-list'
    ),
    path('problem/<str:shortname>/', 
        ProblemDetailView.as_view(), 
        name='problem-detail'
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
