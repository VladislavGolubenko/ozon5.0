from django.urls import path
from .views import MarketplaceList, MarketplaceDetail

urlpatterns = [
    path("marketplaces/", MarketplaceList.as_view()),
    path("marketplaces/<int:pk>/", MarketplaceDetail.as_view())
]
