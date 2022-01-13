from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

class UserTest(APITestCase):

    def test_show_me_user(self):
        url = reverse('me')
        data = {

        }