from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.utils.functional import cached_property
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from pyparsing import Or
from rest_framework import views, permissions, generics, status, filters
from rest_framework.response import Response

from userprofile.models import UserProfile as Profile
from userprofile.serializers import UserProfileBasicSerializer
from organization.exceptions import OrganizationTooDeepError

from organization.serializers import OrganizationSerializer, OrganizationDetailSerializer
from organization.models import Organization

import django_filters

__all__ = [
    'OrganizationListView',
    'MyOrganizationListView',
]

class OrganizationListView(generics.ListCreateAPIView):
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

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Organization.get_public_root_organizations()
        return user.profile.organizations.all()

    def post(self, request):
        user = request.user
        # if not user.is_authenticated or not user.has_perm("organization.create_organization"):
        if not user.is_staff:
            raise PermissionDenied()

        try:
            data = request.data.copy()
            for key in OrganizationSerializer.Meta.read_only_fields:
                data.pop(key, None)
            with transaction.atomic():
                node = Organization.add_root(**data)
                node.admins.add(user.profile)
                node.save()
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError as ie:
            return Response({
                'detail': ie.args[0],
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'detail': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


from organization.serializers import NestedOrganizationBasicSerializer, OrganizationBasicSerializer

class MyOrganizationListView(views.APIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = []

    def get_serializer_context(self):
        return {'request': self.request}

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return(Organization.get_public_root_organizations().all())
        profile = user.profile

        member_of = []
        for org in profile.organizations.all():
            data = OrganizationBasicSerializer(org).data
            data['sub_orgs'] = []

            trv = org
            while True:
                if trv.is_root(): break
                trv = trv.get_parent()
                parent_data = OrganizationBasicSerializer(trv).data
                parent_data['sub_orgs'] = [data]
                data = parent_data
            member_of.append(data)

        return Response({
            'member_of': member_of,
            'admin_of': NestedOrganizationBasicSerializer(
                # Organization.get_visible_root_organizations(user),
                profile.admin_of.all(),
                many=True,
            ).data
        })

