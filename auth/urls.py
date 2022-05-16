from django.urls import path
from auth.views import RegisterView
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    # TokenVerifyView,
)
from .views import MyTokenObtainPairView, MyTokenVerifyView, SignOutView, \
    UserList, UserDetail, GroupList, GroupDetail

urlpatterns = [
    path('sign-in/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sign-in/verify/', MyTokenVerifyView.as_view(), name='token_verify'),
    path('sign-up/', RegisterView.as_view(), name='user_register'),
    path('sign-out/', SignOutView.as_view(), name='user_sign_out'),

    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),

    path('groups/', GroupList.as_view(), name='group-list'),
    path('groups/<int:pk>/', GroupDetail.as_view(), name='group-detail'),
]