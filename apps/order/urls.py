from django.urls import path
from .views import OrderList, OrderDetail

urlpatterns = [

    path('order/', OrderList.as_view()),
    path('order/<int:pk>/', OrderDetail.as_view()),
    
]
