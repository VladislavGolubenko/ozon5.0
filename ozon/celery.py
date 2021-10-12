import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozon.settings')

app = Celery('ozon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_product_order': {
        'task': 'product.tasks.update_product_order',
        'schedule': 15.0,
    }
}
