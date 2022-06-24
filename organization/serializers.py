from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['slug', 'name', 'is_open', 'logo_override_image', 'member_count', 'performance_points']


class OrganizationDetailSerializer(serializers.ModelSerializer):
    admins = serializers.SerializerMethodField()
    def get_admins(self, instance):
        from userprofile.serializers import UserProfileBasicSerializer
        return UserProfileBasicSerializer(instance.admins, many=True).data

    class Meta:
        model = Organization
        fields = '__all__'
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
