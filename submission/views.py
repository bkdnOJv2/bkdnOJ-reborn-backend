from django.shortcuts import render
from rest_framework import views, generics

from .serializers import SubmissionSerializer
from .models import Submission

class SubmissionListView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = []
