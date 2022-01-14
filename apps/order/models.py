from django.db import models
from ..product.models import ProductInOrder
from ..ozon_transaction.models import OzonTransactions

class OrderManager(models.Manager):
    def create_order(self, in_process_at, user_id, status, date_of_order,
                     posting_number, region, city, delivery_type, warehous_id, warehouse_name, order_id=None):

        order = self.create(order_number=order_id, in_process_at=in_process_at, user_id=user_id,
                            status=status, date_of_order=date_of_order,
                            posting_number=posting_number, region=region, city=city, delivery_type=delivery_type,
                            warehous_id=warehous_id, warehouse_name=warehouse_name)
        return order

class Order(models.Model):

    user_id = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="order_to_user", null=True, blank=True)

    order_number = models.CharField(max_length=500, verbose_name="Номер заказа")
    date_of_order = models.DateTimeField(auto_now=False, auto_now_add=False,
                                         verbose_name="Дата и время размещения заказа")
    in_process_at = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name="Дата принятия в обработку",
                                         blank=True, null=True)
    status = models.CharField(max_length=100, verbose_name="Статус заказ", null=True, blank=True)
    posting_number = models.CharField(max_length=100, verbose_name="Номер отправления", blank=True, null=True)
    region = models.CharField(max_length=500, verbose_name='Регион', blank=True, null=True)
    city = models.CharField(max_length=500, verbose_name="Город", blank=True, null=True)
    delivery_type = models.CharField(max_length=100, verbose_name="Тип доставки", blank=True, null=True)
    warehous_id = models.BigIntegerField(verbose_name="ID склада", blank=True, null=True)
    warehouse_name = models.CharField(max_length=500, verbose_name="Склад отгрузки", blank=True, null=True)

    creating_date = models.DateField(auto_now_add=True, blank=True, null=True)

    @property
    def get_product_in_order(self):
        products = ProductInOrder.objects.filter(order_id=self.pk)
        return products

    def get_summ_comission(self):
        comissions = OzonTransactions.objects.filter(posting_number=self.posting_number)
        comissions_summ = 0

        for comission in comissions:
            comissions_summ += (comission.sale_commission)
        return comissions_summ

    def get_amount(self):
        amounts = OzonTransactions.objects.filter(posting_number=self.posting_number)
        amounts_summ = 0

        for amount in amounts:
            amounts_summ += (amount.amount)
        return amounts_summ

    def __str__(self):
        return str(self.order_number)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['id']

    objects = OrderManager()