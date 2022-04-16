from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import UserProfile

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar', 'description']