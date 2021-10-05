from django.db import models
from get_data.models import User
from django.db.models.signals import post_save, pre_save


class ProductManager(models.Manager):
    def create_product(self, preview, ozon_product_id, sku, name, stock_balance, way_to_warehous, user_id):
        product = self.create(preview=preview, ozon_product_id=ozon_product_id, sku=sku, name=name, stock_balance=stock_balance, way_to_warehous=way_to_warehous, user_id=user_id)
        return product
    #
    # def math_data_product(self, days_for_production, reorder_days_of_supply, unit_price, logistics_price, additional_price, summ_price, stock_balance, history, average_order_speed, status, reordering_date, need_to_order, reorder_summ, reorder_profit, stock_for_days, deliveries, return_product, way_to_warehous, stock_profit, stock_price, potential_profit, average_unit_profit):
    #     product = self.update


class Product(models.Model):

    preview = models.CharField(max_length=300, verbose_name='Превью')
    ozon_product_id = models.IntegerField(verbose_name='ID товара')
    sku = models.CharField(max_length=100, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    days_for_production = models.IntegerField(blank=True, null=True, verbose_name='Времени необходимо для производства')
    reorder_days_of_supply = models.IntegerField(blank=True, null=True, verbose_name='Дни повторного заказа поставки')
    unit_price = models.IntegerField(blank=True, null=True, default=0, verbose_name='Цена юнита')
    logistics_price = models.IntegerField(blank=True, null=True, default=0, verbose_name='Цена логистики')
    additional_price = models.IntegerField(blank=True, null=True, default=0, verbose_name='Дополнительные затраты')
    summ_price = models.IntegerField(blank=True, null=True, verbose_name='Итого')

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products_to_user", null=True, blank=True)
    # products = models.ManyToManyField(Product, related_name="user_to_products", null=True, blank=True)

    stock_balance = models.IntegerField(verbose_name="Остатки на складе", null=True)
    history = models.IntegerField(blank=True, null=True, verbose_name="История продаж")
    average_order_speed = models.IntegerField(blank=True, null=True, verbose_name="Средняя скорость заказа")
    status = models.CharField(max_length=100, verbose_name="Статус закааза", default="wait")
    reordering_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата перезаказа")
    need_to_order = models.IntegerField(blank=True, null=True, verbose_name="Необбходимо заказать")
    reorder_summ = models.IntegerField(blank=True, null=True, verbose_name="Сумма перезаказа")
    reorder_profit = models.IntegerField(blank=True, null=True, verbose_name="Прибыль перезаказа")
    stock_for_days = models.IntegerField(blank=True, null=True, verbose_name="Запасов на дней")
    deliveries = models.IntegerField(blank=True, null=True, verbose_name="Количество поставляется")
    return_product = models.IntegerField(blank=True, null=True, verbose_name="Количество возвращаемых товаров")
    way_to_warehous = models.IntegerField(verbose_name="В пути на склад", null=True)
    stock_profit = models.IntegerField(blank=True, null=True, verbose_name="Потенциальная выручка с остатков")
    stock_price = models.IntegerField(blank=True, null=True, verbose_name="Себестоимость остатков")
    potential_profit = models.IntegerField(blank=True, null=True, verbose_name="Потенциальная прибыль")
    average_unit_profit = models.IntegerField(blank=True, null=True, verbose_name="Средняя прибыль единицы товара")

    objects = ProductManager()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['id']

# Использование сигнала
# def save_product(sender, instance, **kwargs):
#     print(sender.id)
#     print("пытается сохранить изменения")
#
# post_save.connect(save_product, sender=Product)

