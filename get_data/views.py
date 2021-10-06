from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
import requests

from .models import *
from .serializers import *


class UserAction(APIView):

    def get(self, request):

        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


def test_action(request):
    user_transaction_query = Transaction.objects.filter(id_user=1)
    return_transaction = ''

    for user_transaction in user_transaction_query:
        return_transaction = return_transaction + f'Номер транзакции:{user_transaction.transaction_number}, \n Дата транзакции:{user_transaction.date_issued}, \n Тип оплаты:{user_transaction.type}, \n Тариф: {user_transaction.rate}, \n Сумма:{user_transaction.summ} \n \n \n'

    return HttpResponse('<h1>Transaction</h1>')