from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from organization.models import Organization

from .models import Problem, ProblemTestProfile, TestCase
import logging
logger = logging.getLogger(__name__)


class ProblemBasicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Problem 
        fields = ['url', 'shortname', 'title']
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class ProblemBriefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Problem 
        fields = ['url', 'shortname', 'title', 'solved_count', 'attempted_count', 'points']
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

# from judger.restful.serializers import LanguageSerializer
# The line above causes Circular Import, and I have been trying to fix 
# this for 30+ mins...
# Fuck it, lets redefine it for now. 
from judger.models import Language
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
        #('id', 'key', 'name', 'short_name', 'common_name', 'ace', 'template')

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
    allowed_languages = LanguageSerializer(many=True)

    class Meta:
        model = Problem 
        fields = [
            'url',
            'shortname', 'title', 'content', 'pdf',
            'source', 'time_limit', 'memory_limit',
            'authors', 'collaborators', 'reviewers',

            'allowed_languages',
            'is_published',
            'is_privated_to_orgs', 'organizations',
            'short_circuit', 'partial',

            'submission_visibility_mode', 'solved_count', 'attempted_count',
        ]
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class ProblemTestProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProblemTestProfile
        # fields = '__all__'
        exclude = ('output_prefix', 'output_limit')
        read_only_fields = ('problem', 'created', 'modified', 'feedback')#'zipfile', 'generator')
        lookup_field = 'problem'
        extra_kwargs = {
            'url': {'lookup_field': 'problem'}
        }
    
class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'
