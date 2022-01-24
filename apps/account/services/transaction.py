from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
import requests
from ...ozon_transaction.models import OzonTransactions
from ...order.models import Order
from ...product.models import ProductInOrder
from ...account.models import User


class TransactionOzon:
    def get_total_pages(api_key:str, ozon_id:str):
        # НУЖНО ИСПОЛЬЗОВАТЬ ДАТУ ПОСЛЕДНЕГО С 00:00:00 что бы подгружать транзакции не все
        #last_transaction= OzonTransactions.objects.all().order_by("-operation_date").first()
        #print(f"!!!!!!!! {last_transaction.operation_date}")
        date_now = datetime.now() - timedelta(days=2)
        date_from = date_now.strftime(f"%Y-%m-{date_now.day}T00:00:00Z")
        date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
        request_post = requests.post('https://api-seller.ozon.ru/v3/finance/transaction/list',
                                    json={
                                            "filter": {
                                                "date": {
                                                    "from": date_from,
                                                    "to": date_to,
                                                },

                                                "transaction_type": "all"
                                            },
                                            "page": 1,
                                            "page_size": 100
                                        },
                                    headers={'Client-Id': ozon_id, 'Api-Key': api_key,
                                            'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
        page_count = request_post.json().get("result").get("page_count")
        return page_count

    def get_transactions(api_key:str, ozon_id:str):
        date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
        total_page = TransactionOzon.get_total_pages(api_key, ozon_id)
        transactions = list()
        for page in range(total_page):
            print(page+1)
            request_post = requests.post('https://api-seller.ozon.ru/v3/finance/transaction/list',
                                        json={
                                                "filter": {
                                                    "date": {
                                                        "from": "2021-02-01T00:00:00Z",
                                                        "to": date_to,
                                                    },

                                                    "transaction_type": "all"
                                                },
                                                "page": page+1,
                                                "page_size": 100
                                            },
                                        headers={'Client-Id': ozon_id, 'Api-Key': api_key,
                                                'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
            request_json = request_post.json()
            if request_json.get('messege', None) == 'Invalid Api-Key, please contact support':
                return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
            transactions += (request_json.get('result').get('operations'))
        return transactions

    def create_transaction(operation, user):
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
            transaction_save = OzonTransactions.objects.create_ozon_transaction(user_id=user, operation_id=operation_id,
                                                            operation_type=operation_type, operation_date=operation_date,
                                                            operation_type_name=operation_type_name,
                                                            accruals_for_sale=accruals_for_sale,
                                                            sale_commission=sale_commission,
                                                            amount=amount, type=finance_type,
                                                            posting_number=posting_number, services=services_array)

            comissions = OzonTransactions.objects.filter(posting_number=transaction_save.posting_number)
            comissions_summ = 0



            for item in items:
                sku = item['sku']

                order = Order.objects.filter(posting_number=posting_number).first()
                if order:
                    product_relation = ProductInOrder.objects.filter(sku=sku, order_id=order.pk).first()
                    transaction_save.product.add(product_relation.pk)

    def create_transactions(api_key: str, ozon_id: str, user):
        operations = TransactionOzon.get_transactions(api_key, ozon_id)
        #print(transactions)
        #operations = transactions
        for operation in operations:
            TransactionOzon.create_transaction(operation, user)
