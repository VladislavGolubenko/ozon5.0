from django.urls import path
from . import views
from .views import *
from .viewsets import MeViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("user/", views.UserAction.as_view()),
    path("me/", MeViewSet.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("test/", test_action)
]
