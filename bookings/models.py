from django.db import models
from django.dispatch import receiver
from userapp.models import CustomUser
from django.db.models.signals import post_save

# Create your models here.


class station(models.Model):
    stname = models.CharField(max_length=30, default='')
    ownername = models.CharField(default='', max_length=25)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='station_user', null=True)
    place = models.CharField(default='', max_length=30)
    photo = models.ImageField(upload_to='pic', default='')
    latitude = models.CharField(max_length=12)
    longitude = models.CharField(max_length=12)
    maxslot = models.IntegerField(default='4')
    description = models.CharField(default='', max_length=250)
    price = models.CharField(max_length=12)
    contact = models.IntegerField(null=True,blank=True)
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


    def __str__(self):
        return str(self.name)


class BookingHistory(models.Model):
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history_by_name')
    email = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history_by_email')
    ownername = models.CharField(default='', max_length=25)
    stname = models.CharField(max_length=30, default='')
    place = models.CharField(default='', max_length=30)
    photo = models.ImageField(upload_to='pic', default='')
    station_id = models.ForeignKey(station, on_delete=models.CASCADE, related_name='historystation_id')
    slotnumber = models.IntegerField(default='')
    price = models.CharField(max_length=12)
    date = models.DateField()
    time = models.TimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status =models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.date} {self.time}'


