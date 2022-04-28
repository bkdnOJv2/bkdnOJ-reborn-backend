from rest_framework import generics, views
from judger.models import Judge
from .serializers import JudgeSerializer

class JudgeListView(generics.ListCreateAPIView):
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()

class JudgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JudgeSerializer
    queryset = Judge.objects.all()