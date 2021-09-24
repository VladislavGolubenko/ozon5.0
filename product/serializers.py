import requests
from django.http import QueryDict

from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):


    # def update(self, instance, validated_data):
    #
    #     for objec in validated_data.items():
    #         print(objec)
    # return instance
            # ('days_for_production', 50)
            # ('reorder_days_of_supply', 201)
            # ('unit_price', 2999)
            # ('logistics_price', 200)
            # ('additional_price', 143)



    class Meta:
        model = Product
        fields = ("id", "preview", "ozon_product_id", "sku", "name", "days_for_production", "reorder_days_of_supply", "unit_price", "logistics_price", "additional_price")
