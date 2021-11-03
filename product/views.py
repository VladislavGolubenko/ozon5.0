import json
import requests
from django.http import HttpResponse, Http404
from datetime import datetime, date
from datetime import timedelta
from django_filters import rest_framework as filters
# from django_filters.rest_framework import DjangoFilterBackend
from .service import OrderFilter

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .serializers import *
from rest_framework import permissions
from .models import *


class ProductListAction(APIView):

    def get(self, request, format=None):
        queryset = Product.objects.filter(user_id=request.user.pk)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListAction(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrderSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrderFilter

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.pk)

        # queryset = Order.objects.filter(user_id=self.request.user.pk)
        # # queryset = Order.objects.all()
        # serializer = OrderSerializer(queryset, many=True)
        # return Response(serializer.data)


    # def post(self, request, format=None):
    #     serializer = OrderSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAction(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WarehouseAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, days):

        email = self.request.POST['email']
        date_sort = datetime.now() - timedelta(days=days)

        # products = Product.objects.filter(user_id=request.user.pk)
        products = Product.objects.filter(user_id__email=email)

        datas = []

        for product in products:

            preview = product.preview
            ozon_product_id = product.ozon_product_id
            sku = product.sku
            name = product.name
            stock_balance = product.stock_balance

            orders_by_period = 0

            products_in_orders = ProductInOrder.objects.filter(sku=product.sku, order_id_id__date_of_order__gte=date_sort)

            for product_in_order in products_in_orders:
                orders_by_period += product_in_order.quantity  # Заказано за период

            orders_speed = orders_by_period / days  # Средняя скорость заказов
            days_for_production = product.days_for_production  # Срок производства

            if orders_speed != 0.0:
                stocks_for_days = round(stock_balance/orders_speed)  # Осталось запасов на дней
            else:
                stocks_for_days = None

            reorder_days_of_supply = product.reorder_days_of_supply  # Глубина поставки
            potencial_proceeds = product.marketing_price * product.stock_balance  # Потенциальная выручка остатков

            if product.summ_price is not None:
                product_price = product.summ_price  # Стоимость товара
            elif product.unit_price and product.additional_price and product.logistics_price is not None:
                product_price = product.unit_price + product.additional_price + product.logistics_price
            else:
                product_price = None

            if product_price is not None:
                stocks_cost_price = product_price * stock_balance  # Себестоимость остатков
            else:
                stocks_cost_price = None

            if reorder_days_of_supply is not None:
                need_to_order = reorder_days_of_supply * orders_speed  # Необходимо заказать
            else:
                need_to_order = None

            if need_to_order and product_price is not None:
                reorder_sum = need_to_order * product_price  # Сумма перезаказа
            else:
                reorder_sum = None

            data = {
                'preview': preview,
                'ozon_product_id': ozon_product_id,
                'sku': sku,
                'name': name,
                'stock_balance': stock_balance,
                'orders_by_period': orders_by_period,
                'orders_speed': orders_speed,
                'days_for_production': days_for_production,
                'reorder_days_of_supply': reorder_days_of_supply,
                'potencial_proceeds': potencial_proceeds,
                'product_price': product_price,
                'stocks_for_days': stocks_for_days,
                'need_to_order': need_to_order,
                'stocks_cost_price': stocks_cost_price,
                'reorder_sum': reorder_sum
            }

            datas.append(data)

        return Response(data=datas, status=status.HTTP_200_OK)


