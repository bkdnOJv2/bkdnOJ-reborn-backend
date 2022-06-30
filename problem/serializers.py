from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from organization.models import Organization
from organization.serializers import OrganizationSerializer

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
            'partial', 'short_circuit',
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

from auth.serializers import UserDetailSerializer

class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    authors = serializers.SerializerMethodField()
    def get_authors(self, problem):
        users = User.objects.filter(id__in=problem.authors.values_list('id', flat=True))
        return UserDetailSerializer(users, many=True).data

    collaborators = serializers.SerializerMethodField()
    def get_collaborators(self, problem):
        users = User.objects.filter(id__in=problem.collaborators.values_list('id', flat=True))
        return UserDetailSerializer(users, many=True).data

    reviewers = serializers.SerializerMethodField()
    def get_reviewers(self, problem):
        users = User.objects.filter(id__in=problem.reviewers.values_list('id', flat=True))
        return UserDetailSerializer(users, many=True).data

    organizations = serializers.SerializerMethodField()
    def get_organizations(self, contest):
        orgs = Organization.objects.filter(id__in=contest.organizations.values_list('id', flat=True))
        return OrganizationSerializer(orgs, many=True).data

    allowed_languages = LanguageBasicSerializer(many=True, required=False)

    def to_internal_value(self, data):
        user_fields = ['authors', 'collaborators', 'reviewers']
        qs = UserProfile.objects.select_related('user')

        profile_dict = {}

        for field in user_fields:
            users = data.pop(field, [])

            profile_ids = []
            for user in users:
                username = user['username']
                p = qs.filter(user__username=username)
                if not p.exists():
                    raise ValidationError(f"User '{username}' does not exist.")
                profile_ids.append(p.first().id)
            profile_dict[field] = profile_ids

        ## Orgs
        qs = Organization.objects.all()
        orgs = data.pop('organizations', [])
        org_ids = []
        for org in orgs:
            org_slug = org['slug']
            o = qs.filter(slug=org_slug)
            if not o.exists():
                raise ValidationError(f"Organization'{org_slug}' does not exist.")
            org_ids.append(o.first().id)

        val_data = super().to_internal_value(data)

        ## Assign Profile ids
        for k, v in profile_dict.items():
            val_data[k] = v

        ## Assign Organization ids
        val_data['organizations'] = org_ids

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
