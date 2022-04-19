from django.contrib.auth.models import Group
from rest_framework import serializers

from usergroup.serializers import UserSerializer
from .models import OrgMembership, Organization

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('url', 'name', 'description')
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class OrgMembershipSerializer(serializers.Serializer):
    user = UserSerializer()
    role_label = serializers.CharField()
    ranking = serializers.IntegerField()

    class Meta:
        model = OrgMembership
        fields = ('user', 'role_label', 'ranking')

class OrganizationDetailSerializer(serializers.HyperlinkedModelSerializer):
    memberships = OrgMembershipSerializer(many=True)

    class Meta:
        model = Organization
        fields = ('url', 'name', 'description', 'memberships')
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }