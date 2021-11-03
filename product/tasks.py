from ozon.celery import app
from get_data.models import User
from rest_framework.response import Response
from rest_framework import status
from itertools import product
from datetime import datetime, date
from datetime import timedelta
import requests


@app.task(bind=True)
def get_product(*args, **kwargs):
    email = kwargs.get('email')

    from product.models import Product
    user_data = User.objects.get(email=email)

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

        if product_json['marketing_price'] != 0.0 or product_json['marketing_price'] is not None:
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

        Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name,
                                       stock_balance=balance, reserved=reserved, way_to_warehous=go_to_warehouse,
                                       marketing_price=marketing_price, user_id=user_data)


@app.task(bind=True)
def get_order(*args, **kwargs):
    email = kwargs.get('email')
    from product.models import Order, ProductInOrder

    user_data = User.objects.get(email=email)
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
        posting_number = order['posting_number']
        in_process_at = order['in_process_at']
        date_of_order = order['created_at']
        status = order['status']  # новое поле
        quantity = 0

        if order['analytics_data'] is not None:
            analitics_data = order['analytics_data']
            city = analitics_data['city']
            region = analitics_data['region']
            warehouse_name = analitics_data['warehouse_name']
            warehous_id = analitics_data['warehouse_id']
            delivery_type = analitics_data['delivery_type']
        else:
            analitics_data = None
            city = None
            region = None
            warehouse_name = None
            warehous_id = None
            delivery_type = None

        order_save = Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, user_id=user_data,
                                   status=status,
                                   date_of_order=date_of_order, posting_number=posting_number, region=region, city=city,
                                   delivery_type=delivery_type, warehous_id=warehous_id, warehouse_name=warehouse_name)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  из двух списков нужно сформировать один по индексу

        financial_data = order['financial_data']
        product_financial = financial_data['products']

        i = 0
        for product_i in order['products']:

            sku = product_i['sku']
            name = product_i['name']
            quantity = product_i['quantity']
            offer_id = product_i['offer_id']
            price = product_i['price']


            product_f = product_financial[i]
            comission_amount = product_f['commission_amount']
            payout = product_f['payout']
            product_id = product_f['product_id']
            price_f = product_f['price']

            item_services = product_f['item_services']
            fulﬁllment = item_services['marketplace_service_item_fulfillment']
            direct_ﬂow_trans = item_services['marketplace_service_item_direct_flow_trans']
            return_ﬂow_trans = item_services['marketplace_service_item_return_flow_trans']
            deliv_to_customer = item_services['marketplace_service_item_deliv_to_customer']
            return_not_deliv_to_customer = item_services['marketplace_service_item_return_not_deliv_to_customer']
            return_part_goods_customer = item_services['marketplace_service_item_return_part_goods_customer']
            return_after_deliv_to_customer = item_services['marketplace_service_item_return_after_deliv_to_customer']

            ProductInOrder.objects.create_product_in_order(user_id=user_data, sku=sku, name=name, order_id=order_save,
                                                           quantity=quantity, offer_id=offer_id, price=price,
                                                           price_f=price_f, comission_amount=comission_amount,
                                                           payout=payout, product_id=product_id,
                                                           fulﬁllment=fulﬁllment,
                                                           direct_ﬂow_trans=direct_ﬂow_trans,
                                                           return_ﬂow_trans=return_ﬂow_trans,
                                                           deliv_to_customer=deliv_to_customer,
                                                           return_not_deliv_to_customer=return_not_deliv_to_customer,
                                                           return_part_goods_customer=return_part_goods_customer,
                                                           return_after_deliv_to_customer=return_after_deliv_to_customer)
            i += 1


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@app.task(bind=True)
def get_ozon_transaction(*args, **kwargs):

    email = kwargs.get('email')
    from product.models import OzonTransactions

    user_data = User.objects.get(email=email)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_to = f"{year}-{month}-0{day}T00:00:00Z"
    else:
        date_to = f"{year}-{month}-{day}T23:30:00Z"

    request_post = requests.post('https://api-seller.ozon.ru/v3/finance/transaction/list',
                                 json={
                                        "filter": {
                                            "date": {
                                                "from": "2021-02-01T00:00:00Z",
                                                "to": date_to,
                                            },

                                            "transaction_type": "all"
                                        },
                                        "page": 1,
                                        "page_size": 10000
                                    },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

    request_items = request_json.get('result')
    operations = request_items['operations']

    for operation in operations:

        operation_id = operation['operation_id']
        operation_type = operation['operation_type']
        operation_date = operation['operation_date']
        operation_type_name = operation['operation_type_name']
        accruals_for_sale = operation['accruals_for_sale']
        sale_commission = operation['sale_commission']
        amount = operation['amount']
        type = operation['type']

        posting = operation['posting']
        posting_number = posting['posting_number']

        items = operation['items']
        services = operation['services']

        items_array = []
        for item in items:
            name = item['name']
            sku = item['sku']
            dict_item = {
                'name': name,
                'sku': sku
            }
            items_array.append(dict_item)

        services_array = []
        for service in services:
            marketplace_services = (
                'MarketplaceServiceItemFulﬁllment',
                'MarketplaceServiceItemDirectFlowTrans',
                'MarketplaceServiceItemReturnFlowTrans',
                'MarketplaceServiceItemDelivToCustomer',
                'MarketplaceServiceItemReturnNotDelivToCustomer',
                'MarketplaceServiceItemReturnPartGoodsCustomer',
                'MarketplaceServiceItemReturnAfterDelivToCustomer',
                'MarketplaceServiceItemDropoffFf',
                'MarketplaceServiceItemDropoffPvz',
                'MarketplaceServiceItemDropoffSc',
            )

            if service['name'] in marketplace_services:
                dict_services = {
                    'service_name': service['name'],
                    'price': service['price']
                }
                services_array.append(dict_services)

        OzonTransactions.objects.create_ozon_transaction(user_id=user_data, operation_id=operation_id,
                                                         operation_type=operation_type, operation_date=operation_date,
                                                         operation_type_name=operation_type_name,
                                                         accruals_for_sale=accruals_for_sale,
                                                         sale_commission=sale_commission,
                                                         amount=amount, type=type, posting_number=posting_number,
                                                         items=items_array, services=services_array)


@app.task(bind=True)
def update_product_order(*args, **kwargs):

    from product.models import Product, Order, ProductInOrder
    from get_data.models import User

    user_data = User.objects.filter(api_key__isnull=False)

    for data in user_data:
        # !!!!!!!!!!!!!!!!!!!!!!!-- Eсли понадобится удаление --!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # old_products = Product.objects.filter(user_id=data.pk)
        # old_orders = Order.objects.filter(user_id=data.pk)

        # for old_product in old_products:
        #     old_product.delete()
        #
        # for old_order in old_orders:
        #     old_order.delete()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

        for order in request_items:

            order_id = order['order_id']
            posting_number = order['posting_number']
            in_process_at = order['in_process_at']
            date_of_order = order['created_at']
            status = order['status']  # новое поле
            quantity = 0

            if order['analytics_data'] is not None:
                analitics_data = order['analytics_data']
                city = analitics_data['city']
                region = analitics_data['region']
                warehouse_name = analitics_data['warehouse_name']
                warehous_id = analitics_data['warehouse_id']
                delivery_type = analitics_data['delivery_type']
            else:
                analitics_data = None
                city = None
                region = None
                warehouse_name = None
                warehous_id = None
                delivery_type = None

            order_save = Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, user_id=data,
                                                    status=status, date_of_order=date_of_order,
                                                    posting_number=posting_number, region=region, city=city,
                                                    delivery_type=delivery_type, warehous_id=warehous_id,
                                                    warehouse_name=warehouse_name)

            financial_data = order['financial_data']
            product_financial = financial_data['products']

            i = 0
            for product_i in order['products']:
                sku = product_i['sku']
                name = product_i['name']
                quantity = product_i['quantity']
                offer_id = product_i['offer_id']
                price = product_i['price']

                product_f = product_financial[i]
                comission_amount = product_f['commission_amount']
                payout = product_f['payout']
                product_id = product_f['product_id']
                price_f = product_f['price']

                item_services = product_f['item_services']
                fulﬁllment = item_services['marketplace_service_item_fulfillment']
                direct_ﬂow_trans = item_services['marketplace_service_item_direct_flow_trans']
                return_ﬂow_trans = item_services['marketplace_service_item_return_flow_trans']
                deliv_to_customer = item_services['marketplace_service_item_deliv_to_customer']
                return_not_deliv_to_customer = item_services['marketplace_service_item_return_not_deliv_to_customer']
                return_part_goods_customer = item_services['marketplace_service_item_return_part_goods_customer']
                return_after_deliv_to_customer = item_services[
                    'marketplace_service_item_return_after_deliv_to_customer']

                ProductInOrder.objects.create_product_in_order(user_id=data, sku=sku, name=name,
                                                               order_id=order_save,
                                                               quantity=quantity, offer_id=offer_id, price=price,
                                                               price_f=price_f, comission_amount=comission_amount,
                                                               payout=payout, product_id=product_id,
                                                               fulﬁllment=fulﬁllment,
                                                               direct_ﬂow_trans=direct_ﬂow_trans,
                                                               return_ﬂow_trans=return_ﬂow_trans,
                                                               deliv_to_customer=deliv_to_customer,
                                                               return_not_deliv_to_customer=return_not_deliv_to_customer,
                                                               return_part_goods_customer=return_part_goods_customer,
                                                               return_after_deliv_to_customer=return_after_deliv_to_customer)
                i += 1




        # Старые заказы
        # request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
        #                              json={"dir": "asc",
        #                                    "filter": {"since": "2021-06-24T14:15:22Z", "to": "2021-10-06T14:15:22Z"},
        #                                    "limit": 1000,
        #                                    "with": {
        #                                           "analytics_data": True,
        #                                           "financial_data": True,
        #                                       }
        #                                    },
        #                              headers={'Client-Id': ozon_ovner, 'Api-Key': api_key,
        #                                       'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        # request_json = request_post.json()
        #
        # if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        #     return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
        #
        # request_items = request_json.get('result')
        #
        # if request_items != None:
        #     for order in request_items:
        #
        #         order_id = order['order_id']
        #         in_process_at = order['in_process_at']
        #         status = order['status']
        #
        #         for items in order['products']:
        #             sku = items['sku']
        #             name = items['name']
        #             quantity = items['quantity']
        #             offer_id = items['offer_id']
        #
        #
        #             if order['analytics_data'] is not None:
        #                 analitics_data = order['analytics_data']
        #                 delivery_place = analitics_data['city'] + analitics_data['region']
        #                 warehouse_name = analitics_data['warehouse_name']
        #             else:
        #                 delivery_place = None
        #                 warehouse_name = None
        #
        #             if order['financial_data'] is not None:
        #                 financial_data = order['financial_data']
        #
        #                 order_products = financial_data['products']
        #                 summ_order_price = sum(
        #                     [order_product['quantity'] * order_product['price'] for order_product in order_products])
        #
        #                 if status == 'delivered' or status == 'cancelled':
        #                     comission_amount = sum([order_product['commission_amount'] for order_product in order_products])
        #
        #                     for order_product in order_products:
        #                         if order_product['picking'] is not None:
        #                             amount = sum(order_product['picking'].amount)
        #                         else:
        #                             amount = None
        #             else:
        #                 summ_order_price = None
        #                 comission_amount = None
        #                 amount = None
        #
        #         Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, price=summ_order_price,
        #                                    user_id=data, delivery_place=delivery_place, warehouse_name=warehouse_name,
        #                                    amount=amount, status=status)



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

                if product_json['marketing_price'] != 0.0 or product_json['marketing_price'] is not None:
                    marketing_price = product_json['marketing_price']
                else:
                    marketing_price = product_json['price']

                sources = product_json['sources']

                for source in sources:
                    sku = source['sku']

            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                # Наработки если понадобится удаление при обновлении товара

                # print(data.pk, sku)
                # old_product_items = Product.objects.filter(sku=sku)
                # print(old_product_items)
                # for old_product_item in old_product_items:
                #
                #     days_for_production = old_product_item["days_for_production"]
                #     reorder_days_of_supply = old_product_item["reorder_days_of_supply"]
                #     unit_price = old_product_item["unit_price"]
                #     logistics_price = old_product_item["logistics_price"]
                #     additional_price = old_product_item["additional_price"]
                #     summ_price = old_product_item["summ_price"]

                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

                Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name,
                                               marketing_price=marketing_price, stock_balance=balance,
                                               reserved=reserved, way_to_warehous=go_to_warehouse, user_id=data)


                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                #Наработки если понадобится удаление товара при обновлении

                # Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name,
                #                                marketing_price=marketing_price, stock_balance=balance,
                #                                way_to_warehous=go_to_warehouse, user_id=data, days_for_production=days_for_production,
                #                                reorder_days_of_supply=reorder_days_of_supply, unit_price=unit_price,
                #                                logistics_price=logistics_price, additional_price=additional_price,
                #                                summ_price=summ_price)

                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@app.task(bind=True)
