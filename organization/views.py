from django.shortcuts import render
from rest_framework import views, permissions, generics

from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .models import Organization

class OrganizationListView(generics.ListCreateAPIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [
        permissions.DjangoModelPermissionsOrAnonReadOnly,
    ]


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Organization.objects.all()
    lookup_field = 'slug'
    serializer_class = OrganizationDetailSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoObjectPermissions,
    ]
