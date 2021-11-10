from ozon.celery import app
from .models import *
from rest_framework.response import Response
from rest_framework import status

import requests


@app.task(bind=True)
def return_user_role(self, user_id):
    user = User.objects.get(pk=user_id)
    user.role = User.USER
    user.save()
