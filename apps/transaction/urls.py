from django.urls import path
from .views import TransactionView

urlpatterns = [
    path("transaction/", TransactionView.as_view()),
]
