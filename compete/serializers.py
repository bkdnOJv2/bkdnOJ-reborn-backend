from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from userprofile.serializers import UserProfileBasicSerializer as ProfileSerializer
from userprofile.models import UserProfile as Profile
from problem.models import Problem
from problem.serializers import ProblemBasicSerializer
from submission.serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Contest, ContestProblem, ContestSubmission, ContestParticipation

class ContestBriefSerializer(serializers.ModelSerializer):
    spectate_allow = serializers.SerializerMethodField()
    def get_spectate_allow(self, obj):
        user = self.context['request'].user
        if obj.is_testable_by(user):
            return True
        return False

    is_registered = serializers.SerializerMethodField()
    def get_is_registered(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        if ContestParticipation.objects.filter(
                virtual=ContestParticipation.LIVE,
                contest=obj, user=user.profile
        ).exists():
            return True
        return False

    class Meta:
        model = Contest
        fields = [
            'spectate_allow', 'is_registered',
            'key', 'name', 'start_time', 'end_time', 'time_limit', 'user_count',
        ]

class ContestSerializer(serializers.ModelSerializer):
    authors = ProfileSerializer(many=True)

    class Meta:
        model = Contest
        fields = [
            'id',
            'authors', 'key', 'name', 'start_time', 'end_time', 'time_limit', 

            'is_visible', 
            'is_private', 'private_contestants',

            'is_organization_private', 'organizations',


            'tags', 'user_count', 'format_name',
            'is_rated', 
        ]

        lookup_field = 'key'
        extra_kwargs = {
            'url': {'lookup_field': 'key'}
        }


class ContestProblemSerializer(serializers.ModelSerializer):
    # problem = serializers.ReadOnlyField(source='problem.shortname')
    # contest = serializers.ReadOnlyField(source='contest.key')
    # problem = ProblemBriefSerializer()
    shortname = serializers.SlugRelatedField(
        source='problem',
        slug_field='shortname',
        queryset=Problem.objects.all(),
    )
    title = serializers.ReadOnlyField(source='problem.title')

    contest = serializers.SlugRelatedField(
        slug_field='key',
        queryset=Contest.objects.all(),
    )
    # contest = serializers.ReadOnlyField(source='contest.key')

    class Meta:
        model = ContestProblem
        fields = [
            #'problem',
            'id',
            'shortname', 'title', 'solved_count', 'attempted_count',
            'contest', 'points', 'partial', 'is_pretested',
            'order', 'output_prefix_override', 'max_submissions',
            'label',
        ]


class ContestDetailSerializer(serializers.ModelSerializer):
    authors = ProfileSerializer(many=True, required=False)
    collaborators = ProfileSerializer(many=True, required=False)
    reviewers = ProfileSerializer(many=True, required=False)

    banned_users = ProfileSerializer(many=True, required=False)

    problems = ContestProblemSerializer(many=True,
        source='contest_problems'
    )

    class Meta:
        model = Contest
        fields = '__all__'
        lookup_field = 'key'
        extra_kwargs = {
            'url': {'lookup_field': 'key'}
        }


class ContestSubmissionSerializer(serializers.ModelSerializer):
    #submission = SubmissionSerializer()
    #shortname = serializers.SlugRelatedField(
    #    source='problem',
    #    slug_field='shortname',
    #    queryset=Problem.objects.all(),
    #)
    id = serializers.ReadOnlyField(source='submission.id')
    date = serializers.ReadOnlyField(source='submission.date')
    time = serializers.ReadOnlyField(source='submission.time')
    memory = serializers.ReadOnlyField(source='submission.memory')
    status = serializers.ReadOnlyField(source='submission.status')
    result = serializers.ReadOnlyField(source='submission.result')
    user = serializers.ReadOnlyField(source='submission.user.username')
    language = serializers.ReadOnlyField(source='submission.language.name')

    # # Problems
    problem = ProblemBasicSerializer(read_only=True, source='problem.problem')

    class Meta:
        model = ContestSubmission
        #fields = '__all__'
        exclude = [
            'participation', 'submission',
        ]

import json

class ContestStandingSerializer(serializers.ModelSerializer):
    #user = ProfileSerializer(required=False)
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        ser_context = {'request': self.context.get('request')}
        user_ser = ProfileSerializer(obj.user, context=ser_context)
        return user_ser.data

    format_data = serializers.SerializerMethodField()

    def get_format_data(self, obj):
        return json.dumps(obj.format_data)

    class Meta:
        model = ContestParticipation
        fields = ['user', 'score', 'cumtime', 'is_disqualified',
            'tiebreaker', 'virtual', 'format_data',
        ]

class ContestParticipationSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=Profile.objects.all(),
    )

    class Meta:
        model = ContestParticipation
        fields = ['id', 'real_start', 'virtual', 'is_disqualified',
            'user',]


class ContestParticipationDetailSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=Profile.objects.all(),
    )

    class Meta:
        model = ContestParticipation
        fields = '__all__'


