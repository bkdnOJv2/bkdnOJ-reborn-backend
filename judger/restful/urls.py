from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import JudgeListView, JudgeDetailView

urlpatterns = [
    path('judge/', 
        JudgeListView().as_view(), 
        name='judge-list'
    ),
    path('judge/<int:pk>/', 
        JudgeDetailView().as_view(), 
        name='judge-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)