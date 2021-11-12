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


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'order_number', 'date_of_order', 'in_process_at', 'status', 'posting_number', 'region',
                    'city', 'delivery_type', 'warehous_id', 'warehouse_name', 'creating_date')


class ProductInOrderAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'order_id', 'sku', 'name', 'quantity', 'offer_id', 'price', 'price_f', 'comission_amount',
                    'payout', 'product_id', 'deliv_to_customer',
                    'return_not_deliv_to_customer', 'return_part_goods_customer', 'return_after_deliv_to_customer',
                    'creating_date')


class OzonTransactionAdmin(admin.ModelAdmin):
    list_display = (
    'user_id', 'operation_id', 'operation_type', 'operation_date', 'operation_type_name', 'accruals_for_sale',
    'sale_commission', 'amount', 'type', 'posting_number', 'items', 'services')


class OzonMetricsAdmin(admin.ModelAdmin):
    list_display = ("user_id", "product_id", "product_name", "hits_view_search", "hits_view_pdp", "hits_view",
                    "hits_tocart_search", "hits_tocart_pdp", "hits_tocart", "session_view_search", "session_view_pdp",
                    "session_view", "conv_tocart_search", "conv_tocart_pdp", "conv_tocart", "revenue", "returns",
                    "cancellations", "ordered_units", "delivered_units", "adv_view_pdp", "adv_view_search_category",
                    "adv_view_all", "adv_sum_all", "position_category", "postings", "postings_premium")


admin.site.register(OzonTransactions, OzonTransactionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductInOrder, ProductInOrderAdmin)
admin.site.register(OzonMetrics, OzonMetricsAdmin)
