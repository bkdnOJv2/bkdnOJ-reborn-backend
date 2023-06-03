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
from helpers.permissions import IsNotAuthenticated

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserDetailSerializer

"""
    Token verify view, receives a JWT token and
    verify if that token is valid. If token is 
    valid, returns the corresponding user.
    Basically a debug view that shares the same
    functionality as WhoAmI
"""
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

"""
    If not authenticated, returns {"user": null}
    Look for JWT token at Authentication header and
    return the identity of that user
"""
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


"""
    Register new account, enforces lowercase alphanum username
"""
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsNotAuthenticated,)
    serializer_class = RegisterSerializer

"""
    SignOut user, should invalidate their current JWT
    (but not implem yet)
"""
class SignOutView(views.APIView):
    def get(self, request, format=None):
        # TODO: Invalidate token
        return Response(status=status.HTTP_204_NO_CONTENT);


from django.http import HttpResponse, HttpResponseNotFound
import django_filters
from rest_framework import permissions, generics, filters

from .serializers import UserSerializer, UserDetailSerializer, GroupSerializer
from helpers.custom_pagination import Page50Pagination

"""
    List all users in the system. Only staff above can access.
"""
class UserList(generics.ListCreateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = Page50Pagination
    lookup_field = 'username'

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['^username', '@first_name', '@last_name']
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    ordering_fields = ['date_joined', 'id', 'username']
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
        
        query_params = self.request.query_params
        date_before = query_params.get('date_joined_before')
        date_after = query_params.get('date_joined_after')
        from helpers.timezone import datetime_from_z_timestring

        # TODO: same problem as `submission/views/SubmissionListView.get_queryset()`
        # We are filtering by second-precision, but submission with
        # subtime HH:mm:ss.001 which is greater than HH:mm:ss.000
        # would not be included in the queryset
        # A workaround is to add .999ms the datetimes, basically a way of "rounding"
        # But let's leave it out for now
        try:
            if date_before is not None:
                qs = qs.filter(date_joined__lte=datetime_from_z_timestring(date_before))
            if date_after is not None:
                qs = qs.filter(date_joined__gte=datetime_from_z_timestring(date_after))
        except ValueError:
            pass

        return qs

"""
    Act view for User model. Only staff above can call.
    We define Act view as a view that receives `act` payload.
    {
        "method": method_name,
        "data": {
            affected_object_class_1: [...],
            affected_object_class_2: [...],
        }
    }
    The purpose of this view is to optimize command/query that
    is applied on a list of objects.
"""
class ActOnUsersView(views.APIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'

    ACTION_DEACTIVATE = 'deactivate'
    ACTION_ACTIVATE = 'activate'
    ACTION_DELETE = 'delete'
    AVAILABLE_ACTIONS = [ACTION_DEACTIVATE, ACTION_ACTIVATE, ACTION_DELETE]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.all()
        if not user.has_perm('user.edit_all_users'):
            qs = qs.filter(is_superuser=False)
        return qs
    
    def post(self, request):
        qs = self.get_queryset()
        action = request.data.get('action')
        if action not in ActOnUsersView.AVAILABLE_ACTIONS:
            return Response({
                'message': f"Unrecognized action '{action}'",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.get('data', {})
        usernames = data.get('users', [])
        users = qs.filter(username__in=usernames)

        if action == ActOnUsersView.ACTION_ACTIVATE:
            with transaction.atomic():
                for user in users: user.is_active = True
                User.objects.bulk_update(users, ['is_active'])
        elif action == ActOnUsersView.ACTION_DEACTIVATE:
            with transaction.atomic():
                for user in users: user.is_active = False
                User.objects.bulk_update(users, ['is_active'])
        elif action == ActOnUsersView.ACTION_DELETE:
            users.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

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

"""
    Receives a CSV file (formdata, key=file) with format as 
    described (call OPTIONS for more info).
    Generate a list of users based on values described.
    Only staff above can call.
"""
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

"""
    Get a certain user, based on `username`.
    Only staff above can call.
    Only admin can make changes to that user.
"""
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'

    def get_queryset(self):
        qs = User.objects.all()

        user = self.request.user
        method = self.request.method
        if method == 'GET':
            if not user.is_superuser:
                qs = qs.filter(is_superuser=False)
        else:
            if not user.is_superuser:
                raise PermissionDenied()
        return qs

from django.shortcuts import get_object_or_404

"""
    Reset password view.
    Only user modifies their password.
    Otherwise only superuser may change.
"""
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

"""
    Get perms group. Unused.
"""
class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

"""
    Get certain perm group. Unused.
"""
class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

"""
    Get CSRF. Unused
"""
@ensure_csrf_cookie
def get_csrf(request):
    raise NotImplementedError
    # response = JsonResponse({'detail': 'CSRF cookie set'},
        # status=status.HTTP_200_OK)
    # response['X-CSRFToken'] = get_token(request)
    # return response
