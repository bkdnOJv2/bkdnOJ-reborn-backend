from functools import lru_cache

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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

from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSubmitSerializer, SubmissionBasicSerializer

from userprofile.models import UserProfile as Profile
from userprofile.serializers import UserProfileBasicSerializer as ProfileSerializer

from helpers.custom_pagination import Page100Pagination, Page50Pagination, Page10Pagination

import logging
logger = logging.getLogger(__name__)

__all__ = [
    ### Contest info
    'ContestDetailView',

    # Problems within Contest
    'ContestProblemListView', 'ContestProblemDetailView',

    ### Submissions within Contest
    'ContestSubmissionListView',

    'ContestProblemSubmissionListView', 'ContestProblemSubmissionDetailView',

    ### Participants within Contest
    'ContestParticipationListView', 'ContestParticipationDetailView',
    'ContestParticipationActView',
    'ContestParticipantListView',
]

class ContestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Contest.objects.none()
    lookup_field = 'key'
    permission_classes = []

    @lru_cache
    def get_object(self):
        user = self.request.user

        try:
            if user.is_staff:
                contest = Contest.objects.prefetch_related(
                    'authors', 'authors__user',
                    'collaborators', 'collaborators__user',
                    'reviewers', 'reviewers__user',
                    'private_contestants', 'private_contestants__user',
                    'banned_users', 'banned_users__user',
                    'view_contest_scoreboard', 'view_contest_scoreboard__user',
                    'rate_exclude', 'rate_exclude__user',
                    'contest_problems', 'contest_problems__problem',
                    'organizations',
                    'tags',
                ).get(key=self.kwargs['key'])
            else:
                contest = Contest.objects.prefetch_related(
                    'authors', 'authors__user',
                    'organizations',
                    'tags',
                ).get(key=self.kwargs['key'])
        except Contest.DoesNotExist:
            raise Http404()

        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            # if not contest.started:
            #     raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    def get_serializer_class(self):
        user = self.request.user
        contest = self.get_object()
        if contest.is_editable_by(user):
            return ContestDetailAdminSerializer
        return ContestDetailUserSerializer
    
    def get(self, request, key):
        if request.query_params.get('description'):
            contest = self.get_object()
            updated_recently = False
            if (timezone.now() - contest.modified).total_seconds() < 3*60:
                updated_recently = True
            if updated_recently:
                return Response({
                    "updated_recently": updated_recently,
                    "description": contest.description,
                }, status=status.HTTP_200_OK)
            return Response({
                "updated_recently": False,
            }, status=status.HTTP_200_OK)
        else:
            return super().get(request, key)

    def put(self, *args, **kwargs):
        return self.patch(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        contest = self.get_object()
        outdated_reasons = []
        before_updated = {}
        for field in Contest.STANDING_RELATED_FIELDS:
            before_updated[field] = getattr(contest, field, None)

        try:
            obj = super().patch(request, *args, **kwargs)
            contest.refresh_from_db()

            for field in Contest.STANDING_RELATED_FIELDS:
                if before_updated[field] != getattr(contest, field, None):
                    outdated_reasons.append(f"f '{field}' changed")
            if outdated_reasons:
                contest.append_standing_outdated_reason(outdated_reasons)

            return obj
        except ValidationError as e:
            return Response({
                'general': e,
            }, status=status.HTTP_400_BAD_REQUEST)


from problem.utils import user_completed_ids, user_attempted_ids
from compete.utils import contest_completed_ids, contest_attempted_ids

class ContestProblemListView(generics.ListCreateAPIView):
    """
        Problems within contests view
    """
    serializer_class = ContestProblemBriefSerializer
    pagination_class = Page100Pagination
    lookup_field = 'shortname'

    def get_serializer_context(self):
        user = self.request.user
        if not user.is_authenticated:
            return { 'request': self.request, }

        participation = self.participation

        # TODO: In the future, contest can be registered multiple times by one user
        # due to virtual participation. Every participation will have a new list of solved/unsolved problems.
        # But for now, one user can only register to one contest only, so
        if participation:# and not participation.ended:
            return {
                'request': self.request,
                'solved': contest_completed_ids(participation),
                'attempted': contest_attempted_ids(participation),
            }
        return { 'request': self.request, }

    def get_object(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    @cached_property
    def contest(self):
        return self.get_object()

    @cached_property
    def participation(self):
        user = self.request.user
        if not user.is_authenticated:
            return None
        contest = self.contest
        return contest.users.filter(user=user.profile).last()

    def get_queryset(self):
        contest = self.contest
        return contest.contest_problems.prefetch_related('problem').filter()

    NON_ASSOCIATE_FIELDS = ('order', 'points', 'partial',)# 'is_pretested', 'max_submissions')
    def create(self, request, *args, **kwargs):
        contest = self.contest
        cproblems = contest.contest_problems # Manager
        visproblems = Problem.get_visible_problems(request.user)

        outdated_reasons = []
        problem_edit_reason_added = False

        contest_problem_ids = set()
        for rowidx, problem_kw in enumerate(request.data):
            try:
                cpf = cproblems.filter(problem__shortname=problem_kw['shortname'])
                if cpf.exists():
                    cpf = cpf.first()
                else:
                    p = visproblems.get(shortname=problem_kw['shortname'])
                    cpf = ContestProblem(contest=contest, problem=p)
                for k, v in problem_kw.items():
                    if k in ContestProblemListView.NON_ASSOCIATE_FIELDS:
                        if getattr(cpf, k, None) != v:
                            if not problem_edit_reason_added :
                                outdated_reasons.append(f"{cpf} changed")
                                problem_edit_reason_added = True
                            setattr(cpf, k, v)
            except Problem.DoesNotExist:
                return Response({ 'detail': _(f"Row {rowidx}: Problem '{problem_kw['shortname']}' "
                                    "does not exist or you do not have permission to it.")},
                    status=status.HTTP_400_BAD_REQUEST)
            except KeyError as ke:
                return Response({ 'detail': _(f"Row {rowidx}: Expecting key='{ke.args[0]}'")},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                cpf.save()
            except Exception as excp:
                return Response({
                    'detail': _(f"Row {rowidx} has the following errors:"),
                    'errors': str(excp),
                }, status=status.HTTP_400_BAD_REQUEST)
            contest_problem_ids.add(cpf.id)

        to_be_deleted = cproblems.exclude(id__in=contest_problem_ids)
        if to_be_deleted.exists():
            outdated_reasons.append(f"Some Problems were deleted")
            to_be_deleted.delete()

        if outdated_reasons:
            contest.append_standing_outdated_reason(outdated_reasons)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ContestProblemDetailView(generics.RetrieveAPIView):
    """
        Certain Problem within Contest view
    """
    pagination_class = None

    def get_serializer_class(self):
        return ContestProblemSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    def get_object(self):
        p = get_object_or_404(ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname'])
        return p

    # def get(self, request, key, shortname):
    #     p = self.get_object()
    #     return Response(
    #         self.get_serializer_class()(p, context={'request': request}).data
    #     )


class ContestSubmissionListView(generics.ListAPIView):
    """
        All Submissions within contest view
    """
    serializer_class = ContestSubmissionSerializer
    pagination_class = Page10Pagination

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method

        if method == 'GET':
            if contest.is_testable_by(user):
                return contest
            if not contest.published:
                raise Http404()
            if not contest.started:
                raise ContestNotStarted()
            if not contest.is_accessible_by(user):
                raise ContestNotAccessible()
        else:
            if not contest.is_editable_by(user):
                raise PermissionDenied()
        return contest

    @cached_property
    def contest(self):
        return self.get_contest()

    def get_queryset(self):
        query_params = self.request.query_params
        contest = self.contest
        user = self.request.user

        cps = ContestProblem.objects.filter(contest=contest).all()
        css = ContestSubmission.objects.select_related(
                'participation',
                'participation__contest',
                'problem',
                'problem__contest',
                'problem__problem',
                'submission',
                'submission__user',
                'submission__user__user',
                'submission__problem',
                'submission__language',
                'submission__contest_object',

                # For some reasons, commenting this reduces some of the SQL queries (~99 -> ~30)
                # But it increase SQL time (60ms -> 90ms ??)
                # I guess it is better to have few SQL queries, as time can be affect by constants as well
            ).filter(problem__in=cps)

        ## Visible subs
        profile = None
        is_editor = False
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            is_editor = contest.is_editable_by(self.request.user)

        is_frozen = contest.is_frozen

        if is_editor:
            get_spectators_sub = not not query_params.get('spectators')
            if get_spectators_sub:
                css = css.filter(participation__virtual=ContestParticipation.SPECTATE)

            get_participants_sub = not not query_params.get('participants')
            if get_participants_sub:
                css = css.filter(participation__virtual=ContestParticipation.LIVE)
        else:
            get_spectators_sub = not not query_params.get('spectators')
            if get_spectators_sub:
                css = ContestSubmission.objects.none()
            else:
                css = css.filter(participation__virtual=ContestParticipation.LIVE)

        ## Query params
        if query_params.get('me'):
            if profile:
                css = css.filter(participation__user=profile)
        else:
            username = query_params.get('user')
            if username is not None:
                css = css.filter(participation__user__user__username=username)

        prob_shortname = query_params.get('problem')
        if prob_shortname is not None:
            css = css.filter(problem__problem__shortname=prob_shortname.upper())

        lang = query_params.get('language')
        if lang is not None:
            css = css.filter(submission__language__common_name=lang)

        ##
        verdict = query_params.get('verdict')
        order_by = query_params.get('order_by')
        order_dec = query_params.get('dec')
        should_hide_frozen_sub = (not is_editor) and is_frozen and (verdict or (order_by and (not order_by=='date')))

        if should_hide_frozen_sub:
            if profile:
                css = css.filter(
                    Q(submission__date__lt=contest.frozen_time) | Q(participation__user=profile)
                )
            else:
                css = css.filter(submission__date__lt=contest.frozen_time)

        if verdict is not None:
            if verdict in ['Q', 'IE', 'SC']:
                if user.is_staff:
                    if verdict == 'Q':
                        css = css.filter(submission__status__in=['QU', 'P', 'G'])
                    elif verdict == 'IE':
                        css = css.filter(submission__result__in=['IE', 'AB'])
                    elif verdict == 'SC':
                        css = css.filter(submission__result='SC')
                else:
                    css = Submission.objects.none()
            else:
                if verdict == 'RTE':
                    css = css.filter(submission__result__in=['RTE', 'IR'])
                else:
                    css = css.filter(submission__result=verdict)


        if order_by is not None:
            key = order_by

            if order_by in ['rejudged_date']:
                if not user.is_staff:
                    return Submission.objects.none()

            if order_by in ['time', 'memory', 'date', 'rejudged_date']:
                key = f"submission__{order_by}"

            if order_dec:
                key = '-'+key

            try:
                css = css.order_by(key)
            except:
                return ContestSubmission.objects.none()

        date_before = query_params.get('date_before')
        date_after = query_params.get('date_after')
        from helpers.timezone import datetime_from_z_timestring

        # @duplicate submission.views L101
        # We are filtering by second-precision, but submission with
        # subtime HH:mm:ss.001 which is greater than HH:mm:ss.000
        # would not be included in the queryset
        # A workaround is to add .999ms the datetimes, basically a way of "rounding"
        # But let's leave it out for now
        if date_before is not None:
            css = css.filter(submission__date__lte=datetime_from_z_timestring(date_before))
        if date_after is not None:
            css = css.filter(submission__date__gte=datetime_from_z_timestring(date_after))

        return css


    def get_serializer_context(self):
        should_freeze_result = self.contest.is_frozen
        # and not self.contest.can_see_full_scoreboard(request.user)
        context = {
            'request': self.request,
            'should_freeze_result': should_freeze_result,
        }
        return context

    def get(self, request, key):
        css = self.get_queryset()
        page = self.paginate_queryset(css)
        data = ContestSubmissionSerializer(page,
                context=self.get_serializer_context(), many=True).data
        return self.get_paginated_response(data)

    """
        Rejudge subs retrieved from `get_queryset()`.
        Staff above, or user with `submission.mass_rejduge` perm can request rejudge.
        But user must be able to edit the contest in order to mass rejudge (check via `get_contest()`)

        If the rejudge count is more than settings.BKDNOJ_REJUDGE_LIMIT, user need extra perm `submission.mass_rejudge_many`
    """
    def patch(self, request, key):
        user = request.user

        if (not user.is_staff) and (not user.has_perm('submission.mass_rejudge')):
            return Response({
                'message': _('You do not have permission to mass rejudge.')
            }, status=status.HTTP_403_FORBIDDEN)

        # get_queryset() checks if user can edit contest object
        qs = self.get_queryset()

        if qs.count() > settings.BKDNOJ_REJUDGE_LIMIT and not user.has_perm('submission.mass_rejudge_many'):
            return Response({
                'message': _(f"You need extra permission to request rejudge with more than {settings.BKDNOJ_REJUDGE_LIMIT} subs.")
            }, status=status.HTTP_403_FORBIDDEN)

        from submission.tasks import mass_rejudge
        async_status = mass_rejudge.delay(
            sub_ids=list(qs.values_list('submission__id', flat=True)),
            rejudge_user_id=user.id
        )
        return Response({}, status=status.HTTP_204_NO_CONTENT)

## NOTE: NOT TESTED
class ContestProblemSubmissionListView(generics.ListAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise ContestNotAccessible
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise ContestNotStarted
        return contest

    def get_queryset(self):
        raise NotImplementedError
        cp = get_object_or_404( ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname']
        )
        queryset = ContestSubmission.objects.filter(problem=cp)
        if not queryset.exists():
            raise Http404
        return queryset

## NOTE: NOT TESTED
class ContestProblemSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Certain Submission within Contest view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise ContestNotAccessible
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise ContestNotStarted
        return contest

    def get_queryset(self):
        raise NotImplementedError
        cp = get_object_or_404( ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname']
        )
        queryset = ContestSubmission.objects.filter(problem=cp)
        return queryset

    def get(self, *args, **kwargs):
        p = get_object_or_404(self.get_queryset(), id=self.kwargs['id'])
        ## TODO raise PermissionDenied see_detail
        return Response(
            ContestSubmissionSerializer(p).data,
            status=status.HTTP_200_OK,
        )


class ContestParticipationListView(generics.ListAPIView):
    """
        ADMIN ONLY:
        Participations List View for Contest `key`
    """
    serializer_class = ContestParticipationSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = Page100Pagination

    """
        Staff that has access to Contest can see list of Participations
    """
    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404()
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users
        request = self.request

        search = request.query_params.get('search')
        if search is not None:
            queryset = queryset.filter(user__user__username__startswith=search)

        virtual = self.request.query_params.get('virtual')
        if virtual is not None:
            if virtual == 'LIVE':
                queryset = queryset.filter(virtual=0)
            elif virtual == 'SPECTATE':
                queryset = queryset.filter(virtual=-1)
            elif virtual == 'VIRTUAL':
                queryset = queryset.filter(virtual__gt=0)
            else:
                queryset = ContestParticipation.objects.none()
        
        if 'organizations[]' in request.query_params:
            org_slugs = request.query_params.getlist('organizations[]')
            include_none = ('' in org_slugs)
            q = Q(organization__slug__in=org_slugs)
            if include_none: q |= Q(organization=None)

            queryset = queryset.filter(q)

        is_disqualified = self.request.query_params.get('is_disqualified')
        if is_disqualified is not None:
            queryset = queryset.filter(is_disqualified=is_disqualified)

        return queryset.select_related().all()

class ContestParticipationActView(views.APIView):
    """
        ADMIN ONLY:
        Participations Act View for Contest `key`
    """
    serializer_class = ContestParticipationSerializer
    permission_classes = [permissions.IsAdminUser]

    """
        Staff that has access to Contest execute actions to modify Participations
    """
    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404()
        return contest
    
    @cached_property
    def contest(self):
        return self.get_contest()

    def get_queryset(self):
        return self.contest.users.filter()
    
    ACTION_SET_ORGS = 'set-org'
    ACTION_DISQUALIFY = 'disqualify'
    ACTION_UNDISQUALIFY = 'undisqualify'
    ACTION_DELETE = 'delete'

    AVAILABLE_ACTIONS = [
        ACTION_SET_ORGS, ACTION_DISQUALIFY, ACTION_UNDISQUALIFY, ACTION_DELETE
    ]
    
    def post(self, request, key):
        act = request.data.get('action')
        data = request.data.get('data')
        if act not in ContestParticipationActView.AVAILABLE_ACTIONS:
            return Response({
                'message': "Invalid 'action' value",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        part_ids = data.get('participations', [])
        parts = self.get_queryset().filter(id__in=part_ids)
        if not parts.exists():
            return Response({
                'message': "Could not find some participations."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if act == ContestParticipationActView.ACTION_SET_ORGS:
            org_slug = data.get('organization', '').upper()
            org = Organization.objects.filter(slug=org_slug)
            if not org.exists():
                return Response({
                    'message': f"Could not find organization(slug={org_slug})."
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                org = org.first()
            parts.update(organization=org)
        elif act == ContestParticipationActView.ACTION_DISQUALIFY:
            with transaction.atomic():
                for part in parts: part.set_disqualified(True)
        elif act == ContestParticipationActView.ACTION_UNDISQUALIFY:
            with transaction.atomic():
                for part in parts: part.set_disqualified(False)
        elif act == ContestParticipationActView.ACTION_DELETE:
            parts.delete()

        self.contest.clear_scoreboard_cache()
        return Response({ 'message': "Success" }, status=status.HTTP_200_OK)


class ContestParticipationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestParticipationDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        method = self.request.method
        if method == 'GET':
            if not contest.is_accessible_by(self.request.user):
                raise PermissionDenied()
        else:
            if not contest.is_editable_by(self.request.user):
                raise PermissionDenied()
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users.all()
        return queryset

    def get_object(self, *args, **kwargs):
        return super().get_object(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.put(*args, **kwargs)

    def put(self, request, key, pk):
        obj = self.get_object()
        user = request.user
        part = self.get_object()

        if "organization" in request.data:
            org = Organization.objects.filter(slug=request.data.get("organization"))
            if not org.exists():
                raise Http404()
            org = org.first()
            # TODO: Should we check if user can modify org here?
            part.organization = org

        part.save()
        return Response(
            ContestParticipationDetailSerializer(part).data,
            status=status.HTTP_200_OK
        )

class ContestParticipantListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    pagination_class = Page50Pagination

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404()
        return contest

    @cached_property
    def contest(self):
        return self.get_contest()

    def get_queryset(self):
        request = self.request

        queryset = Profile.objects.select_related('user', 'display_organization')
        if self.contest.is_editable_by(self.request.user):
            participation_type = request.query_params.get('type')

            q = Q()
            if participation_type == 'live':
                q = Q(virtual=0)
            elif participation_type == 'spectator':
                q = Q(virtual=-1)
            elif participation_type == 'virtual':
                q = Q(virtual__gt=0)

            queryset = queryset.filter(
                id__in=self.contest.users.filter(q).values_list('user__id', flat=True)
            )
        else:
            queryset = queryset.filter(
                id__in=self.contest.users.values_list('user__id', flat=True)
            )

        if request.query_params.get('user'):
            uname = request.query_params.get('user')
            queryset = queryset.filter(user__username__istartswith=uname).order_by('user__username')
            # Here we order by username to make sure the exact match to be the first result. Eg:
            # Find `abc`, get ['abc', 'abc1', 'abc2', ...]

        return queryset

    def get(self, request, key):
        view_full = request.query_params.get('view_full', False) in ['true', '1']

        # Cache is
        if view_full:
            contest = self.contest
            # cache_duration = contest.scoreboard_cache_duration
            # cache_duration = max( int( (contest.end_time - contest.start_time).total_seconds() ), 60 ) # seconds
            cache_duration = 120
            cache_disabled = (cache_duration == 0)
            cache_key = contest.participants_cache_key
            data = None

            if cache_disabled or cache.get(cache_key) == None:
                data = self.get_serializer_class()(self.get_queryset(), many=True, context={'request': request}).data
                if not cache_disabled:
                    cache.set(cache_key, data, cache_duration)
            else:
                data = cache.get(cache_key)

            return Response(data, status=status.HTTP_200_OK)
        else:
            data = self.paginate_queryset(self.get_queryset())
            data = self.get_serializer_class()(data, many=True, context={'request': request}).data,
            return self.get_paginated_response(data)
