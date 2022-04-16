from django.shortcuts import render
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from django.http import Http404

from .models import UserProfile
from .serializers import UserProfileSerializer

# Create your views here.
class UserProfileDetail(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print('ARGS:', args)
        print('KWARGS', kwargs)
        return self.retrieve(request, *args, **kwargs,)

class SelfProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        profile = self.get_object(request.user.id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        profile = self.get_object(request.user.id)
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object(request.user.id)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
