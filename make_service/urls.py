from django.shortcuts import render
from django.urls import path
from make_service import views
from .views import *

urlpatterns = [

    path('', views.service_home, name='service_home'),
    path('select_station/', views.select_station, name='select_station'),
    path('addservicestation/', views.addservicestation, name='addservicestation'),
    path('services/<int:ser_id>', views.services, name='services'),
    path('hide_ser_station/<int:stid3>/', views.hide_ser_station, name="hide_ser_station"),
    path('show_serstation/<int:stid2>/', views.show_serstation, name="show_serstation"),
    path('service_station_list/', views.service_station_list, name='service_station_list'),   
    path('myservice_station/', views.myservice_station, name='myservice_station'),    
    path('add_services/<int:ser_id>', views.add_services, name='add_services'),
    path('update_services/<int:service_id>/', update_services, name='update_services'),
    path('bookservice/<int:service_id>/', views.bookservice, name='bookservice'),  
    path('worker_dash/', views.worker_dash, name='worker_dash'),
    path('closed_service_station/', views.closed_service_station, name='closed_service_station'),   
    path('attend_service_booking/<int:booking_id>/', views.attend_service_booking, name='attend_service_booking'),
    path('ser_update/<int:stid2>', views.ser_update, name='ser_update'),
    path('ser_delete/<int:stid2>', views.ser_delete, name='ser_delete'),
    path('delete_service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('mybooking/', views.mybooking, name='mybooking'),   
    path('toggle_service_visibility/<int:service_id>/<int:station_id>/', views.toggle_service_visibility, name='toggle_service_visibility'),
    path('add_packages/<int:service_id>/', views.add_packages, name='add_packages'),
    path('delete_package/<int:package_id>/', views.delete_package, name='delete_package'),
    path('service_packages/<int:service_id>/', views.service_packages, name='service_packages'),
    path('update_packages/<int:package_id>/', views.update_packages, name='update_packages'),
    path('delete/<int:service_id>/', delete_mybookservice, name='delete_mybookservice'),
    path('detailed_book_data/<int:booking_id>/', detailed_book_data, name='detailed_book_data'),
    path('delete_added_work/<int:service_id>/', views.delete_added_work, name='delete_added_work'),
    path('toggle_add_favorite/<int:station_id>/', views.toggle_add_favorite, name='toggle_add_favorite'),
    path('toggle_rem_favorite/<int:station_id>/', views.toggle_rem_favorite, name='toggle_rem_favorite'),
    path('myfavservicest', views.myfavservicest, name='myfavservicest'),
    path('completed/<int:book_id>/', views.completed, name='completed'),
    path('feedback/<int:ser_id>/', views.feedback_page, name='feedback_page'),
    path('add_comment/<int:ser_id>', views.add_comment, name='add_comment'),
    path('delete_feedback/<int:feedback_id>/<int:ser_id>/', views.delete_feedback, name='delete_feedback'),
    path('ser_book_success', views.ser_book_success, name='ser_book_success'),
    # path('cart', views.cart, name='cart'),
    path('car_guide_view', views.car_guide_view, name='car_guide_view'),
    path('complted_worker_dash', views.complted_worker_dash, name='complted_worker_dash'),


]



