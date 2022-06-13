from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from userprofile.serializers import UserProfileBasicSerializer as ProfileSerializer
from userprofile.models import UserProfile as Profile
from problem.models import Problem
from problem.serializers import ProblemInContestSerializer, ProblemBasicSerializer
from submission.serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Contest, ContestProblem, ContestSubmission, ContestParticipation

__all__ = [
    'ContestSerializer', 
    'ContestBriefSerializer',
    'ContestDetailSerializer',
    'ContestProblemSerializer', 
    'ContestProblemBriefSerializer',
    'ContestSubmissionSerializer',
    'ContestStandingSerializer',
    'ContestParticipationSerializer', 
    'ContestParticipationDetailSerializer',
]

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
    authors = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    collaborators = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    reviewers = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )

    class Meta:
        model = Contest
        fields = [
            'id',
            'key', 'name', 'start_time', 'end_time', 'time_limit', 
            'authors', 'collaborators', 'reviewers',

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


class ContestProblemBriefSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = ContestProblem
        fields = [
            'id',
            'shortname', 'title', 'solved_count', 'attempted_count',
            'contest', 'points', 'partial', 'is_pretested',
            'order', 'output_prefix_override', 'max_submissions',
            'label',
        ]
        read_only_fields = ['id',
            'solved_count', 'attempted_count',
            'label',
        ]


class ContestProblemSerializer(ContestProblemBriefSerializer):
    problem_data = ProblemInContestSerializer(read_only=True, source='problem')
    class Meta:
        model = ContestProblem
        fields = [
            'problem_data',
            'id',
            'shortname', 'title', 'solved_count', 'attempted_count',
            'contest', 'points', 'partial', 'is_pretested',
            'order', 'output_prefix_override', 'max_submissions',
            'label',
        ]


class ContestDetailSerializer(ContestBriefSerializer):
    authors = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    collaborators = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    reviewers = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    banned_users = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )

    def to_internal_value(self, data):
        profiles = ['authors', 'collaborators', 'reviewers', 'banned_users']
        qs = Profile.objects.select_related('owner')
        profiles_val = {}

        for prf in profiles:
            usernames = data.pop(prf, [])
            profile_ins = []
            for uname in usernames:
                p = qs.filter(owner__username=uname)
                if p == None:
                    raise ValidationError(f"User '{uname}' does not exist.")
                profile_ins.append(p.first().id)
            profiles_val[prf] = profile_ins
            
        val_data = super().to_internal_value(data)
        for k, v in profiles_val.items():
            val_data[k] = v
        return val_data

    problems = ContestProblemBriefSerializer(many=True, read_only=True,
        source='contest_problems'
    )

    class Meta:
        model = Contest
        fields = '__all__'
        optional_fields = ['is_registered', 'spectate_allow']
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


