from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from django.db.models import Case, Count, F, FloatField, IntegerField, Max, Min, Q, Sum, Value, When
from django.db import IntegrityError
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError

from rest_framework import views, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from operator import attrgetter, itemgetter

from problem.serializers import ProblemSerializer
from .serializers import *

from .models import Contest, ContestProblem, ContestSubmission, ContestParticipation
from helpers.custom_pagination import BigPageCountPagination

__all__ = [
    'PastContestListView',
    'AllContestListView', 'ContestListView', 'ContestDetailView',
    'ContestProblemListView', 'ContestProblemDetailView', 'ContestProblemSubmitView',
    'ContestSubmissionListView',
    'ContestParticipationListView', 'ContestParticipationDetailView',
    'ContestProblemSubmissionListView', 'ContestProblemSubmissionDetailView',
    'contest_participate_view', 'contest_leave_view', 'contest_standing_view',
]

class PastContestListView(generics.ListAPIView):
    """
        Return a List of all organizations
    """
    serializer_class = ContestSerializer
    permission_classes = [
        permissions.DjangoModelPermissionsOrAnonReadOnly,
    ]

    @cached_property
    def _now(self):
        return timezone.now()

    def get_queryset(self):
        qs = Contest.get_visible_contests(self.request.user).\
                filter(end_time__lt=self._now).order_by('-end_time')
        return qs

class AllContestListView(generics.ListAPIView):
    """
        Return a List of all Contests
    """
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    permission_classes = [permissions.IsAdminUser]

class ContestListView(generics.ListCreateAPIView):
    """
        Return a List of present, active, future contest
    """
    serializer_class = ContestBriefSerializer
    permission_classes = []

    @cached_property
    def _now(self):
        return timezone.now()

    def _get_queryset(self):
        qs = Contest.get_visible_contests(self.request.user)
        return qs.prefetch_related(
                'tags', 'organizations', 'authors', 'collaborators', 'reviewers')

    def get_queryset(self):
        return self._get_queryset().order_by('key').filter(end_time__lt=self._now)

    def get(self, request):
        present, active, future = [], [], []
        finished = set()
        for contest in self._get_queryset().exclude(end_time__lt=self._now):
            if contest.start_time > self._now:
                future.append(contest)
            else:
                present.append(contest)

        if self.request.user.is_authenticated:
            for participation in ContestParticipation.objects.filter(virtual=0, #LIVE
                    user=self.request.user.profile, contest_id__in=present) \
                    .select_related('contest') \
                    .prefetch_related('contest__authors', 'contest__collaborators', 'contest__reviewers') \
                    .annotate(key=F('contest__key')):
                if participation.ended:
                    finished.add(participation.contest)
                else:
                    active.append(participation.contest)
                    present.remove(participation.contest)

        active.sort(key=attrgetter('end_time', 'key'))
        present.sort(key=attrgetter('end_time', 'key'))
        future.sort(key=attrgetter('start_time'))
        context={'request': request}
        return Response({
            'active': ContestBriefSerializer(active, many=True, context=context).data,
            'present': ContestBriefSerializer(present, many=True, context=context).data,
            'future': ContestBriefSerializer(future, many=True, context=context).data,
        }, status=status.HTTP_200_OK)

    #def create(self, request):
    #    raise ViewDoesNotExist


class ContestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of requested organization
    """
    queryset = Contest.objects.all()
    lookup_field = 'key'
    serializer_class = ContestDetailSerializer
    permission_classes = []

    def get_object(self, *a):
        contest = super().get_object(*a)
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        # if (not contest.started) and (not contest.is_testable_by(user)):
        #     raise PermissionDenied
        return contest
    
    def has_permission(self, request):
        if request.user.is_superuser:
            return True
        raise PermissionDenied

    def put(self, *args, **kwargs):
        return self.patch(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if self.has_permission(request):
            try:
                return super().patch(request, *args, **kwargs)
            except ValidationError as e:
                return Response({
                    'general': e,
                }, status=status.HTTP_400_BAD_REQUEST)


class ContestProblemListView(generics.ListCreateAPIView):
    """
        Problems within contests view
    """
    serializer_class = ContestProblemBriefSerializer
    pagination_class = BigPageCountPagination
    lookup_field = 'shortname'

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def get_queryset(self):
        contest = self.get_contest()
        queryset = ContestProblem.objects.filter(contest=contest)
        return queryset
    
    NON_ASSOCIATE_FIELDS = ('order', 'points', 'partial', 'is_pretested', 'max_submissions')
    def create(self, request, *args, **kwargs):
        contest = self.get_contest()
        cproblems = contest.contest_problems
        visproblems = Problem.get_visible_problems(request.user)
        
        new_problem_ids = set()
        for problem_kw in request.data:
            cpf = cproblems.filter(problem__shortname=problem_kw['shortname'])
            if cpf.exists():
                cpf = cpf.first()
            else:
                p = get_object_or_404(visproblems, shortname=problem_kw['shortname'])
                cpf = ContestProblem(contest=contest, problem=p)
            for k, v in problem_kw.items(): 
                if k in ContestProblemListView.NON_ASSOCIATE_FIELDS:
                    setattr(cpf, k, v)
            cpf.save()
            new_problem_ids.add(cpf.id)

        cproblems.exclude(id__in=new_problem_ids).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

class ContestProblemDetailView(generics.RetrieveAPIView):
    """
        Certain Problem within Contest view
    """
    pagination_class = None

    def get_serializer_class(self):
        # print(self.request.method)
        # if self.request.method == 'GET':
        #     return ProblemSerializer
        return ContestProblemSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def get_object(self):
        p = get_object_or_404(ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname'])
        return p


class ContestSubmissionListView(generics.ListAPIView):
    """
        All Submissions within contest view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def get_queryset(self):
        cps = ContestProblem.objects.filter(contest=self.get_contest()).all()
        css = ContestSubmission.objects.select_related('participation', 'problem')\
                .filter(problem__in=cps)

        if not self.request.user.is_superuser:
            css = css.filter(participation__virtual=ContestParticipation.LIVE)

        username = self.request.query_params.get('user')
        if username is not None:
            css = css.filter(participation__user__owner__username=username)
        prob_shortname = self.request.query_params.get('problem')
        if prob_shortname is not None:
            css = css.filter(problem__problem__shortname=prob_shortname)
        return css

    #def get(self, request, key):
    #    css = self.get_queryset()
    #    return Response(ContestSubmissionSerializer(css, many=True).data,
    #        status=status.HTTP_200_OK)


