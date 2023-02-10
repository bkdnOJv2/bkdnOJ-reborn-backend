"""
    Views for auth module
"""

from django.contrib.auth.models import Group
from rest_framework import permissions, generics

from ..serializers import GroupSerializer

__all__ = [
    'GroupList', 'GroupDetail'
]

class GroupList(generics.ListCreateAPIView):
    """
        Get perms group. Unused.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
        Get certain perm group. Unused.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]
