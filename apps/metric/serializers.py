from rest_framework import serializers
from .models import OzonMetrics


class OzonMetricsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OzonMetrics
        fields = "__all__"
