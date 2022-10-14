from rest_framework import serializers
from submission.models import Submission, SubmissionSource, SubmissionTestCase

from userprofile.serializers import UserProfileBaseSerializer
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
        exclude = ['id', 'submission', 'batch', 'output', 'feedback', 'extended_feedback']

class SubmissionTestCaseDetailSerializer(serializers.ModelSerializer):
    input_partial = serializers.SerializerMethodField()
    def get_input_partial(self, sub_case):
        return None # TODO: add implementation

    answer_partial = serializers.SerializerMethodField()
    def get_answer_partial(self, sub_case):
        return None # TODO: add implementation
    
    feedback = serializers.SerializerMethodField()
    def get_feedback(self, sub_case):
        return None # TODO: add implementation

    extended_feedback = serializers.SerializerMethodField()
    def get_extended_feedback(self, sub_case):
        return None # TODO: add implementation

    output = serializers.SerializerMethodField()
    def get_output(self, sub_case):
        return None # TODO: add implementation

    class Meta:
        model = SubmissionTestCase
        exclude = ['submission', 'batch']

class SubmissionResultSerializer(serializers.ModelSerializer):
    test_cases = SubmissionTestCaseSerializer(many=True, read_only=True)
    class Meta:
        model = Submission
        fields = ['status', 'status', 'result', 'error', 'current_testcase',
            'is_pretested', 'test_cases'
        ]

class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserProfileBaseSerializer(read_only=True)
    problem = ProblemBasicSerializer(read_only=True)
    language = serializers.CharField(source='language.name')
    language_ace = serializers.CharField(source='language.ace')

    error = serializers.SerializerMethodField()
    def get_error(self, submission):
        if self.context.get('is_source_visible'): 
            return submission.error
        return None

    source = serializers.SerializerMethodField()
    def get_source(self, submission):
        if self.context.get('is_source_visible'): 
            return submission.source.source
        return None

    # judged_on = JudgeBasicSerializer(read_only=True)
    judged_on = serializers.SerializerMethodField()
    def get_judged_on(self, sub):
        if self.context['request'].user.is_staff:
            return JudgeBasicSerializer(sub.judged_on).data
        return None

    contest_object = serializers.SerializerMethodField()
    def get_contest_object(self, sub):
        if sub.contest_object:
            return sub.contest_object.key
        return None

    class Meta:
        model = Submission
        fields = (
            "id", "date", "time", "memory", "points", "status", "result",
            "error", "current_testcase", "case_total",
            "judged_date", "rejudged_date",
            "contest_object",
            "user", "problem", "language", "language_ace",

            "judged_on", 
            "source",

            #"batch", "case_points", "locked_after", "is_pretested", 
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
