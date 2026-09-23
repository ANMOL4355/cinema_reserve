from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import redirect


class AdminRoutesProtectMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        print(request.path)
        if "cine_admin" in request.path:
            print("yes user is trying to access admin related page")
            # print(request.user.groups.all())
            
            if  not request.user.is_authenticated:
                messages.error(request,"Please login first")
                return redirect("login")
             
            #admin_staff_group = Group.objects.get(name="AdminStaff")
            if not request.user.groups.filter(name="AdminStaff").exists():
                messages.error(request,"You are not authorized to access this page")
                return redirect("back")

        response = self.get_response(request)

        print("After the view")

        return response