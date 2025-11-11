from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    """Simple user signup using Django's built-in form."""
    if request.user.is_authenticated:
        return redirect("user-home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("user-home")
    else:
        form = UserCreationForm()

    # You already have: dashboard/templates/accounts/register.html
    return render(request, "accounts/register.html", {"form": form})
