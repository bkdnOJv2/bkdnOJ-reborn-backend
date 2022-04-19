from django.shortcuts import render
from rest_framework import views, permissions, generics

from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .models import Organization

# Create your views here.
class OrganizationListView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'shortname'
