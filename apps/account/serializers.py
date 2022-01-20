import imp
from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import User
from ..metric.tasks import get_analitic_data
from datetime import datetime, date
from datetime import timedelta
import openpyxl
import requests
from ..transaction.models import Transaction
from ..marketplace.models import Marketplace


# class RegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(required=False)
#     email = serializers.EmailField(required=False)

#     def create(self, validated_data):
#         print(User.objects.filter(email=validated_data.get("email")).first() is not None)
#         if User.objects.filter(email=validated_data.get("email")).first() is not None:
#             raise ValidationError(detail="user_is_exist")
#         user = User(**validated_data)
#         password = validated_data.get("password", None)
#         user.set_password(password)
#         user.save()
#         return user
#     class Meta:
#         model = User
#         fields = ("email", "password")


class MeSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(use_url=False, allow_null=True, required=False)
    class Meta:
        model = User
        fields = ("id", "avatar", "email", "first_name", "last_name", "patronymic", "role", "date_create",
                  "post_agreement", 'card', "card_year", "card_ovner", 'name_org', 'bank', 'inn',
                  'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik', 'user_tarif_data')


class UserSerializer(serializers.ModelSerializer):

    """
    Пользователь

    Сериализатор для создания пользователя, изменения пароля или данных для подключения к ozon и в целом пользователя.

    Поля которые необходимо указывать при сохранении данных маркетплейса
        marketplace_id
        api_key
        marketplace_name

    Поля которые необходимо указывать при изменении пароля:
        new_password

    Для изменения данны
    """
    avatar = serializers.ImageField(use_url=False, allow_null=True, required=False)
    #password = serializers.CharField(required=False)
    #email = serializers.EmailField(required=False)

    def create(self, validated_data):
        user = User(**validated_data)
        print(validated_data.get("password", None))
        password = validated_data.get("password", None)
        user.set_password(password)
        user.save()
        return user

    # def update(self, instance, validated_data):
    #     user_id = self.context['request'].user
    #     if validated_data.get("new_password") is not None:
    #         for attr, value in validated_data.items():
    #             setattr(instance, attr, value)

    #         password = validated_data.get("new_password", None)
    #         instance.set_password(password)

    #         instance.save()
    #         return instance

    #     else:
    #         user = User.objects.get(id=user_id.id)

    #         for attr, value in validated_data.items():
    #             setattr(instance, attr, value)

    #         password = validated_data.get("password", None)

    #         if user.password == password:
    #             instance.save()
    #             return instance
    #         elif password == None:
    #             instance.save()
    #             return instance
    #     return instance
    # new_password = serializers.CharField(max_length=32, write_only=True, required=False)
    # marketplace_id = serializers.IntegerField(write_only=True, required=False)
    # marketplace_name = serializers.CharField(max_length=32, write_only=True, required=False)

    class Meta:
        model = User#"password",  
        
        fields = ("id", "avatar", "password", "email", "first_name", "last_name", "patronymic", "date_create",
                  "post_agreement", 'card', "card_year", "card_ovner", 'name_org', 'bank', 'inn',
                  'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik', 'user_tarif_data')


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordEmailSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    verify_code = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )
