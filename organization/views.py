from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from pyparsing import Or
from rest_framework import views, permissions, generics

from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .models import Organization


class OrganizationListView(generics.ListCreateAPIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = [
        # permissions.DjangoModelPermissionsOrAnonReadOnly,
    ]

    def get_queryset(self):
        user = self.request.user

        # Only get "root" orgs
        queryset = Organization.objects.filter(depth=1)

        ## Exclude orgs that are unlisted if user doesn't have perm
        # if not user.has_perm('organization.see_all'):
        #     queryset.exclude(is_unlisted=True)

        return queryset


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Organization.objects.all()
    lookup_field = 'slug'
    serializer_class = OrganizationDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        # permissions.DjangoObjectPermissions,
    ]

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'].upper())
        return org
        # method = self.request.method
        # if method == 'GET':
        #     return org
        # else:
        #     raise PermissionDenied
