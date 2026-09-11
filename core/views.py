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
from .tasks import send_receipt_in_mail
from django.urls import reverse
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

    pidx = request.GET.get("pidx")
    purchase_order_id = request.GET.get("purchase_order_id")

    if not pidx or not purchase_order_id:
        messages.error(request, "Invalid payment information.")
        return redirect("back")

    try:
        master = MasterReservation.objects.get(
            pidx=pidx,
            pk=purchase_order_id
        )

    except MasterReservation.DoesNotExist:
        messages.error(request, "Reservation not found.")
        return redirect("back")

    except MasterReservation.MultipleObjectsReturned:
        messages.error(request, "Duplicate reservation found.")
        return redirect("back")


    # Prevent processing the same payment twice
    if master.payment_status == "Completed":
        messages.info(request, "This reservation has already been confirmed.")
        return redirect("reservations")


    # Verify directly with Khalti
    data = verify_khalti_payment(pidx)

    print("====================================")
    print("KHALTI VERIFICATION RESPONSE:")
    print(data)
    print("====================================")


    # Payment must be completed
    if data.get("status") != "Completed":
        messages.error(request, "Payment was not completed.")
        return redirect("back")


    # Calculate the amount ourselves
    seat_count = master.reservations.count()

    expected_amount = (
        master.show.price
        * seat_count
        * 100
    )

    khalti_amount = data.get("total_amount")


    print("SHOW PRICE:", master.show.price)
    print("SEAT COUNT:", seat_count)
    print("EXPECTED AMOUNT:", expected_amount)
    print("KHALTI AMOUNT:", khalti_amount)
    print("DATABASE MASTER AMOUNT:", master.amount)


    # Amount must match
    if khalti_amount != expected_amount:

        messages.error(
            request,
            "Payment amount mismatch. Reservation was not confirmed."
        )

        print("PAYMENT AMOUNT MISMATCH")

        return redirect("back")


    # Everything is valid
    with transaction.atomic():

        master.amount = expected_amount
        master.transaction_id = data.get("transaction_id")
        master.payment_status = "Completed"

        master.reservations.all().update(
            status=Reservation.STATUS_CHOICES.confirm
        )

        master.save()


    reservation_url = request.build_absolute_uri(
        reverse(
            "reservation_detail",
            kwargs={"pk": master.id}
        )
    )


    send_receipt_in_mail.delay(
        request.user.email,
        master.id,
        reservation_url
    )


    messages.success(
        request,
        "Payment and Reservation confirmed"
    )

    return redirect("reservations")
 
 
 
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