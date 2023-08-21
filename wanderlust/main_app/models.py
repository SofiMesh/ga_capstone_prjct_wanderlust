from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
# Create your models here.


class Destinations(models.Model):
    name = models.CharField(max_length=250)
    country = models.CharField(max_length=60)
    language = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return self.name, self.country

    def get_absolute_url(self):
        return reverse('destinations_detail', kwargs={'pk': self.id})
        




class Trips(models.Model):
    name = models.CharField(max_length=250)
    startDate = models.DateField()
    endDate = models.DateField()
    budget = models.IntegerField()
    destination_ids = models.ForeignKey(Destinations, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('trips_detail', kwargs={'pk': self.id})

    class Meta: 
        ordering = ['-startDate']




class Checklist(models.Model):
    todos = models.CharField(max_length=250)
    complete = models.BooleanField()
    trip_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Travelers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    trip_id = models.ForeignKey(Trips, on_delete=models.CASCADE)


class Activities(models.Model):
    plannedAct = models.CharField(max_length=250)
    endDate = models.DateField()
    dueDate = models.DateField()
    trip_id = models.ForeignKey(Trips, on_delete=models.CASCADE)


class Photos(models.Model):
    photoUrl = models.CharField(max_length=200)
    destination_id = models.ForeignKey(Destinations, on_delete=models.CASCADE)
    trip_id = models.ForeignKey(Trips, on_delete=models.CASCADE)
