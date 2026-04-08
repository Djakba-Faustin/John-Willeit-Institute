"""
Django settings for John Willeit Higher Institute LMS.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = "postgresql://postgres:ytJoBmKitksXokIivYHyHJkhCpWgPNNJ@mainline.proxy.rlwy.net:56726/railway"

_env_file = BASE_DIR / ".env"
if _env_file.is_file():
    load_dotenv(_env_file, encoding="utf-8")
else:
    load_dotenv(encoding="utf-8")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-in-production")

DEBUG = True

ALLOWED_HOSTS = ['john-willeit-institute-1.onrender.com']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "academics",
    "core",
    "lms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jw_lms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "core.context_processors.site_branding",
            ],
        },
    },
]

WSGI_APPLICATION = "jw_lms.wsgi.application"

_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or os.environ.get("PGPASSWORD", "")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": _POSTGRES_PASSWORD,
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

if not _POSTGRES_PASSWORD:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "PostgreSQL password is missing. Create a .env file in the project root "
        "(copy .env.example) and set POSTGRES_PASSWORD, or set the PGPASSWORD environment variable."
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Africa/Douala"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "lms:index"
LOGOUT_REDIRECT_URL = "core:home"

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Email notifications (materials, assignments, quizzes).
# Default backend prints emails to console in development.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1").lower() in ("1", "true", "yes")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "no-reply@jwhi-lms.local",
)
