from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile
from .forms import ProfileForm


@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("profile")

    else:
        form = ProfileForm(instance=profile)

    context = {
        "profile": profile,
        "form": form,
    }

    return render(request,"accounts/profile.html",context)


@login_required
def logout_view(request):

    if request.method == "POST":
        logout(request)

        messages.success(
            request,
            "You have been logged out successfully."
        )

        return redirect("back")

    return redirect("profile")