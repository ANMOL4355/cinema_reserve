from django.urls import path
from . import views

urlpatterns = [
    path('hall/setup/',views.hall_seat_setup,name="hall_seat_setup"),
    path('cinema/halls/',views.get_cinema_halls,name="get_cinema_halls"),
    path('halls/seats/',views.get_hall_seats,name="get_hall_seats"),
]