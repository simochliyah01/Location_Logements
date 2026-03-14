from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from logements.views import landing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('logements/', include('logements.urls')),
    path('reservations/', include('reservations.urls')),
    path('paiements/', include('paiements.urls')),
    path('', landing, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)