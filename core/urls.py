from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name="back"),
    path('movies/<pk>/',views.movie_detail,name="movie_detail"),
    path('register/',views.register_view,name="register"),
    path('login/',views.login_view,name="login"),
    path('show/<show_id>/hall/',views.hall_seats_view,name="hall_seats"),
    path('reservation/payment/verification',views.verify_reservation_payment,name="verify_reservation_payment"),
    path('reservations/',views.reservations,name="reservations"),
    path('reservations/<pk>/',views.reservation_detail,name="reservation_detail"),
]