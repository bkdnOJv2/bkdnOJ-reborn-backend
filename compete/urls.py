from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('past-contest/', 
        PastContestListView.as_view(), 
        name='pastcontest-list',
    ),
    path('contest/', 
        ContestListView.as_view(), 
        name='contest-list',
    ),
    path('contest/<str:key>/', 
        ContestDetailView.as_view(), 
        name='contest-detail',
    ),
    path('contest/<str:key>/participate', 
        contest_participate_view, 
        name='contest-participate',
    ),
    path('contest/<str:key>/leave', 
        contest_leave_view, 
        name='contest-leave',
    ),


    path('contest/<str:key>/standing', 
        contest_standing_view,
        name='contest-standing',
    ),

    path('contest/<str:key>/submission', 
        ContestSubmissionListView.as_view(), 
        name='contestsubmission-detail',
    ),

    path('contest/<str:key>/problem/', 
        ContestProblemListView.as_view(), 
        name='contestproblem-list',
    ),
    path('contest/<str:key>/problem/<str:shortname>/', 
        ContestProblemDetailView.as_view(), 
        name='contestproblem-detail',
    ),
    path('contest/<str:key>/problem/<str:shortname>/submit', 
        ContestProblemSubmitView.as_view(), 
        name='contestproblem-submit',
    ),

    path('contest/<str:key>/problem/<str:shortname>/submission', 
        ContestProblemSubmissionListView.as_view(), 
        name='contestsubmission-list',
    ),
    path('contest/<str:key>/problem/<str:shortname>/submission/<int:id>/', 
        ContestProblemSubmissionDetailView.as_view(), 
        name='contestsubmission-detail',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
