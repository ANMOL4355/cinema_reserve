from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
# Create your models here.


class Movie(models.Model):
    name=models.CharField(max_length=100)
    genre=models.CharField(max_length=50)
    release_date=models.DateField(null=True)
    poster=models.ImageField(upload_to="movie_poster/",null=True)

    def __str__(self):
        return self.name


class Cinema(models.Model):
    name=models.CharField(max_length=100)
    location=models.CharField(max_length=100)


    def __str__(self):
        return f"{self.name} - {self.location}"


class CinemaHall(models.Model):
    name=models.CharField(max_length=100)
    cinema=models.ForeignKey(Cinema,on_delete=models.PROTECT)


    def __str__(self):
        return self.name


class Seat(models.Model):
    name=models.CharField(max_length=10)
    cinemahall=models.ForeignKey(CinemaHall,on_delete=models.CASCADE,related_name="seats")

    class Meta:
        unique_together=("name","cinemahall")

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

    class STATUS_CHOICES(models.TextChoices):
        pending='pd','Pending'
        confirm='cm','Confirm'
        cancel='cl','Cancelled'
        expired='ex','Expired'

    customer=models.ForeignKey(User, on_delete=models.PROTECT,related_name="reservations")
    show=models.ForeignKey(Show,on_delete=models.PROTECT,related_name="reservations")
    seat=models.ForeignKey(Seat,on_delete=models.PROTECT,related_name="reservations")
    status=models.CharField(max_length=2,choices=STATUS_CHOICES,default=STATUS_CHOICES.pending)

    created_at = models.DateTimeField(auto_now_add=True,null=True)
    expires_at = models.DateTimeField(null=True)
    
    class Meta:
        unique_together=("show","seat")

    def __str__(self):
        return self.customer.first_name


    def save(self,*args,**kwargs):
        if not self.created_at:
            self.created_at=timezone.now()

        self.expires_at = self.created_at + timedelta(minutes=settings.RESERVATION_WINDOW_TIME)

        super().save(*args, **kwargs)