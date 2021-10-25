import requests
from django.http import HttpResponse, Http404
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


# def test_action(request, email):
#
#     # user_data = User.objects.get(pk=request.user.id)
#     user_data = User.objects.get(email=email)
#     ozon_ovner = str(user_data.ozon_id)
#     request_post = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key, 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
#     request_json = request_post.json()
#
#     if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
#         return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
#
#     request_items = request_json.get('result')
#     request_last = request_items['items']
#
#     for product_id_object in request_last:
#         product_request = requests.post('https://api-seller.ozon.ru/v2/product/info', json={"product_id": product_id_object['product_id']},
#                                      headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
#                                               'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
#         product_json_result = product_request.json()
#         product_json = product_json_result['result']
#
#         ozon_id = product_json['id']
#         preview = product_json['primary_image']
#
#         sources = product_json['sources']
#
#         for source in sources:
#             sku = source['sku']
#
#         name = product_json['name']
#         stocks = product_json['stocks']
#
#         coming = stocks['coming']  # Поставки
#         balance = stocks['present']  # Остатки товара
#         reserved = stocks['reserved']  # Зарезервировано
#         warehouse_balance = balance - reserved  # Остатки на складе = остатки - зарезервированные единицы
#
#         return_query = requests.post('https://api-seller.ozon.ru/v2/returns/company/fbs',
#                                         json={"filter": {"product_name": "string"}},
#                                         headers={'Client-Id': ozon_ovner,
#                                                  'Api-Key': user_data.api_key,
#                                                  'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
#
#         try:
#             return_query_result = return_query['result']
#             return_product = return_query_result['count']  # кол-во возвращенных товаров
#         except TypeError:
#             return_product = 0  # кол-во возвращенных товаров
#
#         go_to_warehouse = return_product + coming  # в пути на склад (поставки + возвращенные товары)
#
#         print(ozon_id, preview,  name, sku, warehouse_balance, go_to_warehouse)
#         print('Это id', ozon_id)
#         print('это тип id', type(ozon_id))
#         ozon_id = int(ozon_id)
#         Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name, stock_balance=balance, way_to_warehous=go_to_warehouse, user_id=user_data.id)
#
#     return HttpResponse('<h1>получаем данные продуктов по api</h1>')


def order_action(request):

    from product.models import Order

    user_data = User.objects.get(email='admin@gmail.com')
    ozon_ovner = str(user_data.ozon_id)
    request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                 json={"dir": "asc",
                                       "filter": {"since": "2021-06-24T14:15:22Z", "to": "2021-10-06T14:15:22Z"},
                                       "limit": 1000,
                                       "with": {
                                           "analytics_data": True,
                                           "financial_data": True,
                                       }
                                       },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()

    if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

    request_items = request_json.get('result')

    for order in request_items:

        order_id = order['order_id']
        in_process_at = order['in_process_at']
        status = order['status']  # новое поле

        for items in order['products']:
            sku = items['sku']
            name = items['name']
            quantity = items['quantity']
            offer_id = items['offer_id']

        if order['analytics_data'] is not None:
            analitics_data = order['analytics_data']
            delivery_place = analitics_data['city'] + analitics_data['region']
            warehouse_name = analitics_data['warehouse_name']
        else:
            delivery_place = None
            warehouse_name = None

        if order['financial_data'] is not None:
            financial_data = order['financial_data']

            order_products = financial_data['products']
            summ_order_price = sum([order_product['quantity'] * order_product['price'] for order_product in order_products])

            if status == 'delivered' or status == 'cancelled':
                comission_amount = sum([order_product['commission_amount'] for order_product in order_products])

                for order_product in order_products:
                    if order_product['picking'] is not None:
                        amount = sum(order_product['picking'].amount)
                    else:
                        amount = None
        else:
            summ_order_price = None
            comission_amount = None
            amount = None
        print(order_id, in_process_at, sku, name, quantity, summ_order_price, user_data, offer_id, delivery_place, warehouse_name, comission_amount, amount, status)
        Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, sku=sku, name=name, quantity=quantity, price=summ_order_price, user_id=user_data, offer_id=offer_id, delivery_place=delivery_place, warehouse_name=warehouse_name, comission_amount=comission_amount, amount=amount, status=status)

    return HttpResponse('<h1>получаем данные заказов по api</h1>')

