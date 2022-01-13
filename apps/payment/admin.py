from django.contrib import admin
from .models import PaymentType

class PaymentTypeAdmin(admin.ModelAdmin):

    list_display = ('type', 'description')
    list_display_links = ('type',)



admin.site.register(PaymentType, PaymentTypeAdmin)