from string import ascii_lowercase, digits
ALLOWED_CHARSET = set('' + ascii_lowercase + digits + '-_')

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(MyTokenObtainPairSerializer, self).validate(attrs)
        user = {
            'username': self.user.username,
            'email': self.user.email,
        }
        if self.user.is_staff:
            user['is_staff'] = True
        if self.user.is_superuser:
            user['is_superuser'] = True
        data.update({ 'user': user })
        return data

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=4, max_length=30,)
    email = serializers.EmailField(
        required=False,
    )
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        optional_fields = ['email', 'first_name', 'last_name']
    
    def validate_username(self, username):
        if len(username) < 4 and len(username) > 30:
            raise ValidationError('Username must be between 4 and 30 characters long')
        
        if settings.BKDNOJ_EASTER_EGG_ENABLE:
            if username == '1509':
                raise ValidationError('Believe in yourself. No matter how long it will take.')
            if username == 'undefined':
                raise ValidationError('Your username will confuse the JS devs! Please choose another username!')

        if not (ord('a') <= ord(username[0]) <= ord('z')):
            raise ValidationError('Username must start with a lowercase alphabet letter.')
        if not username.islower():
            raise ValidationError('Username must be in lowercase.')
        
        for c in username:
            if not c in ALLOWED_CHARSET:
                raise ValidationError('Username must only contains alphabet letters, digits, dashes (-) and underscores (_).')

        if User.objects.filter(username=username).exists():
            raise ValidationError(f"This username is already taken.")

        return username

    def validate(self, attrs):
        # if attrs.get('email', '') != '':
        #     if User.objects.filter(email=attrs['email']).exists():
        #         raise serializers.ValidationError({"email": "Email has already been used by someone else."})
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
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

from django.contrib.auth.models import Group, User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        lookup_field = 'username'
        

class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
            'first_name', 'last_name',
            'is_staff', 'is_superuser', 'is_active',
            'date_joined']#, 'last_login']#, 'groups']
        lookup_field = 'username'

class UserMoreDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
            'first_name', 'last_name',
            'is_staff', 'is_superuser', 'is_active',
            'date_joined', 'last_login', 'groups']
        lookup_field = 'username'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'user_set']
