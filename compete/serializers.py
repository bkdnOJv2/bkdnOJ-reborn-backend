from django.contrib.auth.models import Group
from rest_framework import serializers

from auth.serializers import UserSerializer
from userprofile.serializers import UserProfileBasicSerializer as ProfileSerializer
from problem.models import Problem
from problem.serializers import ProblemSerializer
from submission.serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Contest, ContestProblem, ContestSubmission, ContestParticipation

class ContestBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = [
            'key', 'name', 'start_time', 'end_time', 'time_limit', 'user_count',
        ]

class ContestSerializer(serializers.ModelSerializer):
    authors = ProfileSerializer(many=True)

    class Meta:
        model = Contest
        fields = [
            'authors', 'key', 'name', 'start_time', 'end_time',
            'time_limit', 'is_rated', 'tags', 'user_count',
        ]

        lookup_field = 'key'
        extra_kwargs = {
            'url': {'lookup_field': 'key'}
        }

class ContestProblemSerializer(serializers.ModelSerializer):
    # problem = serializers.ReadOnlyField(source='problem.shortname')
    # contest = serializers.ReadOnlyField(source='contest.key')
    problem = serializers.SlugRelatedField(
        slug_field='shortname',
        queryset=Problem.objects.all(),
    )
    contest = serializers.SlugRelatedField(
        slug_field='key',
        queryset=Contest.objects.all(),
    )
    # contest = serializers.ReadOnlyField(source='contest.key')
    class Meta:
        model = ContestProblem
        fields = [
            'problem', 'contest', 'points', 'partial', 'is_pretested',
            'order', 'output_prefix_override', 'max_submissions',
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
    submission = SubmissionSerializer()

    class Meta:
        model = ContestSubmission
        # fields = '__all__'
        exclude = ['problem', 'participation']

class ContestParticipationSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(required=False)

    class Meta:
        model = ContestParticipation
        fields = ['user', 'score', 'cumtime', 'is_disqualified',
            'tiebreaker', 'virtual',
        ]