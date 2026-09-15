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
        print(request.POST)
        
        return redirect("hall_seat_setup")
        
    cinemas = Cinema.objects.all()
    first_cinema = cinemas.first()
    halls = CinemaHall.objects.filter(cinema=first_cinema)
    first_hall = halls.first()
    seats = Seat.objects.filter(cinemahall=first_hall)
    
    context = {
        'cinemas':cinemas,
        'halls':halls,
        'seats':seats,
    }
    
    return render(request,"cine_admin/hall-seats-setup.html",context)
