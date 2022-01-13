from django.contrib import admin

from .models import OzonTransactions

class OzonTransactionAdmin(admin.ModelAdmin):
    list_display = (
    'user_id', 'operation_id', 'operation_type', 'operation_date', 'operation_type_name', 'accruals_for_sale',
    'sale_commission', 'amount', 'type', 'posting_number', 'services')




admin.site.register(OzonTransactions, OzonTransactionAdmin)