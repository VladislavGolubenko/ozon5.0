from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'order_number', 'date_of_order', 'in_process_at', 'status', 'posting_number', 'region',
                    'city', 'delivery_type', 'warehous_id', 'warehouse_name', 'creating_date')
    search_fields = ("order_number",)
admin.site.register(Order, OrderAdmin)
