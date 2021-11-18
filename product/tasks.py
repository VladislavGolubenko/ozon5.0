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
    from product.models import Order, ProductInOrder, OzonTransactions, Product

    user_data = User.objects.get(email=email)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_to = f"{year}-{month}-0{day}T00:00:00Z"
    else:
        date_to = f"{year}-{month}-{day}T23:30:00Z"


    request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                 json={"dir": "asc",
                                       "filter": {"since": "2021-02-01T00:00:00Z", "to": date_to},
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
        status2 = order['status']  # новое поле
        quantity = 0

        if order['analytics_data'] is not None:
            analitics_data = order['analytics_data']
            city = analitics_data['city']
            region = analitics_data['region']
            warehouse_name = analitics_data['warehouse_name']
            warehous_id = analitics_data['warehouse_id']
            delivery_type = analitics_data['delivery_type']
        else:
            city = None
            region = None
            warehouse_name = None
            warehous_id = None
            delivery_type = None

        order_save = Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, user_id=user_data,
                                                status=status2, date_of_order=date_of_order,
                                                posting_number=posting_number, region=region, city=city,
                                                delivery_type=delivery_type, warehous_id=warehous_id,
                                                warehouse_name=warehouse_name)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
            fulfillment = item_services['marketplace_service_item_fulfillment']
            direct_flow_trans = item_services['marketplace_service_item_direct_flow_trans']
            return_flow_trans = item_services['marketplace_service_item_return_flow_trans']
            deliv_to_customer = item_services['marketplace_service_item_deliv_to_customer']
            return_not_deliv_to_customer = item_services['marketplace_service_item_return_not_deliv_to_customer']
            return_part_goods_customer = item_services['marketplace_service_item_return_part_goods_customer']
            return_after_deliv_to_customer = item_services['marketplace_service_item_return_after_deliv_to_customer']

            image_queryset = Product.objects.filter(sku=sku).first()

            if image_queryset is not None:
                preview = image_queryset.preview
            else:
                preview = None

            ProductInOrder.objects.create_product_in_order(preview=preview,
                                                           user_id=user_data, sku=sku, name=name, order_id=order_save,
                                                           quantity=quantity, offer_id=offer_id, price=price,
                                                           price_f=price_f, comission_amount=comission_amount,
                                                           payout=payout, product_id=product_id,
                                                           fulﬁllment=fulfillment,
                                                           direct_flow_trans=direct_flow_trans,
                                                           return_flow_trans=return_flow_trans,
                                                           deliv_to_customer=deliv_to_customer,
                                                           return_not_deliv_to_customer=return_not_deliv_to_customer,
                                                           return_part_goods_customer=return_part_goods_customer,
                                                           return_after_deliv_to_customer=return_after_deliv_to_customer)
            i += 1
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@app.task(bind=True)
def get_ozon_transaction(*args, **kwargs):

    email = kwargs.get('email')
    from product.models import OzonTransactions, Order, ProductInOrder

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

            if posting_number is not None and posting_number != '':
                order_id = Order.objects.filter(posting_number=posting_number).first()

                if order_id is not None:
                    price_query = Order.objects.get(sku=sku, id=order_id.pk)
                    dict_item = {
                        'name': name,
                        'sku': sku,
                        'price': price_query['price']
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


        request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                     json={"dir": "asc",
                                           "filter": {"since": date_from, "to": date_to},
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
            status2 = order['status']  # новое поле
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
                                                    status=status2, date_of_order=date_of_order,
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
                fulfllment = item_services['marketplace_service_item_fulfillment']
                direct_fow_trans = item_services['marketplace_service_item_direct_flow_trans']
                return_fow_trans = item_services['marketplace_service_item_return_flow_trans']
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
                                                               fulﬁllment=fulfllment,
                                                               direct_flow_trans=direct_fow_trans,
                                                               return_flow_trans=return_fow_trans,
                                                               deliv_to_customer=deliv_to_customer,
                                                               return_not_deliv_to_customer=return_not_deliv_to_customer,
                                                               return_part_goods_customer=return_part_goods_customer,
                                                               return_after_deliv_to_customer=return_after_deliv_to_customer)
                i += 1

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


@app.task(bind=True)
def get_analitic_data(*args, **kwargs):
    email = kwargs.get('email')

    from product.models import OzonMetrics
    user_data = User.objects.get(email=email)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_from = f"{year}-{month}-0{day}T00:00:00Z"
        date_to = f"{year}-{month}-0{day}T23:55:00Z"
    else:
        date_from = f"{year}-{month}-{day}T00:00:00Z"
        date_to = f"{year}-{month}-{day}T23:55:00Z"

    request_post = requests.post('https://api-seller.ozon.ru/v1/analytics/data',
                                 json={
                                        "date_from": date_from,
                                        "date_to": date_to,
                                        "dimension": [
                                            "sku"
                                        ],
                                        "limit": 1000,
                                        "metrics": [
                                            "hits_view_search",
                                            "hits_view_pdp",
                                            "hits_view",
                                            "hits_tocart_search",
                                            "hits_tocart_pdp",
                                            "hits_tocart",
                                            "session_view_search",
                                            "session_view_pdp",
                                            "session_view",
                                            "conv_tocart_search",
                                            "conv_tocart_pdp",
                                            "conv_tocart",
                                            "revenue",
                                            "returns",
                                            "cancellations",
                                            "ordered_units",
                                            "delivered_units",
                                            "adv_view_pdp",
                                            "adv_view_search_category",
                                            "adv_view_all",
                                            "adv_sum_all",
                                            "position_category",
                                            "postings",
                                            "postings_premium"
                                        ],
                                        "offset": 0,
                                        "sort": [
                                            {
                                                "key": "hits_view",
                                                "order": "ASC"
                                            }
                                        ]
                                    },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    result = request_json['result']
    datas = result['data']

    for data in datas:
        dimensions = data['dimensions']

        for dimension in dimensions:
            product_id = dimension['id']
            product_name = dimension['name']

        metrics = data['metrics']
        hits_view_search = metrics[0]
        hits_view_pdp = metrics[1]
        hits_view = metrics[2]
        hits_tocart_search = metrics[3]
        hits_tocart_pdp = metrics[4]
        hits_tocart = metrics[5]
        session_view_search = metrics[6]
        session_view_pdp = metrics[7]
        session_view = metrics[8]
        conv_tocart_search = metrics[9]
        conv_tocart_pdp = metrics[10]
        conv_tocart = metrics[11]
        revenue = metrics[12]
        returns = metrics[13]
        cancellations = metrics[14]
        ordered_units = metrics[15]
        delivered_units = metrics[16]
        adv_view_pdp = metrics[17]
        adv_view_search_category = metrics[18]
        adv_view_all = metrics[19]
        adv_sum_all = metrics[20]
        position_category = metrics[21]
        postings = metrics[22]
        postings_premium = metrics[23]

        OzonMetrics.objects.create_ozon_metrics(user_id=user_data, product_id=product_id, product_name=product_name,
                                                hits_view_search=hits_view_search, hits_view_pdp=hits_view_pdp,
                                                hits_view=hits_view, hits_tocart_search=hits_tocart_search,
                                                hits_tocart_pdp=hits_tocart_pdp, hits_tocart=hits_tocart,
                                                session_view_search=session_view_search,
                                                session_view_pdp=session_view_pdp, session_view=session_view,
                                                conv_tocart_search=conv_tocart_search, conv_tocart_pdp=conv_tocart_pdp,
                                                conv_tocart=conv_tocart, revenue=revenue, returns=returns,
                                                cancellations=cancellations, ordered_units=ordered_units,
                                                delivered_units=delivered_units, adv_view_pdp=adv_view_pdp,
                                                adv_view_search_category=adv_view_search_category,
                                                adv_view_all=adv_view_all,
                                                adv_sum_all=adv_sum_all, position_category=position_category,
                                                postings=postings,
                                                postings_premium=postings_premium)


@app.task(bind=True)
def update_analitics_data(*args, **kwargs):

    email = kwargs.get('email')
    date = kwargs.get('today')

    from product.models import OzonMetrics
    user_data = User.objects.get(email=email)
    ozon_ovner = str(user_data.ozon_id)

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if day < 10:
        date_from = f"{year}-{month}-0{day}T00:00:00Z"
        date_to = f"{year}-{month}-0{day}T23:55:00Z"
    else:
        date_from = f"{year}-{month}-{day}T00:00:00Z"
        date_to = f"{year}-{month}-{day}T23:55:00Z"

    request_post = requests.post('https://api-seller.ozon.ru/v1/analytics/data',
                                 json={
                                     "date_from": date_from,
                                     "date_to": date_to,
                                     "dimension": [
                                         "sku"
                                     ],
                                     "limit": 1000,
                                     "metrics": [
                                         "hits_view_search",
                                         "hits_view_pdp",
                                         "hits_view",
                                         "hits_tocart_search",
                                         "hits_tocart_pdp",
                                         "hits_tocart",
                                         "session_view_search",
                                         "session_view_pdp",
                                         "session_view",
                                         "conv_tocart_search",
                                         "conv_tocart_pdp",
                                         "conv_tocart",
                                         "revenue",
                                         "returns",
                                         "cancellations",
                                         "ordered_units",
                                         "delivered_units",
                                         "adv_view_pdp",
                                         "adv_view_search_category",
                                         "adv_view_all",
                                         "adv_sum_all",
                                         "position_category",
                                         "postings",
                                         "postings_premium"
                                     ],
                                     "offset": 0,
                                     "sort": [
                                         {
                                             "key": "hits_view",
                                             "order": "ASC"
                                         }
                                     ]
                                 },
                                 headers={'Client-Id': ozon_ovner, 'Api-Key': user_data.api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    result = request_json['result']
    datas = result['data']

    for data in datas:
        dimensions = data['dimensions']

        for dimension in dimensions:
            product_id = dimension['id']
            product_name = dimension['name']

        metrics = data['metrics']
        hits_view_search = metrics[0]
        hits_view_pdp = metrics[1]
        hits_view = metrics[2]
        hits_tocart_search = metrics[3]
        hits_tocart_pdp = metrics[4]
        hits_tocart = metrics[5]
        session_view_search = metrics[6]
        session_view_pdp = metrics[7]
        session_view = metrics[8]
        conv_tocart_search = metrics[9]
        conv_tocart_pdp = metrics[10]
        conv_tocart = metrics[11]
        revenue = metrics[12]
        returns = metrics[13]
        cancellations = metrics[14]
        ordered_units = metrics[15]
        delivered_units = metrics[16]
        adv_view_pdp = metrics[17]
        adv_view_search_category = metrics[18]
        adv_view_all = metrics[19]
        adv_sum_all = metrics[20]
        position_category = metrics[21]
        postings = metrics[22]
        postings_premium = metrics[23]

        if date is not None:
            date = datetime.now().date()
            metrics_to_update = OzonMetrics.objects.filter(product_id=product_id, creating_date=date)
        else:
            date = datetime.now().date() - timedelta(1)
            metrics_to_update = OzonMetrics.objects.filter(product_id=product_id, creating_date=date)

        metrics_to_update.update(user_id=user_data, product_id=product_id, product_name=product_name,
                                 hits_view_search=hits_view_search, hits_view_pdp=hits_view_pdp, hits_view=hits_view,
                                 hits_tocart_search=hits_tocart_search, hits_tocart_pdp=hits_tocart_pdp,
                                 hits_tocart=hits_tocart, session_view_search=session_view_search,
                                 session_view_pdp=session_view_pdp, session_view=session_view,
                                 conv_tocart_search=conv_tocart_search, conv_tocart_pdp=conv_tocart_pdp,
                                 conv_tocart=conv_tocart, revenue=revenue, returns=returns, cancellations=cancellations,
                                 ordered_units=ordered_units, delivered_units=delivered_units, adv_view_pdp=adv_view_pdp,
                                 adv_view_search_category=adv_view_search_category, adv_view_all=adv_view_all,
                                 adv_sum_all=adv_sum_all, position_category=position_category, postings=postings,
                                 postings_premium=postings_premium)