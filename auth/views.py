from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
User = get_user_model()

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
from rest_framework import permissions, generics, filters

from .serializers import UserSerializer, UserDetailSerializer, GroupSerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-id']

import io, csv

file_format = {
    'user_attributes': {
        'username': {
            'required': True,
        },
        'password': {
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
    
    if request.method == 'OPTIONS':
        return Response(file_format, status=status.HTTP_200_OK)
    else:
        if request.FILES.get('file') == None:
            return badreq({"detail": "No file named 'file' attached."})
        
        line_no = 0
        file = request.FILES['file'].read().decode(file_format['config']['encoding'])
        reader = csv.DictReader(io.StringIO(file))

        many_data = [line for line in reader]

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
            return badreq({"detail": "Cannot create some users. Their password is too weak or username/email already taken."})
        ser.save()

        for data in many_data:
            data.pop('password_confirm', None)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=many_data[0].keys())
        writer.writeheader()
        writer.writerows(many_data)
        return Response(output.getvalue(), status=status.HTTP_201_CREATED)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'},
        status=status.HTTP_200_OK)
    response['X-CSRFToken'] = get_token(request)
    return response
