import json
from django.http import Http404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import (
    ProductSerializer,
    ProductInOrderSerializer,
    CompanyDashbordSerializer
)
from rest_framework import permissions
from ..account.permissions import IsSubscription
from .models import Product, ProductInOrder
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, datetime
from .service import (
    warehous_account_function,
    company_dashbord_function,
)
from django.db.models import Q
from .filters import ProductActualFilter


class ProductInOrderAction(RetrieveUpdateDestroyAPIView):
    """
        Заказанные товары
    """
    permission_classes = [IsSubscription]

    queryset = ProductInOrder.objects.all()
    serializer_class = ProductInOrderSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter)
    ordering_fields = '__all__'
    search_fields = ['sku', 'name', 'product_id', 'offer_id']


    def get_queryset(self):
        return ProductInOrder.objects.filter(user_id=self.request.user.pk)


class ProductListAction(ListCreateAPIView):
    """
        Список товаров
    """
    permission_classes = [permissions.IsAuthenticated]#[IsSubscription]

    queryset = Product.objects.filter(is_visible=True)
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter)
    ordering_fields = '__all__'
    search_fields = ['sku', 'name', 'ozon_product_id', 'offer_id']
    def get_queryset(self):

        actual = self.request.GET.get('actual')  # Получаем True/False (актуальный ли товар) для фильтра

        if actual is not None:
            actual = True if actual == "True" or actual == '1' else False
            queryset = Product.objects.filter(user_id=self.request.user.pk, is_visible=True)
            return ProductActualFilter.actual_products(self, queryset=queryset, actual=actual)

        return Product.objects.filter(user_id=self.request.user.pk, is_visible=True)

    def perform_create(self, serializer):
        return serializer.save()


class ProductDetailAction(APIView):
    """
        Конкретный товар
    """
    permission_classes = [IsAuthenticated, IsSubscription]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk, is_visible=True)
        except Product.DoesNotExist:
            raise Http404

    def get(self, pk):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = ProductSerializer(queryset, data=request.data, context={'request': request, 'sku': queryset.sku, })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





class WarehouseAccountView(APIView):
    """
        Складской учет
        Для поиска использовать параметр search
    """

    #permission_classes = [IsSubscription]
    def get(self, request):

        # serializer = WarehouseAccountSerializer

        # json_with_id = json.loads(request.body.decode("utf-8"))
        # id_of_user = json_with_id['id']
        
        id_user = request.user.id
        
        # print(request.user.id)
        search = request.query_params.get("search")
        days = int(request.query_params.get("days"))
        print(days)
        print(isinstance(search, str))
        products = Product.objects.filter(user_id=id_user, is_visible=True)

        if (search is not None) and (search !=''):

            try:
                if isinstance(int(search), int):

                    products = products.filter(
                                                Q(sku__contains=search)
                                                | Q(name__contains=search)
                                                | Q(ozon_product_id=search)
                                                | Q(offer_id=search)
                                            )
            except:
                products = products.filter(
                                                Q(sku__contains=search)
                                                | Q(name__contains=search)
                                                | Q(offer_id=search)
                                            )


        datas = []

        for product in products:

            data = warehous_account_function(product=product, days=days)

            datas.append(data)
        #print(datas)
        paginator = LimitOffsetPagination()
        result_page = paginator.paginate_queryset(datas, request)

        return Response(data=result_page, status=status.HTTP_200_OK)


# class ObjectInTableView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     """
#     возвращаем кол-во обьектов в каждой из таблиц
#     """

#     def get(self, request, table):

#         if table == 'product':
#             objects = Product.objects.filter(user_id=self.request.user.pk)
#         elif table == 'ozon_transactions':
#             objects = OzonTransactions.objects.filter(user_id=self.request.user.pk)
#         elif table == 'order':
#             objects = Order.objects.filter(user_id=self.request.user.pk)
#         elif table == 'ozon_metrics':
#             objects = OzonMetrics.objects.filter(user_id=self.request.user.pk)
#         else:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         summ_of_object = len(objects)

#         return Response(summ_of_object, status=status.HTTP_200_OK)


class CompanyDashbordView(APIView):
    permission_classes = [IsAuthenticated, IsSubscription]

    """
    Aналитичская информация компании

    для получения необходимо передать
    date - Передается в количестве дней. Дата от кокого числа (и до сегоднешнего дня) будет передана аналитика.

    """

    serializers = CompanyDashbordSerializer

    def get(self, request):
        date = int(self.request.GET.get('date'))
        date_from = datetime.now() - timedelta(date)

        if date is not None:
            data = company_dashbord_function(user_id=self.request.user.pk, date_from=date_from)

            if data['sku'] is not None:
                return Response(data, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(data, status=status.HTTP_200_OK)

        raise ValueError("The given date must be set")

class ProductInOrderSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    '''
        Получение не хватающих данных в архивных товарах
        (в актуальных эти данные вводит пользователь)
        данные передаются через Form-data:

            days_for_production
            reorder_days_of_supply
            unit_price
            logistics_price
            additional_price

        Названия полей на русском:

            'Времени необходимо для производства'
            'Глубина поставки'
            'Цена юнита'
            'Цена логистики'
            'Дополнительные затраты'
    '''

    def post(self, request, sku):

        days_for_production = int(request.data['days_for_production']) if request.data['days_for_production'] is not None else 0
        reorder_days_of_supply = int(request.data['reorder_days_of_supply']) if request.data['reorder_days_of_supply'] is not None else 0
        unit_price = int(request.data['unit_price']) if request.data['unit_price'] is not None else 0
        logistics_price = int(request.data['logistics_price']) if request.data['logistics_price'] is not None else 0
        additional_price = int(request.data['additional_price']) if request.data['additional_price'] is not None else 0

        sum_price = unit_price + logistics_price + additional_price

        products_in_order = ProductInOrder.objects.filter(sku=sku, user_id=request.user.pk)
        for product_in_order in products_in_order:
            product_in_order.days_for_production = days_for_production
            product_in_order.reorder_days_of_supply = reorder_days_of_supply
            product_in_order.unit_price = unit_price
            product_in_order.logistics_price = logistics_price
            product_in_order.additional_price = additional_price
            product_in_order.sum_price = sum_price
            product_in_order.save()
        return Response(status=status.HTTP_202_ACCEPTED)
