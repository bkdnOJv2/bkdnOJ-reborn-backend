# pylint: skip-file
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from organization.models import Organization
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileBasicSerializer

class UserProfileDetail(generics.RetrieveUpdateAPIView):
    """
        Return requested User Profile
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    lookup_field = 'username'

    def get_object(self):
        request = self.request
        user = request.user
        method = request.method
        if method == 'GET' or user.is_superuser:
            return get_object_or_404(self.get_queryset(), user__username=self.kwargs.get('username'))
        raise PermissionDenied()
        
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs,)
    
    def put(self, *args, **kwargs):
        return self.patch(*args, **kwargs)
    
    def patch(self, request, username):
        # profile = self.get_object()

        # if 'organization' in request.data:
        #     org_slug = request.data.get('organization')
        #     org = Organization.objects.filter(slug=org_slug)
        #     if not org.exists(): 
        #         return Response({
        #             'message': f"Not found org(slug={org_slug})"
        #         }, status=status.HTTP_400_BAD_REQUEST)
        #     org = org.first()
        #     profile.display_organization = org
        #     profile.save()

        return super().patch(request, username)

class SelfProfileDetail(generics.RetrieveUpdateAPIView):
    """
        Return user's User Profile, logged-in is required
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def serialize(self, request, data):
        ser_context = { 'request': request, }
        return self.serializer_class(data, context=ser_context)

    def get_object(self, pk):
        if not self.request.user.is_authenticated:
            raise Http404
        return self.request.user.profile

    def get(self, request, *args, **kwargs):
        profile = self.get_object(None)
        return Response(self.serialize(request, profile).data)

    def put(self, request, *args, **kwargs):
        profile = self.get_object(None)
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(self.serialize(request, profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object(None)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(self.serialize(request, profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object(None)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@api_view(['POST'])
def change_password(request):
    user = request.user
    if not user.is_authenticated:
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

    try:
        validate_password(pw)
    except ValidationError as errors:
        return Response({
            'errors': errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(pw)
    user.save()
    return Response({}, status=status.HTTP_204_NO_CONTENT)
