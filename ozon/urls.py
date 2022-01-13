from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from .router import router
from .yasg import urlpatterns as doc_urls

# from product.views import order_action
# test_action,


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("api/products/", include('product.urls')),
    path('api/user/', include('get_data.urls')),
    # path('test/', test_action),
    # path('order/', order_action)
    # path('api/', include('rest_framework.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += doc_urls
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)