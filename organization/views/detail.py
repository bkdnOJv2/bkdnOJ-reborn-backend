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
    'OrganizationDetailView',
    'OrganizationSubOrgListView',
    'OrganizationMembersView',
]

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
        user = request.user
        data = request.data
        if data.get('new_parent_org') and data.get('become_root'):
            return Response({
                'errors': "You cannot set both 'Become Root?' and 'Change Parent Org'."
            }, status=status.HTTP_400_BAD_REQUEST)

        if data.get('become_root'):
            if not user.has_perm('organization.create_root_organization') or not user.has_perm('organization.move_organization_anywhere'):
                raise PermissionDenied()

        parent = None
        try:
            if data.get('new_parent_org'):
                parent = get_object_or_404( Organization, slug=data['new_parent_org']['slug'] )
                # If the user doesn't have the permission to move org anywhere, and the destination is also not managed by the user
                # Deny the request
                if not user.has_perm('organization.move_organization_anywhere') and not parent.is_editable_by(user):
                    raise PermissionDenied()
        except KeyError:
            return Response({
                'errors': "Bad request."
            }, status=status.HTTP_400_BAD_REQUEST)

        obj = self.get_object()
        res = super().patch(request, slug)

        try:
            if data.get('become_root'):
                old_root = obj.get_root()
                obj.become_root()
                # Organization.reupdate_tree_member_count(old_root)
            if data.get('new_parent_org'):
                obj.become_child_of(parent)
                # Organization.reupdate_tree_member_count(parent.get_root())
        except Exception as e:
            return Response({
                'detail': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.refresh_from_db()
        return Response( self.get_serializer_class()( obj, context={'request': request} ).data )

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

    def get_queryset(self):
        org = self.get_object()
        return org.members.all()

    def post(self, request, slug):
        user = request.user
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
        Return a list of child organizations of the current selected org
        Query Params:
            - slug: Org's slug to be selected. Leave none to select root orgs.
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
        slug = self.kwargs.get('slug', None)
        if slug is None:
            return None

        org = get_object_or_404(Organization, slug=slug.upper())

        if self.request.method == 'GET':
            if not org.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not org.is_editable_by(self.request.user):
                raise PermissionDenied()
        return org

    def get_queryset(self):
        user = self.request.user
        if self.selected_org is None:
            queryset = Organization.get_root_nodes()
        else:
            queryset = self.selected_org.get_visible_children(user)
        return queryset

    def post(self, request, slug=None):
        user = request.user
        org = self.selected_org

        if not user.is_staff: #or not user.has_perm("organization.create_organization"):
            raise PermissionDenied()

        if org is None:
            if not user.has_perm('organization.create_root_organization'):
                raise PermissionDenied()
        else: # Is checked by line 166
            pass

        try:
            data = request.data.copy()
            for key in OrganizationSerializer.Meta.read_only_fields:
                data.pop(key, None)

            if org is None:
                with transaction.atomic():
                    node = Organization.add_root(**data)
                    node.admins.add(user.profile)
                    node.save()
            else:
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
