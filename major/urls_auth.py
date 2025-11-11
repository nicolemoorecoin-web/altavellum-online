# major/urls_auth.py
from django.urls import path
from . import views_login_otp as views

urlpatterns = [
    path("accounts/login/", views.login_step1, name="login"),
    path("accounts/otp/", views.login_step2, name="login-otp"),
    path("accounts/otp/<int:uid>/", views.login_step2, name="login-otp-id"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/logout/", views.logout_view, name="logout"),
]
