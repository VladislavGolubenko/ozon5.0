from django.urls import path
from .views import SendMessageEmail

urlpatterns = [
    path('send-email-message/', SendMessageEmail.as_view()),
]
