from rest_framework import serializers
from .models import Order
from ..product.serializers import ProductInOrderSerializer
from ..product.models import ProductInOrder


class OrderSerializer(serializers.ModelSerializer):
    # get_product_in_order = ProductInOrderSerializer(many=True)
    get_product_in_order = serializers.SerializerMethodField('fun_get_product_in_order')

    class Meta:
        model = Order
        fields = ('id', 'user_id', 'order_number', 'date_of_order', 'in_process_at', 'status', 'posting_number',
                  'region', 'city', 'delivery_type', 'warehous_id', 'warehouse_name', 'creating_date',
                  'get_product_in_order', 'summ_comission', 'amount', 'quantity', 'order_sum')

    def fun_get_product_in_order(self, instance):
        products = ProductInOrder.objects.filter(order_id=instance.pk)
        return ProductInOrderSerializer(products, many=True).data
