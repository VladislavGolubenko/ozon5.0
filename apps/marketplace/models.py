from statistics import mode
from django.db import models

class MarketplaceManager(models.Manager):
    def create_marketplace(self, marketplace_name, marketplace_id, api_key, last_validations_date):

        marketplace = self.create(marketplace_name=marketplace_name, marketplace_id=marketplace_id, api_key=api_key,
                                  last_validations_date=last_validations_date)
        return marketplace


class Marketplace(models.Model):

    OZON = "ozon"
    MARKETPLASE = [
        (OZON, 'ozon'),
    ]
    
    marketplace_name = models.CharField(verbose_name="Название маркетплейса", max_length=100)
    marketplace_type = models.CharField(verbose_name="Тип маркетплейса",  blank=True, null=True, max_length=100)
    marketplace_id = models.IntegerField(verbose_name="ID пользователя маркетплейса")
    api_key = models.CharField(verbose_name="API ключ", max_length=500)
    valid = models.BooleanField(verbose_name="Активный", default=False)
    # last_validations_date = models.DateTimeField(verbose_name="Дата последней проверки", blank=True, null=True)
    user = models.ForeignKey("account.User", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    #objects = MarketplaceManager()

    class Meta:
        verbose_name = "маркетплейс"
        verbose_name_plural = "маркетплейсы"
        ordering = ("id",)

    def __str__(self):
        return self.marketplace_name


