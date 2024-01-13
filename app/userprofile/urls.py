# pylint: skip-file
from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from userprofile.views import SelfProfileDetail, UserProfileDetail, change_password

urlpatterns = [
    path('profile/', SelfProfileDetail.as_view(), name='userprofile-detail-self'),
    path('profile/change-password/', change_password, name='userprofile-detail-self-change-password'),
    # path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('profile/<str:username>/', UserProfileDetail.as_view(), name='userprofile-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
