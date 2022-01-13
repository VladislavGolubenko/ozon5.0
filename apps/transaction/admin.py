from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'transaction_number', 'rate', 'status', 'type', 'date_issued', 'summ')

    # list_display = ('id_user', 'transaction_number', 'rate', 'status',  'type', 'date_issued', 'summ')
    # readonly_fields = ('transaction_number', 'date_issued', 'summ')
    # list_editable = ('rate', 'status')
    # fieldsets = (
    #     (None, {
    #         'fields': ('id_user', 'transaction_number', 'rate', 'status',  'payment_type', 'date_issued', 'summ')
    #     }),
    # )

admin.site.register(Transaction, TransactionAdmin)