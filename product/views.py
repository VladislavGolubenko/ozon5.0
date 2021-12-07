import json
import requests
from django.http import HttpResponse, Http404
from datetime import datetime, date
from datetime import timedelta
from django_filters import rest_framework as filters
from rest_framework.pagination import LimitOffsetPagination

from rest_framework.filters import OrderingFilter

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView

from .serializers import *
from rest_framework import permissions
from .permissions import IsSubscription
from .models import *
from .tasks import get_analitic_data, update_analitics_data
from django.db.models import Q, Count, Sum


class ProductInOrderAction(ListAPIView):

    queryset = ProductInOrder.objects.all()
    serializer_class = ProductInOrderSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        return ProductInOrder.objects.filter(user_id=self.request.user.pk)


class OzonTransactionsAction(ListAPIView):

    queryset = OzonTransactions.objects.all()
    serializer_class = OzonTransactionsSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        return OzonTransactions.objects.filter(user_id=self.request.user.pk)


class OzonMetricsAction(ListAPIView):

    queryset = OzonMetrics.objects.all()
    serializer_class = OzonMetricsSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):

        """
        При переходе на отображение страницы перед отображением будет должны обновиться (или подтянуться, в случае
        если их нет) аналитические данные озонконкретного пользователя. В дальнейшем обновления данных за это же число
        будут должны происходить на следующий день для финальной актуализации
        """

        today = datetime.now().date()
        print(today)
        this_day_metrics = OzonMetrics.objects.filter(user_id=self.request.user.pk, creating_date=today)
        email_query = User.objects.get(id=self.request.user.pk)

        if this_day_metrics.exists():
            update_analitics_data.delay(email=email_query.email, today=today)
        else:
            get_analitic_data.delay(email=email_query.email)

        return OzonMetrics.objects.filter(user_id=self.request.user.pk)


