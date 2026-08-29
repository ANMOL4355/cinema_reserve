from django.shortcuts import render
from .models import Movie,Show
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
   shows=Show.objects.filter(movie=movie)
   #print(shows)

   context={
      'movie':movie,
      'shows':shows
   }
   return render(request,"core/movie_detail.html",context)
 