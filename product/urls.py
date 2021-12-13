from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.ProductListAction.as_view()),
    path('product/<int:pk>/', views.ProductDetailAction.as_view()),
    path('order/', views.OrderListAction.as_view()),
    path('order/<int:pk>/', views.OrderDetailAction.as_view()),
    path('warehouse_control/<int:days>/', views.WarehouseAccountView.as_view()),
    path('product_order/', views.ProductInOrderAction.as_view()),
    path('ozon_transaction/', views.OzonTransactionsAction.as_view()),
    path('metrics/', views.OzonMetricsAction.as_view()),
    path('object_in_table/<slug:table>/', views.ObjectInTableView().as_view()),
    path('analitic_company/', views.CompanyDashbordView().as_view()),
    path('analitic_product/', views.ProductDashbordView().as_view()),
]
