from functools import lru_cache as cache
from django.conf import settings

from rest_framework import serializers
from submission.models import Submission, SubmissionSource, SubmissionTestCase

from userprofile.serializers import UserProfileBaseSerializer
from compete.models import ContestParticipation
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

    is_frozen = serializers.SerializerMethodField()
    @cache
    def get_is_frozen(self, obj):
        user = self.context['request'].user
        return not obj.can_see_detail(user)

    def _get_result(self, obj, key, default=None):
        if self.get_is_frozen(obj):
            return default
        return getattr(obj, key, default)

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

def trim_til_length(txt, lng):
    if txt is None: return txt

    if lng < 1: lng = 1
    lim = lng+3
    if len(txt) >= lim:
        txt = txt[:lng-3] + '...'
    return txt

class SubmissionTestCaseDetailSerializer(serializers.ModelSerializer):
    input_partial = serializers.SerializerMethodField()
    def get_input_partial(self, sub_case):
        return sub_case.submission.problem.get_case_partial(sub_case.case)[0]

    answer_partial = serializers.SerializerMethodField()
    def get_answer_partial(self, sub_case):
        return sub_case.submission.problem.get_case_partial(sub_case.case)[1]
    
    feedback = serializers.SerializerMethodField()
    def get_feedback(self, sub_case):
        return trim_til_length(sub_case.feedback, settings.BKDNOJ_TESTCASE_PREVIEW_LENGTH)

    extended_feedback = serializers.SerializerMethodField()
    def get_extended_feedback(self, sub_case):
        return trim_til_length(sub_case.extended_feedback, settings.BKDNOJ_TESTCASE_PREVIEW_LENGTH)

    output = serializers.SerializerMethodField()
    def get_output(self, sub_case):
        return trim_til_length(sub_case.output, settings.BKDNOJ_TESTCASE_PREVIEW_LENGTH)

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
