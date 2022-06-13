from django.utils.timezone import make_aware
from django.db import connection

def from_database_time(datetime):
    # https://docs.djangoproject.com/en/4.0/topics/i18n/timezones/
    # with Postgresql Django obtains correct datetimes in
    # all cases. You don’t need to perform any data conversions.
    return datetime

    # tz = connection.timezone
    # if tz is None:
    #     return datetime
    # return make_aware(datetime, tz)
