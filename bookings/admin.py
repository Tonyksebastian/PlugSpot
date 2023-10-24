from django.contrib import admin
from .models import station,booknow,On_payment,Subscription

admin.site.register(station)
admin.site.register(booknow)
admin.site.register(Subscription)
admin.site.register(On_payment)
