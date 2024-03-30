from django.db import models
from django.dispatch import receiver
from userapp.models import CustomUser
from django.db.models.signals import post_save
from make_service.models import service_station


# Create your models here.


class station(models.Model):
    stname = models.CharField(max_length=30, default='')
    ownername = models.CharField(default='', max_length=25)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='station_user', null=True)
    place = models.CharField(default='', max_length=30)
    photo = models.ImageField(upload_to='pic', default='')
    latitude = models.CharField(max_length=12,null=True)
    longitude = models.CharField(max_length=12,null=True)
    maxslot = models.IntegerField(default='4')
    description = models.CharField(default='', max_length=250)
    price = models.CharField(max_length=12)
    contact = models.IntegerField(null=True,blank=True)
    date = models.DateField(null=True)
    hidden = models.BooleanField(default=False)
    available=models.IntegerField(null=True)
    status= models.BooleanField(default=False)


    def __str__(self):
        return self.user.first_name


class booknow(models.Model):
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_by_name', null=True)
    email = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_by_email', null=True)
    ownername = models.CharField(default='', max_length=25)
    stname = models.CharField(max_length=30, default='')
    place = models.CharField(default='', max_length=30)
    photo = models.ImageField(upload_to='pic', default='')
    station_id = models.ForeignKey(station, on_delete=models.CASCADE, related_name='station_id')
    slotnumber = models.IntegerField(default='')
    price = models.CharField(max_length=12)
    date = models.DateField()
    time = models.TimeField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    status = models.BooleanField(default=False)
    del_status = models.BooleanField(default=False)


    def __str__(self):
            return str(self.name)


# models.py in the On_payment model file


from make_service.models import service_booking  # Adjust the import path as needed

class On_payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user', null=True)
    order = models.CharField(null=True, default='123', max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking = models.OneToOneField('booknow', null=True, blank=True, on_delete=models.SET_NULL)
    subscribe = models.ForeignKey('Subscription', null=True, blank=True, on_delete=models.SET_NULL)    
    additional_service = models.OneToOneField(service_booking, null=True, blank=True, on_delete=models.SET_NULL)
    payment_id = models.CharField(null=True, default='123', max_length=30)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    

VALIDITY_CHOICES = [
        ('1 MONTH', '1 MONTH'),
        ('2 MONTH', '2 MONTH'),
        ('3 MONTH', '3 MONTH'),
        ('4 MONTH', '4 MONTH'),
        ('5 MONTH', '5 MONTH'),
        ('6 MONTH', '6 MONTH'),
        ('7 MONTH', '7 MONTH'),
        ('8 MONTH', '8 MONTH'),
        ('9 MONTH', '9 MONTH'),
        ('10 MONTH', '10 MONTH'),
        ('11 MONTH', '11 MONTH'),
        ('12 MONTH', '12 MONTH'),
    ]

class Subscription(models.Model):  
    sub_type = models.CharField(max_length=40, blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    validity = models.CharField(max_length=40, choices=VALIDITY_CHOICES, blank=True, null=True) 
    features = models.CharField(max_length=255 , default='',null=True) 

    def str(self):
        return f"{self.sub_type} Subscription"


