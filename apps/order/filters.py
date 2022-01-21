import django_filters
from .models import *


class OrderFilter(django_filters.FilterSet):
    """
        Фильтр по полям комиссии и выручки в заказах
    """

    def comission_filter(self, queryset, order):
        if order == 'ask':
            pass
        elif order == 'desk':
            pass
        else:
            return

    # def amount_filter(self):