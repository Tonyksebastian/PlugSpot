from userapp import views
from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    
    path('', views.index,name='index'),
    # path('reg/', views.reg,name='reg'), 
    path('register/', views.register,name='register'),
    path('register_vh/', views.vhowner, name='register_vh'),
    path('registerWK/', views.registerWK, name='registerWK'),
    path('login/', views.login,name='login'),
    path('admin_login/', views.admin_login,name='admin_login'),
    path('logout/', views.logout,name='logout'),
    path('profile/', views.profile,name='profile'), 
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
]
