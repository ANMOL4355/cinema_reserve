from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Movie)
admin.site.register(Cinema)
#admin.site.register(CinemaHall)
#admin.site.register(Reservation)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display=["name","cinemahall"]

@admin.register(CinemaHall)
class CinemaHalladmin(admin.ModelAdmin):
    list_display=["name","cinema"]    

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display=["cinemahall","movie","show_time","price"]  

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display=["customer","show","seat"]        