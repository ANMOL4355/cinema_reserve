from django.shortcuts import render,redirect,get_object_or_404
from .models import Movie,Show
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.utils import timezone
# Create your views here.
def hall_seats_view(request,show_id):
   show=get_object_or_404(Show,pk=show_id)
   #print(show.cinemahall.seat_set.all())
   #print(show.cinemahall.seats.all())
   seats=show.cinemahall.seats.all()
   context={
      'seats':seats
   }
   
   return render(request,"core/hall_seats.html",context)

def home(request):
   
   latest_movies=Movie.objects.order_by("-release_date")[:8]
   #print(latest_movies)
   context={
        'movies':latest_movies
   }

   return render(request,"core/home.html",context)


def movie_detail(request,pk):
   movie=Movie.objects.get(pk=pk)
   shows=Show.objects.filter(movie=movie,show_time__gt=timezone.now())
   #print(shows)

   context={
      'movie':movie,
      'shows':shows,
      'from_date':timezone.now(),
   }
   return render(request,"core/movie_detail.html",context)


def register_view(request):
   if request.method=="POST":
      #print("Request data:", request.POST)
      # username=request.POST.get('username')
      # first_name=request.POST.get('first_name')
      # last_name=request.POST.get('last_name')
      # email=request.POST.get('email')
      # password=request.POST.get('password')
      form = RegisterForm(data=request.POST)
      
      if form.is_valid():
         #print(form.cleaned_data)
         data=form.cleaned_data
         User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
         )
         print("user creation successful")
         return redirect('login')

      else:
         print("form is invalid")
         return render(request,"core/register.html",{'form':form})

      #print(username,first_name,last_name,email,password)
      # if len(username)<6:
      #    print("Username must be at least 6 characters long")

   return render(request,"core/register.html")


def login_view(request):

   if request.method == 'POST':
      #print(request.POST)
      username=request.POST.get('username')
      password=request.POST.get('password')
      #print(username,password)
      user=authenticate(request,username=username,password=password)
      if user is not None:
         login(request,user)
         print("login successful")
         return redirect("back")

   return render (request, "core/login.html")