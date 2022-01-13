from django.urls import path
from . import views
from .views import *
from .viewsets import MeViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("user/<int:pk>/", views.UserView.as_view()),
    path("me/", MeViewSet.as_view(), name="me"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path("test/", test_action),
    path('rates/', RatesView.as_view(), name="rates"),
    path('rate/<int:pk>/', RateView.as_view(), name="rate"),
    path("send-mail-forgot-password/", SendMailForgotPasswordView.as_view()),
    path("email-reset-password/", ForgotPasswordView.as_view()),

]
