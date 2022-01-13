from rest_framework import serializers
from .models import OzonTransactions


class OzonTransactionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OzonTransactions
        fields = "__all__"

