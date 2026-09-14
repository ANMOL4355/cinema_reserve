from django.urls import path
from . import views

urlpatterns = [
    path('hall/setup/',views.hall_seat_setup,name="hall_seat_setup")
]