from pkgutil import iter_modules
import requests
from ...product.models import Product
from ...account.models import User


class ProductOzonCommisions:
    def get_commisions(api_key:str, cliend_id:str):
        url = "https://api-seller.ozon.ru/v2/product/info/prices"
        headers = {
            'Client-Id': str(cliend_id), # ozon_ovner
            'Api-Key': str(api_key) , # user_data.api_key
            'Content-Type': 'application/json', 
            'Host': 'api-seller.ozon.ru'
            }
        items = requests.post(url=url, headers=headers).json().get("result").get("items")
        return items
    
    def update_commisions(api_key:str, cliend_id:str):
        items = ProductOzonCommisions.get_commisions(api_key, cliend_id)
        for item in items:
            product = Product.objects.filter(ozon_product_id=item.get("product_id")).first()
            commisions = item.get("commissions")
            sales_percent = commisions.get("sales_percent")
            fbo_fulfillment_amount = commisions.get("fbo_fulfillment_amount")
            fbo_direct_flow_trans_min_amount = commisions.get("fbo_direct_flow_trans_min_amount")
            fbo_direct_flow_trans_max_amount = commisions.get("fbo_direct_flow_trans_max_amount")
            fbo_deliv_to_customer_amount = commisions.get("fbo_deliv_to_customer_amount")
            if product is not None:
                product.sales_percent = sales_percent
                product.fbo_fulfillment_amount = fbo_fulfillment_amount
                product.fbo_direct_flow_trans_min_amount = fbo_direct_flow_trans_min_amount
                product.fbo_direct_flow_trans_max_amount = fbo_direct_flow_trans_max_amount
                product.fbo_deliv_to_customer_amount = fbo_deliv_to_customer_amount
                product.lower_range_limit = (
                    sales_percent * 1.5
                    ) + (
                    fbo_fulfillment_amount 
                    + fbo_direct_flow_trans_min_amount 
                    + fbo_deliv_to_customer_amount
                    )
                product.upper_range_limit = (
                    sales_percent * 1.5
                    ) + (
                        fbo_fulfillment_amount
                        + fbo_direct_flow_trans_max_amount
                        + fbo_deliv_to_customer_amount
                    )
                product.save()
