from rest_framework import serializers
from .models import Rate


class RateSerializer(serializers.ModelSerializer):
    """
        Сериализатор для тарифа
    """
    class Meta:
        model = Rate
        fields = "__all__"
