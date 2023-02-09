"""
Auth module serializers
"""

from string import ascii_lowercase, digits
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

ALLOWED_CHARSET = set('' + ascii_lowercase + digits + '-_')
User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
        Serializer to retrieve user object from token
    """
    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def validate(self, attrs):
        data = super().validate(attrs)
        user = {
            'username': self.user.username,
            'email': self.user.email,
        }
        if self.user.is_staff:
            user['is_staff'] = True
        if self.user.is_superuser:
            user['is_superuser'] = True
        data.update({'user': user})
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """
        Serializer to register new user
    """
    username = serializers.CharField(
        required=True, min_length=4, max_length=30,)
    email = serializers.EmailField(
        required=False,
    )
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password',
                  'password_confirm', 'first_name', 'last_name')
        optional_fields = ['email', 'first_name', 'last_name']

    def validate_username(self, username):
        """
            Validates username:
            - 4 <= Length <= 30
            - All lowercases
            - Not allow dups
        """

        if len(username) < 4 and len(username) > 30:
            raise ValidationError(
                'Username must be between 4 and 30 characters long')

        if settings.BKDNOJ_EASTER_EGG_ENABLE:
            if username == '1509':
                raise ValidationError(
                    'Believe in yourself. No matter how long it will take.')
            if username == 'undefined':
                raise ValidationError(
                    'Your username will confuse the JS devs! Please choose another username!')

        if not ord('a') <= ord(username[0]) <= ord('z'):
            raise ValidationError(
                'Username must start with a lowercase alphabet letter.')
        if not username.islower():
            raise ValidationError('Username must be in lowercase.')

        for username_char in username:
            if not username_char in ALLOWED_CHARSET:
                raise ValidationError(
                    'Username must only contains alphabet letters, '+
                    'digits, dashes (-) and underscores (_).')

        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def validate(self, attrs):
        """
            Validates other attributes
        """

        # if attrs.get('email', '') != '':
        #     if User.objects.filter(email=attrs['email']).exists():
        #         raise serializers.ValidationError(
        #           {"email": "Email has already been used by someone else."})
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        dat = validated_data.copy()
        dat.pop('password', None)
        dat.pop('password_confirm', None)
        user = User.objects.create(
            # username=validated_data['username'],
            # email=validated_data['email'],
            **dat
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer to get user
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        lookup_field = 'username'


class UserDetailSerializer(UserSerializer):
    """
        Serializer to get user details
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active',
                  'date_joined']  # , 'last_login']#, 'groups']
        lookup_field = 'username'


class UserMoreDetailSerializer(UserSerializer):
    """
        Serializer to get user more details
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active',
                  'date_joined', 'last_login', 'groups']
        lookup_field = 'username'


class GroupSerializer(serializers.ModelSerializer):
    """
        Serializer to get user group
    """
    class Meta:
        model = Group
        fields = ['name', 'user_set']
