from datetime import datetime, timedelta
import django_filters
from .models import *


class OrderFilter(django_filters.FilterSet):
    """
        Фильтр по дате заказа и статусу
    """
    def order_date_filter(self,  queryset):
        date = int(self.request.GET.get('days'))

        if date is not None:
            start_date = datetime.now() - timedelta(date)
            return queryset.filter(date_of_order__gte=start_date)
        else:
            return queryset

    def order_status_filter(self, queryset):
        status = self.request.GET.get('status')
        status_tuple = (
            'awaiting_approve',
            'awaiting_packaging',
            'awaiting_deliver',
            'delivering',
            'delivered',
            'cancelled',
        )

        if status in status_tuple:
            return queryset.filter(status=status)
        else:
            return queryset

    class Meta:
        model = Order
        fields = ['date_of_order', 'status']

