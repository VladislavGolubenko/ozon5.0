<<<<<<< HEAD
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

class UserTest(APITestCase):

    def test_show_me_user(self):
        url = reverse('me')
        data = {

        }
=======
from django.test import TestCase

# Create your tests here.
>>>>>>> 51a146d515a506cfaad0a263234998b7ec998056
