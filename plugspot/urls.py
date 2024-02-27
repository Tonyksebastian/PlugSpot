from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userapp.urls')),
    path('bookings/', include('bookings.urls')),
    path('seminar/', include('seminar.urls')),
    path('accounts/', include('allauth.urls')),
    path('make_service/', include('make_service.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
