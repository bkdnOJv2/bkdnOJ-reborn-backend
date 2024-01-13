# pylint: skip-file
from django.core.exceptions import PermissionDenied
from rest_framework import generics, views, permissions
from judger.models import Judge, Language
from .serializers import *

class JudgeListView(generics.ListCreateAPIView):
    serializer_class = JudgeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('judge.see_all_judges'):
            queryset = Judge.objects.all()
        else:
            queryset = Judge.objects.filter(online=True, is_blocked=False)
        return queryset

class JudgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JudgeDetailSerializer
    queryset = Judge.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied
        return super().get_object()


class LanguageListView(generics.ListCreateAPIView):
    serializer_class = LanguageBasicSerializer
    queryset = Language.objects.all()

class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        method = self.request.method
        user = self.request.user
        if method == 'GET':
            pass
        else:
            if not user.is_superuser:
                raise PermissionDenied
        return super().get_object()

class LanguageDetailKeyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageBasicSerializer
    queryset = Language.objects.all()
    lookup_field = 'key'
    permission_classes = [permissions.IsAdminUser]
