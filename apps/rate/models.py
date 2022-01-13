from django.db import models

class Rate(models.Model):
    rate_name = models.CharField(max_length=200, default='base', verbose_name="Название тарифа")
    validity = models.IntegerField(verbose_name='Срок действия в днях')
    price = models.FloatField(verbose_name="Стоимость тарифа")
    description = models.CharField(max_length=1500, verbose_name="Краткое описание тарифа")
    slag = models.CharField(max_length=100, verbose_name="роль, которую дает тариф")

    def __str__(self):
        return str(self.rate_name)

    class Meta:
        verbose_name = 'тариф'
        verbose_name_plural = 'тарифы'
        ordering = ['id']
