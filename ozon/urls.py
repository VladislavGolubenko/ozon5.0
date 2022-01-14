from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f"api/{settings.VERSION_API}/", include('apps.account.urls')),
    path(f"api/{settings.VERSION_API}/", include('apps.metric.urls')),
    path(f"api/{settings.VERSION_API}/", include('apps.ozon_transaction.urls')),
    path(f"api/{settings.VERSION_API}/", include('apps.product.urls')), 
    path(f"api/{settings.VERSION_API}/", include('apps.rate.urls')),
    path(f"api/{settings.VERSION_API}/", include('apps.transaction.urls')),
    path(f"api/{settings.VERSION_API}/", include('apps.order.urls')),
    #path(f"api/{settings.VERSION_API}/", include('apps.payment.urls')), # Такого файла нет
    path(f"api/{settings.VERSION_API}/", include('apps.marketplace.urls')), # Такого файла нет
]
#Ссылки на статику и медиа файлы
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#Ссылки на документацию
urlpatterns += doc_urls
