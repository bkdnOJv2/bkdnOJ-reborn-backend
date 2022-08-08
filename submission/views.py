from django.http import Http404
from django.core.exceptions import PermissionDenied, ViewDoesNotExist, ValidationError

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import views, generics, status, permissions
from rest_framework.response import Response

from .serializers import SubmissionSerializer, SubmissionTestCaseSerializer, \
    SubmissionDetailSerializer, SubmissionResultSerializer, SubmissionBasicSerializer
from .models import Submission, SubmissionTestCase
from problem.models import Problem
from compete.models import Contest
from organization.models import Organization

class SubmissionListView(generics.ListAPIView):
    """
        Return a list of all submissions on the system
    """
    serializer_class = SubmissionSerializer
    permission_classes = []

    def get_queryset(self):
        user = self.request.user
        org = self.request.query_params.get('org', None)
        qs = None
        if org:
            org = Organization.objects.filter(slug=org).first()
            if org and org.id in user.profile.member_of_org_with_ids:
                if self.request.query_params.get('recursive'):
                    qs = Problem.get_org_visible_problems(org, True)
                else:
                    qs = Problem.get_org_visible_problems(org)
            else:
                return Submission.objects.none()
        else:
            qs = Problem.get_visible_problems(user)
        return Submission.objects.prefetch_related('problem', 'user', 'user__user', 'language', 'contest_object') \
                .filter(problem_id__in=qs)


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
