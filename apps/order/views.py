from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from django_filters import rest_framework as filters

from ..account.permissions import IsSubscription
from .models import Order
from .serializers import OrderSerializer
from .filters import OrderFilter
from ..ozon_transaction.models import OzonTransactions
from ..product.models import ProductInOrder


class OrderList(ListAPIView):
    """
        Вывод списка заказов
    """

    #permission_classes = [IsSubscription]

    serializer_class = OrderSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, SearchFilter)  #CustomSearchFilter)
    ordering_fields = '__all__'
    search_fields = [
        "order_number", 
        "status", 
        "posting_number", 
        "region", 
        "delivery_type", 
        "warehous_id", 
        "warehouse_name", 
        "creating_date", 
        "orderproduct_to_order__offer_id",
        "orderproduct_to_order__name",
        "orderproduct_to_order__sku",
        ]
    def get_queryset(self):
        queryset = Order.objects.filter(user_id=self.request.user.pk)
        status_queryset = OrderFilter.order_status_filter(self, queryset=queryset)
        return OrderFilter.order_date_filter(self, queryset=status_queryset)

    # def post(self, request, format=None):
    #     serializer = OrderSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    """
        Работа с конкретным заказом
    """
    permission_classes = [IsSubscription]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk, is_visible=True)
        except Order.DoesNotExist:
            raise Http404

    def get(self, pk):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
