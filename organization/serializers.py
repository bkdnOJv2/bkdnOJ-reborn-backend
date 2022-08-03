from django.contrib.auth.models import Group
from django.core.cache import cache
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers

from auth.serializers import UserSerializer, UserDetailSerializer
from .models import Organization

__all__ = [
    'OrganizationBasicSerializer',
    'NestedOrganizationBasicSerializer', 'OrganizationSerializer'
]

class OrganizationBasicSerializer(serializers.ModelSerializer):
    suborg_count = serializers.SerializerMethodField()
    def get_suborg_count(self, inst):
        if getattr(inst, 'get_descendant_count', False):
            return inst.get_descendant_count()
        return 0

    real_member_count = serializers.SerializerMethodField()
    def get_real_member_count(self, inst):
        return inst.members.count()

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'logo_url',
            'is_unlisted',
            'suborg_count', 'member_count', 'real_member_count',
        ]

class NestedOrganizationBasicSerializer(OrganizationBasicSerializer):
    sub_orgs = serializers.SerializerMethodField()
    def get_sub_orgs(self, org):
        if org.is_leaf():
            return []

        data = org.get_cache()
        if data is None:
            data = NestedOrganizationBasicSerializer(org.get_children().order_by('-creation_date').all(), many=True, read_only=True).data
            org.set_cache(data)
        return data

    suborg_count = serializers.SerializerMethodField()
    def get_suborg_count(self, inst):
        if getattr(inst, 'get_descendant_count', False):
            return inst.get_descendant_count()
        return 0

    real_member_count = serializers.SerializerMethodField()
    def get_real_member_count(self, inst):
        return inst.members.count()

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'logo_url',
            'is_unlisted',
            'member_count', 'suborg_count',
            'real_member_count',
            'sub_orgs',
        ]


class OrganizationSerializer(OrganizationBasicSerializer):
    suborg_count = serializers.SerializerMethodField()
    def get_suborg_count(self, inst):
        if getattr(inst, 'get_descendant_count', False):
            return inst.get_descendant_count()
        return 0

    real_member_count = serializers.SerializerMethodField()
    def get_real_member_count(self, inst):
        return inst.members.count()

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name',
            'is_open', 'is_unlisted',
            'logo_url',
            'suborg_count', 'member_count', #'performance_points'
            'real_member_count',
        ]
        read_only_fields = ('member_count', 'suborg_count', 'real_member_count')
        # extra_kwargs = {
        #     'logo_url': {'read_only': True},
        #     'member_count': {'read_only': True},
        #     'suborg_count': {'read_only': True},
        # }

from userprofile.models import UserProfile
from django.core.exceptions import ValidationError

class OrganizationDetailSerializer(OrganizationSerializer):
    admins = serializers.SerializerMethodField()
    def get_admins(self, instance):
        users = User.objects.filter(profile__in=instance.admins.all())
        return UserDetailSerializer(users, many=True).data

    parent_org = serializers.SerializerMethodField()
    def get_parent_org(self, instance):
        if instance.is_root():
            return None
        return OrganizationBasicSerializer(instance.get_parent(), read_only=True).data

    real_member_count = serializers.SerializerMethodField()
    def get_real_member_count(self, inst):
        return inst.members.count()
    
    is_member = serializers.SerializerMethodField()
    def get_is_member(self, inst):
        user = self.context['request'].user
        if not user.is_authenticated or not inst.members.filter(id=user.profile.id).exists():
            return False
        return True

    access_code = serializers.SerializerMethodField()
    def get_access_code(self, inst):
        user = self.context['request'].user
        if inst.is_editable_by(user):
            return inst.access_code
        return None

    # Convert username into profiles...
    def to_internal_value(self, data):
        user_fields = ['admins']
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
        
        # access_code
        acode = data.pop('access_code', None)

        val_data = super().to_internal_value(data)

        # profiles
        for k, v in profile_dict.items():
            val_data[k] = v
        # access_code
        val_data['access_code'] = acode
        return val_data

    class Meta:
        model = Organization
        fields = [
            'slug', 'short_name', 'name', 'is_open',
            'logo_url',
            'is_open', 'is_unlisted',

            'admins', 'about', 'creation_date', 'slots',

            'parent_org',

            'suborg_count', 'member_count', #'performance_points'
            'real_member_count',

            'access_code_prompt', 'is_protected',
            'access_code',
            'is_member',
        ]
        read_only_fields = ('member_count', 'suborg_count')
