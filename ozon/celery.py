import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozon.settings')

app = Celery('ozon')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.timezone = 'Europe/Moscow'


app.conf.beat_schedule = {
    # Подгрузка и обновление товаров
    'create_or_update_products_every_day': {
        'task': 'create_or_update_products_every_day',
        'schedule': 30,
    },
    # Подгрузка заказов
    'create_or_update_orders_every_day': {
        'task': 'create_or_update_orders_every_day',
        'schedule': 31,#crontab(minute=17, hour=17),
        # 'schedule': 30,
    },
    # Подгрузка транзакций
    'create_or_update_transactions_every_day': {
        'task': 'create_or_update_transactions_every_day',
        'schedule': 32,#crontab(minute=18, hour=17),
    },

    # Поля комиссии и выручка у заказов
    'update_order_field': {
        'task': 'update_order_field',
        'schedule': 32,#crontab(minute=18, hour=17),
    }





    # 'get_analitic_data': {
    #     'task': 'get_analitic_data',
    #     'schedule': 17,#crontab(minute=19, hour=17),
    # },

    # 'update_analitics_data': {
    #     'task': 'update_analitics_data',
    #     'schedule': 18,#crontab(minute=20, hour=17),
    # }
}

# app.conf.beat_schedule = {
#     'update_product_order': {
#         'task': 'product.tasks.update_product_order',
#         'schedule': crontab(minute=0, hour=0),
#         # 'schedule': 30,
#     },

#     'found_new_ozon_transaction': {
#         'task': 'product.tasks.found_new_ozon_transaction',
#         'schedule': crontab(minute=30, hour=23),
#     },

#     'get_analitic_data': {
#         'task': 'product.tasks.get_analitic_data',
#         'schsdule': crontab(minute=0, hour=1),
#     },

#     'update_analitics_data': {
#         'task': 'product.tasks.update_analitics_data',
#         'schsdule': crontab(minute=0, hour=1),
#     }
# }
