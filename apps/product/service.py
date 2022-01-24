from datetime import datetime, date
from datetime import timedelta
from django.db.models import Q, Count, Sum
from rest_framework import status
from rest_framework.response import Response
import math
from .models import *
from ..ozon_transaction.models import OzonTransactions


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


def company_dashbord_function(user_id, date_from):
    """
        Функция получения аналитической информации компании

        получает: user_id (pk), date_from (date: дата, начиная от которой и до сегоднешнего дня будет формироваться
        аналитика компании)

        возвращает: data (dict: аналитическая информация компании)
    """

    # Получаем продажи
    queryset_of_sales = OzonTransactions.objects.filter(operation_date__gte=date_from, user_id=user_id,
                                                        operation_type="OperationAgentDeliveredToCustomer")
    sales = 0

    for sale in queryset_of_sales:
        sales += sale.accruals_for_sale

    # Возвраты
    queryset_of_returns = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                          user_id=user_id,
                                                          operation_type="ClientReturnAgentOperation")
    returns = 0

    for return_of_client in queryset_of_returns:
        returns += return_of_client.accruals_for_sale

    # Компенсации и другое
    queryset_of_compensation = OzonTransactions.objects.filter(Q(operation_type="OperationCorrectionSeller") |
                                                               Q(operation_type="OperationLackWriteOff") |
                                                               Q(operation_type="OperationClaim") |
                                                               Q(operation_type="OperationSetOff") |
                                                               Q(operation_type="MarketplaceSellerCompensationOperation") |
                                                               Q(operation_type="OperationDefectiveWriteOff") |
                                                               Q(operation_type="MarketplaceSellerShippingCompensationReturnOperation") |
                                                               Q(operation_type="MarketplaceSellerReexposureDeliveryReturnOperation"),
                                                               operation_date__gte=date_from,
                                                               user_id=user_id)
    compensations = 0

    for compensation in queryset_of_compensation:
        compensations += compensation.accruals_for_sale

    proceeds = compensations + returns + sales  # Выручка

    products_sku = ProductInOrder.objects.filter(user_id=user_id).values('sku')
    sku_list = []

    for sku in products_sku:
        if sku not in sku_list:
            sku_list.append(sku)

    unit_price = 0
    logistics = 0
    additional_price = 0

    for sku in sku_list:

        # Колличество товаров доставленных пользователю (из транзакций по sku)
        delivered_to_customer = OzonTransactions.objects.filter(product__sku=sku['sku'],
                                                                operation_date__gte=date_from,
                                                                user_id=user_id,
                                                                operation_type="OperationAgentDeliveredToCustomer").aggregate(Count('id'))

        # Колличество товаров которые вернули (из транзакций по sku)
        return_operation = OzonTransactions.objects.filter(product__sku=sku['sku'],
                                                           operation_date__gte=date_from,
                                                           user_id=user_id,
                                                           operation_type="ClientReturnAgentOperation").aggregate(Count('id'))

        real_summ_of_sale_product = delivered_to_customer['id__count'] - return_operation['id__count']

        product_query = ProductInOrder.objects.filter(user_id=user_id, sku=sku['sku']).last()

        if product_query.unit_price and product_query.logistics_price and product_query.additional_price is not None:
            unit_price += real_summ_of_sale_product * product_query.unit_price  # Себестоимость
            logistics += real_summ_of_sale_product * product_query.logistics_price  # Логистика
            additional_price += real_summ_of_sale_product * product_query.additional_price  # Добавленная стоимость

        else:
            return sku

    services_query = OzonTransactions.objects.filter(Q(operation_type="MarketplaceSaleReviewsOperation") |
                                                     Q(operation_type="OperationMarketplaceCrossDockServiceWriteOff") |
                                                     Q(operation_type="OperationMarketplaceServiceStorage"),
                                                     operation_date__gte=date_from,
                                                     user_id_id=user_id).aggregate(Sum('amount'))

    services = services_query['amount__sum'] if services_query['amount__sum'] is not None else 0  # Услуги

    comissions_by_sales_query = OzonTransactions.objects.filter(operation_date__gte=date_from,
                                                                user_id=user_id).aggregate(Sum('sale_commission'))

    comissions_by_sales = comissions_by_sales_query['sale_commission__sum'] if comissions_by_sales_query[
                                                                                   'sale_commission__sum'] is not None else 0  # Комиссия за продажу

    """
        Тут вопрос. Я суммирую amount (как я понял это цена услуги), а в документации написано что сумировать нужно price
    """
    assembly_query = OzonTransactions.objects.filter(Q(operation_type_name="MarketplaceServiceItemFulfillment") |
                                                     Q(operation_type_name="MarketplaceServiceItemDropoffFf") |
                                                     Q(operation_type_name="MarketplaceServiceItemDropoffPvz") |
                                                     Q(operation_type_name="MarketplaceServiceItemDropoffSc"),
                                                     operation_date__gte=date_from,
                                                     user_id=user_id).aggregate(Sum('amount'))
    assembly = assembly_query['amount__sum'] if assembly_query['amount__sum'] is not None else 0  # Сборка заказа

    highway_query = OzonTransactions.objects.filter(Q(operation_type_name="MarketplaceServiceItemDirectFlowTrans") |
                                                    Q(operation_type_name="MarketplaceServiceItemReturnFlowTrans"),
                                                    operation_date__gte=date_from,
                                                    user_id=user_id).aggregate(Sum('amount'))
    highway = highway_query['amount__sum'] if highway_query['amount__sum'] is not None else 0  # Магистраль

    last_mile_query = OzonTransactions.objects.filter(operation_type_name="MarketplaceServiceItemDelivToCustomer",
                                                      operation_date__gte=date_from,
                                                      user_id=user_id).aggregate(Sum('amount'))

    last_mile = last_mile_query['amount__sum'] if last_mile_query['amount__sum'] is not None else 0  # Последняя миля

    refunds_cancellations_query = OzonTransactions.objects.filter(
        Q(operation_type_name="MarketplaceServiceItemReturnAfterDelivToCustomer") |
        Q(operation_type_name="MarketplaceServiceItemReturnNotDelivToCustomer") |
        Q(operation_type_name="MarketplaceServiceItemReturnPartGoodsCustomer"),
        operation_date__gte=date_from, user_id=user_id).aggregate(Sum('amount'))

    refunds_cancellations = refunds_cancellations_query['amount__sum'] if refunds_cancellations_query[
                                                                              'amount__sum'] is not None else 0  # Плата за возвраты и отмены

    comissions = comissions_by_sales + assembly + highway + last_mile + refunds_cancellations  # Комиссия

    advertising_query = OzonTransactions.objects.filter(operation_type_name="MarketplaceMarketingActionCostOperation",
                                                        operation_date__gte=date_from,
                                                        user_id=user_id).aggregate(Sum('amount'))

    advertising = advertising_query['amount__sum'] if advertising_query['amount__sum'] is not None else 0  # Реклама
    cost = unit_price + logistics + additional_price + services + comissions + advertising  # Стоимость товара

    cost_price = unit_price + logistics + additional_price  # Себестоимость товара
    optional_costs = services + comissions + advertising  # Операционные расходы
    profit = proceeds - cost_price - optional_costs  # Прибыль

    goods_sold_query = OzonTransactions.objects.filter(operation_type="OperationAgentDeliveredToCustomer",
                                                       operation_date__gte=date_from,
                                                       user_id=user_id).aggregate(Count('product__id'))

    goods_sold = goods_sold_query['product__id__count']  # Товаров продано

    goods_returned_query = OzonTransactions.objects.filter(operation_type="ClientReturnAgentOperation",
                                                           operation_date__gte=date_from,
                                                           user_id=user_id).aggregate(Count('product__id'))
    goods_returned = goods_returned_query['product__id__count']  # Товаров возвращенно

    marginality = profit / proceeds * 100 if proceeds != 0 else None  # Маржинальность в %
    roi = profit / unit_price * 100 if unit_price != 0 else None  # ROI

    data = {
        'roi': roi,  # ROI
        'marginality': marginality,  # Маржинальность в %
        'sales': sales,  # Продажи
        'returns': returns,  # Возвраты
        'compensations': compensations,  # Компенсации и другое
        'proceeds': proceeds,  # Выручка
        'unit_price': unit_price,  # Себестоимость
        'logistics': logistics,  # Логистика
        'additional_price': additional_price,  # Добавленная стоимость
        'services': services,  # Услуги
        'comissions': comissions,  # Комиссия
        'comissions_by_sales': comissions_by_sales,  # Комиссия за продажу
        'assembly': assembly,  # Сборка заказа
        'highway': highway,  # Магистраль
        'last_mile': last_mile,  # Последняя миля
        'refunds_cancellations': refunds_cancellations,  # Плата за возвраты и отмены
        'advertising': advertising,  # Реклама
        'profit': profit,  # Прибыль
        'cost': cost,  # Стоимость товара
        'cost_price': cost_price,  # Себестоимость товара
        'optional_costs': optional_costs,  # Опциональные расходы
        'goods_sold': goods_sold,  # Товаров продано
        'goods_returned': goods_returned  # Товаров возвращенно
    }

    return data


