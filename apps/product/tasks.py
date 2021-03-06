import requests
from datetime import datetime, date
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status

from .models import ProductInOrder, Product
#from product.models import OzonMetrics
from ..account.models import User
from ozon.celery import app
from ..ozon_transaction.models import OzonTransactions
from ..order.models import Order

@app.task(bind=True, name="update_product_order")
def update_product_order(*args, **kwargs):
    user_data = User.objects.all()#filter(api_key__isnull=False)

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
        #print(data)
        for marketplace_data in data.marketplace_data.all():
            #print(marketplace_data)
            #print("--"*50)
            """
            marketplace_id
            api_key
            """
            ozon_ovner = str(marketplace_data.marketplace_id)
            api_key = marketplace_data.api_key

            # Заказы
            date_sort = datetime.now() - timedelta(days=1)
            
            date_from = date_sort.strftime("%Y-%m-%dT00:00:00Z")
            date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
            print(date_from)
            print(date_to)
            # if yesterday < 10:
            #     date_from = f"{year}-{month}-0{yesterday}T00:00:00Z"
            # else:
            #     date_from = f"{year}-{month}-{yesterday}T00:00:00Z"

            # if day < 10:
            #     date_to = f"{year}-{month}-0{day}T23:30:00Z"
            # else:
            #     date_to = f"{year}-{month}-{day}T23:30:00Z"


            request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                        json={"dir": "asc",
                                            "filter": {"since": date_from, "to": date_to},
                                            "limit": 1000,
                                            "with": {
                                                "analytics_data": True,
                                                "financial_data": True,
                                            }
                                            },
                                        headers={'Client-Id': str(ozon_ovner), 'Api-Key': str(api_key),
                                                'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
            request_json = request_post.json()

            if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
                return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
            print(request_json)
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
                order_in_model = Order.objects.filter(posting_number=posting_number)
                print(order_in_model)
                if len(order_in_model)==0:
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
                        fulfillment = item_services['marketplace_service_item_fulfillment']
                        direct_flow_trans = item_services['marketplace_service_item_direct_flow_trans']
                        return_flow_trans = item_services['marketplace_service_item_return_flow_trans']
                        deliv_to_customer = item_services['marketplace_service_item_deliv_to_customer']
                        return_not_deliv_to_customer = item_services['marketplace_service_item_return_not_deliv_to_customer']
                        return_part_goods_customer = item_services['marketplace_service_item_return_part_goods_customer']
                        return_after_deliv_to_customer = item_services[
                            'marketplace_service_item_return_after_deliv_to_customer']

                        image_queryset = Product.objects.filter(sku=sku).first()

                        if image_queryset is not None:
                            preview = image_queryset.preview
                        else:
                            preview = None

                        """
                        Данные которые вводит пользователь каждому товару (глубина поставки, время на производство себестоимость и тд
                        """
                        product_data_query = Product.objects.filter(sku=sku).first()

                        if product_data_query is not None:
                            days_for_production = product_data_query.days_for_production
                            reorder_days_of_supply = product_data_query.reorder_days_of_supply
                            unit_price = product_data_query.unit_price
                            logistics_price = product_data_query.logistics_price
                            additional_price = product_data_query.additional_price
                            summ_price = unit_price + logistics_price + additional_price
                        else:
                            days_for_production = None
                            reorder_days_of_supply = None
                            unit_price = None
                            logistics_price = None
                            additional_price = None
                            summ_price = None

                        ProductInOrder.objects.create_product_in_order(preview=preview,
                                                                    user_id=data, sku=sku, name=name,
                                                                    order_id=order_save,
                                                                    quantity=quantity, offer_id=offer_id, price=price,
                                                                    price_f=price_f, comission_amount=comission_amount,
                                                                    payout=payout, product_id=product_id,
                                                                    fulﬁllment=fulfillment,
                                                                    direct_flow_trans=direct_flow_trans,
                                                                    return_flow_trans=return_flow_trans,
                                                                    deliv_to_customer=deliv_to_customer,
                                                                    return_not_deliv_to_customer=return_not_deliv_to_customer,
                                                                    return_part_goods_customer=return_part_goods_customer,
                                                                    return_after_deliv_to_customer=return_after_deliv_to_customer,
                                                                    days_for_production=days_for_production,
                                                                    reorder_days_of_supply=reorder_days_of_supply,
                                                                    unit_price=unit_price, logistics_price=logistics_price,
                                                                    additional_price=additional_price, summ_price=summ_price)
                        i += 1

                # Товары

                request_post = requests.post('https://api-seller.ozon.ru/v1/product/list',
                                            headers={'Client-Id': str(ozon_ovner), 'Api-Key': str(api_key),
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
                                                        headers={'Client-Id': str(ozon_ovner), 'Api-Key': str(api_key),
                                                                'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
                        product_json_result = product_request.json()
                        product_json = product_json_result['result']

                        ozon_id = product_json['id']
                        preview = product_json['primary_image']
                        #print(product_json['marketing_price'] != 0.0)
                        #print(product_json['marketing_price'] is not None)
                        #print(product_json['marketing_price'] != "")
                        #print("price", product_json['price'])
                        #print('marketing_price', product_json['marketing_price'])
                        if (product_json['marketing_price'] != 0.0) or (product_json['marketing_price'] is not None) or (product_json['marketing_price'] != ""):
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
                                                    headers={'Client-Id': str(ozon_ovner),
                                                            'Api-Key': str(api_key),
                                                            'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

                        try:
                            return_query_result = return_query['result']
                            return_product = return_query_result['count']  # кол-во возвращенных товаров
                        except TypeError:
                            return_product = 0  # кол-во возвращенных товаров

                        go_to_warehouse = return_product + coming  # в пути на склад (поставки + возвращенные товары)

                        ozon_id = int(ozon_id)

                        print(f"marketing_price: {marketing_price},  id: {product_json['id']}")
                        Product.objects.create_product(preview=preview, ozon_product_id=ozon_id, sku=sku, name=name,
                                                    marketing_price=marketing_price, stock_balance=balance,
                                                    reserved=reserved, way_to_warehous=go_to_warehouse, user_id=data)


@app.task(bind=True, name="found_new_ozon_transaction")
def found_new_ozon_transaction(*args, **kwargs):


    user_data = User.objects.all()
    for data in user_data:
        for marketplace_data in data.marketplace_data.all():
            ozon_ovner = str(marketplace_data.marketplace_id)
            api_key = marketplace_data.api_key
        

            date_sort = datetime.now() - timedelta(days=1)

            date_from = date_sort.strftime("%Y-%m-%dT00:00:00Z")
            date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")

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
                                        headers={'Client-Id': str(ozon_ovner), 'Api-Key': str(api_key),
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
                finance_type = operation['type']

                posting = operation['posting']
                posting_number = posting['posting_number']

                items = operation['items']
                services = operation['services']

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

                transaction_save = OzonTransactions.objects.create_ozon_transaction(user_id=data, operation_id=operation_id,
                                                                                    operation_type=operation_type,
                                                                                    operation_date=operation_date,
                                                                                    operation_type_name=operation_type_name,
                                                                                    accruals_for_sale=accruals_for_sale,
                                                                                    sale_commission=sale_commission,
                                                                                    amount=amount, type=finance_type,
                                                                                    posting_number=posting_number,
                                                                                    services=services_array)

                for item in items:
                    sku = item['sku']

                    order = Order.objects.filter(posting_number=posting_number).first()
                    if order:
                        product_relation = ProductInOrder.objects.filter(sku=sku, order_id=order.pk).first()
                        transaction_save.product.add(product_relation.pk)


