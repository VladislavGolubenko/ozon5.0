from django.db import models


class MetricsManager(models.Manager):
    def create_ozon_metrics(self, user_id, product_id, product_name, hits_view_search, hits_view_pdp, hits_view,
                            hits_tocart_search, hits_tocart_pdp, hits_tocart, session_view_search, session_view_pdp,
                            session_view, conv_tocart_search, conv_tocart_pdp, conv_tocart, revenue, returns,
                            cancellations, ordered_units, delivered_units, adv_view_pdp, adv_view_search_category,
                            adv_view_all, adv_sum_all, position_category, postings, postings_premium):

        ozon_metrics = self.create(user_id=user_id, product_id=product_id, product_name=product_name,
                                   hits_view_search=hits_view_search, hits_view_pdp=hits_view_pdp, hits_view=hits_view,
                                   hits_tocart_search=hits_tocart_search, hits_tocart_pdp=hits_tocart_pdp,
                                   hits_tocart=hits_tocart, session_view_search=session_view_search,
                                   session_view_pdp=session_view_pdp, session_view=session_view,
                                   conv_tocart_search=conv_tocart_search, conv_tocart_pdp=conv_tocart_pdp,
                                   conv_tocart=conv_tocart, revenue=revenue, returns=returns,
                                   cancellations=cancellations, ordered_units=ordered_units,
                                   delivered_units=delivered_units, adv_view_pdp=adv_view_pdp,
                                   adv_view_search_category=adv_view_search_category, adv_view_all=adv_view_all,
                                   adv_sum_all=adv_sum_all, position_category=position_category, postings=postings,
                                   postings_premium=postings_premium)
        return ozon_metrics

class OzonMetrics(models.Model):

    user_id = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="ozon_metrics_to_user",
        null=True,
        blank=True
    )
    product_id = models.IntegerField(verbose_name='ID товара')
    product_name = models.CharField(max_length=300, verbose_name='Название товара')
    hits_view_search = models.FloatField(verbose_name="показы в поиске и в категории")
    hits_view_pdp = models.FloatField(verbose_name="показы на карточке товара")
    hits_view = models.FloatField(verbose_name="всего показов")
    hits_tocart_search = models.FloatField(verbose_name="в корзину из поиска или категории")
    hits_tocart_pdp = models.FloatField(verbose_name="в корзину из карточки товара")
    hits_tocart = models.FloatField(verbose_name="всего добавлено в корзину")
    session_view_search = models.FloatField(verbose_name="сессии с показом в поиске или в категории")
    session_view_pdp = models.FloatField(verbose_name="сессии с показом на карточке товара")
    session_view = models.FloatField(verbose_name="всего сессий")
    conv_tocart_search = models.FloatField(verbose_name="конверсия в корзину из поиска или категории")
    conv_tocart_pdp = models.FloatField(verbose_name="конверсия в корзину из карточки товара")
    conv_tocart = models.FloatField(verbose_name="общая конверсия в корзину")
    revenue = models.FloatField(verbose_name="заказано на сумму")
    returns = models.FloatField(verbose_name="возвращено товаров")
    cancellations = models.FloatField(verbose_name="отменено товаров")
    ordered_units = models.FloatField(verbose_name="заказано товаров")
    delivered_units = models.FloatField(verbose_name="доставлено товаров")
    adv_view_pdp = models.FloatField(verbose_name="показы на карточке товара, спонсорские товары")
    adv_view_search_category = models.FloatField(verbose_name="показы в поиске и в категории, спонсорские товары")
    adv_view_all = models.FloatField(verbose_name="показы всего, спонсорские товары,")
    adv_sum_all = models.FloatField(verbose_name="всего расходов на рекламу")
    position_category = models.FloatField(verbose_name="позиция в поиске и категории")
    postings = models.FloatField(verbose_name="отправления")
    postings_premium = models.FloatField(verbose_name="отправления с подпиской Premium")
    creating_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Метрика'
        verbose_name_plural = 'метрики'
        ordering = ['id']

    objects = MetricsManager()