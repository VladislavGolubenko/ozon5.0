import imp
from re import I
from ozon.celery import app
from ..account.services.products import ProductsOzon
from ..account.models import User
from ..account.services.orders import OrdersOzon
from ..account.services.transaction import TransactionOzon
from ..account.services.stocks import StocksOzon


# Работа с продуктами
@app.task(name="upload_products")
def upload_products(api_key: str, client_id, user_id):

    """Обновление продуктов по одному пользователю"""

    user = User.objects.get(pk=user_id)
    ProductsOzon.update_or_create_products(api_key, client_id, user)


@app.task(bind=True, name="create_or_update_products_every_day")
def create_or_update_products_every_day(*args, **kwargs):

    """Обновление продуктов по всем пользователям"""

    for user in User.objects.all():
        for marketplace in user.marketplace_data.all():
            marketplace_id = marketplace.marketplace_id
            api_key = marketplace.api_key
            ProductsOzon.update_or_create_products(api_key, marketplace_id, user)


# Работа с заказами
@app.task(name="upload_orders")
def upload_orders(api_key: str, client_id, user_id):
    
    """Обновление заказов по одному пользователю"""

    user = User.objects.get(pk=user_id)
    OrdersOzon.update_or_create_orders(api_key, client_id, user)


@app.task(bind=True, name="create_or_update_orders_every_day")
def create_or_update_orders_every_day(*args, **kwargs):

    """Обновление заказов по всем пользователям"""

    for user in User.objects.all():
        for marketplace in user.marketplace_data.all():
            marketplace_id = marketplace.marketplace_id
            api_key = marketplace.api_key
            OrdersOzon.update_or_create_orders(api_key, marketplace_id, user)


@app.task(name="update_order_field")
def update_order_field(user_id):

    """Подсчет полей сумма комиссий и выручка, кол-во, сумма заказа"""

    user = User.objects.get(pk=user_id)
    OrdersOzon.update_order_fields(user=user)


@app.task(bind=True, name="update_order_fields_every_day")
def update_order_fields_every_day(*args, **kwargs):

    """постоянное обновление денежных полей заказа"""

    for user in User.objects.all():
        OrdersOzon.update_order_fields(user=user)



# Работа с транзакциями озона
@app.task(name="upload_transactions")
def upload_transactions(api_key: str, client_id, user_id):

    """Обновление заказов по одному пользователю"""

    user = User.objects.get(pk=user_id)
    TransactionOzon.create_transactions(api_key, client_id, user)


@app.task(bind=True, name="create_or_update_transactions_every_day")
def create_or_update_transactions_every_day(*args, **kwargs):

    """Обновление заказов по всем пользователям"""

    for user in User.objects.all():
        for marketplace in user.marketplace_data.all():
            marketplace_id = marketplace.marketplace_id
            api_key = marketplace.api_key
            TransactionOzon.create_transactions(api_key, marketplace_id, user)


# Работа с транзакциями озона
@app.task(name="upload_stocks")
def upload_stocks(api_key:str, client_id, user_id):

    """Обновление остатков товаров по одному пользователю"""

    StocksOzon.update_stocks(api_key, client_id)


@app.task(bind=True, name="create_or_update_stocks_every_day")
def create_or_update_stocks_every_day(*args, **kwargs):

    """Обновление остатков товаров по всем пользователям"""

    for user in User.objects.all():
        for marketplace in user.marketplace_data.all():
            marketplace_id = marketplace.marketplace_id
            api_key = marketplace.api_key
            StocksOzon.update_stocks(api_key, marketplace_id)
