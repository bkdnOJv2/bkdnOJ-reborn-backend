from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Case, Count, F, FloatField, IntegerField, Max, Min, Q, Sum, Value, When
from django.db import IntegrityError
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError
from django.core.cache import cache

import django_filters

from rest_framework import views, permissions, generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.serializers import DateTimeField
from rest_framework.serializers import Serializer

from operator import attrgetter, itemgetter
from organization.models import Organization
from organization.serializers import OrganizationBasicSerializer

from problem.serializers import ProblemSerializer
from userprofile.models import UserProfile as Profile

from compete.serializers import *
from compete.models import Contest, ContestProblem, ContestSubmission, ContestParticipation, Rating
from compete.ratings import rate_contest
from compete.exceptions import *
from compete.tasks import recompute_standing

from helpers.custom_pagination import Page100Pagination, Page10Pagination

import logging
logger = logging.getLogger(__name__)

__all__ = [
    ## Guests
    'contest_participate_view', 

    ## Participants
    'ContestProblemSubmitView', 
    'contest_leave_view', 

    ## Contest Admin
    'ContestRecomputeStandingView',
    'ContestProblemRejudgeView',
    'contest_participation_add_many',
]

from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, SubmissionBasicSerializer

class ContestProblemSubmitView(generics.CreateAPIView):
    """
        Submit to Problem in Contest
    """
    queryset = Problem.objects.none()
    serializer_class = SubmissionSubmitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not contest.is_in_contest(user):
            raise ContestNotRegistered

        if contest.is_testable_by(user):
            return contest

        if contest.ended:
            raise ContestEnded

        if not contest.started:
            raise ContestNotStarted

        return contest

    def create(self, request, *args, **kwargs):
        profile = request.user.profile
        contest = self.get_contest() # Accesibility checks

        participation = contest.users.filter(user=profile).last()
        if participation == None or participation.ended:
            return Response({
                'detail': "You are not registered."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Compulsory spam checks
        if (
            not self.request.user.has_perm('submission.spam_submission')
            and Submission
                .objects.filter(user=self.request.user.profile, rejudged_date__isnull=True)
                .exclude(status__in=['D', 'IE', 'CE', 'AB']).count() >= settings.BKDNOJ_SUBMISSION_LIMIT
        ):
            return Response({
                'error': _('You have reached maximum pending submissions allowed. '
                            'Please wait until your previous submissions finish grading.')
                }, status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Constructing ContestSubmission object
        problem = get_object_or_404(contest.problems, shortname=self.kwargs['shortname'])

        data = request.data.copy()
        sub = SubmissionSubmitSerializer(data=request.data)
        if not sub.is_valid():
            return Response(sub.errors, status=status.HTTP_400_BAD_REQUEST)

        sub_obj = sub.save(problem=problem, user=request.user.profile, contest_object=contest)
        sub_obj.judge()
        consub = ContestSubmission(
                submission=sub_obj,
                problem=contest.contest_problems.get(problem=problem),
                participation=participation,
                # is_pretest=contest. # TODO: is_pretest
        )
        consub.save()

        return Response(
            SubmissionBasicSerializer(sub_obj, context={'request':request}).data,
            status=status.HTTP_200_OK,
        )

from judger.tasks.submission import rejudge_problem_filter, apply_submission_filter

class ContestProblemRejudgeView(views.APIView):
    """
        Rejudge submissions of a Problem within Contest
    """
    queryset = Submission.objects.none()
    serializer_class = SubmissionBasicSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not contest.is_testable_by(user):
            raise PermissionDenied
        return contest

    def get_sub_id_range(self, request):
        data = request.data
        if data == {}:
            data = request.GET
        if data.get('use_range', 'off') == 'on':
            try:
                start = int(data.get('start'))
                end = int(data.get('end'))
                return (start, end)
            except (KeyError, ValueError, TypeError):
                pass
        return None

    def get(self, request, key, shortname):
        contest = self.get_contest()
        cproblem = get_object_or_404(contest.contest_problems, problem__shortname=shortname)
        problem = cproblem.problem
        queryset = Submission.objects.filter(contest__in=cproblem.submissions.all())
        if not queryset.exists():
            return Response({
                'detail': 'There are no submission to rejudge.'
            }, status=status.HTTP_400_BAD_REQUEST)

        id_range = self.get_sub_id_range(request)
        if id_range is None:
            id_range = (queryset.last().id, queryset.first().id)

        queryset = apply_submission_filter(queryset, id_range, None, None)
        ##
        cnt = queryset.count()
        return Response({
            'count': cnt,
            'msg': f"This will rejudge {cnt} submission(s).",
        })

    def post(self, request, key, shortname):
        contest = self.get_contest()
        cproblem = get_object_or_404(contest.contest_problems, problem__shortname=shortname)
        problem = cproblem.problem
        queryset = Submission.objects.filter(contest__in=cproblem.submissions.all())
        if not queryset.exists():
            return Response({
                'detail': 'There are no submission to rejudge.'
            }, status=status.HTTP_400_BAD_REQUEST)

        id_range = self.get_sub_id_range(request)
        if id_range is None:
            id_range = (queryset.last().id, queryset.first().id)

        queryset = apply_submission_filter(queryset, id_range, None, None)

        ## ---
        async_status = rejudge_problem_filter.delay(
            problem.id, id_range, user_id=request.user.id)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

class ContestRecomputeStandingView(views.APIView):
    """
        Rejudge submissions of a Problem within Contest
    """
    queryset = Contest.objects.none()
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not contest.is_testable_by(user):
            raise PermissionDenied
        return contest
    
    def post(self, request, key):
        contest = self.get_contest()
        contest.recompute_standing()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


from compete.utils import key_contest_registered_ids


@api_view(['POST'])
def contest_participate_view(request, key):
    def not_found():
        return Response({ 'detail': _("Contest not found.")},
            status=status.HTTP_404_NOT_FOUND)
    def banned():
        return Response({
            'detail': _("You have been banned from joining this contest.")},
            status=status.HTTP_403_FORBIDDEN)
    def not_authorized():
        return Response({
            'detail': _("You are banned or don't have permissions to register to this contest.")},
            status=status.HTTP_401_UNAUTHORIZED)

    # TODO: access code
    user = request.user
    contest = get_object_or_404(Contest, key=key)

    if not contest.is_registerable_by(user):
        return not_authorized()

    # user should be authenticated now
    profile = user.profile

    # if (not profile.current_contest == None):
    #     if profile.current_contest.contest != contest:
    #         return Response({ 'detail': _("You are currently in another contest."),
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #     if profile.current_contest.contest != contest:
    #         return Response({ 'detail': _("You are already in this contest."),
    #             }, status=status.HTTP_400_BAD_REQUEST)

    if contest.ended:
        return Response({
            'detail': _("Contest has ended.")},
            status=status.HTTP_400_BAD_REQUEST)

        ## Virtual Participation feature
        # if not contest.is_testable_by(user):
        #     return Response({
        #         'detail': _("Contest has ended.")},
        #         status=status.HTTP_400_BAD_REQUEST)
        # while True:
        #     virtual_id = max((ContestParticipation.objects.filter(contest=contest, user=profile)
        #                         .aggregate(virtual_id=Max('virtual'))['virtual_id'] or 0) + 1, 1)
        #     try:
        #         participation = ContestParticipation.objects.create(
        #             contest=contest, user=profile, virtual=virtual_id,
        #             real_start=timezone.now(),
        #         )
        #     # There is obviously a race condition here, so we keep trying until we win the race.
        #     except IntegrityError:
        #         pass
        #     else:
        #         break
    else:
        SPECTATE = ContestParticipation.SPECTATE
        LIVE = ContestParticipation.LIVE
        try:
            participation = ContestParticipation.objects.get(
                contest=contest, user=profile,
                virtual=(SPECTATE if contest.is_testable_by(user) else LIVE),
            )
        except ContestParticipation.DoesNotExist:
            participation = ContestParticipation.objects.create(
                contest=contest, user=profile,
                virtual=(SPECTATE if contest.is_testable_by(user) else LIVE),
                real_start=timezone.now(),
            )
        else:
            if participation.ended:
                participation = ContestParticipation.objects.get_or_create(
                    contest=contest, user=profile, virtual=SPECTATE,
                    defaults={'real_start': timezone.now()},
                )[0]

    profile.current_contest = participation
    profile.save()
    contest._updating_stats_only = True
    contest.update_user_count()

    cache.delete_many([ 
        contest.participants_cache_key,
        key_contest_registered_ids(contest)
    ])

    return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def contest_leave_view(request, key):
    user = request.user
    if not user.is_authenticated:
        return Response({'detail': "Not logged in."},
            status=status.HTTP_400_BAD_REQUEST)

    # TODO: get visible contests
    # contests = Contest.get_visible_contests(user).filter(key=key) ## TOO SLOW
    # contest = contests[0]
    contest = get_object_or_404(Contest, key=key)
    profile = user.profile
    if profile.current_contest is None or profile.current_contest.contest_id != contest.id:
        return Response({'detail': f"Contest not exists/Not in this contest."},
            status=status.HTTP_400_BAD_REQUEST) ## Prevent user from guessing the existing of contest

    profile.remove_contest()
    return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def contest_participation_add_many(request, key):
    contest = get_object_or_404(Contest, key=key)
    if not contest.is_editable_by(request.user):
        raise PermissionDenied()

    data = request.data
    try:
        part_type = data['participation_type']
        if part_type not in ['LIVE', 'SPECTATE']:
            raise ValueError(f"'participation_type' is unrecognizable ({part_type})")
        if part_type == 'LIVE': part_type = 0
        elif part_type == 'SPECTATE': part_type = -1

        to_be_updated = []

        users = set(data['users'])
        p = Profile.objects.select_related('user').filter(user__username__in=users)
        if p.count() != len(users):
            notfound = [uname for uname in users
                        if uname not in set(p.values_list('user__username', flat=True))]
            return Response({
                'general': f"Cannot find some users.",
                'detail': {'username': f"Users not found: {', '.join(notfound)}"}
            }, status.HTTP_400_BAD_REQUEST)

        for profile in p:
            cp, _ = ContestParticipation.objects.get_or_create(
                user=profile, contest=contest, virtual__in=[0, -1]
            )
            # If the participation has different virtual, set them to be updated
            if cp.virtual != part_type:
                cp.virtual = part_type
                to_be_updated.append(cp)

        ContestParticipation.objects.bulk_update(to_be_updated, ['virtual'])
        contest._updating_stats_only = True
        contest.update_user_count()
        contest.save()

        ## Delete participants cache
        cache.delete(contest.participants_cache_key)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    except KeyError as ke:
        return Response({ 'detail': f"Expecting '{ke.args[0]}' in request data"
        }, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as ve:
        return Response({ 'detail': str(ve),
        }, status=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #     print(e)
    #     return Response({ 'detail': "Something went wrong and we didn't expect it!"
    #     }, status=status.HTTP_400_BAD_REQUEST)
