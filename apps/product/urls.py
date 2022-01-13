from django.urls import path
from .views import ProductListAction, ProductDetailAction, WarehouseAccountView, ProductInOrderAction, CompanyDashbordView, ProductInOrderSet

urlpatterns = [
    path('product/', ProductListAction.as_view()),
    path('product/<int:pk>/', ProductDetailAction.as_view()),
    path('warehouse_control/<int:days>/', WarehouseAccountView.as_view()),
    path('product_order/', ProductInOrderAction.as_view()),
    # path('object_in_table/<slug:table>/', views.ObjectInTableView().as_view()),
    path('analitic_company/', CompanyDashbordView.as_view()),
    path('productinorder/<slug:sku>/', ProductInOrderSet.as_view()),
]
