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

from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .models import Organization

import django_filters

__all__ = [
    'OrganizationListView', 'OrganizationDetailView',
    'MyOrganizationListView',
    'OrganizationSubOrgListView',
    'OrganizationMembersView',
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

    def get_queryset(self):
        user = self.request.user
        queryset = Organization.get_visible_organizations(user)
        return queryset

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


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Organization.objects.none()
    lookup_field = 'slug'
    serializer_class = OrganizationDetailSerializer
    permission_classes = []

    def get_serializer_context(self):
        return {'request': self.request}

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'])
        if self.request.method == 'GET':
            if not org.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not org.is_editable_by(self.request.user):
                raise PermissionDenied()
        return org

    def put(self, *args):
        return self.patch(*args)

    def patch(self, request, slug):
        data = request.data
        if data.get('new_parent_org') and data.get('become_root'):
            return Response({
                'errors': "You cannot set both 'Become Root?' and 'Change Parent Org'."
            }, status=status.HTTP_400_BAD_REQUEST)
        obj = self.get_object()

        res = super().patch(request, slug)

        try:
            if data.get('become_root'):
                old_root = obj.get_root()
                obj.become_root()
                # Organization.reupdate_tree_member_count(old_root)
            if data.get('new_parent_org'):
                parent = Organization.objects.get(slug=data['new_parent_org']['slug'])
                obj.become_child_of(parent)
                # Organization.reupdate_tree_member_count(parent.get_root())
        except Exception as e:
            return Response({
                'detail': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        obj.refresh_from_db()
        return Response( self.get_serializer_class()( obj ).data )

class OrganizationMembersView(generics.ListAPIView):
    """
        View for List/Create members of Org
    """
    lookup_field = 'slug'
    serializer_class = UserProfileBasicSerializer
    permission_classes = []
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^user__username', '@user__first_name', '@user__last_name']
    ordering_fields = ['rating', 'user__username']
    ordering = ['-rating', 'user__username']


    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'])
        if self.request.method == 'GET':
            if not org.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not org.is_editable_by(self.request.user):
                raise PermissionDenied()
        return org

    def get_queryset(self):
        org = self.get_object()
        return org.members.all()

    def post(self, request, slug):
        org = self.get_object()

        toBeMembers = request.data.get('users', [])
        profiles = Profile.objects.filter(user__username__in=toBeMembers)
        if profiles.count() != len(toBeMembers):
            not_found = []
            for uname in toBeMembers:
                if not Profile.objects.filter(user__username=uname).exists():
                    not_found.append(uname)
            return Response({
                'errors': f"Cannot find some of the users: {not_found}"
            }, status=status.HTTP_400_BAD_REQUEST)

        org.add_members(profiles.all())
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, slug):
        org = self.get_object()
        members = request.data.get('members', [])
        toBeRemoved = org.members.filter(user__username__in=members)
        org.remove_members(toBeRemoved.all())
        return Response({}, status=status.HTTP_204_NO_CONTENT)


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

    def get_serializer_context(self):
        return {'request': self.request}

    @cached_property
    def selected_org(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'].upper())
        if self.request.method == 'GET':
            if not org.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not org.is_editable_by(self.request.user):
                raise PermissionDenied()
        return org

    def get_queryset(self):
        return self.selected_org.get_children()

    def post(self, request, slug):
        user = request.user
        if not user.is_staff: #or not user.has_perm("organization.create_organization"):
            raise PermissionDenied()

        org = self.selected_org

        try:
            data = request.data.copy()
            for key in OrganizationSerializer.Meta.read_only_fields:
                data.pop(key, None)
            with transaction.atomic():
                child = org.add_child(**data)
                # child.admins.add(user.profile) # Don't need because user is already admin of child's ancestor
                child.save()
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError as ie:
            return Response({
                'detail': ie.args[0],
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'detail': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
