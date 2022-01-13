from datetime import datetime, date
from datetime import timedelta
from django.db.models import Q, Count, Sum
from rest_framework import status
from rest_framework.response import Response

from ..product.models import ProductInOrder, Product
from .models import OzonTransactions


def company_products_function(user_id, date):
    """
        Функция возвращающая "Аналитику продукта"

        получает: user_id (pk), date (int: кол-во дней для формирования статистики)
        возвращает: data_list (list: аналитическая информация для каждого из продуктов, представляет собой список товаров
                                     из словарей, в каждом из которых находится аналитика для конкретного товара)
    """

    date_from = datetime.now() - timedelta(date)

    products_sku = ProductInOrder.objects.filter(user_id=user_id).values('sku')
    sku_list = []

    for sku in products_sku:
        if sku['sku'] not in sku_list:
            sku_list.append(sku['sku'])

    sales = 0
    refunds = 0
    data_list = []

    for sku in sku_list:

        delivered_to_customer_query = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                                      operation_type="OperationAgentDeliveredToCustomer",
                                                                      product__sku=sku).values('product__price')
        for delivered_to_customer in delivered_to_customer_query:
            sales += delivered_to_customer['product__price']  # Продажи

        client_return_query = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                              operation_type="ClientReturnAgentOperation",
                                                              product__sku=sku).values('product__price')
        for client_return in client_return_query:
            refunds += client_return['product__price']  # Возвраты

        revenue = sales + refunds  # Выручка

        delivered_numbers_of_product_query = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                                             operation_type="OperationAgentDeliveredToCustomer",
                                                                             product__sku=sku).aggregate(
            Count('product__id'))
        delivered_numbers_of_product = delivered_numbers_of_product_query['product__id__count']

        return_numbers_of_product_query = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                                          operation_type="ClientReturnAgentOperation",
                                                                          product__sku=sku).aggregate(
            Count('product__id'))
        return_numbers_of_product = return_numbers_of_product_query['product__id__count']

        real_number_of_product = delivered_numbers_of_product - return_numbers_of_product

        """
        !!!!!!!!!!!!!!!!!!!!!!!
        тут возможно нужно будет подвязать к конкретной транзакции, тк в архиве их много
        """
        product_query = ProductInOrder.objects.filter(user_id=user_id, sku=sku).first()
        preview = product_query.preview  # Превью
        name = product_query.name  # Название товара
        sku = product_query.sku  # Артикул

        if product_query.unit_price and product_query.additional_price and product_query.logistics_price is not None:
            cost_price = real_number_of_product * product_query.unit_price  # Себестоимость
            logistic_price = real_number_of_product * product_query.logistics_price  # Логистика
            dop_price = real_number_of_product * product_query.additional_price  # Доп расходы
            comissions = 0  # Комисии (пока в доработке, поэтому ноль)
            price = cost_price + logistic_price + dop_price + comissions  # Стоимость
        else:
            sku_dict = {'sku': sku, }
            return Response(sku_dict, status=status.HTTP_404_NOT_FOUND)

        # Себестоимость товаров (НА УТОЧНЕНИИ)
        # Операционные расходы (НА УТОЧНЕНИИ)
        # Прибыль (НА УТОЧНЕНИИ)
        # Маржинальность (НЕ МОГУ ПОСЧИТАТЬ ИЗ-ЗА ПОЛЕЙ НА УТОЧНЕНИИ)
        # ROI (НЕ МОГУ ПОСЧИТАТЬ ИЗ-ЗА ПОЛЕЙ НА УТОЧНЕНИИ)

        goods_sold_query = OzonTransactions.objects.filter(operation_type="OperationAgentDeliveredToCustomer",
                                                           operation_date__gte=date_from, product__sku=sku,
                                                           user_id=user_id).aggregate(Count('product__id'))

        goods_sold = goods_sold_query['product__id__count'] if goods_sold_query[
                                                                   'product__id__count'] is not None else None  # Товаров продано

        goods_returned_query = OzonTransactions.objects.filter(operation_type="ClientReturnAgentOperation",
                                                               operation_date__gte=date_from, product__sku=sku,
                                                               user_id=user_id).aggregate(
            Count('product__id'))

        goods_returned = goods_returned_query['product__id__count'] if goods_returned_query[
                                                                           'product__id__count'] is not None else None  # Товаров возвращенно

        returns_percent = goods_returned / goods_sold * 100 if goods_sold != 0 else 0  # Процентов возврата

        data = {
            'sales': sales,  # Продажи
            'refunds': refunds,  # Возвраты
            'revenue': revenue,  # Выручка
            'cost_price': cost_price,  # Себестоимость
            'logistic_price': logistic_price,  # Логистика
            'dop_price': dop_price,  # Доп расходы
            'price': price,  # Стоимость
            'goods_sold': goods_sold,  # Товаров продано
            'goods_returned': goods_returned,  # Товаров возвращенно

            'comissions': comissions,  # Комисии (пока в доработке, поэтому ноль)
            'sale_comissions': None,  # Комиссии за продажу
            'order_assembly': None,  # Сборка заказа
            'magistral': None,  # Магистраль
            'last_mile': None,  # Последняя миля
            'price_of_returns': None,  # Плата за возвраты и отмены
            'cost_price_all': None,  # Себестоимость товаров
            'operational_cost': None,  # Операционные расходы
            'profit': None,  # Прибыль
            'roi': None,  # ROI
            'marginality': None,  # Маржинальность

            'preview': preview,  # Превью
            'name': name,  # Название товара
            'sku': sku,  # Артикул
            'returns_percent': returns_percent,  # Процентов возврата
        }
        data_list.append(data)
    return data_list

