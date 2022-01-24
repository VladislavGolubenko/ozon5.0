from django.db import models
# from ..product.models import ProductInOrder
from ..ozon_transaction.models import OzonTransactions
from django.apps import apps
from django.db.models import Sum


# ProductInOrder = apps.get_model('ProductInOrder')


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
    summ_comission = models.FloatField(blank=True, null=True, default=0, verbose_name='Сумма комиссий')
    amount = models.FloatField(blank=True, null=True, default=0, verbose_name='Прибыль')

    # @property
    # def get_product_in_order(self):
    #     products = ProductInOrder.objects.filter(order_id=self.pk)
    #     return products

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

        # products_price_query = ProductInOrder.objects.filter(order_id=self.pk).aggregate(Sum('summ_price'))
        # products_price = products_price_query['summ_price__sum'] if products_price_query['summ_price__sum'] is not None else 0
        #
        # comissions = OzonTransactions.objects.filter(posting_number=self.posting_number)
        # comissions_summ = 0
        #
        # for comission in comissions:
        #     comissions_summ += (comission.sale_commission)
        #
        # amount = products_price - comissions_summ
        # return amount

    def __str__(self):
        return str(self.order_number)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['id']

    objects = OrderManager()
