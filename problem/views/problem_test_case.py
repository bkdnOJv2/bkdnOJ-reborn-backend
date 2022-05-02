from rest_framework import generics, views, response, status

from problem.models import TestCase, ProblemTestProfile, Problem
from problem.serializers import TestCaseSerializer

import logging
logger = logging.getLogger(__name__)

class TestCaseListView(generics.ListCreateAPIView):
    serializer_class = TestCaseSerializer
    
    def get_queryset(self):
        problem = self.kwargs['problem']
        queryset = TestCase.objects.filter(test_profile__problem=problem)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            problem = Problem.objects.get(shortname=self.kwargs['problem'])
        except Problem.DoesNotExist:
            return response.Response('Cannot find such problem.', 
                status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()

        data['test_profile'] = problem.test_profile
        order = data.pop('order', None)
        if order == ['']:
            order = problem.test_profile.cases.count()
        else:
            order = order[0]
        data['order'] = order
        
        serializer = TestCaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
            status=status.HTTP_201_CREATED,
        )

class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TestCaseSerializer
    queryset = TestCase.objects.all()