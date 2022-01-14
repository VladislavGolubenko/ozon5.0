import imp
from rest_framework import serializers
from .models import Marketplace
from ..account.models import User
import requests

class CreateMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ("id", "marketplace_name", "marketplace_id", "api_key")
    
    def create(self, validated_data):
        print(validated_data)
       
        marketplace_id = str(validated_data.get('marketplace_id'))
        api_key = validated_data.get('api_key')
        marketplace_name = validated_data.get('marketplace_name')
        user = self.context['request'].user
        print(user)
        

        
        api_key_isset = requests.post('https://api-seller.ozon.ru/v1/product/list',  headers={'Client-Id': marketplace_id,
                                                                                                'Api-Key': api_key,
                                                                                                'Content-Type': 'application/json',
                                                                                                'Host': 'api-seller.ozon.ru'})
        if api_key_isset.status_code == 200:
            valid = True
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

class ViewMarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ("id", "marketplace_name", "marketplace_id", "api_key", "valid")