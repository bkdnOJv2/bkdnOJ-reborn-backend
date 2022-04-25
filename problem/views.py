from rest_framework import views, permissions, generics, viewsets

from .serializers import ProblemSerializer, ProblemTestDataProfileSerializer
from .models import Problem, ProblemTestDataProfile

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

class ProblemTestDataProfileListView(generics.ListCreateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer

class ProblemTestDataProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProblemTestDataProfile.objects.all()
    serializer_class = ProblemTestDataProfileSerializer
    lookup_field = 'problem'