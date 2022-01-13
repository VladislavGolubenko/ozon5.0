from django.urls import path
from .views import OzonMetricsAction

urlpatterns = [
    path('metrics/', OzonMetricsAction.as_view()),
]
