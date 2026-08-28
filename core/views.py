from django.shortcuts import render
from .models import Movie
# Create your views here.
def home(request):
   
   latest_movies=Movie.objects.order_by("-release_date")[:8]
   #print(latest_movies)
   context={
        'movies':latest_movies
   }

   return render(request,"core/home.html",context)


def movie_detail(request,pk):
   movie=Movie.objects.get(pk=pk)
   context={
      'movie':movie
   }
   return render(request,"core/movie_detail.html",context)
 