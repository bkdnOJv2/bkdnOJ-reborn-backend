from rest_framework import serializers
from .models import Problem, ProblemTestDataProfile
from organization.serializers import OrganizationSerializer

class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    shared_orgs = OrganizationSerializer(many=True, read_only=True)

    class Meta:
        model = Problem 
        fields = [
            'shortname', 'title', 'content',
            'source', 'time_limit', 'memory_limit',
            'allowed_language', 
            'authors', 'collaborators', 'reviewers',

            'is_published',
            'is_privated_to_orgs', 'shared_orgs',

            'submission_visibility_mode',

            '',
        ]
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }