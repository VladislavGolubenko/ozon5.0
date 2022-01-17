from re import I
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import OrderingFilter


class TransactionView(ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    ordering_fields = 'all'

    def get_queryset(self):
        return Transaction.objects.filter(id_user=self.request.user.pk)
