from django.db import models

# Create your models here.
class station():
    name=models.CharField(max_length=30,default='')
    place=models.EmailField(unique=True)
    profilepic=models.ImageField(upload_to='pic',default='')
    maxslot=models.CharField(max_length=13,default='')
    description=models.BooleanField(default=False)
    station_owners=models.BooleanField(default=False)