class ProductListAction(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        return Product.objects.filter(user_id=self.request.user.pk)

    def perform_create(self, serializer):
        return serializer.save()

# class ProductListAction(APIView):
#
#     ordering_fields = ['id', ]
#     filter_fields = ('unit_price', )
#
#     def get(self, request):
#         queryset = Product.objects.filter(user_id=request.user.pk)
#
#         filter = ProductFilter()
#         filtered_queryset = filter.filter_queryset(request, queryset, self)
#         paginator = LimitOffsetPagination()
#
#         if filtered_queryset.exists():
#
#             result_page = paginator.paginate_queryset(queryset, request)
#             serializer = ProductSerializer(result_page, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response([], status=status.HTTP_200_OK)
#
#
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListAction(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrderSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.pk)

        # queryset = Order.objects.filter(user_id=self.request.user.pk)
        # # queryset = Order.objects.all()
        # serializer = OrderSerializer(queryset, many=True)
        # return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = OrderSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = OrderSerializer(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WarehouseAccountView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [IsSubscription]

    def post(self, request, days):

        # email = self.request.POST['json']
        json_with_id = json.loads(request.body.decode("utf-8"))
        id_of_user = json_with_id['id']

        date_sort = datetime.now() - timedelta(days=days)

        # products = Product.objects.filter(user_id=request.user.pk)
        products = Product.objects.filter(user_id=id_of_user)
        datas = []

        for product in products:

            preview = product.preview
            ozon_product_id = product.ozon_product_id
            sku = product.sku
            name = product.name
            stock_balance = product.stock_balance

            orders_by_period = 0

            products_in_orders = ProductInOrder.objects.filter(sku=product.sku,
                                                               order_id_id__date_of_order__gte=date_sort)

            for product_in_order in products_in_orders:
                orders_by_period += product_in_order.quantity  # Заказано за период

            orders_speed = orders_by_period / days  # Средняя скорость заказов
            days_for_production = product.days_for_production  # Срок производства

            if orders_speed != 0.0:
                stocks_for_days = round(stock_balance / orders_speed)  # Осталось запасов на дней
            else:
                stocks_for_days = None

            reorder_days_of_supply = product.reorder_days_of_supply  # Глубина поставки
            potencial_proceeds = product.marketing_price * product.stock_balance  # Потенциальная выручка остатков

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
                need_to_order = reorder_days_of_supply * orders_speed  # Необходимо заказать
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
                reorder_date = datetime.now() + timedelta(stocks_for_days-days_for_production)
            else:
                reorder_date = None

            data = {
                'preview': preview,  # Превью
                'ozon_product_id': ozon_product_id,  # ID
                'sku': sku,  # Артикул
                'name': name,  # Название
                'stock_balance': stock_balance,  # Остатки на складе
                'orders_by_period': orders_by_period,  # Заказано товарa
                'orders_speed': orders_speed,  # Скорость заказа
                'days_for_production': days_for_production,  # Срок производства
                'reorder_days_of_supply': reorder_days_of_supply,  # Глубина поставки
                'potencial_proceeds': potencial_proceeds,  # Потенциальная выручка с остатков
                'product_price': product_price,  # Стоимость товара
                'stocks_for_days': stocks_for_days,  # Осталось запасов на дней
                'need_to_order': need_to_order,  # Необходимо заказать (количество для заказа)
                'stocks_cost_price': stocks_cost_price,  # Себестоимость остатков
                'reorder_sum': reorder_sum,  # Сумма перезаказа
                'status_of_product': status_of_product,  # Статус
                'reorder_date': reorder_date,  # Дата перезаказа

                # Параметр на согласовании:
                # Средняя прибыль единицы товара

                # Параметры, которые потерялись из-за средней прибыли единицы товара
                # Прибыль перезаказа
                # Потенциальная прибыль остатков
            }

            datas.append(data)
            paginator = LimitOffsetPagination()
            result_page = paginator.paginate_queryset(datas, request)

        return Response(data=result_page, status=status.HTTP_200_OK)


class ObjectInTableView(APIView):
    def get(self, request, table):

        if table == 'product':
            objects = Product.objects.filter(user_id=self.request.user.pk)
        elif table == 'ozon_transactions':
            objects = OzonTransactions.objects.filter(user_id=self.request.user.pk)
        elif table == 'order':
            objects = Order.objects.filter(user_id=self.request.user.pk)
        elif table == 'ozon_metrics':
            objects = OzonMetrics.objects.filter(user_id=self.request.user.pk)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

        summ_of_object = len(objects)

        return Response(summ_of_object, status=status.HTTP_200_OK)


class CompanyDashbordView(APIView):
    """
    Вьющка аналитичской информации компании

    для получения необходимо передать
    date - Передается в количестве дней. Дата от кокого числа (и до сегоднешнего дня) будет передана аналитика.
    sku - SKU товара в БД

    Пример запроса:

    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sku = self.request.GET['sku']
        date = self.request.GET['date']
        date = int(date)
        date_from = datetime.now() - timedelta(date)

        if date is not None:
            # Получаем продажи
            queryset_of_sales = OzonTransactions.objects.filter(operation_date__lte=date_from, user_id=self.request.user.pk,
                                                                operation_type="OperationAgentDeliveredToCustomer")
            sales = 0

            for sale in queryset_of_sales:
                sales += sale.accruals_for_sale

            # Возвраты
            queryset_of_returns = OzonTransactions.objects.filter(operation_date__lte=date_from,
                                                                  user_id=self.request.user.pk,
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
                                                                       operation_date__lte=date_from,
                                                                       user_id=self.request.user.pk, )
            compensations = 0

            for compensation in queryset_of_compensation:
                compensations += compensation.accruals_for_sale

            proceeds = compensations + returns + sales  # Выручка
            print("compensations", compensations)  # Компенсации и другое
            print("returns", returns)  # Возвраты
            print("sales", sales)  # Продажи

            if sku is not None:

                """ 
                    тут нужно продумать логику и как оно должно отображаться, возможно просто убрать sku из запроса и 
                    оставить только пользователя, а возможно перебрать все sku которые есть у пользователя 
                """

                # Колличество товаров доставленных пользователю (из транзакций по sku)
                delivered_to_customer = OzonTransactions.objects.filter(product__sku=sku, operation_date__lte=date_from,
                                                                        user_id=self.request.user.pk,
                                                                        operation_type="OperationAgentDeliveredToCustomer").aggregate(Count('id'))

                # Колличество товаров которые вернули (из транзакций по sku)
                return_operation = OzonTransactions.objects.filter(product__sku=sku, operation_date__lte=date_from,
                                                                   user_id=self.request.user.pk,
                                                                   operation_type="ClientReturnAgentOperation").aggregate(Count('id'))

                real_summ_of_sale_product = delivered_to_customer['id__count'] - return_operation['id__count']
                product = Product.objects.filter(user_id=self.request.user.pk, sku=sku).first()

                unit_price = real_summ_of_sale_product * product.unit_price  # Себестоимость
                logistics = real_summ_of_sale_product * product.logistics_price  # Логистика
                additional_price = real_summ_of_sale_product * product.additional_price  # Добавленная стоимость

                '''
                    Дальше вроде все нормально
                '''

                services_query = OzonTransactions.objects.filter(Q(operation_type="MarketplaceSaleReviewsOperation") |
                                                                 Q(operation_type="OperationMarketplaceCrossDockServiceWriteOff") |
                                                                 Q(operation_type="OperationMarketplaceServiceStorage"),
                                                                 operation_date__lte=date_from,
                                                                 user_id=self.request.user.pk).aggregate(Sum('amount'))
                services = services_query['amount__sum']  # Услуги

                comissions_by_sales_query = OzonTransactions.objects.filter(operation_date__lte=date_from, user_id=self.request.user.pk).aggregate(Sum('sale_commission'))
                comissions_by_sales = comissions_by_sales_query['sale_commission__summ']  # Комиссия за продажу

                """
                    Тут вопрос. Я суммирую amount (как я понял это цена услуги), а в документации написано что сумировать нужно price
                """
                assembly_query = OzonTransactions.objects.filter(Q(operation_type_name="MarketplaceServiceItemFulfillment") |
                                                                 Q(operation_type_name="MarketplaceServiceItemDropoffFf") |
                                                                 Q(operation_type_name="MarketplaceServiceItemDropoffPvz") |
                                                                 Q(operation_type_name="MarketplaceServiceItemDropoffSc"),
                                                                 operation_date__lte=date_from, user_id=self.request.user.pk).aggregate(Sum('amount'))
                assembly = assembly_query['amount__summ']  # Сборка заказа

                highway_query = OzonTransactions.objects.filter(Q(operation_type_name="MarketplaceServiceItemDirectFlowTrans") |
                                                                Q(operation_type_name="MarketplaceServiceItemReturnFlowTrans"),
                                                                operation_date__lte=date_from, user_id=self.request.user.pk).aggregate(Sum('amount'))
                highway = highway_query['amount__summ']  # Магистраль

                last_mile_query = OzonTransactions.objects.filter(operation_type_name="MarketplaceServiceItemDelivToCustomer",
                                                                  operation_date__lte=date_from, user_id=self.request.user.pk).aggregate(Sum('amount'))  # Последняя миля
                last_mile = last_mile_query['amount__summ']  # Последняя миля

                refunds_cancellations_query = OzonTransactions.objects.filter(Q(operation_type_name="MarketplaceServiceItemReturnAfterDelivToCustomer") |
                                                                Q(operation_type_name="MarketplaceServiceItemReturnNotDelivToCustomer") |
                                                                Q(operation_type_name="MarketplaceServiceItemReturnPartGoodsCustomer"),
                                                                operation_date__lte=date_from, user_id=self.request.user.pk).aggregate(Sum('amount'))
                refunds_cancellations = refunds_cancellations_query['amount__summ'] # Плата за возвраты и отмены

                comissions = comissions_by_sales + assembly + highway + last_mile + refunds_cancellations # Комиссия
                # cost = unit_price + logistics + additional_price  # Стоимость товара

        return Response("hui", status=status.HTTP_200_OK)


# class DashbordView(ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     queryset = OzonTransactions.objects.all()
#     serializer_class = OzonTransactionsSerializer
#     pagination_class = LimitOffsetPagination
#     filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
#     ordering_fields = '__all__'
#
#     def get_queryset(self):
#         date = self.request.GET['date']
#         sku = self.request.GET['sku']
#         if date is None:
#             raise ValueError("The given date must be set")
#         else:
#             #Таблица "Дашборт"
#             filter_date = datetime.now() - timedelta(date)
#
#             delivered_to_customer_query = OzonTransactions.objects.filter(operation_date__lte=filter_date, operation_type="OperationAgentDeliveredToCustomer", sku=sku)
#             for delivered_to_customer in delivered_to_customer_query:
#                 sales = delivered_to_customer['price']  # Продажи


