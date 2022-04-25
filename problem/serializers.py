from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from organization.models import Organization

from .models import Problem, ProblemTestDataProfile

class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    shared_orgs = serializers.SlugRelatedField(
        queryset=Organization.objects.all(), many=True, slug_field="shortname"
    )
    authors = serializers.SlugRelatedField(
        queryset=User.objects.all(), many=True, slug_field="username"
    )
    collaborators = serializers.SlugRelatedField(
        queryset=User.objects.all(), many=True, slug_field="username"
    )
    reviewers = serializers.SlugRelatedField(
        queryset=User.objects.all(), many=True, slug_field="username"
    )

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
        ]
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }


class ProblemTestDataProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTestDataProfile
        fields = '__all__'
        read_only_fields = ('problem',)
        lookup_field = 'problem'
        extra_kwargs = {
            'url': {'lookup_field': 'problem'}
        }
    