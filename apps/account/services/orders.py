from email import header
import requests
import json
from datetime import datetime, date
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status

from apps.metric.models import OzonMetrics
from ..models import User
from ...order.models import Order
from ...product.models import Product, ProductInOrder


class OrdersOzon:
    def _get_orders(api_key:str, ozon_id:str):
        date_to = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
        url = "https://api-seller.ozon.ru/v2/posting/fbo/list"

        payload = json.dumps({
            "dir": "asc",
            "filter": {
                "since": "2021-02-01T00:00:00Z", 
                "to": date_to
                },
                "limit": 1000,
                "with": {
                "analytics_data": True,
                "financial_data": True,
                }
            }) 
        #"{\n            \"dir\": \"asc\",\n            \"filter\": {\n                \"since\": \"2021-02-01T00:00:00Z\", \n                \"to\": \"2022-01-18T23:59:59Z\"\n                },\n                \"limit\": 1000,\n                \"with\": {\n                \"analytics_data\": true,\n                \"financial_data\": true\n                }\n            }"
        headers = {
        'Client-Id': f'{ozon_id}',
        'Api-Key': f'{api_key}',
        'Content-Type': 'text/plain',
        #'Cookie': 'incap_ses_374_2701794=9OsrZWgeBHwk9MUnh7cwBZ+B5mEAAAAA8rygrrIinR09oktZDQdf6w==; nlbi_2701794=twFoCq7VjgRvFh+ah6p8LAAAAAB0/HlCB5ou3THO4oCyt7mr; visid_incap_2701794=GBOT5EKwQzCRt3d2f91jH5yB5mEAAAAAQUIPAAAAAADzTW4RPiEO/i3NSHCVAkym'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    def get_orders_in_json(api_key:str, ozon_id:str) -> list:
        request_post = OrdersOzon._get_orders(api_key, ozon_id)
        if request_post.json().get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
        return request_post.json().get("result")

    def _add_product_in_order(order:json, order_save:Order, user:User):
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
                                                        user_id=user, sku=sku, name=name, order_id=order_save,
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

    def _create_order(order:json, user:User, ozon_id:int):
        order_id = order.get('order_id')
        posting_number = order.get('posting_number')
        in_process_at = order.get('in_process_at')
        date_of_order = order.get('created_at')
        status2 = order.get('status')  # новое поле
        quantity = 0
        analitics_data = order.get('analytics_data')
        city = None
        region = None
        warehouse_name = None
        warehous_id = None
        delivery_type = None
        if analitics_data is not None:
            city = analitics_data.get('city')
            region = analitics_data.get('region')
            warehouse_name = analitics_data.get('warehouse_name')
            warehous_id = analitics_data.get('warehouse_id')
            delivery_type = analitics_data.get('delivery_type')
        
        order_in_model = Order.objects.filter(posting_number=posting_number)
        if len(order_in_model)==0:
            order_save = Order.objects.create_order(order_id=order_id, in_process_at=in_process_at, user_id=user,
                                                    status=status2, date_of_order=date_of_order,
                                                    posting_number=posting_number, region=region, city=city,
                                                    delivery_type=delivery_type, warehous_id=warehous_id,
                                                    warehouse_name=warehouse_name, marketplace_id=ozon_id,
                                                    is_visible=True)
            OrdersOzon._add_product_in_order(order, order_save, user)


    @staticmethod
    def update_or_create_orders(api_key:str, ozon_id:str, user:User) -> None:
        orders = OrdersOzon.get_orders_in_json(api_key, ozon_id)
        for order in orders:
            OrdersOzon._create_order(order, user, ozon_id)
