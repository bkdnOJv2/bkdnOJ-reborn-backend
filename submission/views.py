from django.http import Http404
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError
from django.conf import settings

from django.utils.translation import gettext_lazy as _

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import views, generics, status, permissions
from rest_framework.response import Response

from .serializers import SubmissionSerializer, SubmissionTestCaseSerializer, \
    SubmissionDetailSerializer, SubmissionResultSerializer, SubmissionBasicSerializer
from .models import Submission, SubmissionTestCase
from problem.models import Problem
from compete.models import Contest, ContestParticipation
from organization.models import Organization

from submission.tasks import mass_rejudge

class SubmissionListView(generics.ListAPIView):
    """
        Return a list of all submissions on the system
    """
    serializer_class = SubmissionSerializer
    permission_classes = []

    def get_queryset(self):
        query_params = self.request.query_params
        user = self.request.user
        org = self.request.query_params.get('org', None)
        qs = None

        if org:
            org = Organization.objects.filter(slug=org).first()
            if org and org.id in user.profile.member_of_org_with_ids:
                if self.request.query_params.get('recursive'):
                    probs = Problem.get_org_visible_problems(org, True)
                    contests = Contest.get_org_visible_contests(org, True)
                else:
                    probs = Problem.get_org_visible_problems(org)
                    contests = Contest.get_org_visible_contests(org)
            else:
                return Submission.objects.none()
        else:
            probs = Problem.get_visible_problems(user)
            contests = Contest.get_visible_contests(user)

        queryset = Submission.objects.prefetch_related(
            'problem', 'user', 'user__user', 'language', 'contest_object',
            'contest', 'contest__participation'
        ).filter(
            Q(contest_object=None, problem_id__in=probs) |
            Q(contest_object_id__in=contests, contest__participation__virtual=ContestParticipation.LIVE)
        )

        ## Query Params
        is_logged_in = user.is_authenticated
        if is_logged_in and query_params.get('me'):
            queryset = queryset.filter(user=user.profile)
        else:
            username = query_params.get('user')
            if username is not None:
                queryset = queryset.filter(user__user__username=username)

        prob_shortname = query_params.get('problem')
        if prob_shortname is not None:
            queryset = queryset.filter(problem__shortname=prob_shortname.upper())

        lang = query_params.get('language')
        if lang is not None:
            queryset = queryset.filter(language__common_name=lang)

        ##
        verdict = query_params.get('verdict')
        order_by = query_params.get('order_by')
        order_dec = query_params.get('dec')

        if verdict is not None:
            if verdict == 'RTE':
                queryset = queryset.filter(result__in=['RTE', 'IR'])
            elif user.is_staff and verdict == 'Q':
                queryset = queryset.filter(status__in=['QU', 'P', 'G'])
            elif user.is_staff and verdict == 'IE':
                queryset = queryset.filter(result__in=['IE', 'AB'])
            elif user.is_staff and verdict == 'SC':
                queryset = queryset.filter(result='SC')
            else:
                queryset = queryset.filter(result=verdict)

        if order_by is not None:
            key = order_by
            if order_by in ['time', 'memory', 'date']:
                key = f"{order_by}"

            if order_dec:
                key = '-'+key

            try:
                queryset = queryset.order_by(key)
            except:
                return Submission.objects.none()

        date_before = query_params.get('date_before')
        date_after = query_params.get('date_after')
        from helpers.timezone import datetime_from_z_timestring

        # We are filtering by second-precisions, so submission with
        # subtime HH:mm:ss.001 which is greater than HH:mm:ss.000
        # would not be included in the queryset
        # A workaround is to add .999ms the datetimes, basically a way of "rounding"
        # But let's leave it out for now
        if date_before is not None:
            queryset = queryset.filter(date__lte=datetime_from_z_timestring(date_before))
        if date_after is not None:
            queryset = queryset.filter(date__gte=datetime_from_z_timestring(date_after))

        return queryset

    def patch(self, request):
        user = request.user
        if (not user.is_staff) and (not user.has_perm('submission.mass_rejudge')):
            return Response({
                'message': _('You do not have permission to mass rejudge.')
            }, status=status.HTTP_403_FORBIDDEN)

        qs = self.get_queryset()
        if qs.count() > settings.BKDNOJ_REJUDGE_LIMIT and not user.has_perm('submission.mass_rejudge_many'):
            return Response({
                'message': _(f"You need permission to rejudge more than {settings.BKDNOJ_REJUDGE_LIMIT} subs.")
            }, status=status.HTTP_403_FORBIDDEN)

        async_status = mass_rejudge.delay(
            sub_ids=list(qs.values_list('id', flat=True)),
            rejudge_user_id=user.id
        )
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Return a detailed view of a certain submission
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailSerializer
    permission_classes = []

    def get_object(self, *args, **kwargs):
        sub = super().get_object(*args)

        user = self.request.user

        contest_key = self.request.query_params.get('contest', None)
        contest = Contest.objects.filter(key=contest_key).first()

        if sub.can_see_detail(user, contest):
            return sub
        raise PermissionDenied

class SubmissionRejudgeView(views.APIView):
    """
        View for rejudge submission
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionBasicSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        sub = get_object_or_404(Submission, id=pk)
        user = self.request.user
        if sub.can_see_detail(user):
            return sub
        raise PermissionDenied

    def post(self, request, pk):
        sub = self.get_object(pk)
        if not sub.problem.is_editable_by(request.user):
            raise PermissionDenied()
        try:
            sub.judge(force_judge=True, rejudge=True)
        except Exception as e:
            return Response({
                'error': f"Rejudge submission {sub.id} failed.",
                'details': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            SubmissionBasicSerializer(sub, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

class SubmissionResultView(views.APIView):
    """
        Return a list of test case results for that submission
    """
    permission_classes = []

    def get_queryset(self):
        return SubmissionDetailTestCase.objects.filter(
            submission=self.kwargs['pk'])

    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        serial = SubmissionResultSerializer(submission)
        return Response(serial.data, status=status.HTTP_200_OK)

class SubmissionResultTestCaseView(views.APIView):
    """
        Return a specific case with number `case_num`
        that belongs to submission `pk`
    """
    queryset = SubmissionTestCase.objects.none()
    serializer_class = SubmissionTestCaseSerializer
    permission_classes = []

    def get(self, request, pk, case_num):
        Qfilter = Q(submission=pk) & Q(case=case_num)
        inst = get_object_or_404(SubmissionTestCase, Qfilter)
        serial = SubmissionTestCaseSerializer(inst)
        return Response(serial.data, status=status.HTTP_200_OK)
