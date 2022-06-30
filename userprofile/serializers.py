from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import *
from .models import UserProfile

from judger.restful.serializers import LanguageBasicSerializer

from compete.ratings import rating_class, rating_level, rating_name

class UserProfileBasicSerializer(serializers.ModelSerializer):

    organization = serializers.SerializerMethodField()
    def get_organization(self, prf):
        if prf.display_organization is None:
            return None
        return prf.display_organization.slug
        #return OrganizationBasicSerializer(prf.organization).data

    class Meta:
        model = UserProfile
        fields = [
            'username', 'avatar', 'first_name', 'last_name',
            'rating', #'rank', 'rank_class',
            'organization',
        ]


class UserProfileSerializer(UserProfileBasicSerializer):
    user = UserSerializer(required=False)
    language = LanguageBasicSerializer()

    organization = serializers.SerializerMethodField()
    def get_organization(self, prf):
        if prf.organization is None:
            return None
        return OrganizationBasicSerializer(prf.organization).data

    member_of = serializers.SerializerMethodField()
    def get_member_of(self, prf):
        data_list = []
        for org in prf.organizations.all():
            data = OrganizationBasicSerializer(org).data
            data['sub_orgs'] = []

            trv = org
            while True:
                if trv.is_root(): break
                trv = trv.get_parent()
                parent_data = OrganizationBasicSerializer(trv).data
                parent_data['sub_orgs'] = [data]
                data = parent_data
            data_list.append(data)
        return data_list

    admin_of = serializers.SerializerMethodField()
    def get_admin_of(self, prf):
        return NestedOrganizationBasicSerializer(prf.admin_of, many=True).data

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'first_name', 'last_name', 'full_name',
            'username', 'display_name', 'avatar',
            'organization', 'member_of', 'admin_of',
            'about', 'timezone', 'language', 'performance_points', 'problem_count', 'points',
            'rating', #'rank', 'rank_class',
        ]
