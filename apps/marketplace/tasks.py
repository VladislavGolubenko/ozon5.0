from re import I
from ozon.celery import app
from ..account.services.products import ProductsOzon
from ..account.models import User


@app.task(name="upload_products")
def upload_products(api_key:str, client_id, user_id):
    user = User.objects.get(pk=user_id)
    ProductsOzon.update_or_create_products(api_key, client_id, user)