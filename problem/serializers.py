from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from organization.models import Organization

from .models import Problem, ProblemTestProfile, TestCase
import logging
logger = logging.getLogger(__name__)


class ProblemBriefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Problem 
        fields = ['url', 'shortname', 'title']
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    organizations = serializers.SlugRelatedField(
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
            'url',
            'shortname', 'title', 'content', 'pdf',
            'source', 'time_limit', 'memory_limit',
            'allowed_languages', 
            'authors', 'collaborators', 'reviewers',

            'is_published',
            'is_privated_to_orgs', 'organizations',

            'submission_visibility_mode',
        ]
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class ProblemTestProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProblemTestProfile
        fields = '__all__'
        read_only_fields = ('problem', 'created', 'modified', 'feedback')#'zipfile', 'generator')
        lookup_field = 'problem'
        extra_kwargs = {
            'url': {'lookup_field': 'problem'}
        }
    
class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'
