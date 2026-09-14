from django.shortcuts import render


def hall_seat_setup(request):
    return render(request,"cine_admin/hall-seats-setup.html")
