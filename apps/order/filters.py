import django_filters
from .models import *


class OrderFilter(django_filters.FilterSet):
    """
        Фильтр по полям комиссии и выручки в заказах
    """

    def comission_filter(self, queryset, order):

        comissions = OzonTransactions.objects.filter(posting_number=self.posting_number)
        comissions_summ = 0

        for comission in comissions:
            comissions_summ += (comission.sale_commission)

        if order == 'ask':
            pass
        elif order == 'desk':
            pass
        else:
            return queryset

    def amount_filter(self, queryset, order):

        amounts = OzonTransactions.objects.filter(posting_number=self.posting_number)
        amounts_summ = 0

        for amount in amounts:
            amounts_summ += (amount.amount)

        if order == "ask":
            pass
        elif order == "desk":
            pass
        else:
            return queryset
