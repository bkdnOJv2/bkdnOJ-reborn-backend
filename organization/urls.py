from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

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
        OrganizationSubOrgListView.as_view(),
        # OrganizationListView.as_view(),
        name='organization-list',
    ),
    path('orgs/my/',
        MyOrganizationListView.as_view(),
        name='my-organization-list',
    ),

    path('org/<str:slug>/',
        OrganizationDetailView.as_view(),
        name='organization-detail',
    ),
    path('org/<str:slug>/members/',
        OrganizationMembersView.as_view(),
        name='organization-members',
    ),
    path('org/<str:slug>/orgs/',
        OrganizationSubOrgListView.as_view(),
        name='organization-suborg-list',
    ),

    # Join/Leave
    path('org/<str:slug>/membership/',
        OrganizationMembershipView.as_view(),
        name='organization-membership-view',
    ),

]

urlpatterns = format_suffix_patterns(urlpatterns)
