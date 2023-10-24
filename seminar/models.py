from django.db import models

# Create your models here.
# traffic_prediction_app/models.py

from django.db import models

class TrafficData(models.Model):
    is_holiday = models.CharField(max_length=10)
    temperature = models.FloatField()
    hour = models.IntegerField()
    month_day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    weekday = models.IntegerField()
    location = models.CharField(max_length=10)
    prediction = models.CharField(max_length=10)

    def __str__(self):
        return f"Traffic Data - {self.id}"
