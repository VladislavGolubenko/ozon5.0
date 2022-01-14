from django.db import models
from ..account.models import User
from django.db.models.signals import post_save, pre_save
from datetime import datetime, date
from datetime import timedelta
from ..order.models import Order 

class ProductManager(models.Manager):
    def create_product(self, preview, ozon_product_id, sku, name, stock_balance, way_to_warehous, marketing_price,
                       reserved, user_id):

        product = self.create(preview=preview, ozon_product_id=ozon_product_id, sku=sku, name=name,
                              stock_balance=stock_balance, way_to_warehous=way_to_warehous,
                              marketing_price=marketing_price, reserved=reserved, user_id=user_id)
        return product


class ProductInOrderManager(models.Manager):
    def create_product_in_order(self, preview, user_id, order_id, sku, name, quantity, offer_id, price, price_f,
                                comission_amount, payout, return_after_deliv_to_customer,
                                product_id, fulfillment, direct_flow_trans, return_flow_trans, deliv_to_customer,
                                return_not_deliv_to_customer, return_part_goods_customer, days_for_production,
                                reorder_days_of_supply, unit_price, logistics_price, additional_price, summ_price):

        product_in_order = self.create(preview=preview,
                                       user_id=user_id, order_id=order_id, sku=sku, name=name, quantity=quantity,
                                       offer_id=offer_id, price=price, comission_amount=comission_amount, payout=payout,
                                       product_id=product_id, fulfillment=fulfillment,
                                       direct_flow_trans=direct_flow_trans,
                                       return_flow_trans=return_flow_trans, deliv_to_customer=deliv_to_customer,
                                       return_not_deliv_to_customer=return_not_deliv_to_customer, price_f=price_f,
                                       return_part_goods_customer=return_part_goods_customer,
                                       return_after_deliv_to_customer=return_after_deliv_to_customer,
                                       days_for_production=days_for_production,
                                       reorder_days_of_supply=reorder_days_of_supply, unit_price=unit_price,
                                       logistics_price=logistics_price, additional_price=additional_price,
                                       summ_price=summ_price)
        return product_in_order


class Product(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products_to_user", null=True, blank=True)
    preview = models.CharField(max_length=300, verbose_name='Превью')
    ozon_product_id = models.IntegerField(verbose_name='ID товара')
    sku = models.CharField(max_length=100, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    days_for_production = models.IntegerField(blank=True, null=True, verbose_name='Времени необходимо для производства')
    reorder_days_of_supply = models.IntegerField(blank=True, null=True, verbose_name='Глубина поставки')
    unit_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена юнита')
    logistics_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена логистики')
    additional_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Дополнительные затраты')
    summ_price = models.FloatField(blank=True, null=True, verbose_name='Итого')
    marketing_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена')
    stock_balance = models.IntegerField(verbose_name="Остатки на складе", null=True)
    way_to_warehous = models.IntegerField(verbose_name="В пути на склад", null=True)
    reserved = models.IntegerField(verbose_name="Зарезервировано", blank=True, null=True)
    creating_date = models.DateField(auto_now_add=True, blank=True, null=True)
    objects = ProductManager()

    @property
    def order_for_thirty_days(self):
        date_sort = datetime.now() - timedelta(days=30)
        orders = Order.objects.filter(date_of_order__gte=date_sort, user_id=self.user_id)
        thirty_days = []
        for order in orders:

            products_in_order = ProductInOrder.objects.filter(order_id=order.pk)
            for product_in_order in products_in_order:
                if product_in_order.sku == self.sku:
                    thirty_days.append(product_in_order)

        lenth_thirty_days = len(thirty_days)
        return lenth_thirty_days

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['id']


class ProductInOrder(models.Model):

    preview = models.CharField(max_length=300, verbose_name='Превью', null=True, blank=True)
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orderproduct_to_user",
        null=True,
        blank=True
    )

    order_id = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="orderproduct_to_order",
        null=True,
        blank=True
    )

    sku = models.CharField(max_length=100, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    quantity = models.IntegerField(verbose_name='Кол-во')
    offer_id = models.CharField(max_length=100, verbose_name="Номер предложения")
    price = models.FloatField(verbose_name="Цена товара")
    price_f = models.FloatField(verbose_name="Цена товара в заказе", blank=True, null=True)
    comission_amount = models.FloatField(verbose_name="Сумма комиссий")
    payout = models.FloatField(verbose_name="Cтоимость товара")
    product_id = models.IntegerField("ID продукта")
    fulfillment = models.FloatField(verbose_name="Выполнение предмета услуг на торговой площадке")
    direct_flow_trans = models.FloatField(verbose_name="Транзит товара на маркетплейсе")
    return_flow_trans = models.FloatField(verbose_name="Возврат товара через")
    deliv_to_customer = models.FloatField(verbose_name="Доставка товара покупателю")
    return_not_deliv_to_customer = models.FloatField(verbose_name="Возврат товара от покупателя")
    return_part_goods_customer = models.FloatField(verbose_name="Возврат части заказа покупателю")
    return_after_deliv_to_customer = models.FloatField(verbose_name="Возврат доставленного товара")
    days_for_production = models.IntegerField(blank=True, null=True, verbose_name='Времени необходимо для производства')
    reorder_days_of_supply = models.IntegerField(blank=True, null=True, verbose_name='Глубина поставки')
    unit_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена юнита')
    logistics_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена логистики')
    additional_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Дополнительные затраты')
    summ_price = models.FloatField(blank=True, null=True, verbose_name='Итого')
    creating_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.sku)

    class Meta:
        verbose_name = 'заказаный товар'
        verbose_name_plural = 'заказаные товары'
        ordering = ['id']

    objects = ProductInOrderManager()
