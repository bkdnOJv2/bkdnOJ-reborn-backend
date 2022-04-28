from rest_framework import serializers
from judger.models import Judge

class JudgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Judge
        fields = '__all__'
