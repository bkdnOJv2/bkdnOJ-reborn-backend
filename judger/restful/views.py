from rest_framework import generics, views, permissions
from judger.models import Judge, Language
from .serializers import JudgeSerializer, LanguageSerializer,\
    JudgeBasicSerializer, LanguageBasicSerializer

class JudgeListView(generics.ListCreateAPIView):
    serializer_class = JudgeBasicSerializer
    queryset = Judge.objects.all()

class JudgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()
    permission_classes = [permissions.IsAdminUser]

class LanguageListView(generics.ListCreateAPIView):
    serializer_class = LanguageBasicSerializer
    queryset = Language.objects.all()

class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    permission_classes = [permissions.IsAdminUser]

class LanguageDetailKeyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageBasicSerializer
    queryset = Language.objects.all()
    lookup_field = 'key'
