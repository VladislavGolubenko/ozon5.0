import django_filters
from .models import *


class ProductActualFilter(django_filters.FilterSet):
    """
        Фиильтр возвращающий товары с количеством больше 0
    """

    def actual_products(self, queryset, actual: bool):

        if actual == True:
            return queryset.filter(stock_balance__gt=0)
        else:
            return queryset

    class Meta:
        model = Product
        fields = ['stock_balance']


class WarehousFilterByList:
    """
        Фильтр возвращающий акктуальные товары в складском учете (модель динамическая, формируется в список)
    """

    def actual_warehous(self, data: list, actual: bool):
        if actual == True:
            new_data = list()
            for value in data:
                if value['stocks_cost_price'] is not None:
                    if value['stocks_cost_price'] > 0:
                        new_data.append(value)
            return new_data
        else:
            return data
