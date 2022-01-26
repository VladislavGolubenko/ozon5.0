from ozon.celery import app
from ..models import User
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from datetime import timedelta
import requests
from ...product.models import Product, Categories
import json


class CategoriesOzon:
    """Класс для загрузки категорий с озона"""
    def get_category_ozon(api_key:str, cliend_id:int, category_id:int) -> json:
        url = "https://api-seller.ozon.ru/v2/category/tree"
        print("category_id: ", category_id)
        data = {
                "category_id": int(category_id),
                "language": "DEFAULT"
                }
        headers = {
            'Client-Id': str(cliend_id), # ozon_ovner
            'Api-Key': str(api_key) , # user_data.api_key
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        category = requests.post(url=url, headers=headers, json=data).json()
        return category
    
    def get_category(category_id:int, name:str) -> Categories:
        category = Categories.objects.filter(category_id=category_id, name=name).first()
        if category is None: 
            category = Categories.objects.create(category_id=category_id, name=name)
        return category
    



class ProductsOzon:
    """
    Класс для интеграции продуктов с OZON
    """
    def _get_one_product(api_key, cliend_id, product_id:str) -> json:
        """
        Отдает один товар в JSON формате
        """
        url = 'https://api-seller.ozon.ru/v2/product/info'
        json = {"product_id": product_id}
        headers = {
            'Client-Id': str(cliend_id), # ozon_ovner
            'Api-Key': str(api_key) , # user_data.api_key
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        product_request = requests.post(url=url,
                                        json=json,
                                        headers=headers
                                        )
        product_json = product_request.json().get("result")
        return product_json

    def _get_products(api_key, cliend_id) -> json:
        """
        Отдает все товары
        """
        url = 'https://api-seller.ozon.ru/v1/product/list'
        headers = {
            'Client-Id': str(cliend_id), # ozon_ovner
            'Api-Key': str(api_key) , # user_data.api_key
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        request_post = requests.post(url=url, headers=headers)
        return request_post.json()
    
    def _get_count_product_return(api_key, cliend_id, name_product:str) -> int:
        """Отдает количество возвращенных экземпляров товара"""
        url = 'https://api-seller.ozon.ru/v2/returns/company/fbs'
        json={
            "filter": {
                "product_name": name_product
                }
            }
        headers={
            'Client-Id': str(cliend_id),
            'Api-Key': str(api_key),
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        requests_data = requests.post(
            url=url,
            json=json,
            headers=headers
            )
        result = requests_data.json().get("result")
        count = result.get("count")
        return count

    @staticmethod
    def get_products_in_json(api_key, cliend_id):
        """
        Отдает все товары в JSON формате
        """
        request_json = ProductsOzon._get_products(api_key, cliend_id)
        if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
        request_items = request_json.get('result').get('items')

        products = list()

        for product_id_object in request_items:
            product = ProductsOzon._get_one_product(api_key, cliend_id, product_id_object.get('product_id'))
            products.append(product)
        return products


    def update_or_create_products(api_key:str, cliend_id:str, user:User) -> None:
        """
        Обновляет товары которые пришли из OZON
        """
        products = ProductsOzon.get_products_in_json(api_key, cliend_id)
        for product_json in products:
            # volume_weight
            # category_id
            if product_json.get('visible') is True:
                ozon_id = product_json.get('id')
                preview = product_json.get('primary_image')
                volume_weight = product_json.get('volume_weight')
                category_id = product_json.get('category_id')
                category_json = CategoriesOzon.get_category_ozon(api_key, cliend_id, category_id)
                print(category_json)
                category_name = category_json.get("result")[0].get("title")
                category_id_result = category_json.get("result")[0].get("category_id")
                category = CategoriesOzon.get_category(category_id_result, category_name)
                offer_id = product_json.get('offer_id')
                marketing_price = product_json.get('marketing_price') 
                if (marketing_price == 0.0) or (marketing_price is None) or (marketing_price==''):
                    marketing_price = product_json['price']

                sources = product_json.get('sources')
                sku = None
                for source in sources:
                    if source.get("source") == "fbo":
                        sku = source.get('sku')

                name = product_json.get('name')
                stocks = product_json.get('stocks')

                coming = stocks.get('coming')  # Поставки
                balance = stocks.get('present')  # Остатки товара
                reserved = stocks.get('reserved')  # Зарезервировано
                go_to_warehouse = ProductsOzon._get_count_product_return(api_key, cliend_id, name) + coming  # в пути на склад (поставки + возвращенные товары)
                ozon_id = int(ozon_id)
                product = Product.objects.filter(ozon_product_id=ozon_id).first()
                if product is not None:
                    #Обновление
                    #product.
                    product.preview=preview
                    product.ozon_product_id=ozon_id
                    product.sku=sku
                    product.name=name
                    product.stock_balance=balance
                    product.reserved=reserved
                    product.way_to_warehous=go_to_warehouse
                    product.marketing_price=marketing_price
                    product.user_id=user
                    product.offer_id = offer_id,
                    product.is_visible=True
                    product.volume_weight= volume_weight
                    product.category = category
                    product.save()
                else:
                    Product.objects.create_product(
                        preview=preview, 
                        ozon_product_id=ozon_id, 
                        sku=sku, 
                        name=name,
                        stock_balance=balance, 
                        reserved=reserved, 
                        way_to_warehous=go_to_warehouse,
                        marketing_price=marketing_price, 
                        user_id=user,
                        offer_id = offer_id,
                        marketplace_id = cliend_id,
                        is_visible=True,
                        volume_weight= volume_weight,
                        category=category
                        )
