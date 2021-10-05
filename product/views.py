import requests
from django.http import HttpResponse
import json

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from get_data.models import User
from .serializers import *


def test_action(request):
    user_data = User.objects.get(pk=request.user.id)
    ozon_ovner = str(user_data.ozon_id)
    request_post = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key, 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()

    if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

    request_items = request_json.get('result')
    request_last = request_items['items']

    for product_id_object in request_last:
        product_request = requests.post('https://api-seller.ozon.ru/v2/product/info', json={"product_id": product_id_object['product_id']},
                                     headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                              'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        product_json_result = product_request.json()
        product_json = product_json_result['result']

        ozon_id = product_json['id']
        preview = product_json['primary_image']

        sources = product_json['sources']

        for source in sources:
            sku = source['sku']

        name = product_json['name']
        stocks = product_json['stocks']

        coming = stocks['coming']  # Поставки
        balance = stocks['present']  # Остатки товара
        reserved = stocks['reserved']  # Зарезервировано
        warehouse_balance = balance - reserved  # Остатки на складе = остатки - зарезервированные единицы

        return_query = requests.post('https://api-seller.ozon.ru/v2/returns/company/fbs',
                                        json={"filter": {"product_name": "string"}},
                                        headers={'Client-Id': ozon_ovner,
                                                 'Api-Key': user_data.api_key,
                                                 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

        try:
            return_query_result = return_query['result']
            return_product = return_query_result['count']  # кол-во возвращенных товаров
        except TypeError:
            return_product = 0  # кол-во возвращенных товаров

        go_to_warehouse = return_product + coming  # в пути на склад (поставки + возвращенные товары)

        print(ozon_id, preview,  name, sku, warehouse_balance, go_to_warehouse)
        print('Это id', ozon_id)
        print('это тип id', type(ozon_id))
        ozon_id = int(ozon_id)
        Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name, stock_balance=balance, way_to_warehous=go_to_warehouse, user_id=request.user)

    return HttpResponse('<h1>получаем данные по api</h1>')
