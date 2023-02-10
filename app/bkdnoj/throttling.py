"""
    Throttling policies for bkdnoj
"""

from rest_framework.throttling import UserRateThrottle


class BkdnojThrottling(UserRateThrottle):
    """
        Throttling policy
        Don't throttle req from staff, superusers
        Otherwise, use default
    """

    def allow_request(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return super().allow_request(request, view)
