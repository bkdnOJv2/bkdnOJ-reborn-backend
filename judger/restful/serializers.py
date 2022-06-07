from rest_framework import serializers
from judger.models import Judge, RuntimeVersion, Language
from problem.serializers import ProblemBriefSerializer
from problem.models import Problem

class JudgeBasicSerializer(serializers.ModelSerializer):
    problems = serializers.SlugRelatedField(
        queryset=Problem.objects.all(), many=True, slug_field="shortname",
        required=False,
    )
    runtimes = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Judge
        fields = ['id', 'name', 'online', 'is_blocked', 
                'load', 'ping', 'problems', 'runtimes', 'start_time']

class JudgeSerializer(serializers.ModelSerializer):
    problems = serializers.SlugRelatedField(
        queryset=Problem.objects.all(), many=True, slug_field="shortname",
        required=False,
    )
    runtimes = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Judge
        fields = ['id', 'name', 'auth_key', 'online', 'is_blocked', 
                'last_ip', 'load', 'ping', 'problems', 'runtimes', 'start_time']
        optional_fields = ['id', 'last_ip', 'online', 'is_blocked', 
                'load', 'ping', 'problems', 'runtimes', 'start_time']

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
