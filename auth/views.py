from ast import IsNot
from os import access
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

from rest_framework_simplejwt.tokens import AccessToken
from usergroup.serializers import UserDetailSerializer

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


from helpers.permissions import IsNotAuthenticated
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsNotAuthenticated,)
    serializer_class = RegisterSerializer

class SignOutView(views.APIView):
    def get(self, request, format=None):
        # TODO: Invalidate token
        return Response(status=status.HTTP_204_NO_CONTENT);