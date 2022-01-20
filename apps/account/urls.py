from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserDetail, MeView, UserView, ResetPasswordView, SendMailForgotPasswordView, ForgotPasswordView


urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/<int:pk>/", UserDetail.as_view()),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ResetPasswordView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("send-mail-forgot-password/", SendMailForgotPasswordView.as_view()),
    path("email-reset-password/", ForgotPasswordView.as_view()),
]