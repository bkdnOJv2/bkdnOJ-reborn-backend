from rest_framework import generics, views
from judger.models import Judge, Language
from .serializers import JudgeSerializer, LanguageSerializer

class JudgeListView(generics.ListCreateAPIView):
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()

class JudgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()

class LanguageListView(generics.ListCreateAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()

class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()

class LanguageDetailKeyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    lookup_field = 'key'