from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission

class AuthenticatedForbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You need to logout to perform this action"

class IsNotAuthenticated(BasePermission):
    """
    Allows access only to non authenticated users.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            raise AuthenticatedForbidden
        return True