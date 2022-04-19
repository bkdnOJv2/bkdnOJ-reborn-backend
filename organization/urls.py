from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import OrganizationListView, OrganizationDetailView

urlpatterns = [
    path('org/', OrganizationListView.as_view(), 
        name='organization-list'),
    path('org/<str:shortname>/', 
        OrganizationDetailView.as_view(), name='organization-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
