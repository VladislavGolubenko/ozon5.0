from django.db import models
from get_data.models import User
from django.db.models.signals import post_save, pre_save
from datetime import datetime, date
from datetime import timedelta


class ProductManager(models.Manager):
    def create_product(self, preview, ozon_product_id, sku, name, stock_balance, way_to_warehous, marketing_price,
                       reserved, user_id):

        product = self.create(preview=preview, ozon_product_id=ozon_product_id, sku=sku, name=name,
                              stock_balance=stock_balance, way_to_warehous=way_to_warehous,
                              marketing_price=marketing_price, reserved=reserved, user_id=user_id)
        return product


class OrderManager(models.Manager):
    def create_order(self, in_process_at, user_id, status, date_of_order,
                     posting_number, region, city, delivery_type, warehous_id, warehouse_name, order_id=None):

        order = self.create(order_number=order_id, in_process_at=in_process_at, user_id=user_id,
                            status=status, date_of_order=date_of_order,
                            posting_number=posting_number, region=region, city=city, delivery_type=delivery_type,
                            warehous_id=warehous_id, warehouse_name=warehouse_name)
        return order


class ProductInOrderManager(models.Manager):
    def create_product_in_order(self, preview, user_id, order_id, sku, name, quantity, offer_id, price, price_f,
                                comission_amount, payout, return_after_deliv_to_customer,
                                product_id, fulfillment, direct_flow_trans, return_flow_trans, deliv_to_customer,
                                return_not_deliv_to_customer, return_part_goods_customer):

        product_in_order = self.create(preview=preview,
                                       user_id=user_id, order_id=order_id, sku=sku, name=name, quantity=quantity,
                                       offer_id=offer_id, price=price, comission_amount=comission_amount, payout=payout,
                                       product_id=product_id, fulfillment=fulfillment,
                                       direct_flow_trans=direct_flow_trans,
                                       return_flow_trans=return_flow_trans, deliv_to_customer=deliv_to_customer,
                                       return_not_deliv_to_customer=return_not_deliv_to_customer, price_f=price_f,
                                       return_part_goods_customer=return_part_goods_customer,
                                       return_after_deliv_to_customer=return_after_deliv_to_customer)
        return product_in_order


class OzonTransactionsManager(models.Manager):
    def create_ozon_transaction(self, user_id, operation_id, operation_type, operation_date, operation_type_name,
                                accruals_for_sale, sale_commission, amount, type, posting_number, services):

        ozon_transaction = self.create(user_id=user_id, operation_id=operation_id, operation_type=operation_type,
                                       operation_date=operation_date, operation_type_name=operation_type_name,
                                       accruals_for_sale=accruals_for_sale, sale_commission=sale_commission,
                                       amount=amount, type=type, posting_number=posting_number,
                                       services=services)
        return ozon_transaction


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


class OzonTransactions(models.Model):

    user_id = models.ForeignKey(
        User,
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
    # items = models.CharField(max_length=5000, verbose_name="Товары")
    services = models.CharField(max_length=10000, verbose_name="Виды услуг")

    product = models.ManyToManyField("ProductInOrder", related_name="product_in_transaction", blank=True, null=True)




    def __str__(self):
        return str(self.operation_id)

    class Meta:
        verbose_name = 'транзакцию ozon'
        verbose_name_plural = 'транзакции ozon'
        ordering = ['id']

    objects = OzonTransactionsManager()


class Order(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_to_user", null=True, blank=True)

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


class Product(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products_to_user", null=True, blank=True)

    preview = models.CharField(max_length=300, verbose_name='Превью')
    ozon_product_id = models.IntegerField(verbose_name='ID товара')
    sku = models.CharField(max_length=100, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    days_for_production = models.IntegerField(blank=True, null=True, verbose_name='Времени необходимо для производства')
    reorder_days_of_supply = models.IntegerField(blank=True, null=True, verbose_name='Глубина поставки')
    unit_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена юнита')
    logistics_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена логистики')
    additional_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Дополнительные затраты')
    summ_price = models.FloatField(blank=True, null=True, verbose_name='Итого')

    # Поле равное маркетинг прайс или в случае нуля обычной цене (получается по апи)
    marketing_price = models.FloatField(blank=True, null=True, default=0, verbose_name='Цена')

    stock_balance = models.IntegerField(verbose_name="Остатки на складе", null=True)
    way_to_warehous = models.IntegerField(verbose_name="В пути на склад", null=True)
    reserved = models.IntegerField(verbose_name="Зарезервировано", blank=True, null=True)

    creating_date = models.DateField(auto_now_add=True, blank=True, null=True)

    objects = ProductManager()

    @property
    def order_for_thirty_days(self):
        date_sort = datetime.now() - timedelta(days=30)
        orders = Order.objects.filter(date_of_order__gte=date_sort, user_id=self.user_id)
        thirty_days = []
        for order in orders:

            products_in_order = ProductInOrder.objects.filter(order_id=order.pk)
            for product_in_order in products_in_order:
                if product_in_order.sku == self.sku:
                    thirty_days.append(product_in_order)

        lenth_thirty_days = len(thirty_days)
        return lenth_thirty_days

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['id']


class ProductInOrder(models.Model):

    preview = models.CharField(max_length=300, verbose_name='Превью', null=True, blank=True)
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orderproduct_to_user",
        null=True,
        blank=True
    )

    order_id = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orderproduct_to_order",
        null=True,
        blank=True
    )

    sku = models.CharField(max_length=100, verbose_name='SKU')
    name = models.CharField(max_length=300, verbose_name='Название товара')
    quantity = models.IntegerField(verbose_name='Кол-во')
    offer_id = models.CharField(max_length=100, verbose_name="Номер предложения")
    price = models.FloatField(verbose_name="Цена товара")
    price_f = models.FloatField(verbose_name="Цена товара в заказе", blank=True, null=True)
    comission_amount = models.FloatField(verbose_name="Сумма комиссий")
    payout = models.FloatField(verbose_name="Cтоимость товара")
    product_id = models.IntegerField("ID продукта")
    fulfillment = models.FloatField(verbose_name="Выполнение предмета услуг на торговой площадке")
    direct_flow_trans = models.FloatField(verbose_name="Транзит товара на маркетплейсе")
    return_flow_trans = models.FloatField(verbose_name="Возврат товара через")
    deliv_to_customer = models.FloatField(verbose_name="Доставка товара покупателю")
    return_not_deliv_to_customer = models.FloatField(verbose_name="Возврат товара от покупателя")
    return_part_goods_customer = models.FloatField(verbose_name="Возврат части заказа покупателю")
    return_after_deliv_to_customer = models.FloatField(verbose_name="Возврат доставленного товара")

    creating_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.sku)

    class Meta:
        verbose_name = 'заказаный товар'
        verbose_name_plural = 'заказаные товары'
        ordering = ['id']

    objects = ProductInOrderManager()


class OzonMetrics(models.Model):

    user_id = models.ForeignKey(
        User,
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


# Использование сигнала
# def save_product(sender, instance, **kwargs):
#     print(sender.id)
#     print("пытается сохранить изменения")
#
# post_save.connect(save_product, sender=Product)

