from rest_framework import generics, permissions
from ..models import ProblemTag
from ..serializers import ProblemTagSerializer, ProblemTagDetailsSerializer
from helpers.custom_pagination import PageBillionPagination


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
            raise permissions.PermissionDenied("You do not have permission")
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
            raise permissions.PermissionDenied("You do not have permission")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise permissions.PermissionDenied("You do not have permission")
        return super().destroy(request, *args, **kwargs)
