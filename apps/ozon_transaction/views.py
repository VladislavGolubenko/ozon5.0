from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..account.permissions import IsSubscription
from .serializers import OzonTransactionsSerializer
from .models import OzonTransactions
from .service import (
    company_products_function,
)

# Create your views here.
class OzonTransactionsList(ListAPIView):
    """
        Список транзакций оzon
    """
    permission_classes = [IsSubscription]

    queryset = OzonTransactions.objects.all()
    serializer_class = OzonTransactionsSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        return OzonTransactions.objects.filter(user_id=self.request.user.pk)


class ProductDashbordView(APIView):
    permission_classes = [IsSubscription]

    """"
    Аналитическая информация продукта
    """

    serializer_class = OzonTransactionsSerializer

    def get(self, request):
        date = request.GET['date']
        date = int(date)

        if date is None:
            raise ValueError("The given date must be set")
        else:
            #Таблица "Дашборт"
            user_id = self.request.user.pk
            data_list = company_products_function(user_id, date)

            return Response(data_list, status=status.HTTP_200_OK)