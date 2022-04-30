from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SubmissionListView, SubmissionDetailView

urlpatterns = [
    path('submission/', 
        SubmissionListView.as_view(), 
        name='submission-list'
    ),

    path('submission/<int:pk>/', 
        SubmissionDetailView.as_view(), 
        name='submission-detail'
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)