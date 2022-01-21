from django.core.mail import EmailMultiAlternatives, message
from django.conf import settings
from ..account.models import User

class SMS:
    @staticmethod
    def send_sms_to_email(message:str, header_message:str, emails:list) -> None:
        """Отправляет сообщение на определенную почту из настроек в админке"""
        users = User.objects.filter(pk__in=emails) 
        emails = [user.email for user in users]
        text_content = "Инофрмационное сообщение."
        msg = EmailMultiAlternatives(header_message, text_content, settings.EMAIL_HOST_USER, emails)
        msg.attach_alternative(message, "text/html")
        msg.send()
