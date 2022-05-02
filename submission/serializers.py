from rest_framework import serializers
from submission.models import Submission, SubmissionSource, SubmissionTestCase

from userprofile.serializers import UserProfileSerializer
from problem.serializers import ProblemBriefSerializer
from judger.restful.serializers import LanguageSerializer

import logging
logger = logging.getLogger(__name__)

class SubmissionSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionSource
        fields = ('source',)

class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.owner.username')
    problem = serializers.CharField(source='problem.shortname')
    language = serializers.CharField(source='language.name')

    class Meta:
        model = Submission
        fields = (
            "id", "date", "time", "memory", "points", "status", "result",
            "case_points", "case_total", "judged_date", "rejudged_date",
            "user", "problem", "language",
            "judged_on", "contest_object",
        )
        read_only_fields = ('id',)

class SubmissionTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionTestCase
        fields = '__all__'

class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    problem = ProblemBriefSerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    source = serializers.CharField(source='source.source')
    test_cases = SubmissionTestCaseSerializer(many=True)

    class Meta:
        model = Submission
        fields = ("id", "date", "time", "memory", "points", "status", "result",
            "error", "current_testcase", "batch", "case_points", "case_total", "judged_date", "rejudged_date",
            "is_pretested", "locked_after",
            "user", "problem", "language", "source",
            "judged_on", "contest_object",

            'test_cases',
        )

class SubmissionURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Submission
        fields = ('url',)

class SubmissionSubmitSerializer(serializers.ModelSerializer):
    source = serializers.CharField()

    class Meta:
        model = Submission
        fields = (
            'problem','language','source',
        )
        read_only_fields = ('problem',)
    
    def create(self, validated_data):
        logger.warn("Validated Data:", validated_data)
        src = validated_data.pop('source')
        sub = Submission.objects.create(**validated_data)

        subsource = SubmissionSource.objects.create(
            submission=sub, source=src
        )
        return sub
