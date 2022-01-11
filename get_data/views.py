from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
import requests

from .models import *
from .serializers import *


class UserAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


class RatesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        rates = Rate.objects.all()
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)


class RateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Rate.objects.get(pk=pk)
        except Rate.DoesNotExist:
            raise Http404

    def put(self, request, pk):

        queryset = self.get_object(pk)
        serializer = RateSerializer(queryset, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):

        rate = self.get_object(pk)
        serializer = RateSerializer(rate)
        return Response(serializer.data)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = UserSerializer(queryset, data=request.data, context={'request': request, 'pk': pk, })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = UserSerializer(queryset)
        return Response(serializer.data)

# def test_action(request):
#     permission_classes = [permissions.IsAuthenticated]
#     user_transaction_query = Transaction.objects.filter(id_user=1)
#     return_transaction = ''
#
#     for user_transaction in user_transaction_query:
#         return_transaction = return_transaction + f'Номер транзакции:{user_transaction.transaction_number}, \n ' \
#                                                   f'Дата транзакции:{user_transaction.date_issued}, \n Тип оплаты:' \
#                                                   f'{user_transaction.type}, \n Тариф: {user_transaction.rate}, \n ' \
#                                                   f'Сумма:{user_transaction.summ} \n \n \n'
#
#     return HttpResponse('<h1>Transaction</h1>')

