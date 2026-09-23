from django.shortcuts import render,redirect, get_object_or_404
from core.models import Cinema,CinemaHall,Seat,Movie,Show,MasterReservation
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import datetime
from django.utils import timezone



def reservation_qr_verification(request):
   if request.method == 'POST':
      master_id = request.POST.get('master_id')
      try:
         master = get_object_or_404(MasterReservation,pk=master_id)
      except Exception:
         return HttpResponse("<h1> Ticket doesn't exist </h1>")
         
      context = {
         'movie_name':master.show.movie.name,
         'show_time' : master.show.show_time,
         'seats' : Seat.objects.filter(reservations__in=master.reservations.all())
      }
      
      if master:
         return render(request,"core/ticket.html",context)
      else:
         return HttpResponse("<h1> Ticket doesn't exist </h1>")
      
         
   return render(request,"core/qr_verification.html")




def get_hall_seats(request):
    hall_id = request.GET.get("hall_id")
    seats = Seat.objects.filter(cinemahall_id=hall_id)
    html = render_to_string('cine_admin/seats-setup-partial.html',{'seats':seats})
    
    return HttpResponse(html)



def get_cinema_halls(request):
    cinema_id = request.GET.get("cinema_id")
    halls = CinemaHall.objects.filter(cinema_id=cinema_id)
    html = render_to_string('cine_admin/hall-select-partial.html',{'halls':halls})
    
    return HttpResponse(html)



def hall_seat_setup(request):

    if request.method == "POST":
        post_data = request.POST
        cinema_id = post_data.get('cinema_id')
        hall_id = post_data.get('hall')
        seat_names = post_data.getlist('seat')
        row = post_data.get('row')
        col = post_data.get('col')

        CinemaHall.objects.filter(pk=hall_id).update(
            row=row,
            col=col,
        )

        created_count = 0
        for seat in seat_names:
            seat, created = Seat.objects.get_or_create(
                name=seat,
                cinemahall_id=hall_id,
            )
            if created:
                created_count += 1

        if seat_names:
            Seat.objects.filter(cinemahall_id=hall_id).exclude(name__in=seat_names).delete()

        print(f"New seats created for hall {hall_id} are {created_count}")

        return redirect(f"/cine_admin/hall/setup/?hall_id={hall_id}")

    cinemas = Cinema.objects.all()

    hall_id = request.GET.get("hall_id")
    if hall_id:
        first_hall = CinemaHall.objects.filter(pk=hall_id).first()
    else:
        first_hall = None

    if first_hall:
        first_cinema = first_hall.cinema
    else:
        first_cinema = cinemas.first()
        first_hall = CinemaHall.objects.filter(cinema=first_cinema).first()

    halls = CinemaHall.objects.filter(cinema=first_cinema)
    seats = Seat.objects.filter(cinemahall=first_hall)
    seats = sorted(
        seats,
        key=lambda seat: (seat.name[0], int(seat.name[1:]))
    )

    context = {
        'cinemas': cinemas,
        'halls': halls,
        'seats': seats,
        'first_hall': first_hall,
    }

    return render(request, "cine_admin/hall-seats-setup.html", context)



def show_setup(request):

    if request.method == "POST":
        post_data = request.POST
        hall_id = post_data.get('hall')
        movie_id = post_data.get('movie')
        show_date = post_data.get('show_date')
        price = post_data.get('price') or 0
        timeslots = post_data.getlist('timeslot')

        created_count = 0
        skipped_count = 0

        for time_str in timeslots:
            if not time_str:
                continue

            show_time = datetime.strptime(f"{show_date} {time_str}", "%Y-%m-%d %H:%M")

            show, created = Show.objects.get_or_create(
                movie_id=movie_id,
                cinemahall_id=hall_id,
                show_time=show_time,
                defaults={'price': int(price)},
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        return redirect(f"/cine_admin/show/setup/?hall_id={hall_id}")

    cinemas = Cinema.objects.all()
    movies = Movie.objects.all()

    hall_id = request.GET.get("hall_id")
    if hall_id:
        first_hall = CinemaHall.objects.filter(pk=hall_id).first()
    else:
        first_hall = None

    if first_hall:
        first_cinema = first_hall.cinema
    else:
        first_cinema = cinemas.first()
        first_hall = CinemaHall.objects.filter(cinema=first_cinema).first()

    halls = CinemaHall.objects.filter(cinema=first_cinema)

    shows = (
        Show.objects.filter(cinemahall=first_hall)
        .select_related("movie", "cinemahall")
        .order_by("show_time")
    )

    # attach a couple of extra display-only values to each show
    for show in shows:
        hall = show.cinemahall
        show.total_seats = (hall.row or 0) * (hall.col or 0)
        show.booked_seats = show.reservations.filter(status__in=["pd", "cm"]).count()

    context = {
        'cinemas': cinemas,
        'movies': movies,
        'halls': halls,
        'first_cinema': first_cinema,
        'first_hall': first_hall,
        'shows': shows,
    }

    return render(request, "cine_admin/show-setup.html", context)



def dashboard(request):
    context = {
        'cinema_count': Cinema.objects.count(),
        'hall_count': CinemaHall.objects.count(),
        'movie_count': Movie.objects.count(),
        'show_count': Show.objects.count(),
        'upcoming_shows': (
            Show.objects
            .select_related('movie', 'cinemahall')
            .filter(show_time__gte=timezone.now())
            .order_by('show_time')[:8]
        ),
    }
    return render(request, "cine_admin/dashboard.html", context)