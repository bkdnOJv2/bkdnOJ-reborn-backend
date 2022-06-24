from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import OrganizationSerializer
from .models import UserProfile

from judger.restful.serializers import LanguageBasicSerializer

class UserProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'avatar']

class UserProfileSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False)
    language = LanguageBasicSerializer()

    organization = serializers.SerializerMethodField()
    def get_organization(self, profile):
        if profile.organization:
            from organization.serializers import OrganizationSerializer
            return OrganizationSerializer(profile.organization).data
        return None

    class Meta:
        model = UserProfile
        fields = [
            'owner',
            'first_name', 'last_name', 'full_name',
            'username', 'display_name', 'avatar',
            'organization',
            'about', 'timezone', 'language', 'performance_points', 'problem_count', 'points', 'rating', ]
