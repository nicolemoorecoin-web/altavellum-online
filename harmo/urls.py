# harmo/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public/site routes (your main app)
    path("", include("major.urls")),

    # OTP / Auth routes (login, otp, signup, logout)
    path("", include("major.urls_auth")),

    # Dashboard routes (namespaced "dashboard")
    path("dashboard/", include(("dashboard.home.urls", "dashboard"), namespace="dashboard")),

    # Optional: Django auth helpers (password reset etc.)
    # Your own login at /accounts/login/ still wins because it's declared earlier.
    path("accounts/", include("django.contrib.auth.urls")),

    # Static terms page (you already referenced it)
    path("terms/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
