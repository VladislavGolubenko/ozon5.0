from ozon.celery import app
from .models import User
from datetime import datetime
import requests
from rest_framework.response import Response
from rest_framework import status
from ..order.models import Order
from ..ozon_transaction.models import OzonTransactions
from ..product.models import ProductInOrder, Product
from .services.products import ProductsOzon


@app.task(bind=True)
def return_user_role(self, user_id):
    user = User.objects.get(pk=user_id)
    user.role = User.USER
    user.save()

@app.task(bind=True)
def create_or_update_products(*args, **kwargs):
    user_id = kwargs.get('user_id')

    user_data = User.objects.get(id=user_id)
    ozon_ovner = str(user_data.ozon_id)
    ProductsOzon.update_or_create_products(user_data.api_key, ozon_ovner, user_data)



@app.task(name="get_order")
def get_order(api_key, client_id, user_id):
    #user_id = kwargs.get('user_id')
    

    user_data = User.objects.get(id=user_id)
    #ozon_ovner = str(user_data.ozon_id)

    date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
    request_post = requests.post('https://api-seller.ozon.ru/v2/posting/fbo/list',
                                 json={"dir": "asc",
                                       "filter": {"since": "2021-02-01T00:00:00Z", "to": date_to},
                                       "limit": 1000,
                                       "with": {
                                           "analytics_data": True,
                                           "financial_data": True,
                                       }
                                       },
                                 headers={'Client-Id': client_id, 'Api-Key': api_key,
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

        order_in_model = Order.objects.filter(posting_number=posting_number)
        print(order_in_model)
        if len(order_in_model)>0:
            print({
                "order_id": order_id,
                "in_process_at": in_process_at,
                "user_data": user_data,
                "status2": status2,
                "date_of_order": date_of_order,
                "posting_number": posting_number,
                "region": region,
                "city": "city",
                "delivery_type": delivery_type,
                "warehous_id": warehous_id,
                "warehouse_name": warehouse_name
            })
        if len(order_in_model)==0:
            order_save = Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, user_id=user_data,
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
                return_after_deliv_to_customer = item_services['marketplace_service_item_return_after_deliv_to_customer']

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
                                                            return_after_deliv_to_customer=return_after_deliv_to_customer,
                                                            days_for_production=days_for_production,
                                                            reorder_days_of_supply=reorder_days_of_supply,
                                                            unit_price=unit_price, logistics_price=logistics_price,
                                                            additional_price=additional_price, summ_price=summ_price)
                i += 1


@app.task(name="get_ozon_transaction")
def get_ozon_transaction(api_key, client_id, user_id):

    #user_id = kwargs.get('user_id')
    

    user_data = User.objects.get(id=user_id)
    #ozon_ovner = str(user_data.ozon_id)

    date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
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
                                 headers={'Client-Id': client_id, 'Api-Key': api_key,
                                          'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
    request_json = request_post.json()
    if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
        return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
    operations = request_json.get('result').get('operations')

    for operation in operations:

        operation_id = operation.get('operation_id')
        operation_type = operation.get('operation_type')
        operation_date = operation.get('operation_date')
        operation_type_name = operation.get('operation_type_name')
        accruals_for_sale = operation.get('accruals_for_sale')
        sale_commission = operation.get('sale_commission')
        amount = operation.get('amount')
        finance_type = operation.get('type')

        posting = operation.get('posting')
        posting_number = posting.get('posting_number')

        items = operation.get('items')
        services = operation.get('services')
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

            if service.get('name') in marketplace_services:
                dict_services = {
                    'service_name': service.get('name'),
                    'price': service.get('price')
                }
                services_array.append(dict_services)
        transaction_in_model = OzonTransactions.objects.filter(operation_id=operation_id)
        if len(transaction_in_model) == 0:
            transaction_save = OzonTransactions.objects.create_ozon_transaction(user_id=user_data, operation_id=operation_id,
                                                            operation_type=operation_type, operation_date=operation_date,
                                                            operation_type_name=operation_type_name,
                                                            accruals_for_sale=accruals_for_sale,
                                                            sale_commission=sale_commission,
                                                            amount=amount, type=finance_type,
                                                            posting_number=posting_number, services=services_array)

            for item in items:
                sku = item['sku']

                order = Order.objects.filter(posting_number=posting_number).first()
                if order:
                    product_relation = ProductInOrder.objects.filter(sku=sku, order_id=order.pk).first()
                    transaction_save.product.add(product_relation.pk)

