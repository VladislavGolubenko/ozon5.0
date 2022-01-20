import django_filters
from .models import *


class ProductActualFilter(django_filters.FilterSet):
    """
        Фиильтр возвращающий товары с количеством больше 0
    """

    def actual_products(self, queryset, actual: bool):
        print("actual=====================", actual)
        if actual == True:
            return queryset.filter(stock_balance__gt=0)
        else:
            return queryset

    class Meta:
        model = Product
        fields = ['stock_balance']
