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
                  "unit_price", "logistics_price", "additional_price", "summ_price",  "marketing_price")


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'name', 'order_number', 'sku', 'date_of_order', 'order_place', 'shipping_warehouse',
                  'number', 'price', 'comission', 'profit', 'status')


class WarehouseAccountSerializer(serializers.Serializer):
    """
        Сериализатор получения данных складского учета.
        Пример POST запроса: http://.../api/products/warehouse_control/90/

        Обязательные параметры:

            email


        Поля которые можно получчить:

            preview -- 'Превью',
            ozon_product_id -- 'ID проекта на озоне',
            sku -- 'СКУ',
            name -- 'Название',
            stock_balance -- 'Кол-во остатков',
            orders_by_period -- 'Заказов за выбранный период',
            orders_speed -- 'Скорость заказа',
            days_for_production -- 'Дней необходимо для производства',
            reorder_days_of_supply -- 'Глубина поставки',
            potencial_proceeds -- 'Потенциальная выручка остатков',
            product_price -- 'Цена продукта',
            stocks_for_days -- 'Остатков на дней',
            need_to_order -- 'Необходимо заказать',
            stocks_cost_price -- 'Себестоимость остатков',
            reorder_sum -- 'Cумма перезаказа'
    """

    # username = serializers.CharField(max_length=255, write_only=True, help_text="логин")
    # password = serializers.CharField(max_length=128, write_only=True, help_text="пароль")
    #
    # # Ignore these fields if they are included in the request.
    #
    # token = serializers.CharField(max_length=255, read_only=True)

    preview = serializers.CharField(max_length=300, write_only=True, help_text="Превью")
    ozon_product_id = serializers.IntegerField(write_only=True, help_text="ID продукта на озоне")
    sku = serializers.CharField(max_length=100, write_only=True, help_text="СКУ")
    name = serializers.CharField(max_length=300, write_only=True, help_text="Название продукта")
    stock_balance = serializers.IntegerField(help_text="Остатки на складе", write_only=True)
    orders_by_period = serializers.IntegerField(help_text="Заказано за период", write_only=True)
    orders_speed = serializers.FloatField(help_text="Средняя скорость заказов", write_only=True)
    days_for_production = serializers.IntegerField(help_text="Срок производства", write_only=True)
    reorder_days_of_supply = serializers.IntegerField(help_text="Глубина поставки", write_only=True)
    potencial_proceeds = serializers.FloatField(help_text="Потенциальная выручка остатков", write_only=True)
    product_price = serializers.FloatField(help_text="Стоимость товара", write_only=True)
    stocks_for_days = serializers.IntegerField(help_text="Остатков на дней", write_only=True)
    need_to_order = serializers.FloatField(help_text="Необходимо заказать", write_only=True)
    stocks_cost_price = serializers.FloatField(help_text="Себестоимость остатков", write_only=True)
    reorder_sum = serializers.FloatField(help_text="Cумма перезаказа", write_only=True)

