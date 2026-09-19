from django.shortcuts import render,redirect
from core.models import Cinema,CinemaHall,Seat
from django.http import HttpResponse
from django.template.loader import render_to_string



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