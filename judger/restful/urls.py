from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import JudgeListView, JudgeDetailView, \
    LanguageListView, LanguageDetailView, LanguageDetailKeyView

urlpatterns = [
    path('judge/', 
        JudgeListView().as_view(), 
        name='judge-list'
    ),
    path('judge/<int:pk>/', 
        JudgeDetailView().as_view(), 
        name='judge-detail',
    ),

    path('language/',
        LanguageListView().as_view(),
        name='language-list',
    ),
    path('language/<int:pk>/',
        LanguageDetailView().as_view(),
        name='language-detail',
    ),
    path('language/key/<slug:key>/',
        LanguageDetailKeyView().as_view(),
        name='language-detail-key',
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)