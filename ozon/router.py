from get_data.viewsets import *
from product.viewsets import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', UserViewSet)
# router.register('users_payment', UserPaymentViewSet)
router.register('transaction', TransactionViewSet)
router.register('product', ProductViewSet)

