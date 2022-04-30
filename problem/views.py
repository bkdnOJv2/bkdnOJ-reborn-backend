from rest_framework import views, permissions, generics, viewsets, response, status

from .serializers import ProblemSerializer, ProblemTestDataProfileSerializer
from .models import Problem, ProblemTestDataProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
    SubmissionURLSerializer

import logging
logger = logging.getLogger(__name__)

import json

# Create your views here.
class ProblemListView(generics.ListCreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = []

class ProblemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer #ProblemDetailSerializer
    permission_classes = []
    lookup_field = 'shortname'

class ProblemSubmitView(generics.CreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = SubmissionSubmitSerializer
    lookup_field = 'shortname'
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        prob = self.get_object()

        sub = SubmissionSubmitSerializer(data=request.data)
        if not sub.is_valid():
            return response.Response(sub.errors, status=status.HTTP_400_BAD_REQUEST)
        sub_obj = sub.save(problem=prob, user=request.user.profile)

        return response.Response(
            SubmissionURLSerializer(sub_obj, context={'request':request}).data,
            status=status.HTTP_200_OK
        )

class ProblemTestDataProfileListView(generics.ListCreateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer

class ProblemTestDataProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer
    lookup_field = 'problem'