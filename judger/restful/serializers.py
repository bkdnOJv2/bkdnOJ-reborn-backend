from rest_framework import serializers
from judger.models import Judge, RuntimeVersion, Language
from problem.serializers import ProblemBriefSerializer
from problem.models import Problem

__all__ = [
    'JudgeSerializer', 'JudgeDetailSerializer',
    'RuntimeVersionSerializer',
    'LanguageBasicSerializer', 'LanguageSerializer'
]

class JudgeSerializer(serializers.ModelSerializer):
    problems = serializers.SlugRelatedField(
        queryset=Problem.objects.all(), many=True, slug_field="shortname",
        required=False,
    )
    runtimes = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Judge
        fields = ['id', 'name', 'auth_key', 'online', 'is_blocked', 'description',
                'last_ip', 'load', 'ping', 'problems', 'runtimes', 'start_time']
        extra_kwargs = {
            'auth_key': {'write_only': True},
            'start_time': {'write_only': True},
            'description': {'write_only': True},
            'load': {'write_only': True},
            'ping': {'write_only': True},
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
