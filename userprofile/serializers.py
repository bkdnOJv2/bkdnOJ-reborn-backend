from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from organization.models import OrgMembership
from organization.serializers import OrganizationSerializer
from .models import UserProfile

class MemberOfOrgSerializer(serializers.Serializer):
    org = OrganizationSerializer()
    role_label = serializers.CharField()
    ranking = serializers.IntegerField()

    class Meta:
        model = OrgMembership
        fields = ('org', 'role_label', 'ranking')

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserMoreDetailSerializer(read_only=True)
    member_of_orgs = MemberOfOrgSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar', 'description', 'global_ranking',
            'owner', 'member_of_orgs']
