from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

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
    username = serializers.CharField(required=True, min_length=4, max_length=30)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
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

class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'is_staff', 'is_superuser',
            'is_active', 'date_joined', 'last_login']#, 'groups']

class UserMoreDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'is_staff', 'is_superuser',
            'is_active', 'date_joined', 'last_login', 'groups']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'user_set']