def warehous_account_function(product, days):
    """
        Функция возвращающая "Складской учет"

        получает: product (class), days (int: кол-во дней для формирования статистики)
        возвращает: data (dict: аналитическая информация товаров для складского учета)

        p.s.: некоторые поля могут возвращать None при недастаче данных (которые должен вводить пользователь) у товара
    """
    date_sort = datetime.now() - timedelta(days=days)

    preview = product.preview
    ozon_product_id = product.ozon_product_id
    sku = product.sku
    name = product.name
    stock_balance = product.stock_balance

    orders_by_period = 0

    products_in_orders = ProductInOrder.objects.filter(sku=product.sku,
                                                       order_id_id__date_of_order__gte=date_sort)
    #print(products_in_orders)
    for product_in_order in products_in_orders:
        orders_by_period += product_in_order.quantity  # Заказано за период
    #print("orders_by_period: ", orders_by_period)
    orders_speed = orders_by_period / days  # Средняя скорость заказов
    #print("orders_speed: ", orders_speed)
    days_for_production = product.days_for_production  # Срок производства

    if orders_speed != 0.0:
        stocks_for_days = round(stock_balance / orders_speed)  # Осталось запасов на дней
    else:
        stocks_for_days = None

    reorder_days_of_supply = product.reorder_days_of_supply  # Глубина поставки
    potencial_proceeds = product.marketing_price * product.stock_balance  # Потенциальная выручка остатков
    # print(product.stock_balance)
    # print(product.marketing_price)
    if product.summ_price is not None:
        product_price = product.summ_price  # Стоимость товара
    elif product.unit_price and product.additional_price and product.logistics_price is not None:
        product_price = product.unit_price + product.additional_price + product.logistics_price
    else:
        product_price = None

    if product_price is not None:
        stocks_cost_price = product_price * stock_balance  # Себестоимость остатков
    else:
        stocks_cost_price = None

    if reorder_days_of_supply is not None:
        need_to_order = math.ceil(reorder_days_of_supply * orders_speed)  # Необходимо заказать
    else:
        need_to_order = None

    if need_to_order and product_price is not None:
        reorder_sum = need_to_order * product_price  # Сумма перезаказа
    else:
        reorder_sum = None

    if reorder_days_of_supply and stocks_for_days is not None:
        if reorder_days_of_supply >= stocks_for_days:
            status_of_product = "Заказать сейсчас"
        elif reorder_days_of_supply < stocks_for_days and reorder_days_of_supply <= stocks_for_days + 7:
            status_of_product = "Заказать скоро"
        elif stocks_for_days <= reorder_days_of_supply + 7 and stocks_for_days <= reorder_days_of_supply + 21:
            status_of_product = "В наличии"
        elif stocks_for_days > reorder_days_of_supply + 21:
            status_of_product = "Избыток"
    else:
        status_of_product = None

    if stocks_for_days and days_for_production is not None:
        reorder_date = datetime.now() + timedelta(stocks_for_days - days_for_production)
    else:
        reorder_date = None

    # average_profit_unit = product.summ_price -   None # Средняя прибыль единицы товара =  Цена - среднне(коммисии) - стоимость товара  (итого стоимость)
    # Потенциальная прибыль остатков = Остатки на складе * Средняя прибыль единицы товара
    # Прибыль перезаказа = Средняя прибыль единицы товара * необходимо заказать

    data = {
        'preview': preview,  # Превью
        'ozon_product_id': ozon_product_id,  # ID +
        'sku': sku,  # Артикул + 
        'name': name,  # Название +
        'stock_balance': stock_balance,  # Остатки на складе +
        'orders_by_period': orders_by_period,  # Заказано товарa + 
        'orders_speed': orders_speed,  # Скорость заказа + 
        'days_for_production': days_for_production,  # Срок производства +
        'reorder_days_of_supply': reorder_days_of_supply,  # Глубина поставки +
        'potencial_proceeds': potencial_proceeds,  # Потенциальная выручка с остатков + 
        'product_price': product_price,  # Стоимость товара + 
        'stocks_for_days': stocks_for_days,  # Осталось запасов на дней +
        'need_to_order': need_to_order,  # Необходимо заказать (количество для заказа) + 
        'stocks_cost_price': stocks_cost_price,  # Себестоимость остатков + 
        'reorder_sum': reorder_sum,  # Сумма перезаказа + 
        'status_of_product': status_of_product,  # Статус + 
        'reorder_date': reorder_date,  # Дата перезаказа +
        #'average_profit_unit': average_profit_unit, # Средняя прибыль единицы товара
        # Параметр на согласовании:
        # Средняя прибыль единицы товара

        # Параметры, которые потерялись из-за средней прибыли единицы товара
        # Прибыль перезаказа
        # Потенциальная прибыль остатков
    }
    #print(data)
    return data