class ContestProblemSubmissionListView(generics.ListAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def get_queryset(self):
        cp = get_object_or_404( ContestProblem,
            contest=self.get_contest(),
            problem__shortname=self.kwargs['shortname']
        )
        queryset = ContestSubmission.objects.filter(problem=cp)
        if not queryset.exists():
            raise Http404
        return queryset


class ContestProblemSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Certain Submission within Contest view
    """
    serializer_class = ContestSubmissionSerializer

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        user = self.request.user
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def get_queryset(self):
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
        if not (contest.is_visible or contest.is_accessible_by(user)):
            raise PermissionDenied
        if (not contest.started) and (not contest.is_testable_by(user)):
            raise PermissionDenied
        return contest

    def create(self, request, *args, **kwargs):
        profile = request.user.profile

        contest = self.get_contest() # Accesibility checks
        if contest.ended:
            return Response({ 'detail': "Contest has ended." },
                                status=status.HTTP_400_BAD_REQUEST)

        # Check if user still have parts in the contest
        # We checks this because later we have to take care of Virtual Participations

        # Because Participations are in `date` order, and we only allow 1 participation
        # that is not ended per user/contest. So, we only need to check the last Part.
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
            return Response(
                _('You have reached maximum pending submissions allowed. '
                    'Please wait until your previous submissions finish grading.'),
                status=status.HTTP_429_TOO_MANY_REQUESTS,
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
                participation=profile.current_contest,
                # is_pretest=contest. # TODO: is_pretest
        )
        consub.save()

        return Response(
            SubmissionBasicSerializer(sub_obj, context={'request':request}).data,
            status=status.HTTP_200_OK,
        )


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
            'detail': _("You don't have permission to register to this contest.")},
            status=status.HTTP_401_UNAUTHORIZED)

    # TODO: access code
    user = request.user
    contest = get_object_or_404(Contest, key=key)
    
    if not contest.is_registerable_by(user):
        return not_authorized()

    profile = request.user.profile
    if not request.user.is_superuser and contest.banned_users.filter(owner_id=profile.user.id).exists():
        return banned()
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


from collections import defaultdict, namedtuple
from django.core.cache import cache

@api_view(['GET'])
def contest_standing_view(request, key):
    user = request.user
    contest = get_object_or_404(Contest, key=key)

    if not contest.is_visible and not contest.is_accessible_by(user):
        return Response({
            'detail': "Contest is not public to view."
        }, status=status.HTTP_403_FORBIDDEN)

    ## TODO: Scoreboard visibility

    queryset = contest.users.filter(virtual=ContestParticipation.LIVE).\
        order_by('-score', 'cumtime').all()

    cache_key = f"contest-{contest.key}-problem-data"
    if cache.get(cache_key) == None:
        cprobs = contest.contest_problems.all()
        problem_data = [{
            'id': p.id,
            'label': p.label,
            'shortname': p.problem.shortname,
            'points': p.points,
        } for p in cprobs]
        cache.set(cache_key, problem_data, 60)
    else:
        problem_data = cache.get(cache_key)

    return Response({
        'problems': problem_data,
        'results': ContestStandingSerializer(queryset, many=True, context={'request': request}).data,
    }, status=status.HTTP_200_OK)


class ContestParticipationListView(generics.ListCreateAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestParticipationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users

        username = self.request.query_params.get('user')
        if username is not None:
            queryset = queryset.filter(user__owner__username=username)

        virtual = self.request.query_params.get('virtual')
        if virtual is not None:
            if virtual == 'LIVE':
                queryset = queryset.filter(virtual=0)
            elif virtual == 'SPECTATE':
                queryset = queryset.filter(virtual=-1)
            elif virtual == 'VIRTUAL':
                queryset = queryset.filter(virtual__gt=0)
            else:
                raise Http404

        is_disqualified = self.request.query_params.get('is_disqualified')
        if is_disqualified is not None:
            queryset = queryset.filter(is_disqualified=is_disqualified)

        return queryset.all()


class ContestParticipationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Submissions within contests view
    """
    serializer_class = ContestParticipationDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_contest(self):
        contest = get_object_or_404(Contest, key=self.kwargs['key'])
        if not contest.is_accessible_by(self.request.user):
            raise Http404
        return contest

    def get_queryset(self):
        queryset = self.get_contest().users.all()
        return queryset


