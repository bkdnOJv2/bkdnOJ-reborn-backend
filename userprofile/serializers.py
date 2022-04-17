from django.contrib.auth.models import Group
from rest_framework import serializers

from usergroup.serializers import UserMoreDetailSerializer

from .models import UserProfile

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserMoreDetailSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar', 'description', 'owner']