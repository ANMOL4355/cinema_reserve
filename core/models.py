from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Movie(models.Model):
    name=models.CharField(max_length=100)
    genre=models.CharField(max_length=50)


    def __str__(self):
        return self.name


class CinemaHall(models.Model):
    name=models.CharField(max_length=100)
    location=models.CharField(max_length=50)


    def __str__(self):
        return self.name


class Seat(models.Model):
    name=models.CharField(max_length=10)
    cinemahall=models.ForeignKey(CinemaHall,on_delete=models.CASCADE)


    def __str__(self):
        return self.name


class Show(models.Model):
    movie=models.ForeignKey(Movie,on_delete=models.PROTECT)   
    cinemahall=models.ForeignKey(CinemaHall,on_delete=models.PROTECT)
    show_time=models.DateTimeField() 
    price=models.PositiveBigIntegerField()

    class Meta:
            unique_together=("cinemahall","show_time","movie")

    def __str__(self):
        return f"{self.movie} - {self.cinemahall}"


class Reservation(models.Model):
    customer=models.ForeignKey(User, on_delete=models.PROTECT)
    show=models.ForeignKey(Show,on_delete=models.PROTECT)
    seat=models.ForeignKey(Seat,on_delete=models.PROTECT)

    class Meta:
        unique_together=("show","seat")

    def __str__(self):
        return self.customer.first_name
