from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name="cine_admin_dashboard"),
    path('hall/setup/',views.hall_seat_setup,name="hall_seat_setup"),
    path('cinema/halls/',views.get_cinema_halls,name="get_cinema_halls"),
    path('halls/seats/',views.get_hall_seats,name="get_hall_seats"),
    path('show/setup/',views.show_setup,name="show_setup"),
    path('reservations/qr/verify/',views.reservation_qr_verification,name="reservation_qr_verification"),
        
]