from django.urls import path
from auth.views import RegisterView
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    # TokenVerifyView,
)
from .views import MyTokenObtainPairView, MyTokenVerifyView, SignOutView, \
    UserList, UserDetail, GroupList, GroupDetail, get_csrf, WhoAmI, \
    generate_user_from_file

urlpatterns = [
    path('csrf/', get_csrf, name='get-csrf'),

    path('sign-in/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token-verify/', MyTokenVerifyView.as_view(), name='token_verify'),
    path('verify/', WhoAmI.as_view(), name='who-am-i'),

    path('sign-up/', RegisterView.as_view(), name='user_register'),
    path('sign-out/', SignOutView.as_view(), name='user_sign_out'),

    path('users/', UserList.as_view(), name='user-list'),
    path('user/', UserList.as_view(), name='user-list'),

    path('user/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('user/generate/csv/', generate_user_from_file, name='user-gen-csv'),

    path('group/', GroupList.as_view(), name='group-list'),
    path('group/<int:pk>/', GroupDetail.as_view(), name='group-detail'),
]
