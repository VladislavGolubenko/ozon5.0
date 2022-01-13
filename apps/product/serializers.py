from rest_framework import serializers
from .models import (
    Product,
    ProductInOrder
)


class ProductSerializer(serializers.ModelSerializer):
    '''
        изменение продукта представляет собой заполнение input полей (глубина поставки, дней для производства,
        цена юнита, цена логистики, добавленная стоимость)

        Передаем через form-data:
            unit_price
            logistics_price
            additional_price
            days_for_production
            reorder_days_of_supply
    '''

    preview = serializers.CharField(required=False)
    ozon_product_id = serializers.CharField(required=False)
    sku = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        user_id = self.context['request'].user
        sku = self.context['sku']

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        summ_price = validated_data['unit_price'] + validated_data['logistics_price'] + validated_data['additional_price']
        setattr(instance, 'summ_price', summ_price)

        product_in_order_query = ProductInOrder.objects.filter(user_id=user_id.pk, sku=sku)

        for product_in_order in product_in_order_query:
            unit_price = validated_data['unit_price']
            logistics_price = validated_data['logistics_price']
            additional_price = validated_data['additional_price']
            days_for_production = validated_data['days_for_production']
            reorder_days_of_supply = validated_data['reorder_days_of_supply']

            product_in_order.days_for_production = days_for_production
            product_in_order.reorder_days_of_supply = reorder_days_of_supply
            product_in_order.unit_price = unit_price
            product_in_order.logistics_price = logistics_price
            product_in_order.additional_price = additional_price

            product_in_order.sum_price = summ_price
            product_in_order.save()

        instance.save()
        return instance

    class Meta:
        model = Product
        fields = ("id", "preview", "ozon_product_id", "sku", "name", "days_for_production", "reorder_days_of_supply",
                  "unit_price", "logistics_price", "additional_price", "summ_price",  "marketing_price",
                  "order_for_thirty_days", "stock_balance")


class ProductInOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInOrder
        fields = "__all__"






class WarehouseAccountSerializer(serializers.Serializer):
    """
        Сериализатор получения данных складского учета.
        Пример POST запроса: http://.../api/products/warehouse_control/90/

        Обязательные параметры:
            id пользователя (json формат в теле запроса)


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


class CompanyDashbordSerializer(serializers.Serializer):
    """
            Сериализатор получения аналитических данных компании.
            Пример GET запроса: http://.../api/products/analitic_company/?date=700

            Параметры для фильтрации:
                date (через get параметр) - кол-во дней для установки периода


            Поля которые можно получчить:

                roi -- ROI
                marginalit -- Маржинальность в %
                sales -- Продажи
                returns -- Возвраты
                сompensations -- Компенсации и другое
                proceeds -- Выручка
                unit_price -- Себестоимость
                logistics -- Логистика
                additional_price -- Добавленная стоимость
                services -- Услуги
                comissions -- Комиссия
                comissions_by_sales -- Комиссия за продажу
                assembly -- Сборка заказа
                highway -- Магистраль
                last_mile -- Последняя миля
                refunds_cancellations -- Плата за возвраты и отмены
                advertising -- Реклама
                profit -- Прибыль
                cost -- Стоимость товара
                cost_price -- Себестоимость товара
                optional_costs -- Опциональные расходы
                goods_sold -- Товаров продано
                goods_returne -- Товаров возвращенно
    """

    roi = serializers.IntegerField(write_only=True, help_text="ROI")
    marginalit = serializers.IntegerField(write_only=True, help_text="Маржинальность в %")
    sales = serializers.IntegerField(write_only=True, help_text="Продажи")
    returns = serializers.IntegerField(write_only=True, help_text="Возвраты")
    сompensations = serializers.IntegerField(write_only=True, help_text="Компенсации и другое")
    proceeds = serializers.IntegerField(write_only=True, help_text="Выручка")
    unit_price = serializers.IntegerField(write_only=True, help_text="Себестоимость")
    logistics= serializers.IntegerField(write_only=True, help_text="Логистика")
    additional_price = serializers.IntegerField(write_only=True, help_text="Добавленная стоимость")
    services = serializers.IntegerField(write_only=True, help_text="Услуги")
    comissions = serializers.IntegerField(write_only=True, help_text="Комиссия")
    comissions_by_sales = serializers.IntegerField(write_only=True, help_text="Комиссия за продажу")
    assembly = serializers.IntegerField(write_only=True, help_text="Сборка заказа")
    highway = serializers.IntegerField(write_only=True, help_text="Магистраль")
    last_mile = serializers.IntegerField(write_only=True, help_text="Последняя миля")
    refunds_cancellations = serializers.IntegerField(write_only=True, help_text="Плата за возвраты и отмены")
    advertising = serializers.IntegerField(write_only=True, help_text="Реклама")
    profit = serializers.IntegerField(write_only=True, help_text="Прибыль")
    cost = serializers.IntegerField(write_only=True, help_text="Стоимость товара")
    cost_price = serializers.IntegerField(write_only=True, help_text="Себестоимость товара")
    optional_costs = serializers.IntegerField(write_only=True, help_text="Опциональные расходы")
    goods_sold = serializers.IntegerField(write_only=True, help_text="Товаров продано")
    goods_returne= serializers.IntegerField(write_only=True, help_text="Товаров возвращенно")



