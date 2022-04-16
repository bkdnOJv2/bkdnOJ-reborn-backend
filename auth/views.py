from ast import IsNot
from django.contrib.auth import get_user_model
User = get_user_model()

from .serializers import RegisterSerializer
from rest_framework import generics

from helpers.permissions import IsNotAuthenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsNotAuthenticated,)
    serializer_class = RegisterSerializer