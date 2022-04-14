from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from usergroup.views import UserList, UserDetail, GroupList, GroupDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),

    path('groups/', GroupList.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupDetail.as_view(), name='group-detail'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
