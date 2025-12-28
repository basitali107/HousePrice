from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('HousePricePrediction.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('price-page/', include('price_page.urls')), # maps /price-page/ to price_page_view
    path('floor-map/', include('floor_map.urls')),
    



]

# REQUIRED for profile_pic uploads
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)