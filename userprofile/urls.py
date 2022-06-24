from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from userprofile.views import SelfProfileDetail, UserProfileDetail

urlpatterns = [
    path('profile/', SelfProfileDetail.as_view(), name='userprofile-detail-self'),
    # path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('profile/<str:username>/', UserProfileDetail.as_view(), name='userprofile-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
