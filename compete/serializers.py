from functools import lru_cache as cache

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
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
    'ContestStandingFrozenSerializer', 'ContestStandingSerializer',
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

    register_allow = serializers.SerializerMethodField()
    def get_register_allow(self, obj):
        user = self.context['request'].user
        return obj.is_registerable_by(user)

    is_registered = serializers.SerializerMethodField()
    def get_is_registered(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        if ContestParticipation.objects.filter(
            virtual__in=[ContestParticipation.LIVE, ContestParticipation.SPECTATE],
            contest=obj, user=user.profile
        ).exists():
            return True
        return False

    class Meta:
        model = Contest
        fields = [
            'spectate_allow', 'register_allow', 'is_registered',
            'key', 'name',
            'start_time', 'end_time', 'time_limit',
            'enable_frozen', 'frozen_time', 'is_frozen',
            'user_count',
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

            'frozen_time',
            'is_frozen',


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

class ContestProblemBasicSerializer(serializers.ModelSerializer):
    shortname = serializers.SlugRelatedField(
        source='problem',
        slug_field='shortname',
        queryset=Problem.objects.all(),
    )
    title = serializers.ReadOnlyField(source='problem.title')

    time_limit = serializers.SerializerMethodField()
    def get_time_limit(self, cp):
        return cp.problem.time_limit

    memory_limit = serializers.SerializerMethodField()
    def get_memory_limit(self, cp):
        return cp.problem.memory_limit

    class Meta:
        model = ContestProblem
        fields = [
            'id',
            'shortname', 'title', 'time_limit', 'memory_limit',
            'points', 'order', 'label',
        ]

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

    time_limit = serializers.SerializerMethodField()
    def get_time_limit(self, cp):
        return cp.problem.time_limit

    memory_limit = serializers.SerializerMethodField()
    def get_memory_limit(self, cp):
        return cp.problem.memory_limit

    class Meta:
        model = ContestProblem
        fields = [
            'id',
            'shortname', 'title', 'solved_count', 'attempted_count',
            'time_limit', 'memory_limit',
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
    private_contestants = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )
    banned_users = serializers.SlugRelatedField(
        queryset=Profile.objects.all(), many=True, slug_field="username", required=False,
    )

    def to_internal_value(self, data):
        profiles = ['authors', 'collaborators', 'reviewers',
            'private_contestants', 'banned_users']
        qs = Profile.objects.select_related('owner')
        profiles_val = {}

        for prf in profiles:
            usernames = data.pop(prf, [])
            profile_ins = []
            for uname in usernames:
                p = qs.filter(owner__username=uname)
                if not p.exists():
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
        optional_fields = ['is_registered', 'spectate_allow', 'register_allow']
        lookup_field = 'key'
        extra_kwargs = {
            'url': {'lookup_field': 'key'}
        }

from django.utils.functional import cached_property

class ContestSubmissionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='submission.id')
    date = serializers.ReadOnlyField(source='submission.date')

    is_frozen = serializers.SerializerMethodField()
    @cache
    def get_is_frozen(self, obj):
        user = self.context['request'].user
        return obj.submission.is_frozen_to(user)

    def _get_result(self, obj, key, default=None):
        if self.get_is_frozen(obj):
            return default
        return getattr(obj.submission, key, default)

    time = serializers.SerializerMethodField()
    def get_time(self, cs):
        return self._get_result(cs, 'time')

    memory = serializers.SerializerMethodField()
    def get_memory(self, cs):
        return self._get_result(cs, 'memory')

    status = serializers.SerializerMethodField()
    def get_status(self, cs):
        return self._get_result(cs, 'status', 'FR')

    result = serializers.SerializerMethodField()
    def get_result(self, cs):
        return self._get_result(cs, 'result', 'FR')

    points = serializers.SerializerMethodField()
    def get_points(self, cs):
        if self.get_is_frozen(cs):
            return None
        return cs.points

    user = serializers.ReadOnlyField(source='submission.user.username')
    language = serializers.ReadOnlyField(source='submission.language.name')

    # # Problems
    problem = ContestProblemBasicSerializer(read_only=True)

    class Meta:
        model = ContestSubmission
        fields = ['id', 'date', 'is_frozen',
            'time', 'memory', 'status', 'result', 'user', 'language', 'problem',
            'points'
        ]

import json

class ContestStandingFrozenSerializer(serializers.ModelSerializer):
    #user = ProfileSerializer(required=False)
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        ser_context = {'request': self.context.get('request')}
        user_ser = ProfileSerializer(obj.user, context=ser_context)
        return user_ser.data

    format_data = serializers.SerializerMethodField()
    def get_format_data(self, obj):
        data = obj.frozen_format_data
        data = json.dumps(data)
        return data

    class Meta:
        model = ContestParticipation
        fields = [
            'user',
            'frozen_score', 'frozen_cumtime', 'frozen_tiebreaker',
            'virtual', 'is_disqualified', 'is_frozen',
            'format_data',
        ]

class ContestStandingSerializer(ContestStandingFrozenSerializer):
    format_data = serializers.SerializerMethodField()
    def get_format_data(self, obj):
        data = obj.format_data
        data = json.dumps(data)
        return data

    class Meta:
        model = ContestParticipation
        fields = [
            'user',
            'score', 'cumtime', 'tiebreaker',
            'frozen_score', 'frozen_cumtime', 'frozen_tiebreaker',
            'virtual', 'is_disqualified', 'is_frozen',
            'format_data',
        ]


class ContestParticipationSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', queryset=Profile.objects.all(),
    )

    def to_internal_value(self, data):
        data = data.copy()
        usernames = data.pop('user', [])
        qs = Profile.objects.filter(owner__username__in=usernames)
        if not qs.exists():
            raise ValidationError(f"User '{usernames[0]}' does not exist.")

        data['user'] = qs.first()
        val_data = super().to_internal_value(data)
        return val_data

    class Meta:
        model = ContestParticipation
        fields = [
            'id', 'real_start', 'virtual', 'is_disqualified',
            'user',]


class ContestParticipationDetailSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=Profile.objects.all(),
    )

    class Meta:
        model = ContestParticipation
        fields = '__all__'
