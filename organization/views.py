from django.utils.functional import cached_property
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from pyparsing import Or
from rest_framework import views, permissions, generics, status, filters
from rest_framework.response import Response

from organization.exceptions import OrganizationTooDeepError

from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .models import Organization

import django_filters

__all__ = [
    'OrganizationListView', 'OrganizationDetailView',
    'OrganizationSubOrgListView',
]

class OrganizationListView(generics.ListCreateAPIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = [
        # permissions.DjangoModelPermissionsOrAnonReadOnly,
    ]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^slug', '@short_name', '@name']
    filterset_fields = ['is_open', 'is_unlisted']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']

    def get_queryset(self):
        user = self.request.user

        # Only get "root" orgs
        queryset = Organization.objects.filter(depth=1)

        ## Exclude orgs that are unlisted if user doesn't have perm
        # if not user.has_perm('organization.see_all'):
        #     queryset.exclude(is_unlisted=True)

        return queryset

    def post(self, request):
        seri = OrganizationSerializer(data=request.data)
        if seri.is_valid():
            data = seri.data.copy()
            for key in OrganizationSerializer.Meta.read_only_fields:
                data.pop(key, None)
            new_root = Organization.add_root(**data)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(seri.errors, status=status.HTTP_400_BAD_REQUEST)


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


class OrganizationSubOrgListView(generics.ListCreateAPIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = []
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^slug', '@short_name', '@name']
    filterset_fields = ['is_open', 'is_unlisted']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']

    @cached_property
    def selected_org(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'].upper())
        return org

    def get_queryset(self):
        return self.selected_org.get_children()

    def post(self, request, slug):
        seri = OrganizationSerializer(data=request.data)
        if seri.is_valid():
            data = seri.data.copy()
            for key in OrganizationSerializer.Meta.read_only_fields:
                data.pop(key, None)
            try:
                child = self.selected_org.add_child(**data)
                return Response(data, status=status.HTTP_201_CREATED)
            except OrganizationTooDeepError as otde:
                return Response({
                    'details': str(otde),
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(seri.errors, status=status.HTTP_400_BAD_REQUEST)
