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


from organization.serializers import NestedOrganizationBasicSerializer, OrganizationBasicSerializer

class MyOrganizationListView(views.APIView):
    """
        Return a List of all organizations
    """
    queryset = Organization.objects.none()
    serializer_class = OrganizationSerializer
    permission_classes = [
        permissions.IsAdminUser
    ]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return([])
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
            'admin_of': NestedOrganizationBasicSerializer(profile.admin_of, many=True).data
        })


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

    def get_serializer_context(self):
        return {'request': self.request}

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'].upper())
        return org
        # method = self.request.method
        # if method == 'GET':
        #     return org
        # else:
        #     raise PermissionDenied

from django.http import Http404
from userprofile.models import UserProfile as Profile
from userprofile.serializers import UserProfileBasicSerializer

class OrganizationMembersView(generics.ListCreateAPIView):
    """
        View for List/Create members of Org
    """
    lookup_field = 'slug'
    serializer_class = UserProfileBasicSerializer
    permission_classes = []

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'])
        if not org.is_accessible_by(self.request.user):
            raise Http404()
        return org

    def get_queryset(self):
        org = self.get_object()
        return org.members.all()

    def post(self, request, slug):
        org = self.get_object()
        pass
        #new_members = request.data.get('new', [])
        #pfs = Profile.objects.filter(user__username__in=new_members)
        #org.members.add(pfs)

class OrganizationMemberDeleteView(generics.DestroyAPIView):
    """
        View for List/Create members of Org
    """
    lookup_field = 'slug'
    serializer_class = UserProfileBasicSerializer
    permission_classes = []

    def get_object(self):
        org = get_object_or_404(Organization, slug=self.kwargs['slug'])
        if not org.is_accessible_by(self.request.user):
            raise Http404()
        return org

    def delete(self, request, slug):
        pass


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
        return org

    def get_queryset(self):
        return self.selected_org.get_children()

    def post(self, request, slug):
        seri = OrganizationSerializer(data=request.data, context={'request': request})
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
