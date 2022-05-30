from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from .models import Organization

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

class OrganizationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['slug', 'shortname']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
