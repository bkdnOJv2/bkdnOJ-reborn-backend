from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import OrganizationListView, OrganizationDetailView

urlpatterns = [
    # path('organizations/',
    #     OrganizationListView.as_view(),
    #     name='organization-list',
    # ),
    # path('organization/<str:slug>/',
    #     OrganizationDetailView.as_view(),
    #     name='organization-detail',
    # ),

    path('orgs/',
        OrganizationListView.as_view(),
        name='organization-list',
    ),

    path('org/<str:slug>/',
        OrganizationDetailView.as_view(),
        name='organization-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
