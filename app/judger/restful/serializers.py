from rest_framework import serializers
from judger.models import Judge, RuntimeVersion, Language
from problem.serializers import ProblemBriefSerializer
from problem.models import Problem

__all__ = [
    'JudgeSerializer', 'JudgeDetailSerializer',
    'RuntimeVersionSerializer',
    'LanguageBasicSerializer', 'LanguageSerializer'
]

class JudgeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Judge
        fields = ['id', 'name',]

class JudgeSerializer(serializers.ModelSerializer):
    runtimes = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Judge
        fields = [
            'id', 'name', 'auth_key', 'online', 'is_blocked',
            'load', 'ping', 'runtimes', 'start_time',
        ]
        extra_kwargs = {
            'auth_key': {'write_only': True},
            'start_time': {'read_only': True},
            'description': {'write_only': True},
            'load': {'read_only': True},
            'ping': {'read_only': True},
            'problem': {'write_only': True},
            'runtimes': {'write_only': True},
        }

class JudgeDetailSerializer(serializers.ModelSerializer):
    problems = serializers.SlugRelatedField(
        queryset=Problem.objects.all(), many=True, slug_field="shortname",
        required=False,
    )
    runtimes = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Judge
        fields = '__all__'

class RuntimeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuntimeVersion
        fields = '__all__'

class LanguageBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
