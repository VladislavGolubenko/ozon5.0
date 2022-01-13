from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserDetail, MeView, UserView


urlpatterns = [
    path("user/", UserView.as_view()),
    path("user/<int:pk>/", UserDetail.as_view()),
    path("me/", MeView.as_view(), name="me"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
