from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import *
from .models import UserProfile

from judger.restful.serializers import LanguageBasicSerializer

from compete.ratings import rating_class, rating_level, rating_name
from organization.models import Organization


class UserProfileBaseSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    def get_display_name(self, profile):
        return profile.display_name

    username = serializers.SerializerMethodField()
    def get_username(self, profile):
        return profile.username

    first_name = serializers.SerializerMethodField()
    def get_first_name(self, profile):
        return profile.first_name

    last_name = serializers.SerializerMethodField()
    def get_last_name(self, profile):
        return profile.last_name

    email = serializers.SerializerMethodField()
    def get_email(self, profile):
        return profile.email

    class Meta:
        model = UserProfile
        fields = [
            'display_name',
            'username', 'avatar', 'first_name', 'last_name', 'email',
            'rating',
        ]


class UserProfileWithRoleSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    def get_username(self, profile):
        return profile.username

    first_name = serializers.SerializerMethodField()
    def get_first_name(self, profile):
        return profile.first_name

    last_name = serializers.SerializerMethodField()
    def get_last_name(self, profile):
        return profile.last_name

    email = serializers.SerializerMethodField()
    def get_email(self, profile):
        return profile.email

    is_active = serializers.SerializerMethodField()
    def get_is_active(self, profile):
        return profile.user.is_active

    is_staff = serializers.SerializerMethodField()
    def get_is_staff(self, profile):
        return profile.user.is_staff

    is_superuser = serializers.SerializerMethodField()
    def get_is_superuser(self, profile):
        return profile.user.is_superuser

    class Meta:
        model = UserProfile
        fields = [
            'username', 'avatar', 'first_name', 'last_name', 'email',
            'rating',
            'is_staff', 'is_superuser', 'is_active',
        ]


class UserProfileBasicSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    def get_display_name(self, profile):
        return profile.display_name

    organization = serializers.SerializerMethodField()
    def get_organization(self, prf):
        if prf.display_organization is None:
            return None
        return prf.display_organization.slug
        #return OrganizationBasicSerializer(prf.organization).data

    class Meta:
        model = UserProfile
        fields = [
            'username', 'display_name',
            'avatar', 'first_name', 'last_name',
            'rating', #'rank', 'rank_class',
            'organization',
        ]


class UserProfileSerializer(UserProfileBasicSerializer):
    user = UserSerializer(required=False, read_only=True)
    username = serializers.CharField(read_only=True)
    avatar = serializers.CharField(read_only=True)
    # language = LanguageBasicSerializer()

    organization = serializers.SerializerMethodField()
    def get_organization(self, prf):
        if prf.organization is None:
            return None
        return OrganizationBasicSerializer(prf.organization).data
    
    display_name = serializers.CharField(source="username_display_override")

    # member_of = serializers.SerializerMethodField()
    # def get_member_of(self, prf):
    #     data_list = []
    #     for org in prf.organizations.all():
    #         data = OrganizationBasicSerializer(org).data
    #         data['sub_orgs'] = []

    #         trv = org
    #         while True:
    #             if trv.is_root(): break
    #             trv = trv.get_parent()
    #             parent_data = OrganizationBasicSerializer(trv).data
    #             parent_data['sub_orgs'] = [data]
    #             data = parent_data
    #         data_list.append(data)
    #     return data_list

    # admin_of = serializers.SerializerMethodField()
    # def get_admin_of(self, prf):
    #     return NestedOrganizationBasicSerializer(prf.admin_of, many=True).data


    class Meta:
        model = UserProfile
        fields = [
            'user',
            'first_name', 'last_name', 'full_name',
            'username', 'display_name', 'avatar',
            'organization',
            #'member_of', 'admin_of',
            'about', 
            #'timezone', 'language', 
            'performance_points', 'problem_count', 'points',
            'rating', #'rank', 'rank_class',
        ]
        read_only_fields = ('username',)
