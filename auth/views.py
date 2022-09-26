from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

from userprofile.models import UserProfile
from organization.models import Organization
User = get_user_model()

from django.core.exceptions import PermissionDenied

from rest_framework import generics, status, views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserDetailSerializer

class MyTokenVerifyView(TokenVerifyView):
    serializer_class = TokenVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            token = request.data['token']
            access_token_obj = AccessToken(token)
            user_id = access_token_obj['user_id']
            user_obj = User.objects.get(id=user_id)

            return Response({
                'user': {
                    'username': user_obj.username,
                    'is_staff': user_obj.is_staff,
                    'is_active': user_obj.is_active,
                }
            },status=status.HTTP_200_OK)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class WhoAmI(views.APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            user_obj = request.user
            return Response({
                'user': {
                    'username': user_obj.username,
                    'is_staff': user_obj.is_staff,
                    'is_active': user_obj.is_active,
                }
            },status=status.HTTP_200_OK)
        return Response({'user' : None}, status=status.HTTP_200_OK)


from helpers.permissions import IsNotAuthenticated
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsNotAuthenticated,)
    serializer_class = RegisterSerializer

class SignOutView(views.APIView):
    def get(self, request, format=None):
        # TODO: Invalidate token
        return Response(status=status.HTTP_204_NO_CONTENT);


from django.http import HttpResponse, HttpResponseNotFound
import django_filters
from rest_framework import permissions, generics, filters

from .serializers import UserSerializer, UserDetailSerializer, GroupSerializer

class UserList(generics.ListCreateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^username', '@first_name', '@last_name']
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    ordering_fields = ['date_joined']
    ordering = ['-id']

    def get_queryset(self):
        qs = User.objects.all()

        user = self.request.user
        method = self.request.method
        if method == 'GET':
            if user.is_staff and not user.is_superuser:
                qs = qs.filter(is_superuser=False)
        else:
            if not user.is_superuser:
                raise PermissionDenied()
        return qs

import io, csv

file_format = {
    'user_attributes': {
        'username': {
            'required': True,
        },
        'password': {
            'required': False,
        },
        'first_name': {
            'required': False,
        },
        'last_name': {
            'required': False,
        },
        'email': {
            'required': False,
        },
    },
    'config': {
        'encoding': 'utf-8',
    }
}

@api_view(['OPTIONS', 'POST'])
def generate_user_from_file(request):
    def badreq(msg):
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if not user.is_staff:
        raise PermissionDenied

    if request.method == 'OPTIONS':
        return Response(file_format, status=status.HTTP_200_OK)
    else:
        if request.FILES.get('file') == None:
            return badreq({"detail": "No file named 'file' attached."})

        line_no = 0
        file = request.FILES['file'].read().decode(file_format['config']['encoding'])
        reader = csv.DictReader(io.StringIO(file))

        many_data = [line for line in reader]

        with transaction.atomic():
            for i in range(len(many_data)):
                data = many_data[i]
                pwd = None
                if 'password' in data.keys():
                    pwd = data['password']
                else:
                    pwd = get_random_string(length=16)
                data['password'] = data['password_confirm'] = pwd
                many_data[i] = data

            ser = RegisterSerializer(data=many_data, many=True)
            if not ser.is_valid():
                return badreq({'detail': "Cannot create some users.", 'errors': ser.errors})

            users = ser.save()

            # Post value assignment
            profiledata = {}
            for i in range(len(many_data)):
                data = many_data[i]
                profiledatapoint = {}
                if 'display_name' in data:
                    profiledatapoint['display_name'] = data['display_name']
                if 'organization' in data:
                    orgslug = data['organization'].upper()
                    try:
                        org = Organization.objects.get(slug=orgslug)
                        profiledatapoint['organization'] = org
                    except Organization.DoesNotExist:
                        data['organization'] = ''
                        profiledatapoint['organization'] = None
                profiledata[data['username']] = profiledatapoint

            for user in users:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profiledatapoint = profiledata[user.username]
                print(profiledatapoint)
                if profiledatapoint.get('display_name', False):
                    profile.username_display_override = profiledatapoint.get('display_name')
                if profiledatapoint.get('organization', False):
                    profile.organizations.add(profiledatapoint.get('organization'))
                    profile.display_organization = profiledatapoint.get('organization')
                profile.first_name = user.first_name
                profile.last_name = user.last_name
                profile.save()

        for data in many_data:
            data.pop('password_confirm', None)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=many_data[0].keys())
        writer.writeheader()
        writer.writerows(many_data)
        return Response(output.getvalue(), status=status.HTTP_201_CREATED)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_queryset(self):
        qs = User.objects.all()

        user = self.request.user
        method = self.request.method
        if method == 'GET':
            if not user.is_staff:
                raise PermissionDenied()
            if not user.is_superuser:
                qs = qs.filter(is_superuser=False)
        else:
            if not user.is_superuser:
                raise PermissionDenied()
        return qs

from django.shortcuts import get_object_or_404

@api_view(['POST'])
def reset_password(request, username):
    user = get_object_or_404(User, username=username)
    if (not request.user.is_superuser) or (not user != request.user):
        raise PermissionDenied()

    pw = request.data.get('password', None)
    pw2 = request.data.get('password', None)
    if pw is None or pw2 is None:
        return Response({
            'detail': "'password' and 'password_confirm' cannot be empty."
        }, status=status.HTTP_400_BAD_REQUEST)
    if pw != pw2:
        return Response({
            'detail': "'password' and 'password_confirm' must not be different."
        }, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(pw)
    user.save()
    return Response({}, status=status.HTTP_204_NO_CONTENT)


class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf(request):
    raise NotImplementedError
    # response = JsonResponse({'detail': 'CSRF cookie set'},
        # status=status.HTTP_200_OK)
    # response['X-CSRFToken'] = get_token(request)
    # return response
