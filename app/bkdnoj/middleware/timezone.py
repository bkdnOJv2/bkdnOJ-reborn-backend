import pytz
from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def get_timezone(self, request):
        tzname = settings.DEFAULT_USER_TIME_ZONE
        if request.profile:
            tzname = request.profile.timezone
        return pytz.timezone(tzname)

    def __call__(self, request):
        with timezone.override(self.get_timezone(request)):
            return self.get_response(request)
