from django.contrib.auth.models import Group
from rest_framework import serializers

from django.contrib.auth import get_user_model
User = get_user_model()

from auth.serializers import UserSerializer, UserDetailSerializer
from .models import Organization

__all__ = [
    'OrganizationBasicSerializer',
    'NestedOrganizationBasicSerializer', 'OrganizationSerializer'
]

class OrganizationBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'logo_url',
        ]


class NestedOrganizationBasicSerializer(OrganizationBasicSerializer):
    sub_orgs = serializers.SerializerMethodField()
    def get_sub_orgs(self, org):
        if org.is_leaf():
            return []
        return NestedOrganizationBasicSerializer(org.get_children(), many=True, read_only=True).data

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'logo_url', 'sub_orgs',
        ]


class OrganizationSerializer(OrganizationBasicSerializer):
    suborg_count = serializers.SerializerMethodField()
    def get_suborg_count(self, inst):
        if getattr(inst, 'get_descendant_count', False):
            return inst.get_descendant_count()
        return 0

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name',
            'is_open', 'is_unlisted',
            'logo_url',
            'member_count', #'performance_points'
            'suborg_count',
        ]
        read_only_fields = ('member_count', 'suborg_count')
        # extra_kwargs = {
        #     'logo_url': {'read_only': True},
        #     'member_count': {'read_only': True},
        #     'suborg_count': {'read_only': True},
        # }


class OrganizationDetailSerializer(OrganizationSerializer):
    admins = serializers.SerializerMethodField()
    def get_admins(self, instance):
        users = User.objects.filter(id__in=instance.admins.values_list('id', flat=True))
        return UserDetailSerializer(users, many=True).data

    parent_org = serializers.SerializerMethodField()
    def get_parent_org(self, instance):
        if instance.is_root():
            return None
        return OrganizationBasicSerializer(instance.get_parent(), read_only=True).data

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'is_open',
            'logo_url',

            'admins', 'about', 'creation_date', 'slots',

            'parent_org',

            'member_count', #'performance_points'
            'suborg_count',
        ]
        read_only_fields = ('member_count', 'suborg_count')