def found_new_ozon_transaction(*args, **kwargs):

    from product.models import OzonTransactions
    from get_data.models import User

    user_data = User.objects.filter(api_key__isnull=False)

    for user_data in user_data:

        ozon_ovner = str(user_data.ozon_id)

        date_sort = datetime.now() - timedelta(days=1)

        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        yesterday = date_sort.day

        if yesterday < 10:
            date_from = f"{year}-{month}-0{yesterday}T00:00:00Z"
        else:
            date_from = f"{year}-{month}-{yesterday}T00:00:00Z"

        if day < 10:
            date_to = f"{year}-{month}-0{day}T23:30:00Z"
        else:
            date_to = f"{year}-{month}-{day}T23:30:00Z"

        request_post = requests.post('https://api-seller.ozon.ru/v3/finance/transaction/list',
                                     json={
                                            "filter": {
                                                "date": {
                                                    "from": date_from,
                                                    "to": date_to
                                                },

                                                "transaction_type": "all"
                                            },
                                            "page": 1,
                                            "page_size": 10000
                                        },
                                     headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                              'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        request_json = request_post.json()
        if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)

        request_items = request_json.get('result')
        operations = request_items['operations']

        for operation in operations:

            operation_id = operation['operation_id']
            operation_type = operation['operation_type']
            operation_date = operation['operation_date']
            operation_type_name = operation['operation_type_name']
            accruals_for_sale = operation['accruals_for_sale']
            sale_commission = operation['sale_commission']
            amount = operation['amount']
            type = operation['type']

            posting = operation['posting']
            posting_number = posting['posting_number']

            items = operation['items']
            services = operation['services']

            items_array = []
            for item in items:
                name = item['name']
                sku = item['sku']
                dict_item = {
                    'name': name,
                    'sku': sku
                }
                items_array.append(dict_item)

            services_array = []
            for service in services:
                marketplace_services = (
                    'MarketplaceServiceItemFulﬁllment',
                    'MarketplaceServiceItemDirectFlowTrans',
                    'MarketplaceServiceItemReturnFlowTrans',
                    'MarketplaceServiceItemDelivToCustomer',
                    'MarketplaceServiceItemReturnNotDelivToCustomer',
                    'MarketplaceServiceItemReturnPartGoodsCustomer',
                    'MarketplaceServiceItemReturnAfterDelivToCustomer',
                    'MarketplaceServiceItemDropoffFf',
                    'MarketplaceServiceItemDropoffPvz',
                    'MarketplaceServiceItemDropoffSc',
                )

                if service['name'] in marketplace_services:
                    dict_services = {
                        'service_name': service['name'],
                        'price': service['price']
                    }
                    services_array.append(dict_services)

            OzonTransactions.objects.create_ozon_transaction(user_id=user_data, operation_id=operation_id,
                                                             operation_type=operation_type,
                                                             operation_date=operation_date,
                                                             operation_type_name=operation_type_name,
                                                             accruals_for_sale=accruals_for_sale,
                                                             sale_commission=sale_commission,
                                                             amount=amount, type=type, posting_number=posting_number,
                                                             items=items_array, services=services_array)

