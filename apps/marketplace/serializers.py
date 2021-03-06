import imp
from rest_framework import serializers
from .models import Marketplace
from ..account.models import User
import requests
from .tasks import upload_products, upload_orders, upload_transactions, upload_stocks, update_order_field, return_marketplace, commisions_products
from ..account.services.orders import OrdersOzon 


class CreateMarketplaceSerializer(serializers.ModelSerializer):
    valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Marketplace
        fields = ("id", "marketplace_name", "marketplace_id", "api_key", "valid")
    
    def create(self, validated_data):
        marketplace_id = str(validated_data.get('marketplace_id'))
        api_key = validated_data.get('api_key')
        marketplace_name = validated_data.get('marketplace_name')
        user = self.context['request'].user

        api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',
                                      headers={'Client-Id': str(marketplace_id), 'Api-Key': str(api_key),
                                               'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

        if api_key_isset.status_code == 200:
            valid = True
            return_marketplace.delay(marketplace_id)

            upload_products.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_orders.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_transactions.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_stocks.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            update_order_field.delay(
                user_id=user.pk,
            )
            commisions_products.delay(
                api_key=api_key,
                client_id=marketplace_id,
            )
        else:
            valid = False

        marketplace = Marketplace.objects.create(
            marketplace_name=marketplace_name, 
            api_key=api_key, 
            marketplace_id=marketplace_id, 
            valid=valid,
            user=user
            )
        user.marketplace_data.add(marketplace.pk)
        return marketplace

    def update(self, instance, validated_data):

        marketplace_id = str(validated_data.get('marketplace_id'))
        api_key = validated_data.get('api_key')
        marketplace_name = validated_data.get('marketplace_name')
        user = self.context['request'].user
        for attr, value in validated_data.items():
            print(attr, value)
            setattr(instance, attr, value)

        api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',
                                      headers={'Client-Id': str(marketplace_id), 'Api-Key': str(api_key),
                                               'Content-Type': 'application/json', 'Host': 'api-seller.ozon.ru'})

        if api_key_isset.status_code == 200:

            upload_products.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_orders.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_transactions.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            upload_stocks.delay(
                api_key=api_key,
                client_id=marketplace_id,
                user_id=user.pk
                )
            update_order_field.delay(
                user_id=user.pk
            )
            commisions_products.delay(
                api_key=api_key,
                client_id=marketplace_id,
            )
            valid = True
        else:
            valid = False
        instance.valid = valid
        instance.save()
        return instance


class ViewMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ("id", "marketplace_name", "marketplace_id", "api_key", "valid")