from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_photo', 'user_id', 'ozon_product_id', 'marketing_price', 'sku', 'name', 'stock_balance', 'way_to_warehous', 'unit_price',
                    'logistics_price', 'additional_price', 'summ_price', 'reorder_days_of_supply', 'days_for_production')

    readonly_fields = ('summ_price',)

    fieldsets = (
        (None, {
            'fields': ('preview', 'user_id', 'ozon_product_id', 'marketing_price','sku', 'name', 'unit_price',
                    'logistics_price', 'additional_price', 'summ_price', 'reorder_days_of_supply', 'days_for_production')
        }),

        # ('Складской учет', {
        #     'classes': ('collapse',),
        #     'fields': (
        #         'stock_balance', 'history', 'average_order_speed', 'status', 'reordering_date',
        #         'need_to_order', 'reorder_summ', 'reorder_profit', 'stock_for_days', 'deliveries', 'return_product',
        #         'way_to_warehous', 'stock_profit', 'stock_price', 'potential_profit', 'average_unit_profit'),
        # })
    )

    def get_photo(self, obj):
        if obj.preview:
            return mark_safe(f'<img src="{obj.preview}" width="150">')
        return '-'

    get_photo.short_description = 'Фото'


class OrderAdmin(admin.ModelAdmin):

    list_display = ('name', 'user_id', 'order_number', 'sku', 'date_of_order', 'order_place', 'shipping_warehouse', 'number', 'price', 'comission', 'profit', 'status')


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
