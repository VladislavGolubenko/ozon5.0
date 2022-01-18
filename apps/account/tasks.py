from ast import Or
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
from .services.orders import OrdersOzon

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