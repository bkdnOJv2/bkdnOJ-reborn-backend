from django.contrib import admin
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from usergroup.views import UserList, UserDetail, GroupList, GroupDetail

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),

    path('groups/', GroupList.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupDetail.as_view(), name='group-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
