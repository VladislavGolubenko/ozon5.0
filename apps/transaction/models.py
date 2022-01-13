from django.db import models


class Transaction(models.Model):
    id_user = models.ForeignKey("account.User", on_delete=models.CASCADE, blank=True, null=True, related_name="user_transaction",
                                verbose_name='Пользователь')
    transaction_number = models.CharField(max_length=200, default='000000000000000', verbose_name="Номер транзакции")
    date_issued = models.DateTimeField(auto_now_add=True, verbose_name="Дата выполнения", blank=True)
    type = models.ForeignKey("payment.PaymentType", on_delete=models.CASCADE, blank=True, null=True,
                             related_name="payment_transaction", verbose_name='Способ оплаты')
    rate = models.ForeignKey("rate.Rate", on_delete=models.CASCADE, blank=True, null=True,
                             related_name="rate_transaction", verbose_name='Тариф')
    summ = models.IntegerField(default=0, verbose_name='Сумма списания')
    status = models.CharField(max_length=100, default='wait', verbose_name='Статус', blank=True)

    def __str__(self):
        return str(self.transaction_number)

    class Meta:
        verbose_name = 'транзакцию'
        verbose_name_plural = 'транзакции'
        ordering = ['id']
