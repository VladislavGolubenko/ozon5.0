from django.urls import path
from .views import OzonTransactionsList, ProductDashbordView

urlpatterns = [
    path('ozon_transaction/', OzonTransactionsList.as_view()),
    path('analitic_product/', ProductDashbordView().as_view()),
]
