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
    path('booking_dash/', views.booking_dash, name='booking_dash'),
    path('station_dash/', views.station_dash, name='station_dash'),
    path('update/<int:stid2>/', views.update, name='update'),
    path('bookstation/<int:station_id>', views.bookstation, name='bookstation'),
    path('allbooking/', views.allbooking, name='allbooking'),
    path('calculate_cost/<int:stid2>/', views.calculate_cost, name='calculate_cost'),
    path('payment1/booking/<int:booking_id>/<int:cost>/', views.payment1, name='payment1'),
    path('payment1/subscription/<int:sub_id>/', views.payment1, name='payment2'),
    path('delete_items/<int:stid2>/', views.delete_items, name="delete_items"),
    path('show/<int:stid2>/', views.show, name="show"),
    path('hide/<int:stid2>/', views.hide, name="hide"),
    path('closed', views.closed, name="closed"),
    path('booking_receipt/', views.booking_receipt, name='booking_receipt'),
    path('station_receipt/', views.station_receipt, name='station_receipt'),  
    path('adm_booking_receipt/', views.adm_booking_receipt, name='adm_booking_receipt'),    
    path('adm_station_receipt/', views.adm_station_receipt, name='adm_station_receipt'), 
    path('adm_payment_receipt/', views.adm_payment_receipt, name='adm_payment_receipt'), 
    path('adm_user_receipt/', views.adm_user_receipt, name='adm_user_receipt'),    
    path('delete_booking/<int:stid2>/', views.delete_booking, name="delete_booking"),
    path('delete_adm_user/<int:stid2>/', views.delete_adm_user, name="delete_adm_user"),
    path('delete_adm_book/<int:stid2>/', views.delete_adm_book, name="delete_adm_book"),
    path('delete_adm_station/<int:stid2>/', views.delete_adm_station, name="delete_adm_station"),
    path('print_as_pdf/<int:stid2>/', views.print_as_pdf, name='print_as_pdf'),
    path('check_bookings', views.check_bookings, name='check_bookings'),
    path('predict', views.predict, name='predict'),
    path('contact', views.contact, name='contact'),
    path('subscription', views.subscription, name='subscription'),
    path('add_subscription', views.add_subscription, name='add_subscription'),
    path('paymenthandler/<int:booking_id>/', views.paymenthandler, name='paymenthandler_booking'),
    path('paymenthandler/subscription/<int:sub_id>/', views.paymenthandler, name='paymenthandler_subscription'),
    path('payment3/<str:total_cost>/<int:service_id>/', views.payment1, name='payment3'),
    path('paymenthandler1/<int:service_id>/', views.paymenthandler, name='paymenthandler_service'),


    
]
