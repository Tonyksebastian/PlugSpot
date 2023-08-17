from bookings import views
from django.urls import include, path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('booking/', views.booking,name='booking'),
]
