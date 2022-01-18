from rest_framework.pagination import LimitOffsetPagination

from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from .serializers import OzonMetricsSerializer

from ..account.permissions import IsSubscription
from .models import OzonMetrics
from .tasks import get_analitic_data, update_analitics_data
from datetime import datetime


class OzonMetricsAction(ListAPIView):
    """
        Список метрик (аналитической информации) ozon
    """
    permission_classes = [IsAuthenticated, IsSubscription]

    queryset = OzonMetrics.objects.all()
    serializer_class = OzonMetricsSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        """
        При переходе на отображение страницы перед отображением будет должны обновиться (или подтянуться, в случае
        если их нет) аналитические данные озонконкретного пользователя. В дальнейшем обновления данных за это же число
        будут должны происходить на следующий день для финальной актуализации
        """

        today = datetime.now().date()
        this_day_metrics = OzonMetrics.objects.filter(user_id=self.request.user.pk, creating_date=today)
        #email_query = User.objects.get(id=self.request.user.pk)
        user_id = self.request.user.pk
        if this_day_metrics.exists():
            update_analitics_data.delay(user_id=user_id, today=today)
        else:
            get_analitic_data.delay(user_id=user_id)

        return OzonMetrics.objects.filter(user_id=self.request.user.pk)