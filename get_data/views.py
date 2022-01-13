import uuid
import requests
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView

from .models import *
from .serializers import *
from ozon.settings import URL_FRONT
from django.db.models import Q
from .service import send_email_reset_password
from .utils import AccountUtils


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
        serializer = UserSerializer(
            queryset,
            data=request.data,
            files=request.FILES,
            context={'request': request, 'pk': pk, }
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = UserSerializer(queryset)
        return Response(serializer.data)


class SendMailForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SendResetPasswordEmailSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        user = User.objects.filter(email=request.data.get("email")).first()
        if user is None:
            return Response(
                data={"error send mail": "user does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verify_code = uuid.uuid4().hex
        UserResetPasswordCode.objects.create(user=user, verify_code=verify_code)
        url_confirm = (
            URL_FRONT + f"/email-reset-password/?verify_code={verify_code}&id={user.pk}"
        )
        print(url_confirm)
        send_email_reset_password(request.data.get("email"), url_confirm)
        return Response(data={"status": "email sent"}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        id_user = request.data.get("id", None)
        verify_code = request.data.get("verify_code", None)
        password = request.data.get("password", None)

        if id_user is None or verify_code is None or password is None:

            return Response(
                data={"confirmation error": "required id field is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if str(id_user).isdigit() is False:
            return Response(
                data={"confirmation error": "required id field is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        verify_object = UserResetPasswordCode.objects.filter(
            Q(user=id_user) & Q(verify_code=verify_code)
        ).first()

        if verify_object is None:
            return Response(
                data={"confirmation error": "id or verify_code is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            verify_object.delete()
            user = User.objects.filter(pk=id_user).first()
            if user:
                user.set_password(password)
                user.save()
                tokens = AccountUtils.get_tokens_for_user(user)
                return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response(
                    data={"confirmation error": "required id field is missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # return Response(data={"status": "password changed"}, status=status.HTTP_200_OK)


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

