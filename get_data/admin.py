from django.contrib import admin
from .models import *
from product.models import Product

# TabularInline, StackedInline


class ProductInline(admin.TabularInline):
    model = Product
    readonly_fields = ('ozon_product_id', 'sku', 'summ_price')
    fields = ('ozon_product_id', 'sku', 'days_for_production', 'reorder_days_of_supply', 'unit_price',
              'logistics_price', 'additional_price', 'summ_price')
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'patronymic', 'role', 'date_create', 'is_staff', 'is_active',
                    'post_agreement', 'is_superuser')
    list_display_links = ('email',)  # какие поля будут ссылками
    readonly_fields = ('transaction_data',)

    inlines = [
        ProductInline,
    ]

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'patronymic', 'post_agreement', 'is_staff', 'is_active')
        }),

        ('Данные OZON', {
            'classes': ('collapse',),
            'fields': (
                'ozon_id', 'api_key'),
        }),

        ('Данные для оплаты', {
            'classes': ('collapse',),
            'fields': ('card', 'card_year', 'card_ovner', 'name_org', 'bank', 'inn', 'orgn', 'kpp', 'bank_account',
                       'correspondent_bank_account', 'bik'),
        }),


        # ('Товары пользователя', {
        #     'classes': ('collapse',),
        #     'fields': ('products',),
        # }),

        ('Проведенные транзакции', {
            'classes': ('collapse',),
            'fields': ('transaction_data',),
        }),

        ('Дополнительные настройки', {
            'classes': ('collapse',),
            'fields': ('is_superuser', 'role'),
        }),
    )

    list_editable = ('is_staff', 'is_active', 'post_agreement')  # какие поля можно редактировать сразу в таблице
    # search_fields = ()  по каким полям будет происходить поиск
    # list_editable = ('contact_phone',)  # какие поля можно редактировать сразу в таблице
    # list_filter = ('airport_name',)  # для вывода боковых фильтров вывода


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


class PaymentTypeAdmin(admin.ModelAdmin):

    list_display = ('type', 'description')
    list_display_links = ('type',)


class RateAdmin(admin.ModelAdmin):
    list_display = ('id', 'rate_name', 'validity', 'price', 'description')


admin.site.register(User, UserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PaymentType, PaymentTypeAdmin)
admin.site.register(Rate, RateAdmin)
