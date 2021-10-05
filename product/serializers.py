import requests
from django.http import QueryDict

from rest_framework import serializers
from .models import Product
import os
import datetime


class ProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        print(type(validated_data))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        summ_price = validated_data['unit_price'] + validated_data['logistics_price'] + validated_data['additional_price']

        # history = requests.post('https://api-seller.ozon.ru/v2/product/info', json={"product_id": product_id_object['product_id']},
        #         headers={'Client-Id': '100524', 'Api-Key': '8ca8166a-2e3f-4940-8cc8-daf8100ca758',
        #         'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

        # average_order_speed

        # if validated_data['reorder_days_of_supply'] >= 3.12:
        #     status = "Заказать Сейчас"
        # elif validated_data['reorder_days_of_supply'] < 1.2 and validated_data['reorder_days_of_supply']
        # status = "Заказать скоро"
        # status = "В наличии"
        # status = "Избыток"

        # reordering_date
        # need_to_order
        # reorder_summ
        # reorder_profit
        # stock_for_days
        # deliveries
        # return_product
        # stock_profit
        # stock_price
        # potential_profit
        # average_unit_profit

        print(validated_data['days_for_production'], validated_data['reorder_days_of_supply'], validated_data['unit_price'], validated_data['logistics_price'], validated_data['additional_price'])
        # instance.save()
        return instance



    class Meta:
        model = Product
        fields = ("id", "preview", "ozon_product_id", "sku", "name", "days_for_production", "reorder_days_of_supply", "unit_price", "logistics_price", "additional_price")
