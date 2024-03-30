from django.db import models
from userapp.models import CustomUser

# Create your models here.
class service_station(models.Model):
    stname = models.CharField(max_length=30, default='')
    ownername = models.CharField(default='', max_length=25)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)
    place = models.CharField(default='', max_length=30)
    photo = models.ImageField(upload_to='pic', default='')
    latitude = models.CharField(max_length=12,null=True)
    longitude = models.CharField(max_length=12,null=True)
    maxslot = models.IntegerField(default='4')
    description = models.CharField(default='', max_length=250)
    contact = models.IntegerField(null=True,blank=True)
    date = models.DateField(null=True)
    hidden = models.BooleanField(default=False)
    available=models.IntegerField(null=True)
    status= models.BooleanField(default=False)

    def __str__(self):
        return str(self.stname)
    
class add_service(models.Model):
    photo = models.ImageField(upload_to='pic', default='')
    ser_name = models.CharField(max_length=30, default='')
    description = models.CharField(default='', max_length=250)
    price = models.FloatField(null= True)
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_by_name', null=True)
    service=models.ForeignKey(service_station,null=True,on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    delete_status = models.BooleanField(default=False)


class add_package(models.Model):

    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='package_by_name', null=True)
    service=models.ForeignKey(add_service,null=True,on_delete=models.CASCADE)
    package_name = models.CharField(max_length=30, default='')
    duration = models.CharField(max_length=30, default='')
    package_desc = models.CharField(default='', max_length=250)
    orginal_price = models.FloatField(null= True)
    discount_price = models.FloatField(null=True)
    package_image = models.ImageField(upload_to='pic', default='')
    package_status = models.BooleanField(default=False)
    package_del_status = models.BooleanField(default=False)

class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    station_id = models.ForeignKey(service_station, on_delete=models.CASCADE)  # Assuming station ID is an integer
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s favorite: Station {self.station_id}"

class CarService(models.Model):
    name = models.CharField(max_length=55, unique=True)

class service_booking(models.Model):
    vehno = models.CharField(default='', max_length=250) 
    company = models.CharField(default='', max_length=250)
    model = models.CharField(default='', max_length=250)
    km_done = models.FloatField()
    desc = models.CharField(default='', max_length=250)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    slotnumber = models.CharField(null=True, max_length=250)
    package=models.ForeignKey(add_package,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    status = models.BooleanField(default=False)
    del_status = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    payment_done=models.BooleanField(default=False)


class AdditionalService(models.Model):
    name = models.CharField(max_length=100,null=True)
    cost = models.FloatField(null=True)
    total_cost = models.FloatField(default=0.0)
    booking = models.ForeignKey(service_booking, on_delete=models.CASCADE, related_name='additional_services')

    def __str__(self):
        return f"Service: {self.name}, Cost: {self.cost}"

class Feedback(models.Model):
    userprofile = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    station = models.ForeignKey(service_station, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,null=True)
    message = models.TextField()
    date=models.DateTimeField(null=True)
    rating = models.IntegerField(default=0,null=True)
    status =models.BooleanField(default = False)

    def str(self):
        return self.first_name
    
class cart(models.Model):
    
    package=models.ForeignKey(add_package,on_delete=models.CASCADE,null=True)
    service=models.ForeignKey(service_station,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    status = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    payment_done=models.BooleanField(default=False)