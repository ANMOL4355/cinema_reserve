from django.shortcuts import render,redirect
from .models import Movie,Show
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
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