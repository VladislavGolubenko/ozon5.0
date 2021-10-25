from rest_framework import serializers
from django_filters import rest_framework as filters
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        print(type(validated_data))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            print(attr, value)

        summ_price = validated_data['unit_price'] + validated_data['logistics_price'] + validated_data['additional_price']
        setattr(instance, 'summ_price', summ_price)

        instance.save()
        return instance

    class Meta:
        model = Product
        fields = ("id", "preview", "ozon_product_id", "sku", "name", "days_for_production", "reorder_days_of_supply",
                  "unit_price", "logistics_price", "additional_price", "summ_price")



class OrderSerializer(serializers.ModelSerializer):



    class Meta:
        model = Order
        fields = ('id', 'name', 'order_number', 'sku', 'date_of_order', 'order_place', 'shipping_warehouse',
                  'number', 'price', 'comission', 'profit', 'status')
