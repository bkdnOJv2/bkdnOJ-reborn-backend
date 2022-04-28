from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SubmissionListView

urlpatterns = [
    path('submission/', 
        SubmissionListView.as_view(), 
        name='submission-list'
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)