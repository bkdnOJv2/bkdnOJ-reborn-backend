from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import OrganizationSerializer
from .models import UserProfile

from judger.restful.serializers import LanguageBasicSerializer

from compete.ratings import rating_class, rating_level, rating_name

class UserProfileBasicSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    def get_rank(self, prf):
        if prf.rating is None:
            return None
        return rating_name(prf.rating)

    rank_class = serializers.SerializerMethodField()
    def get_rank_class(self, prf):
        if prf.rating is None:
            return 'rate-none'
        return rating_class(prf.rating)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'avatar',
            'first_name', 'last_name',
            'rating', 'rank', 'rank_class']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    language = LanguageBasicSerializer()

    organization = serializers.SerializerMethodField()
    def get_organization(self, profile):
        if profile.organization:
            from organization.serializers import OrganizationSerializer
            return OrganizationSerializer(profile.organization).data
        return None

    rank = serializers.SerializerMethodField()
    def get_rank(self, prf):
        if prf.rating is None:
            return None
        return rating_name(prf.rating)

    rank_class = serializers.SerializerMethodField()
    def get_rank_class(self, prf):
        if prf.rating is None:
            return 'rate-none'
        return rating_class(prf.rating)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'first_name', 'last_name', 'full_name',
            'username', 'display_name', 'avatar',
            'organization',
            'about', 'timezone', 'language', 'performance_points', 'problem_count', 'points',
            'rating', 'rank', 'rank_class',
        ]
