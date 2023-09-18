from bookings import views
from django.urls import include, path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('booking/', views.booking, name='booking'),
    path('addstation/', views.addstation, name='addstation'),
    path('mystation/', views.mystation, name='mystation'),
    path('mybookings/', views.mybookings, name='mybookings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('station_dash/', views.station_dash, name='station_dash'),
    path('update/<int:stid2>/', views.update, name='update'),
    path('bookstation/<int:station_id>', views.bookstation, name='bookstation'),
    path('payment/', views.payment, name='payment'),
    path('delete_items/<int:stid2>/', views.delete_items, name="delete_items"),
    path('delete_booking/<int:stid2>/', views.delete_booking, name="delete_booking"),
    path('delete_adm_user/<int:stid2>/', views.delete_adm_user, name="delete_adm_user"),

]
