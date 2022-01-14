from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Marketplace
from .serializers import CreateMarketplaceSerializer, ViewMarketplaceSerializer
from .permissions import IsOwnerMarketplace


class MarketplaceList(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    #serializer_class = MarketplaceSerializer
    pagination_class = None
    def get_queryset(self):
        queryset = Marketplace.objects.filter(user=self.request.user)
        return queryset
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ViewMarketplaceSerializer
        else:
            return CreateMarketplaceSerializer
        #return super().get_serializer_class()
    
class MarketplaceDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerMarketplace]

    #serializer_class = MarketplaceSerializer
    queryset = Marketplace.objects.all()
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ViewMarketplaceSerializer
        else:
            return CreateMarketplaceSerializer
    # def get_queryset(self):
    #     queryset = Marketplace.objects.filter(user=self.request.user)
    #     return queryset