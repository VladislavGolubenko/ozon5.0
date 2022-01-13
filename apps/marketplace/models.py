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
    marketplace_id = models.IntegerField(verbose_name="ID пользователя маркетплейса", default=0, blank=True, null=True)
    api_key = models.CharField(verbose_name="API ключ", max_length=500, blank=True, null=True)
    last_validations_date = models.DateTimeField(verbose_name="Дата последней проверки", blank=True, null=True)

    objects = MarketplaceManager()

    class Meta:
        verbose_name = "маркетплейс"
        verbose_name_plural = "маркетплейсы"
        ordering = ("id",)

    def __str__(self):
        return self.id


