from django.contrib import admin
from .models import Rate


class RateAdmin(admin.ModelAdmin):
    list_display = ('id', 'rate_name', 'validity', 'price', 'description')

admin.site.register(Rate, RateAdmin)