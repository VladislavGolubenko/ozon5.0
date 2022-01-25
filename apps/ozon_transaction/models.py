from django.db import models


class OzonTransactionsManager(models.Manager):
    def create_ozon_transaction(self, user_id, operation_id, operation_type, operation_date, operation_type_name,
                                accruals_for_sale, sale_commission, amount, type, posting_number, services, marketplace_id, is_visible):

        ozon_transaction = self.create(user_id=user_id, operation_id=operation_id, operation_type=operation_type,
                                       operation_date=operation_date, operation_type_name=operation_type_name,
                                       accruals_for_sale=accruals_for_sale, sale_commission=sale_commission,
                                       amount=amount, type=type, posting_number=posting_number,
                                       services=services, marketplace_id=marketplace_id, is_visible=is_visible)
        return ozon_transaction


class OzonTransactions(models.Model):

    user_id = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="ozon_transaction_to_user",
        null=True,
        blank=True
    )

    operation_id = models.BigIntegerField(verbose_name="Номер опирации")
    operation_type = models.CharField(max_length=250, verbose_name="Тип опирации")
    operation_date = models.DateTimeField(verbose_name="Дата опирации")
    operation_type_name = models.CharField(max_length=250, verbose_name="Название типа опирации")
    accruals_for_sale = models.FloatField(verbose_name="Начисления за продажу")
    sale_commission = models.FloatField(verbose_name="Комиссия за продажу")
    amount = models.FloatField(verbose_name="Amount")
    type = models.CharField(max_length=250, verbose_name="Тип")
    posting_number = models.CharField(max_length=500, verbose_name="Номер доставки")
    services = models.CharField(max_length=10000, verbose_name="Виды услуг")
    is_visible = models.BooleanField(default=True, verbose_name="Видимость товара")
    marketplace_id = models.IntegerField(null=True, blank=True, verbose_name="ID маркетплейса")
    product = models.ManyToManyField("product.ProductInOrder", related_name="product_in_transaction", blank=True, null=True)

    def __str__(self):
        return str(self.operation_id)

    class Meta:
        verbose_name = 'транзакцию ozon'
        verbose_name_plural = 'транзакции ozon'
        ordering = ['id']

    objects = OzonTransactionsManager()
