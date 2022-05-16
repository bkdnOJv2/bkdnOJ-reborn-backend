from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import SubmissionListView, SubmissionDetailView, \
    SubmissionResultView, SubmissionResultTestCaseView

urlpatterns = [
    path('submission/', 
        SubmissionListView.as_view(), 
        name='submission-list'
    ),

    path('submission/<int:pk>/', 
        SubmissionDetailView.as_view(), 
        name='submission-detail'
    ),

    path('submission/<int:pk>/testcase/', 
        SubmissionResultView.as_view(), 
        name='submission-result'
    ),

    path('submission/<int:pk>/testcase/<int:case_num>/', 
        SubmissionResultTestCaseView.as_view(), 
        name='submission-result-testcase'
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)