from django.urls import path
from . import views
from major import views_login_otp as authv

from . import views_profile 
# if you keep your OTP views in views_login_otp.py this stays unchanged

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/user/", views.user_home, name="user-home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("overview/", views.OverviewView.as_view(), name="trading"),
    path("plans/", views.PlansView.as_view(), name="plans"),
    path("contact/", views.contact, name="contact"),
    path("invest/start/", views.invest_start, name="invest-start"),
    path("terms/", authv.terms_view, name="terms"),

    path("account/profile/", views_profile.profile_view, name="profile"),
    path("account/profile/edit/", views_profile.profile_edit, name="profile_edit"),

    # NEW: registration page so {% url 'register' %} works
    path("register/", views.register, name="register"),
]
