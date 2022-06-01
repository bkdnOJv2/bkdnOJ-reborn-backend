from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserMoreDetailSerializer

from auth.serializers import UserSerializer
from organization.serializers import OrganizationSerializer
from .models import UserProfile

class UserProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'avatar']

class UserProfileSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False)
    current_contest = serializers.SerializerMethodField('get_current_contest')

    def get_current_contest(self, instance):
        if (instance.current_contest == None):
            return None

        contest = instance.current_contest.contest
        return { 
            'contest' : {
                'key': contest.key, 
                'name': contest.name, 
                'start_time': contest.start_time, 
                'end_time': contest.end_time, 
                'time_limit': contest.time_limit, 
                'is_rated': contest.is_rated,
            },
            'virtual': instance.current_contest.virtual,
        }

    class Meta:
        model = UserProfile
        fields = ['owner', 'first_name', 'last_name', 'username', 'avatar',
            'about', 'timezone', 'language', 'points', 'rating', 'current_contest']
