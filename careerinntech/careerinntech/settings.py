from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url


# ================= BASE =================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

print("OPENAI KEY LOADED:", bool(os.getenv("OPENAI_API_KEY")))

# ================= SECURITY =================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-dev-key-change-this"
)

# ================= OPENAI =================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY NOT FOUND")
else:
    print("✅ OPENAI_API_KEY LOADED")

# ================= AZURE SPEECH =================

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
AZURE_SPEECH_VOICE = os.getenv("AZURE_SPEECH_VOICE", "en-US-JennyNeural")

# ================= TTS (OpenAI fallback) =================

OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")

# ================= DEBUG =================

DEBUG = os.environ.get("DEBUG", "False") == "True"

# ================= ALLOWED HOSTS =================

ALLOWED_HOSTS = [
    "careerinntech.onrender.com",
    "careerinntech.com",
    "www.careerinntech.com",
    "127.0.0.1",
    "localhost",
    ".onrender.com",
]

# ================= APPLICATIONS =================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "channels",  # ✅ REQUIRED FOR WEBSOCKETS
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    # Social account providers disabled for now — implement later

    # Local apps
    "core",
    "college",
    "skills",
    "projects",
    "AI",
]

# ================= I18N =================

USE_I18N = True

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("hi", "Hindi"),
    ("te", "Telugu"),
    ("ta", "Tamil"),
]

LANGUAGE_COOKIE_NAME = "django_language"

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# ================= MIDDLEWARE =================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# ================= URL / SERVER =================

ROOT_URLCONF = "careerinntech.urls"

# ✅ KEEP THIS (normal Django HTTP)
WSGI_APPLICATION = "careerinntech.wsgi.application"

# ✅ ADD THIS (real-time WebSocket support)
ASGI_APPLICATION = "careerinntech.asgi.application"

# ================= TEMPLATES =================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
                BASE_DIR / "templates",
                # Also include the inner project templates directory where
                # the `ai` templates are located (careerinntech/templates)
                Path(__file__).resolve().parent / "templates",
            ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.student_profile",
            ],
        },
    },
]

# ================= DATABASE =================

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ================= PASSWORD VALIDATION =================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================= TIMEZONE =================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

# ================= AUTH =================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "post_login"
LOGOUT_REDIRECT_URL = "home"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SIGNUP_FIELDS = ["email", "username"]

# Social account provider settings (Google)
# SOCIALACCOUNT_PROVIDERS kept for reference; social login currently disabled
SOCIALACCOUNT_PROVIDERS = {}

# ================= STATIC FILES =================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================= MEDIA =================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ================= DEFAULT FIELD =================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'careerinntech@gmail.com'
EMAIL_HOST_PASSWORD = 'vgttouhpqvtkmhrm'

