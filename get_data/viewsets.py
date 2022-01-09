from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import *
from .serializers import *


class MeViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_data = UserSerializer(
            User.objects.get(pk=self.request.user.pk)
        )

        return Response(data=user_data.data, status=status.HTTP_200_OK)


# class UserViewSet(viewsets.ModelViewSet):
#
#     queryset = User.objects.all()
#     serializer_class = UserSerializer(context={'request': request, 'sku': queryset.sku, })

    # def perform_create(self, serializer):
    #     user = None
    #     if self.request and hasattr(self.request, "user"):
    #         user = self.request.user
    #     serializer.save(user=user, foo='foo')



class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id_user',)
