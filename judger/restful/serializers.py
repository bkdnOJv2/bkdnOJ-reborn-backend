from rest_framework import serializers
from judger.models import Judge, RuntimeVersion, Language
from problem.serializers import ProblemBriefSerializer
from problem.models import Problem

class JudgeSerializer(serializers.ModelSerializer):
    problems = serializers.SlugRelatedField(
        queryset=Problem.objects.all(), many=True, slug_field="shortname"
    )
    runtimes = serializers.StringRelatedField(many=True)

    class Meta:
        model = Judge
        fields = '__all__'

class RuntimeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuntimeVersion
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
