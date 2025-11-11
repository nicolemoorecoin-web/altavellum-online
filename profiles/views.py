# profiles/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.core.files.images import get_image_dimensions

from .models import Profile


@login_required
def edit_profile(request):
    """
    Edit the logged-in user's profile (first/last/email, phone, country, avatar).
    - Handles file uploads safely.
    - Shows success/error messages.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # ---- Update User core fields
        request.user.first_name = (request.POST.get("first_name") or "").strip()
        request.user.last_name  = (request.POST.get("last_name") or "").strip()
        request.user.email      = (request.POST.get("email") or "").strip()

        # ---- Update Profile simple fields
        profile.phone   = (request.POST.get("phone") or "").strip()
        profile.country = (request.POST.get("country") or "").strip()

        # ---- Optional avatar upload
        file_obj = request.FILES.get("avatar")
        if file_obj:
            # quick sanity checks (you can relax/tune these)
            if file_obj.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, "Avatar too large (max 5 MB).")
                return render(request, "profiles/edit_profile.html", {"profile": profile})

            try:
                # ensure it's an image
                get_image_dimensions(file_obj)
            except Exception:
                messages.error(request, "Please upload a valid image file.")
                return render(request, "profiles/edit_profile.html", {"profile": profile})

            # assign to ImageField (Profile.avatar)
            profile.avatar = file_obj

        # ---- Save both objects atomically
        with transaction.atomic():
            request.user.save()
            profile.save()

        messages.success(request, "Your profile has been updated.")
        return redirect("user-home")  # or redirect("profiles:edit") if you want to stay

    return render(request, "profiles/edit_profile.html", {"profile": profile})


def register(request):
    """
    Creates a new user with a *hashed* password, ensures Profile exists,
    authenticates and logs the user in, then redirects to the dashboard.
    """
    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name  = (request.POST.get("last_name") or "").strip()
        username   = (request.POST.get("username") or "").strip()
        email      = (request.POST.get("email") or "").strip()
        pw1        = request.POST.get("password1") or ""
        pw2        = request.POST.get("password2") or ""

        if not all([first_name, last_name, username, email, pw1, pw2]):
            messages.error(request, "Please fill out all fields.")
            return render(request, "profiles/register.html")

        if pw1 != pw2:
            messages.error(request, "Passwords do not match.")
            return render(request, "profiles/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "profiles/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, "profiles/register.html")

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=pw1,   # hashed automatically
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.get_or_create(user=user)

        user = authenticate(request, username=username, password=pw1)
        if user is None:
            messages.error(request, "Could not authenticate the new account.")
            return render(request, "profiles/register.html")

        login(request, user)
        return redirect("user-home")

    return render(request, "profiles/register.html")
