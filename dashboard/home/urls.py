# dashboard/home/urls.py
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("deposit/", views.deposit, name="deposit"),
    path("withdraw/", views.withdraw_request, name="withdraw"),
    path("withdraw/confirm/", views.withdraw_confirm, name="withdraw_confirm"),
    path("investments/", views.investments, name="investments"),
    path("invest/", views.invest, name="invest"),
    path("plans/", views.plans, name="plans"),
    path("transactions/", views.transactions, name="transactions"),
    path("chart/", views.chart, name="chart"),

    # ✅ profile routes
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),

    # ✅ NEW: staff-only datetime editor
    path("tx/<str:kind>/<int:pk>/time/", views.tx_time_edit_staff, name="tx_time_edit_staff"),
]
