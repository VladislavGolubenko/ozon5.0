from django.db import models

# Create your models here.
class PaymentType(models.Model):
    type = models.CharField(max_length=100, default='card', verbose_name="Способ оплаты")
    description = models.CharField(max_length=1000, verbose_name="Описание способа оплаты")

    def __str__(self):
        return str(self.type)

    class Meta:
        verbose_name = 'способ оплаты'
        verbose_name_plural = 'способы оплаты'
        ordering = ['type']
