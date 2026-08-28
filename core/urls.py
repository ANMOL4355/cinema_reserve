from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name="back"),
    path('movies/<pk>/',views.movie_detail,name="movie_detail")
]