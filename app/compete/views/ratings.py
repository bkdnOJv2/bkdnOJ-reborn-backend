# pylint: skip-file
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Case, Count, F, FloatField, IntegerField, Max, Min, Q, Sum, Value, When
from django.db import connection, transaction, IntegrityError
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError

from rest_framework import views, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.serializers import DateTimeField, Serializer

from userprofile.models import UserProfile as Profile
from compete.serializers import *
from compete.models import *
from compete.exceptions import *
from compete.ratings import rate_contest

__all__ = [
  'get_ranks_view',
  'ContestRateView', 'RateAllView',
  'RatingListView', 'RatingDetailView',
  'ContestRatingListView',
  'ProfileRatingListView',
]

from compete.ratings import RATING_VALUES, RATING_LEVELS, RATING_CLASS
_values = [0] + RATING_VALUES
RANKS = [ {'rank': RATING_LEVELS[i], 'rating_floor': _values[i], 'rank_class': RATING_CLASS[i] }
            for i in range(len(RATING_LEVELS)) ]

@api_view(['GET'])
def get_ranks_view(request):
    return Response(RANKS)


class RateAllView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE `%s`' % Rating._meta.db_table)
            Profile.objects.update(rating=None)
            for contest in Contest.objects.filter(is_rated=True, end_time__lte=timezone.now()).order_by('end_time'):
                rate_contest(contest)


class ContestRateView(generics.RetrieveAPIView):
    """
        View for rating contest
    """
    serializer_class = Serializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        contest = get_object_or_404(Contest, key=self.kwargs.get('key'))
        user = self.request.user
        if not contest.is_editable_by(user):
            raise PermissionDenied
        return contest

    def check_rateable(self, request, contest):
        if not contest.is_rated:
            raise ContestNotRated
        if not contest.ended:
            raise ContestNotFinished
        return True

    def get(self, request, key):
        contest = self.get_object()
        self.check_rateable(request, contest)
        if Rating.objects.filter(contest=contest).exists():
            return Response({ 'msg': 'This contest has been rated. You can re-rate it if you want.' })
        return Response({ 'msg': 'This contest has not been rated yet.'  })

    def post(self, request, key):
        contest = self.get_object()
        self.check_rateable(request, contest)

        try:
            contest.rate()
            contest.clear_cache()
        except Exception:
            raise
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class RatingListView(generics.ListAPIView):
    """
        Rating List view
    """
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()
    permission_classes = [permissions.IsAdminUser]


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Rating Detail view
    """
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()
    permission_classes = [permissions.IsAdminUser]


class ContestRatingListView(generics.ListAPIView):
    """
      List of all Ratings objects from that contest
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAdminUser]

    @cached_property
    def contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise ContestNotAccessible
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise ContestNotStarted
        return contest

    def get_queryset(self):
        contest = self.contest
        return contest.ratings.all()


class ProfileRatingListView(generics.ListAPIView):
    """
      List of all Ratings objects from an User
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAdminUser]

    @cached_property
    def profile(self):
        profile = get_object_or_404(Profile, user__username=self.kwargs['username'])
        return profile

    def get_queryset(self):
        profile = self.profile
        return profile.ratings.all()
