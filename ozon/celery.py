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
        'schedule': crontab(hour="*/1"),
    },
    # Подгрузка заказов
    'create_or_update_orders_every_day': {
        'task': 'create_or_update_orders_every_day',
        'schedule': crontab(hour="*/1"),
        
    },
    # Подгрузка транзакций
    'create_or_update_transactions_every_day': {
        'task': 'create_or_update_transactions_every_day',
        'schedule': crontab(hour="*/1"),
    },

    # Поля комиссии и выручка у заказов
    'update_order_fields_every_day': {
        'task': 'update_order_fields_every_day',
        'schedule': crontab(hour="*/1"),
    }


    # # Обновление коммисий продуктов
    # 'commisions_products_every_day': {
    #     'task': 'commisions_products_every_day',
    #     'schedule': crontab(hour="*/1"),
    # }


    # 'get_analitic_data': {
    #     'task': 'get_analitic_data',
    #     'schedule': 17,#crontab(minute=19, hour=17),
    # },

    # 'update_analitics_data': {
    #     'task': 'update_analitics_data',
    #     'schedule': 18,#crontab(minute=20, hour=17),
    # }
}
