import requests
from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import *
from product.tasks import get_product, get_order, get_ozon_transaction


class UserSerializer(serializers.ModelSerializer):

    """
    Сериализатор для создания пользователя, изменения пароля или данных для подключения к ozon.

    Обязательные поля:
        email
        password

    Поля которые необходимо указывать при сохранении данных ozon:
        email
        password
        ozon_id
        api_key

    Поля которые необходимо указывать при изменении пароля:
        email
        password
        new_password
    """

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
            email = str(validated_data.get('email'))

            api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': ozon_id, 'Api-Key': api_key, 'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})
            user = User.objects.get(email=validated_data.get("email"))

            if api_key_isset.status_code == 200 and user.password == instance.password:

                for attr, value in validated_data.items():
                    setattr(instance, attr, value)

                password = validated_data.get("password", None)
                instance.set_password(password)

                instance.save()
                # get_product.delay(email=email)
                # get_order.delay(email=email)
                get_ozon_transaction.delay(email=email)
                return instance
            else:
                raise ValidationError(
                    detail={"Invalid Api-Key, please contact support": "404"}
                )

        elif validated_data.get("new_password") is not None:
            print('заходит в сохранение нового пароля')
            user = User.objects.get(email=validated_data.get("email"))
            if user.password == instance.password:
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)

                password = validated_data.get("new_password", None)
                instance.set_password(password)

                instance.save()
                return instance
            else:
                raise ValidationError(
                    detail={"Invalid password, please enter correct password": "404"}
                )
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

    new_password = serializers.CharField(max_length=32, write_only=True, required=False)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "patronymic", "role", "date_create",
                  "post_agreement", 'card', "card_year", "card_ovner", "ozon_id", "api_key", 'name_org', 'bank', 'inn',
                  'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik', 'new_password')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Transaction
        fields = ("id", "id_user", "transaction_number", "date_issued", "type", "rate", "summ", "status")
