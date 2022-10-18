from functools import lru_cache as cache

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from auth.serializers import UserSerializer, UserDetailSerializer

from userprofile.serializers import UserProfileWithRoleSerializer
from userprofile.models import UserProfile as Profile

from organization.models import Organization
from organization.serializers import OrganizationSerializer, OrganizationIdentitySerializer

from problem.models import Problem
from problem.serializers import ProblemInContestSerializer, ProblemBasicSerializer
from submission.serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Contest, ContestProblem, ContestSubmission, ContestParticipation, Rating

from compete.utils import contest_registered_ids

__all__ = [
    'ContestSerializer',
    'PastContestBriefSerializer', 'ContestBriefSerializer',

    'ContestDetailUserSerializer',
    'ContestDetailAdminSerializer',

    'ContestProblemSerializer',
    'ContestProblemBriefSerializer',
    'ContestSubmissionSerializer',
    'ContestStandingFrozenSerializer', 'ContestStandingSerializer',
    'ContestParticipationSerializer',
    'ContestParticipationDetailSerializer',

    'RatingSerializer',
]

class PastContestBriefSerializer(serializers.ModelSerializer):
    spectate_allow = serializers.SerializerMethodField()
    def get_spectate_allow(self, obj):
        return False

    register_allow = serializers.SerializerMethodField()
    def get_register_allow(self, obj):
        return False

    is_registered = serializers.SerializerMethodField()
    def get_is_registered(self, obj):
        return False

    class Meta:
        model = Contest
        fields = [
            'spectate_allow', 'register_allow','is_registered',
            'key', 'name', 'format_name',

            'is_rated',
            'published',
            'is_visible',
            'is_private',
            'is_organization_private',

            'start_time', 'end_time', 'time_limit',
            'enable_frozen', 'frozen_time', 'is_frozen',
            'user_count',
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
    def get_is_registered(self, contest):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False

        return user.profile.id in contest_registered_ids(contest)

        # if ContestParticipation.objects.filter(
        #     virtual__in=[ContestParticipation.LIVE, ContestParticipation.SPECTATE],
        #     contest=obj, user=user.profile
        # ).exists():
        #     return True
        # return False

    def to_internal_value(self, data):
        user_fields = ['authors']
        qs = Profile.objects.select_related('user')

        profile_dict = {}
        for field in user_fields:
            users = data.pop(field, [])

            profile_ids = []
            for user in users:
                username = user['username']
                p = qs.filter(user__username=username)
                if not p.exists():
                    raise ValidationError(f"User '{username}' does not exist.")
                profile_ids.append(p.first().id)
            profile_dict[field] = profile_ids


        val_data = super().to_internal_value(data)

        ## Assign Profile ids
        for k, v in profile_dict.items():
            val_data[k] = v
        return val_data

    class Meta:
        model = Contest
        fields = [
            'spectate_allow', 'register_allow','is_registered',
            'key', 'name', 'format_name',

            'is_rated',
            'published',
            'is_visible',
            'is_private',
            'is_organization_private',

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

            'published',
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
    solved = serializers.SerializerMethodField()
    def get_solved(self, problem):
        context = self.context
        if problem.problem.id in context.get('solved', []):
            return True
        return False

    attempted = serializers.SerializerMethodField()
    def get_attempted(self, problem):
        context = self.context
        if problem.problem.id in context.get('attempted', []):
            return context['attempted'][problem.problem.id]
        return None

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

    solved_count = serializers.SerializerMethodField()
    def get_solved_count(self, cp):
        return cp.frozen_solved_count if cp.contest.is_frozen else cp.solved_count

    attempted_count = serializers.SerializerMethodField()
    def get_attempted_count(self, cp):
        return cp.frozen_attempted_count if cp.contest.is_frozen else cp.attempted_count

    class Meta:
        model = ContestProblem
        fields = [
            'id',
            'solved', 'attempted',

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
    problem_data = serializers.SerializerMethodField()
    def get_problem_data(self, cp):
        # print(self.context['request'].GET)
        return ProblemInContestSerializer(cp.problem, read_only=True, context=self.context).data

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

from userprofile.serializers import UserProfileBaseSerializer


class ContestDetailUserSerializer(ContestBriefSerializer):
    authors = UserProfileBaseSerializer(many=True, read_only=True)
    # collaborators = UserProfileBaseSerializer(many=True, read_only=True)
    # reviewers = UserProfileBaseSerializer(many=True, read_only=True)

    # private_contestants = UserProfileBaseSerializer(many=True, read_only=True)
    # banned_users = UserProfileBaseSerializer(many=True, read_only=True)

    organizations = serializers.SerializerMethodField()
    def get_organizations(self, contest):
        orgs = contest.organizations.all()
        return OrganizationIdentitySerializer(orgs, many=True).data

    problems = serializers.SerializerMethodField()
    def get_problems(self, contest):
        data = []
        if contest.started:
            for p in contest.contest_problems.all():
                data.append({
                    'label': p.label,
                    'title': p.problem.title,
                    'shortname': p.problem.shortname,
                })
        return data

    class Meta:
        model = Contest
        fields = [
            # 'id', 
            'spectate_allow', 'register_allow', 'is_registered',
            'authors', 'organizations', 
            # 'tags',
            'published', 'is_visible', 'is_organization_private',
            'key', 'name', 'description', 'start_time', 'end_time',
            'points_precision',

            'problems',
            'scoreboard_cache_duration',
            'enable_frozen', 'frozen_time',
            'use_clarifications', 'format_name',

            'is_rated', 'rating_floor', 'rating_ceiling',
            'user_count',
        ]#'__all__'
        optional_fields = ['is_registered', 'spectate_allow', 'register_allow']
        lookup_field = 'key'
        extra_kwargs = {
            'url': {'lookup_field': 'key'}
        }

class ContestDetailAdminSerializer(ContestBriefSerializer):
    authors = UserProfileWithRoleSerializer(many=True, read_only=True)
    collaborators = UserProfileWithRoleSerializer(many=True, read_only=True)
    reviewers = UserProfileWithRoleSerializer(many=True, read_only=True)
    private_contestants = UserProfileWithRoleSerializer(many=True, read_only=True)
    banned_users = UserProfileWithRoleSerializer(many=True, read_only=True)
    view_contest_scoreboard = UserProfileWithRoleSerializer(many=True, read_only=True)
    rate_exclude = UserProfileWithRoleSerializer(many=True, read_only=True)

    organizations = serializers.SerializerMethodField()
    def get_organizations(self, contest):
        orgs = contest.organizations.all()
        return OrganizationIdentitySerializer(orgs, many=True).data

    problems = serializers.SerializerMethodField()
    def get_problems(self, contest):
        data = []
        if contest.started:
            for p in contest.contest_problems.all():
                data.append({
                    'label': p.label,
                    'title': p.problem.title,
                    'shortname': p.problem.shortname,
                })
        return data

    def to_internal_value(self, data):
        ## Users
        user_fields = ['authors', 'collaborators', 'reviewers',
            'private_contestants', 'banned_users']
        qs = Profile.objects.select_related('user')
        profile_dict = {}
        for field in user_fields:
            users = data.pop(field, [])

            profile_ids = []
            for user in users:
                username = user['username']
                p = qs.filter(user__username=username)
                if not p.exists():
                    raise ValidationError(f"User '{username}' does not exist.")
                profile_ids.append(p.first().id)
            profile_dict[field] = profile_ids

        ## Orgs
        qs = Organization.objects.all()
        orgs = data.pop('organizations', [])
        org_ids = []
        for org in orgs:
            org_slug = org['slug']
            o = qs.filter(slug=org_slug)
            if not o.exists():
                raise ValidationError(f"Organization'{org_slug}' does not exist.")
            org_ids.append(o.first().id)

        val_data = super().to_internal_value(data)

        ## Assign Profile ids
        for k, v in profile_dict.items():
            val_data[k] = v

        ## Assign Organization ids
        val_data['organizations'] = org_ids
        return val_data

    class Meta:
        model = Contest
        fields = '__all__'
        # exclude = ('problems',)
        # fields = [
        #     'id', 'spectate_allow', 'register_allow', 'is_registered',
        #     'authors',
        #     'collaborators', 'reviewers', 'private_contestants', 'banned_users', 'organizations',
        #     'published', 'is_visible', 'is_organization_private',
        #     'key', 'name', 'format_name', 'start_time', 'end_time',
        #     # 'problems'
        # ]#'__all__'
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
        return not obj.submission.can_see_detail(user)

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

    virtual = serializers.SerializerMethodField()
    def get_virtual(self, cs):
        if cs.participation.virtual == ContestParticipation.LIVE:
            return 'live'
        if cs.participation.virtual == ContestParticipation.SPECTATE:
            return 'spectate'
        return 'virtual'

    user = serializers.ReadOnlyField(source='submission.user.username')
    language = serializers.ReadOnlyField(source='submission.language.name')

    # # Problems
    problem = ContestProblemBasicSerializer(read_only=True)

    class Meta:
        model = ContestSubmission
        fields = [
            'id', 'date', 'is_frozen',
            'time', 'memory', 'status', 'result', 'user', 'language', 'problem',
            'points', 'virtual'
        ]

import json

class ContestStandingFrozenSerializer(serializers.ModelSerializer):
    #user = ProfileSerializer(required=False)
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.username
        # ser_context = {'request': self.context.get('request')}
        # user_ser = ProfileSerializer(obj.user, context=ser_context)
        # return user_ser.data

    format_data = serializers.SerializerMethodField()
    def get_format_data(self, obj):
        data = obj.frozen_format_data
        data = json.dumps(data)
        return data

    organization = OrganizationIdentitySerializer()

    class Meta:
        model = ContestParticipation
        fields = [
            'user', 'organization',
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
            'user', 'organization',
            'score', 'cumtime', 'tiebreaker',
            'frozen_score', 'frozen_cumtime', 'frozen_tiebreaker',
            'virtual', 'is_disqualified', 'is_frozen',
            'format_data',
        ]


class ContestParticipationSerializer(serializers.ModelSerializer):
    user = UserProfileBaseSerializer()
    organization = OrganizationIdentitySerializer()

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
            'id', 'user', 'organization', 'real_start',
            'virtual', 'is_disqualified',
        ]


class ContestParticipationDetailSerializer(serializers.ModelSerializer):
    # user = serializers.SlugRelatedField(
    #     slug_field='user__username',
    #     queryset=Profile.objects.all(),
    # )
    user = serializers.SerializerMethodField()
    def get_user(self, part):
        return part.user.user.username

    organization = OrganizationIdentitySerializer()

    class Meta:
        model = ContestParticipation
        fields = [
            'id', 'user', 'organization', 'real_start',
            'score', 'cumtime', 'tiebreaker',
            'is_disqualified', 'virtual',
            'modified',
        ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
