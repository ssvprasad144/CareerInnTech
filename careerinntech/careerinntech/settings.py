from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url


# ================= LOAD ENV =================


# ================= BASE =================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
print("OPENAI KEY LOADED:", bool(os.getenv("OPENAI_API_KEY")))
# ================= SECURITY =================

# SECRET KEY
# - Local: uses fallback
# - Render: uses environment variable
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

    "core",
    "college",
    'skills',
]
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
    
]

# ================= URL / WSGI =================

ROOT_URLCONF = "careerinntech.urls"
WSGI_APPLICATION = "careerinntech.wsgi.application"

# ================= TEMPLATES =================

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
                "core.context_processors.student_profile",
            ],
        },
    },
]

# ================= DATABASE =================
# SQLite (local) | PostgreSQL (Render)

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

# ================= INTERNATIONALIZATION =================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ================= AUTH =================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "post_login"
LOGOUT_REDIRECT_URL = "home"

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

# ================= DEFAULT FIELD =================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
