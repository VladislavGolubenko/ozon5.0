from binascii import Incomplete
import requests
from ...product.models import Product
import json


class StocksOzon:
    def get_stocks(api_key:str, ozon_id:str):
        url = "https://api-seller.ozon.ru/v2/product/info/stocks"
        headers = {
            "Client-Id": ozon_id,
            "Api-Key": api_key
        } 
        stocks = requests.post(url=url, headers=headers)
        return stocks.json().get("result").get("items")


    def update_stock(stock: json):
        product_id = stock.get("product_id")
        product = Product.objects.filter(ozon_product_id=product_id).first()
        if product is not None:
            stocks = stock.get("stocks")
            fbo_stocks = 0
            discounted_stocks = 0
            for stock in stocks:
                if stock.get("type") == "fbo":
                    fbo_stocks = stock.get("present")
                if stock.get("type") == "discounted":
                    discounted_stocks = stock.get("present")

            
            product.stock_balance = fbo_stocks + discounted_stocks
            product.save()
    
    def update_stocks(api_key:str, ozon_id:str):
        for stock in StocksOzon.get_stocks(api_key, ozon_id):
            StocksOzon.update_stock(stock)