from rest_framework import serializers
from judger.models import Judge, RuntimeVersion, Language
from problem.serializers import ProblemBriefSerializer

class JudgeSerializer(serializers.ModelSerializer):
    problems = ProblemBriefSerializer(
        many=True,
        read_only=True,
    )

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
