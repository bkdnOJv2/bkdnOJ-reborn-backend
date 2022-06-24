from rest_framework import serializers
from submission.models import Submission, SubmissionSource, SubmissionTestCase

from userprofile.serializers import UserProfileSerializer, UserProfileSerializer
from problem.serializers import ProblemBriefSerializer, ProblemBasicSerializer
from judger.restful.serializers import JudgeBasicSerializer, LanguageSerializer

import logging
logger = logging.getLogger(__name__)

class SubmissionSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionSource
        fields = ('source',)

class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.owner.username')
    problem = ProblemBasicSerializer(read_only=True)
    language = serializers.CharField(source='language.name')

    contest_object = serializers.SerializerMethodField()
    def get_contest_object(self, sub):
        if sub.contest_object:
            return sub.contest_object.key
        return None

    class Meta:
        model = Submission
        fields = (
            "id", "date", "time", "memory", "points", "status", "result",
            "user", "problem", "language", "contest_object",
            #"judged_on", "judged_date", "rejudged_date", "case_points", "case_total",
        )
        read_only_fields = ('id',)

class SubmissionTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestCase
        exclude = ['submission',]

class SubmissionResultSerializer(serializers.ModelSerializer):
    test_cases = SubmissionTestCaseSerializer(many=True, read_only=True)
    class Meta:
        model = Submission
        fields = ['status', 'status', 'result', 'error', 'current_testcase',
            'is_pretested', 'test_cases'
        ]

class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    problem = ProblemBriefSerializer(read_only=True)
    language = serializers.CharField(source='language.name')
    language_ace = serializers.CharField(source='language.ace')
    source = serializers.CharField(source='source.source')
    test_cases = SubmissionTestCaseSerializer(many=True)

    judged_on = JudgeBasicSerializer(read_only=True)

    contest_object = serializers.SerializerMethodField()
    def get_contest_object(self, sub):
        if sub.contest_object:
            return sub.contest_object.key
        return None

    class Meta:
        model = Submission
        fields = ("id", "date", "time", "memory", "points", "status", "result",
            "error", "current_testcase", "batch", "case_points", "case_total",
            "judged_date", "rejudged_date",

            "contest_object",

            "is_pretested", "locked_after",
            "user", "problem", "language", "language_ace",
            "source",
            "judged_on", "contest_object",

            'test_cases',
        )

class SubmissionBasicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('url', 'id')

class SubmissionSubmitSerializer(serializers.ModelSerializer):
    source = serializers.CharField()

    class Meta:
        model = Submission
        fields = (
            'problem','language','source',
        )
        read_only_fields = ('problem',)

    def create(self, validated_data):
        src = validated_data.pop('source')
        sub = Submission.objects.create(**validated_data)

        subsource = SubmissionSource.objects.create(
            submission=sub, source=src
        )
        return sub
