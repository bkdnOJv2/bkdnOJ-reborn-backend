from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from organization.models import Organization

from userprofile.models import UserProfile
from .models import Problem, ProblemTestProfile, TestCase

import logging
logger = logging.getLogger(__name__)

class ProblemBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem 
        fields = ['shortname', 'title', 'points', 'time_limit', 'memory_limit']
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

class ProblemBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem 
        fields = [
            'shortname', 'title', 'solved_count', 'points', 'time_limit', 'memory_limit',
            'attempted_count', 'points', 'is_public', 'is_organization_private',
            'created', 'modified',
        ]
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'}
        }

    def create(self, validated_data):
        inst = super().create(validated_data)
        request = self.context.get('request')
        if request is not None:
            inst.authors.add(request.user.profile)
            inst.save()
        return inst

# from judger.restful.serializers import LanguageSerializer
# The line above causes Circular Import, and I have been trying to fix 
# this for 30+ mins...
# F*** it, lets redefine it for now. 
from judger.models import Language
class LanguageBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'key', 'name', 'short_name', 'common_name', 'ace']
        read_only_fields = ['id', 'key', 'name', 'short_name', 'common_name', 'ace']
        optional_fields = ['name', 'short_name', 'common_name', 'ace']
    
    def to_internal_value(self, data):
        if type(data) in [str, int]:
            lookup_key = ('key' if type(data) == str else 'id')
            langs = Language.objects.filter(**{f'{lookup_key}': data})
            if langs.exists():
                return langs[0].id

            raise serializers.ValidationError({
                'language_not_exist': f"Cannot find language with '{lookup_key}' = {data}"
            })
        else:
            return super().to_internal_value(data)


class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    organizations = serializers.SlugRelatedField(
        queryset=Organization.objects.all(), many=True, slug_field="shortname", required=False 
    )
    authors = serializers.SlugRelatedField(
        queryset=UserProfile.objects.all(), many=True, slug_field="username", required=False,
    )
    collaborators = serializers.SlugRelatedField(
        queryset=UserProfile.objects.all(), many=True, slug_field="username", required=False,
    )
    reviewers = serializers.SlugRelatedField(
        queryset=UserProfile.objects.all(), many=True, slug_field="username", required=False,
    )
    allowed_languages = LanguageBasicSerializer(many=True, required=False)

    def to_internal_value(self, data):
        profiles = ['authors', 'collaborators', 'reviewers']
        qs = UserProfile.objects.select_related('owner')
        profiles_val = {}

        for prf in profiles:
            usernames = data.pop(prf, [])
            profile_ins = []
            for uname in usernames:
                p = qs.filter(owner__username=uname)
                if p == None:
                    raise ValidationError(f"User '{uname}' does not exist.")
                profile_ins.append(p.first().id)
            profiles_val[prf] = profile_ins
            
        val_data = super().to_internal_value(data)
        for k, v in profiles_val.items():
            val_data[k] = v
        return val_data

    class Meta:
        model = Problem 
        fields = [
            'url',
            'shortname', 'title', 'content', 'pdf', 
            'created', 'modified',

            'source', 'time_limit', 'memory_limit',
            'authors', 'collaborators', 'reviewers',

            'allowed_languages',
            'is_public', 'date',
            'is_organization_private', 'organizations',
            'points', 'short_circuit', 'partial',

            'submission_visibility_mode', 'solved_count', 'attempted_count',
        ]
        read_only_fields = ['url', ]
        optional_fields = ['allowed_languages', 'collaborators', 'reviewers', 'organizations']
        lookup_field = 'shortname'
        extra_kwargs = {
            'url': {'lookup_field': 'shortname'},
        }
    
    def update(self, instance, validated_data):
        if validated_data.get('allowed_languages', None) != None:
            langs = validated_data.pop('allowed_languages')
            instance.allowed_languages.set(langs)
        return super().update(instance, validated_data)


class ProblemInContestSerializer(ProblemSerializer):
    class Meta:
        model = Problem 
        fields = [
            'shortname', 'title', 'content', 'pdf',
            'source', 'time_limit', 'memory_limit',
            'authors', 'collaborators', 'reviewers',
            'allowed_languages',
            #'is_public',
            #'is_organization_private', 'organizations',
            #'points', 'short_circuit', 'partial',
            'submission_visibility_mode',
            #'solved_count', 'attempted_count',
        ]
    
    def update(self, instance, validated_data):
        raise NotImplementedError

class ProblemTestProfileSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(slug_field='shortname', read_only=True)

    class Meta:
        model = ProblemTestProfile
        fields = '__all__'
        read_only_fields = ('problem', 'created', 'modified', 'feedback')#'zipfile', 'generator')
        extra_kwargs = {
            'url': {'lookup_field': 'problem'}
        }
    
class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'
