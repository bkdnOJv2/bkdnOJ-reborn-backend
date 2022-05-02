from django.shortcuts import render
from rest_framework import views, generics, status
from rest_framework.response import Response

from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Submission

class SubmissionListView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = []

class SubmissionDetailView(generics.RetrieveUpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailSerializer
    permission_classes = []
