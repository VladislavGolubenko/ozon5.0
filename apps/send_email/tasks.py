from ozon.celery import app
from .services import SMS


@app.task(name="send_message")
def send_message(title, text, emails):
    SMS.send_sms_to_email(text, title, emails)

