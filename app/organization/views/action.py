# pylint: skip-file
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
    'OrganizationMembershipView',
]

class OrganizationMembershipView(views.APIView):
    """
        View to edit membership with this organization.
        @Params:
            - slug: Organization ID code
        @Method:
            - POST: Join organization
            - DELETE: Leave organization
    """
    queryset = Organization.objects.none()
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'])
        if not org.is_accessible_by(self.request.user):
            raise PermissionDenied()
        return org

    def post(self, request, slug):
        user = request.user
        org = self.get_object()

        if org.members.filter(id=user.profile.id).exists():
            return Response({
                'error': "You are already a member of this organization."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not org.is_open:
            if not user.has_perm('organization.join_private_organization'):
                return Response({
                    'error': "This organization is private."
                }, status=status.HTTP_400_BAD_REQUEST)

        if org.is_protected:
            if not user.has_perm('organization.join_without_access_code'):
                code = request.data.get('access_code', None)
                if code is None:
                    return Response({
                        'error': "An Access code is needed to join this organization."
                    }, status=status.HTTP_400_BAD_REQUEST)
                if code != org.access_code:
                    return Response({
                        'error': "Access code is not correct."
                    }, status=status.HTTP_400_BAD_REQUEST)

        if not org.is_root():
            org_parent = org.get_parent()
            if not org_parent.members.filter(id=user.profile.id).exists():
                return Response({
                    'error': f"You must be a member of organization '{org_parent.slug}' before joining."
                }, status=status.HTTP_400_BAD_REQUEST)

        org.add_members([request.user.profile])
        return Response({
            'detail': "OK Joined."
        }, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, slug):
        user = request.user
        org = self.get_object()

        if not org.members.filter(id=user.profile.id).exists():
            return Response({
                'error': "You are not a member of this organization."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not org.is_leaf() and org.get_children().filter(id__in=user.profile.organizations.values_list('id', flat=True)).exists():
            return Response({
                'error': "You must leave all child organizations before leaving this organization."
            }, status=status.HTTP_400_BAD_REQUEST)

        org.remove_members([request.user.profile])
        return Response({
            'detail': "OK Leave organization."
        }, status=status.HTTP_204_NO_CONTENT)
