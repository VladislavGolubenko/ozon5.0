import requests
import json
from datetime import datetime, date
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from get_data.models import User

class OrdersOzon:
    @staticmethod
    def _get_orders_in_json(ozon_id:str, api_key:str) -> json:
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day

        date_to = datetime.now().strftime("%y-%m-%dT23:59:59Z")
        url = 'https://api-seller.ozon.ru/v2/posting/fbo/list'
        json={
            "dir": "asc",
            "filter": {
                "since": "2021-02-01T00:00:00Z", 
                "to": date_to
                },
                "limit": 1000,
                "with": {
                "analytics_data": True,
                "financial_data": True,
                }
            }
        headers={
            'Client-Id': ozon_id, 
            'Api-Key': api_key,
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        request_post = requests.post(
            url=url,
            json=json,
            headers=headers
            )
        if request_post.json().get('messege', None) == 'Invalid Api-Key, please contact support':
            return Response(data='Invalid Api-Key, please contact support', status=status.HTTP_400_BAD_REQUEST)
        return request_post.json()
    
    @staticmethod
    def update_or_create_orders(ozon_id:str, api_key:str, user:User) -> None:


        OrdersOzon._get_orders_in_json(ozon_id, api_key)


        

