from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction

try:
    from profiles.models import Profile
except Exception:
    Profile = None

# Accept common aliases so we don't break if your model uses different names
FIELD_ALIASES = {
    "phone":   ["phone", "phone_number", "mobile", "tel"],
    "country": ["country", "country_name", "country_code"],
    "avatar":  ["avatar", "photo", "image", "picture"],
}

def _get_profile(user):
    if Profile:
        obj, _ = Profile.objects.get_or_create(user=user)
        return obj
    class Dummy:  # fallback if you don't have a Profile model yet
        avatar = None; phone = ""; country = ""
    return Dummy()

def _first_attr(obj, names):
    for n in names:
        if hasattr(obj, n):
            val = getattr(obj, n)
            if val:
                return val
    return None

def _set_first_existing(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return True
    return False

@login_required
def profile_view(request):
    profile = _get_profile(request.user)
    phone_val   = _first_attr(profile, FIELD_ALIASES["phone"]) or ""
    country_val = _first_attr(profile, FIELD_ALIASES["country"]) or ""
    avatar_obj  = _first_attr(profile, FIELD_ALIASES["avatar"])
    avatar_url  = getattr(avatar_obj, "url", None) if avatar_obj else None

    return render(request, "account/profile.html", {
        "profile": profile,
        "phone_display": phone_val,
        "country_display": country_val,
        "avatar_url": avatar_url,
    })

@login_required
@transaction.atomic
def profile_edit(request):
    user = request.user
    profile = _get_profile(user)

    if request.method == "POST":
        # User fields
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name  = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        if email:
            user.email = email

        # Profile fields (map aliases)
        phone_in   = (request.POST.get("phone") or
                      request.POST.get("phone_number") or
                      request.POST.get("mobile") or
                      request.POST.get("tel") or "").strip()
        country_in = (request.POST.get("country") or
                      request.POST.get("country_name") or
                      request.POST.get("country_code") or "").strip()

        if Profile:
            _set_first_existing(profile, FIELD_ALIASES["phone"], phone_in)
            _set_first_existing(profile, FIELD_ALIASES["country"], country_in)

            file_in = (request.FILES.get("avatar") or
                       request.FILES.get("photo") or
                       request.FILES.get("image") or
                       request.FILES.get("picture"))
            if file_in:
                _set_first_existing(profile, FIELD_ALIASES["avatar"], file_in)

        user.save()
        if Profile:
            profile.save()

        messages.success(request, "Profile updated.")
        return redirect("profile")

    return render(request, "account/edit_profile.html", {"profile": profile})
