from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

__all__ = [
    'ContestNotAccessible',
    'ContestNotStarted',
    'ContestNotFinished',
    'ContestEnded',
    'ContestNotRated',
    'ContestNotRegistered',
]

class ContestNotAccessible(APIException):
    status_code = 400
    default_detail = _("Contest is not accessible")
    default_code = 'contest_not_accessible'

class ContestNotStarted(APIException):
    status_code = 400
    default_detail = _("Contest is not started yet.")
    default_code = 'contest_not_started'

class ContestNotFinished(APIException):
    status_code = 400
    default_detail = _("Contest is not finished yet.")
    default_code = 'contest_not_finished'

class ContestEnded(APIException):
    status_code = 400
    default_detail = _("Contest has ended.")
    default_code = 'contest_ended'

class ContestNotRegistered(APIException):
    status_code = 400
    default_detail = _("You are not registered to this contest.")
    default_code = 'contest_not_registered'


class ContestNotRated(APIException):
    status_code = 400
    default_detail = _("Contest is Unrated.")
    default_code = 'contest_not_rated'
