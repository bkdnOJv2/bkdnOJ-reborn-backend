from django.utils.translation import gettext as _
from rest_framework import views, permissions, generics, viewsets, response, status

from problem.serializers import ProblemBriefSerializer, ProblemSerializer, \
    ProblemTestProfileSerializer
from problem.models import Problem, ProblemTestProfile

from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, \
    SubmissionURLSerializer

import logging
logger = logging.getLogger(__name__)

# Create your views here.
class ProblemListView(generics.ListCreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemBriefSerializer
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
        if (
            not self.request.user.has_perm('judge.spam_submission') and
            Submission.objects.filter(user=self.request.user.profile, rejudged_date__isnull=True)
                              .exclude(status__in=['D', 'IE', 'CE', 'AB']).count() >= settings.BKDNOJ_SUBMISSION_LIMIT
        ):
            return response.Response(
                _('You have reached maximum pending submissions allowed. Please wait until your submissions is graded.'),
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        prob = self.get_object()

        sub = SubmissionSubmitSerializer(data=request.data)
        if not sub.is_valid():
            return response.Response(sub.errors, status=status.HTTP_400_BAD_REQUEST)
        
        sub_obj = sub.save(problem=prob, user=request.user.profile)
        return response.Response(
            SubmissionURLSerializer(sub_obj, context={'request':request}).data,
            status=status.HTTP_200_OK,
        )
