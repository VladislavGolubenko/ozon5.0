from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_photo', 'user_id', 'ozon_product_id', 'marketing_price', 'sku', 'name', 'stock_balance',
                    'way_to_warehous', 'unit_price', 'logistics_price', 'additional_price', 'summ_price',
                    'reorder_days_of_supply', 'days_for_production')

    readonly_fields = ('summ_price',)

    fieldsets = (
        (None, {
            'fields': ('preview', 'user_id', 'ozon_product_id', 'marketing_price','sku', 'name', 'unit_price',
                       'logistics_price', 'additional_price', 'summ_price', 'reorder_days_of_supply',
                       'days_for_production')
        }),
    )

    def get_photo(self, obj):
        if obj.preview:
            return mark_safe(f'<img src="{obj.preview}" width="150">')
        return '-'

    get_photo.short_description = 'Фото'




class ProductInOrderAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'order_id', 'sku', 'name', 'quantity', 'offer_id', 'price', 'price_f', 'comission_amount',
                    'payout', 'product_id', 'deliv_to_customer',
                    'return_not_deliv_to_customer', 'return_part_goods_customer', 'return_after_deliv_to_customer',
                    'creating_date')



admin.site.register(Product, ProductAdmin)

admin.site.register(ProductInOrder, ProductInOrderAdmin)

