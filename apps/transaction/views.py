from re import I
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id_user',)
