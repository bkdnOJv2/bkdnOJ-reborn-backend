# pylint: skip-file
from django.utils.timezone import make_aware
from django.db import connection

from datetime import datetime
from dateutil import tz

def from_database_time(datetime):
    # https://docs.djangoproject.com/en/4.0/topics/i18n/timezones/
    # with Postgresql Django obtains correct datetimes in
    # all cases. You don’t need to perform any data conversions.
    return datetime

    # tz = connection.timezone
    # if tz is None:
    #     return datetime
    # return make_aware(datetime, tz)

"""
    Convert a military timestring (UTC+00:00) to datetime object
    eg: '2022-08-19T09:15:00.000Z' -> ...
"""
def datetime_from_z_timestring(timestr: str) -> datetime:
    timezone = tz.gettz('UTC+00:00')
    utc = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc = utc.replace(tzinfo=timezone)
    return utc
