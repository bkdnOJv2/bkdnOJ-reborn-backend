from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import OrganizationSerializer
from .models import UserProfile

class UserProfileBasicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'avatar']

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserSerializer(required=False)

    class Meta:
        model = UserProfile
        fields = ['owner', 'first_name', 'last_name', 'username', 'avatar',
            'about', 'timezone', 'language', 'points', 'rating']
