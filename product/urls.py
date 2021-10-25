from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.ProductListAction.as_view()),
    path('product/<int:pk>/', views.ProductDetailAction.as_view()),
    path('order/', views.OrderListAction.as_view()),
    path('order/<int:pk>/', views.OrderDetailAction.as_view()),
]
