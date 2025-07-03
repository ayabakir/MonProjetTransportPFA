# systeme_transport_config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transport.urls')),
    path('paiement/', include('a_stripe.urls')),
    # Inclut toutes les URLs de 'transport' à la racine
    path('auth/', include('django.contrib.auth.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)