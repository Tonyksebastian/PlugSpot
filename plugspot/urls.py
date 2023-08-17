
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userapp.urls')),
    path('bookings/', include('bookings.urls')),
    path('accounts/', include('allauth.urls')),
  
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
