import imp
from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import User
from .tasks import create_or_update_products, get_order, get_ozon_transaction
from ..metric.tasks import get_analitic_data
from datetime import datetime, date
from datetime import timedelta
import openpyxl
import requests
from ..transaction.models import Transaction
from ..marketplace.models import Marketplace


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def create(self, validated_data):
        print(User.objects.filter(email=validated_data.get("email")).first() is not None)
        if User.objects.filter(email=validated_data.get("email")).first() is not None:
            raise ValidationError(detail="user_is_exist")
        user = User(**validated_data)
        password = validated_data.get("password", None)
        user.set_password(password)
        user.save()
        return user
    class Meta:
        model = User
        fields = ("email", "password")

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

    password = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.get("password", None)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user_id = self.context['request'].user

        if validated_data.get("api_key") is not None:
            marketplace_id = str(validated_data['marketplace_id'])
            api_key = validated_data['api_key']
            marketplace_name = validated_data['marketplace_name']
            pk = self.context['pk']
            user = User.objects.get(pk=pk)

            if marketplace_name == "ozon":
                api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': marketplace_id,
                                                                                                      'Api-Key': api_key,
                                                                                                      'Content-Type': 'application/json',
                                                                                                      'Host': 'api-seller.ozon.ru'})
                if api_key_isset.status_code == 200:
                    last_validations_date = datetime.now()
                    marketplace = Marketplace.objects.create_marketplace(marketplace_name=marketplace_name, marketplace_id=marketplace_id,
                                                                         api_key=api_key, last_validations_date=last_validations_date)

                    user.marketplace_data.add(marketplace.pk)

                    # instance.save()
                    # get_product.delay(user_id=user_id.id)
                    # get_order.delay(user_id=user_id.id)
                    # get_ozon_transaction.delay(user_id=user_id.id)
                    # get_analitic_data.delay(user_id=user_id.id)
                    return marketplace
                else:
                    raise ValidationError(
                        detail={"Invalid Api-Key, please contact support": "404"}
                    )

        elif validated_data.get("new_password") is not None:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            password = validated_data.get("new_password", None)
            instance.set_password(password)

            instance.save()
            return instance

        else:
            user = User.objects.get(id=user_id.id)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            password = validated_data.get("password", None)

            if user.password == password:
                instance.save()
                return instance
            elif password == None:
                instance.save()
                return instance

    new_password = serializers.CharField(max_length=32, write_only=True, required=False)
    marketplace_id = serializers.IntegerField(write_only=True, required=False)
    marketplace_name = serializers.CharField(max_length=32, write_only=True, required=False)


    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "patronymic", "role", "date_create",
                  "post_agreement", 'card', "card_year", "card_ovner", "ozon_id", "api_key", 'name_org', 'bank', 'inn',
                  'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik', 'new_password', 'user_tarif_data',
                  'return_status', 'marketplace_id', 'marketplace_name')
