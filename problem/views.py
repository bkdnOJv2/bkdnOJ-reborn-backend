from rest_framework import views, permissions, generics, viewsets

from .serializers import ProblemSerializer, ProblemTestDataProfileSerializer
from .models import Problem, ProblemTestDataProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer

import logging
logger = logging.getLogger(__name__)

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

class ProblemSubmitView(generics.UpdateAPIView):
    queryset = Problem.objects.all()
    serializer_class = SubmissionSubmitSerializer
    lookup_field = 'shortname'
    permission_classes = []
    
    def create(request, *args, **kwargs):
        prob = self.get_object()
        logger.debug("Submitting to problem %s", prob.shortname)

        sub = SubmissionSubmitSerializer(data=request.data)
        logger.debug('Request data: %s', json.dumps(request.data))

class ProblemTestDataProfileListView(generics.ListCreateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer

class ProblemTestDataProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer
    lookup_field = 'problem'