from django.utils.timezone import make_aware
from django.db import connection

def from_database_time(datetime):
    tz = connection.timezone
    if tz is None:
        return datetime
    return make_aware(datetime, tz)