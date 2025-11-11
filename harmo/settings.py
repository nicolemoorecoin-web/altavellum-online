# harmo/settings.py
from pathlib import Path
import os

# ===== Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== Security (adjust for production)
SECRET_KEY = "dev-secret-key-not-for-production"
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1", "localhost",
    "nicolemoore.pythonanywhere.com",
    "shipishly.com", "www.shipishly.com",
]

# ===== Apps
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Project apps
    "major",
    "profiles",
    "dashboard.home",
    "dashboard.app",
]

# ===== Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serve collected static files
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "harmo.urls"

# ===== Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",               # ✅ add this
            BASE_DIR / "major" / "templates",
            BASE_DIR / "dashboard" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "harmo.wsgi.application"

# ===== Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ===== Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===== I18N
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ===== Static / Media
STATIC_URL = "/static/"
# where collectstatic will place files
STATIC_ROOT = BASE_DIR / "staticfiles"

# extra source folders (only used at build/collect time)
_static_dirs = [
    BASE_DIR / "dashboard" / "static",
    BASE_DIR / "major" / "static",
]
STATICFILES_DIRS = [p for p in _static_dirs if p.exists()]

# WhiteNoise storage:
# Non-manifest avoids errors from missing *.map files (Bootstrap, etc.)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Optional WhiteNoise tunables
WHITENOISE_AUTOREFRESH = DEBUG           # auto-reload static in debug
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 7    # 1 week cache for static files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth redirects
LOGIN_URL = "/accounts/login/"          # <-- not /signin/ anymore
LOGIN_REDIRECT_URL = "user-home"
LOGOUT_REDIRECT_URL = "home"



# ===== CSRF (use your real domain(s))
CSRF_TRUSTED_ORIGINS = [
    "https://nicolemoore.pythonanywhere.com",
    "https://shipishly.com",
    "https://www.shipishly.com",
]

# ===== Email (LOCAL dev)
# Prints emails (OTP + login alert) to the runserver console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Altavellum <no-reply@altavellum.local>"

# Handy constants used in email templates
SITE_NAME = "Altavellum"
SITE_URL = "http://127.0.0.1:8000"
LOGIN_OTP_EXPIRY_MINUTES = 10
LOGIN_OTP_MAX_ATTEMPTS = 5


# Auth / OTP switches
LOGIN_REQUIRE_OTP = True
LOGIN_ALLOW_OTP_FALLBACK = False   # don't silently log in if OTP email fails
SHOW_DEV_OTP_IN_MESSAGES = True    # also show "DEV OTP: 123456" as a flash message
