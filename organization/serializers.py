from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from .models import Organization


class OrganizationBasicSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    def get_logo_url(self, org):
        return org.logo_override_image

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'logo_url',
        ]

class OrganizationSerializer(OrganizationBasicSerializer):
    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'is_open',
            'logo_url',
            'member_count', 'performance_points'
        ]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    def get_logo_url(self, org):
        return org.logo_override_image

    admins = serializers.SerializerMethodField()
    def get_admins(self, instance):
        from userprofile.serializers import UserProfileBasicSerializer
        return UserProfileBasicSerializer(instance.admins, many=True).data

    class Meta:
        model = Organization
        fields = '__all__'
        # exclude = ['logo_override_image', ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
