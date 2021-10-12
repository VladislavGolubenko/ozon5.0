import requests
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .models import *
from product.tasks import get_product, get_order


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.get("password", None)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):

        if validated_data.get("api_key") is not None:

            ozon_id = str(validated_data['ozon_id'])
            api_key = validated_data['api_key']
            email = validated_data['email']

            api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': ozon_id, 'Api-Key': api_key, 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

            if api_key_isset.status_code == 200:
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                print('после сохранения')
                get_product.delay(validated_data.email)
                get_order.delay(validated_data.email)
                return instance

            else:
                raise ValidationError(
                    detail={"Invalid Api-Key, please contact support": "404"}
                )
                # return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "patronymic", "role", "date_create", "post_agreement", 'card', "card_year", "card_ovner", "ozon_id", "api_key", 'name_org', 'bank', 'inn', 'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Transaction
        fields = ("id", "id_user", "transaction_number", "date_issued", "type", "rate", "summ", "status")
