from rest_framework import serializers
from .models import Order
from ..product.serializers import ProductInOrderSerializer


class OrderSerializer(serializers.ModelSerializer):
    get_product_in_order = ProductInOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'user_id', 'order_number', 'date_of_order', 'in_process_at', 'status', 'posting_number',
                  'region', 'city', 'delivery_type', 'warehous_id', 'warehouse_name', 'creating_date',
                  'get_product_in_order', 'get_summ_comission', 'get_amount')