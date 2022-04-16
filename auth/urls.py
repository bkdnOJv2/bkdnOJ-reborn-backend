from django.urls import path
from auth.views import RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('sign-in/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sign-in/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('sign-up/', RegisterView.as_view(), name='user_register'),
]