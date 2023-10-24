from seminar import views
from django.urls import path

app_name = 'seminar'

urlpatterns = [
    
path('hi/', views.hi, name='hi'),
path('predict_traffic', views.predict_traffic, name='predict_traffic'),
]