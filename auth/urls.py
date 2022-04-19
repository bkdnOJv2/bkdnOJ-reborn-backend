from django.urls import path
from auth.views import RegisterView
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    # TokenVerifyView,
)
from .views import MyTokenObtainPairView, MyTokenVerifyView, SignOutView

urlpatterns = [
    path('sign-in/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sign-in/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sign-in/verify/', MyTokenVerifyView.as_view(), name='token_verify'),
    path('sign-up/', RegisterView.as_view(), name='user_register'),
    path('sign-out/', SignOutView.as_view(), name='user_sign_out'),
]