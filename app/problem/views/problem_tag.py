# pylint: skip-file
from rest_framework import views, permissions, generics, status, filters
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from helpers.custom_pagination import PageBillionPagination

from ..models import ProblemTag, Problem
from ..serializers import ProblemTagSerializer, ProblemTagDetailsSerializer


class ProblemTagListView(generics.ListCreateAPIView):
    """
    List view for Problem Tags.
    Anyone can list problem tags available in the system.
    Only SUPERUSER/ADMIN can create them.
    """

    queryset = ProblemTag.objects.order_by('id').all()
    serializer_class = ProblemTagSerializer
    pagination_class = PageBillionPagination

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().create(request, *args, **kwargs)


class ProblemTagDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Details view for Problem Tags.
    Anyone can view problem tag in details.
    Only SUPERUSER/ADMIN can update and delete them.
    """

    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagDetailsSerializer

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().destroy(request, *args, **kwargs)

class ProblemTriggerTaggingView(views.APIView):
    """
        Problem Trigger Tagging vieew
        Manually trigger a problem tagging 
    """
    queryset = Problem.objects.none()
    permission_classes = [permissions.IsAdminUser]

    def get_problem(self):
        problem = get_object_or_404(Problem, shortname=self.kwargs['shortname'])
        user = self.request.user
        if not problem.is_editable_by(user):
            raise PermissionDenied
        return problem
    
    def post(self, request, shortname):
        problem = self.get_problem()
        problem.auto_tagging()
        return Response({}, status=status.HTTP_204_NO_CONTENT)