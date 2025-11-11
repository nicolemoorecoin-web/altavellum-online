# dashboard/app/apps.py
from django.apps import AppConfig

class DashboardAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard.app"      # full dotted path to the app package
    label = "dashapp"           # short label; avoids generic 'app'
    verbose_name = "Dashboard Data"
