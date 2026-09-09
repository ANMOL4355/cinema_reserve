from django.shortcuts import render,redirect,get_object_or_404
from .models import Movie,Show,Reservation,Seat,MasterReservation
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Exists, OuterRef
from django.db import IntegrityError,transaction
from django.contrib import messages
from django.conf import settings
from .services import verify_khalti_payment, initiate_khalti_payment
# Create your views here.

@login_required
def reservation_detail(request,pk):
   master= get_object_or_404(MasterReservation,pk=pk)
   
   reserved_seats = list(master.reservations.values_list('seat__name',flat=True))
   
   amount_rupees = master.amount/100
   context={
      'master':master,
      'seats':reserved_seats,
      'amount':amount_rupees,
   }
   return render(request,"core/reservation_detail.html",context)



@login_required
def reservations(request):
   master_reservations = MasterReservation.objects.all()
   context ={
      'master_reservations': master_reservations
   }
   return render(request,"core/reservations.html",context)



@login_required
def verify_reservation_payment(request):
   data = request.GET
   pidx = data.get('pidx')
   purchase_order_id = data.get('purchase_order_id')
   try:
      master = MasterReservation.objects.get(pidx=pidx,pk=purchase_order_id)
   except MasterReservation.DoesNotExist:
      print("Something went wrong. Masterreservation doesn't exists")
   except MasterReservation.MultipleObjectsReturned:
      print("Duplicate pidx exists")

   data = verify_khalti_payment(pidx)

   if data.get('status') == 'Completed':
       if data.get('total_amount') == master.amount:

          
          with transaction.atomic():
               master.transaction_id = data.get('transaction_id')
               master.payment_status = 'Completed'
               master.reservations.all().update(status=Reservation.STATUS_CHOICES.confirm)
               master.save()

          messages.success(request,"Pyment and Reservation confirmed")
          return redirect ("reservations")
       else:
          messages.error(request,"Amount mismatch, Reservation confirmation failed")
   else:
      print("Amount mismatch, Reservation confirmation failed")

   return redirect("back")


@login_required
def hall_seats_view(request,show_id):

   if request.method=="POST":
      form_show_id=request.POST.get('show')
      form_seats=request.POST.get('seats')
      seats_ids=form_seats.split(',')
       # print("Reservation process")
       # print(seats_names)
       # print(form_show_id,form_seats)

      try:
         with transaction.atomic():
            show=Show.objects.get(pk=form_show_id)
            master = MasterReservation.objects.create(show=show)
            for seat_id in seats_ids:
               seat=Seat.objects.get(pk=seat_id)
               Reservation.objects.create(
                  master_reservation=master,
                  show=show,
                  seat=seat,
                  customer=request.user
            )
      except IntegrityError:
         messages.error(request,"one of these seats has just been reserved by another customer")
         return redirect("hall_seats",show_id=show_id)
      except Seat.DoesNotExist:
         messages.error(request,"Incorrect seat selection")
         return redirect("hall_seats",show_id=show_id)
      
      messages.success(request,f"seats reserved for {settings.RESERVATION_WINDOW_TIME} minutes. Please confirm payment within given time")
      

      # initiate_khalti_payment()
      data,amount = initiate_khalti_payment(master,show,seats_ids,request.user)
      pidx = data.get("pidx")
      payment_url=data.get("payment_url")

      master.pidx = pidx
      master.amount = amount
      master.save()

      return redirect(payment_url)



   show=get_object_or_404(Show,pk=show_id)
   #print(show.cinemahall.seat_set.all())
   #print(show.cinemahall.seats.all())
   seats = show.cinemahall.seats.annotate(
     reserved=Exists(
         Reservation.objects.filter(
            show=show,
            seat=OuterRef("pk"),
            status__in=[Reservation.STATUS_CHOICES.confirm,
                        Reservation.STATUS_CHOICES.pending
                     ]
        )
    )
)
   context={
      'show':show,
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