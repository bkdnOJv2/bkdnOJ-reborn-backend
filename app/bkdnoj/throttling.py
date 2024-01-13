# pylint: skip-file
from rest_framework.throttling import UserRateThrottle

class BkdnojThrottling(UserRateThrottle):
    def allow_request(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return super().allow_request(request, view)
