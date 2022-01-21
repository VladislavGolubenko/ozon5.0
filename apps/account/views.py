import uuid
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
import requests
from rest_framework.generics import CreateAPIView, UpdateAPIView
from .models import User, UserResetPasswordCode
from .serializers import (
    UserSerializer,
    #RegistrationSerializer,
    MeSerializer,
    SendResetPasswordEmailSerializer,
    ResetPasswordEmailSerializer,
)
from .utils import AccountUtils
from .models import User
from .serializers import UserSerializer, MeSerializer
from .permissions import IsOwnerAccount
from django.contrib.auth import password_validation
from django.db.models import Q
from .services.reset_password import send_email_reset_password


# Пока не используется, так как нет такой потребности
class UserView(CreateAPIView): 
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer#RegistrationSerializer
    queryset = User.objects.all()
    # def get(self, request):
    #     user = User.objects.all()
    #     serializer = UserSerializer(user, many=True)
    #     return Response(serializer.data)


class ChangePasswordView(APIView):

    def post(self, request, *args, **kwargs):

        old_password = self.request.data.get("old_password")
        new_password = self.request.data.get("new_password")
        print(old_password, new_password)
        if old_password is not None and new_password is not None:
            user = User.objects.filter(pk=self.request.user.pk).first()
            if user.check_password(old_password) is False:
                return Response(data={"old password not match current": "old password not match current"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.set_password(new_password)
                user.save()
                data = MeSerializer(user).data
                return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data={"field old_password or new_password is not find": "field old_password or new_password is not find"}, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerAccount]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # def get_object(self, pk):
    #     try:
    #         return User.objects.get(pk=pk)
    #     except User.DoesNotExist:
    #         raise Http404

    # def patch(self, request, pk):
    #     queryset = self.get_object(pk)
    #     serializer = UserSerializer(queryset, data=request.data, context={'request': request, 'pk': pk, })

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request, pk):
    #     queryset = self.get_object(pk)
    #     serializer = MeSerializer(queryset)
    #     return Response(serializer.data)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_data = MeSerializer(
            User.objects.get(pk=self.request.user.pk)
        )

        return Response(data=user_data.data, status=status.HTTP_200_OK)


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
            settings.URL_FRONT + f"/email-reset-password/?verify_code={verify_code}&id={user.pk}"
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