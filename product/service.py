from django_filters import rest_framework as filters
from .models import Order

class OrderFilter(filters.FilterSet):
    date_of_order = filters.DateFromToRangeFilter()
    class Meta:
        model = Order
        fields = ['date_of_order', ]