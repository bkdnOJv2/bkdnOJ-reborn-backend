from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']#, 'groups']

class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class UserMoreDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups', 'is_staff', 'is_superuser']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name', 'user_set']