from django.urls import path
from .views import OzonTransactionsList

urlpatterns = [
    path('ozon_transaction/', OzonTransactionsList.as_view()),
]
