# profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("register/", views.register, name="register"),
]
