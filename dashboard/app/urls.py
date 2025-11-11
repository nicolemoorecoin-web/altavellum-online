from django.urls import path
from .views import register

urlpatterns = [
    path("register/", register, name="register"),
    # optional alias (covers some templates that might use 'signup'):
    path("signup/", register, name="signup"),
]
