from rest_framework import serializers
from .models import Submission, SubmissionSource

import logging
logger = logging.getLogger(__name__)

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'

class SubmissionSubmitSerializer(serializers.ModelSerializer):
    source = serializers.CharField()

    class Meta:
        model = Submission
        fields = (
            'problem','language','source',
        )
    
    def create(self, validated_data):
        logger.debug("Validated Data:", validated_data)
        src = validated_data.pop('source')
        sub = Submission.objects.create(**validated_data)

        subsource = SubmissionSource.objects.create(
            submission=sub, source=src
        )
        return Submission


class SubmissionDetailSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer()
    class Meta:
        model = SubmissionSource
        fields = ('submission', 'source')

class SubmissionSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ('submission',)
