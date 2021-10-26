from ozon.celery import app
from get_data.models import User
from rest_framework.response import Response
from rest_framework import status
import requests


@app.task(bind=True)
def get_product(email, *args, **kwargs):

    from product.models import Product
    user_data = User.objects.get(email='admin@gmail.com')
    ozon_ovner = str(user_data.ozon_id)
    request_post = requests.post('https://api-seller.ozon.ru/v1/product/list',
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()

    if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

    request_items = request_json.get('result')
    request_last = request_items['items']

    for product_id_object in request_last:
        product_request = requests.post('https://api-seller.ozon.ru/v2/product/info',
                                        json={"product_id": product_id_object['product_id']},
                                        headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                                 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        product_json_result = product_request.json()
        product_json = product_json_result['result']

        ozon_id = product_json['id']
        preview = product_json['primary_image']

        if product_json['marketing_price'] is not 0.0 or product_json['marketing_price'] is not None:
            marketing_price = product_json['marketing_price']
        else:
            marketing_price = product_json['price']

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
        ozon_id = int(ozon_id)

        Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name, stock_balance=balance,
                                       way_to_warehous=go_to_warehouse, marketing_price=marketing_price, user_id=user_data)


@app.task(bind=True)
def get_order(email, *args, **kwargs):
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
        quantity = 0


        for items in order['products']:
            sku = items['sku']
            name = items['name']
            quantity += items['quantity']
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
            summ_order_price = sum(
                [order_product['quantity'] * order_product['price'] for order_product in order_products])

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

        Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, sku=sku, name=name,
                                   quantity=quantity, price=summ_order_price, user_id=user_data, offer_id=offer_id,
                                   delivery_place=delivery_place, warehouse_name=warehouse_name,
                                   comission_amount=comission_amount, amount=amount, status=status)


@app.task(bind=True)
def update_product_order(*args, **kwargs):

    from product.models import Product, Order
    from get_data.models import User

    user_data = User.objects.filter(api_key__isnull=False)

    for data in user_data:
        old_products = Product.objects.filter(user_id=data.pk)
        old_orders = Order.objects.filter(user_id=data.pk)

        for old_product in old_products:
            old_product.delete()

        for old_order in old_orders:
            old_order.delete()

        ozon_ovner = str(data.ozon_id)
        api_key = data.api_key

        # Заказы

        request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                     json={"dir": "asc",
                                           "filter": {"since": "2021-06-24T14:15:22Z", "to": "2021-10-06T14:15:22Z"},
                                           "limit": 1000,
                                           "with": {
                                                  "analytics_data": True,
                                                  "financial_data": True,
                                              }
                                           },
                                     headers={'Client-Id': ozon_ovner, 'Api-Key': api_key,
                                              'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        request_json = request_post.json()

        if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

        request_items = request_json.get('result')

        if request_items != None:
            for order in request_items:

                order_id = order['order_id']
                in_process_at = order['in_process_at']
                status = order['status']

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
                        summ_order_price = sum(
                            [order_product['quantity'] * order_product['price'] for order_product in order_products])

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

                Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, sku=sku, name=name,
                                           quantity=quantity, price=summ_order_price, user_id=data, offer_id=offer_id,
                                           delivery_place=delivery_place, warehouse_name=warehouse_name,
                                           comission_amount=comission_amount, amount=amount, status=status)



        # Товары
        request_post = requests.post('https://api-seller.ozon.ru/v1/product/list',
                                     headers={'Client-Id': ozon_ovner, 'Api-Key': api_key,
                                              'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        request_json = request_post.json()

        if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

        request_items = request_json.get('result')
        request_last = request_items['items'] if request_items != None else 'NoneType'


        if request_last != 'NoneType':
            for product_id_object in request_last:

                product_request = requests.post('https://api-seller.ozon.ru/v2/product/info',
                                                json={"product_id": product_id_object['product_id']},
                                                headers={'Client-Id': ozon_ovner, 'Api-Key': api_key,
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
                                                      'Api-Key': api_key,
                                                      'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

                try:
                    return_query_result = return_query['result']
                    return_product = return_query_result['count']  # кол-во возвращенных товаров
                except TypeError:
                    return_product = 0  # кол-во возвращенных товаров

                go_to_warehouse = return_product + coming  # в пути на склад (поставки + возвращенные товары)

                ozon_id = int(ozon_id)

                Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name, stock_balance=balance, way_to_warehous=go_to_warehouse, user_id=data)


