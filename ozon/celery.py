import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozon.settings')

app = Celery('ozon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'update_product_order': {
        'task': 'product.tasks.update_product_order',
        'schedule': crontab(minute=0, hour=0),
        # 'schedule': 30,
    },

    'found_new_ozon_transaction': {
        'task': 'product.tasks.found_new_ozon_transaction',
        'schedule': crontab(minute=30, hour=23),
    },

    'get_analitic_data': {
        'task': 'product.tasks.get_analitic_data',
        'schsdule': crontab(minute=0, hour=1),
    },

    'update_analitics_data': {
        'task': 'product.tasks.update_analitics_data',
        'schsdule': crontab(minute=0, hour=1),
    }
}
