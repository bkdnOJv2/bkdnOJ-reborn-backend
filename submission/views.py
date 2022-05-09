from django.shortcuts import render
from rest_framework import views, generics, status
from rest_framework.response import Response

from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from .models import Submission

class SubmissionListView(generics.ListAPIView):
    """
        Return a list of all submissions on the system
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = []

class SubmissionDetailView(generics.RetrieveUpdateAPIView):
    """
        Return a detailed view of a certain submission
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailSerializer
    permission_classes = []
