from ..product.models import Product
from ..order.models import Order
from ..ozon_transaction.models import OzonTransactions

def set_is_visible_false(marketplace_id:int, status:bool):
    products = Product.objects.filter(marketplace_id=marketplace_id)
    orders = Order.objects.filter(marketplace_id=marketplace_id)
    transactions = OzonTransactions.objects.filter(marketplace_id=marketplace_id)   
    products.update(is_visible = status)
    orders.update(is_visible = status)
    transactions.update(is_visible = status)
    #for product in products:
    #    print("product: ", product)
    #    product.is_visible = status
    #    product.save()
    # for order in orders:
    #     print("order: ", order)
    #     order.is_visible = status
    #     order.save()
    # for transaction in transactions:
    #     print("transaction: ", transaction)
    #     transaction.is_visible = status
    #     transaction.save()
