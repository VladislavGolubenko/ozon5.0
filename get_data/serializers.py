from rest_framework import serializers
from .models import *



class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.get("password", None)
        user.set_password(password)
        user.save()
        return user


    class Meta:

        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "patronymic", "role", "date_create", "post_agreement", 'card', 'name_org', 'bank', 'inn', 'orgn', 'kpp', 'bank_account', 'correspondent_bank_account', 'bik')



class TransactionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Transaction
        fields = ("id", "id_user", "transaction_number", "date_issued", "payment_type", "rate", "summ", "status")
