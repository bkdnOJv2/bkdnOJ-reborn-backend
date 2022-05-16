from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import views, generics, status
from rest_framework.response import Response

from .serializers import SubmissionSerializer, SubmissionTestCaseSerializer, \
    SubmissionDetailSerializer, SubmissionResultSerializer
from .models import Submission, SubmissionTestCase

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

class SubmissionResultView(views.APIView):
    """
        Return a list of test case results for that submission
    """
    permission_classes = []

    def get_queryset(self):
        return SubmissionDetailTestCase.objects.filter(
            submission=self.kwargs['pk'])
    
    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        serial = SubmissionResultSerializer(submission)
        return Response(serial.data, status=status.HTTP_200_OK)

class SubmissionResultTestCaseView(views.APIView):
    """
        Return a specific case with number `case_num`
        that belongs to submission `pk`
    """
    queryset = SubmissionTestCase.objects.none()
    serializer_class = SubmissionTestCaseSerializer
    permission_classes = []
    
    def get(self, request, pk, case_num):
        Qfilter = Q(submission=pk) & Q(case=case_num)
        inst = get_object_or_404(SubmissionTestCase, Qfilter)
        serial = SubmissionTestCaseSerializer(inst)
        return Response(serial.data, status=status.HTTP_200_OK)
