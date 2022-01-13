from django.urls import path
from .views import *


urlpatterns = [
    path('rates/', RatesView.as_view(), name="rates"),
    path('rate/<int:pk>/', RateView.as_view(), name="rate")
]
