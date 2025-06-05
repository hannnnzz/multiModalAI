"""
Pengaturan Django untuk proyek multiModalAI.

Dibuat dengan perintah 'django-admin startproject' menggunakan Django 5.1.7.
Dokumentasi: https://docs.djangoproject.com/en/5.1/topics/settings/
Daftar lengkap pengaturan: https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
import dj_database_url

# -------------------------------------
# Direktori dasar proyek
# -------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------
# Keamanan
# -------------------------------------

# PERINGATAN: Jangan gunakan kunci rahasia ini di produksi!
SECRET_KEY = "django-insecure-0n94_50mm$e1$z-6u)n%k23eml_q+!*60zvey(&@t-l+o#7-9n"

# PERINGATAN: Jangan aktifkan debug di lingkungan produksi
DEBUG = True

# Daftar host yang diizinkan untuk mengakses proyek ini
ALLOWED_HOSTS = []

# -------------------------------------
# Aplikasi yang terinstal
# -------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "multiModalAIApp",  # Aplikasi kustom kamu
]

# -------------------------------------
# Middleware (perantara permintaan HTTP)
# -------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Untuk mengelola file statis di produksi
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------
# URL & WSGI
# -------------------------------------
ROOT_URLCONF = "multiModalAI.urls"
WSGI_APPLICATION = "multiModalAI.wsgi.application"

# -------------------------------------
# Template (untuk rendering HTML)
# -------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["template"],  # Folder untuk menyimpan template HTML
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

# -------------------------------------
# Database
# -------------------------------------

# Pengaturan database lokal menggunakan MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "multimodalai",
        "USER": "root",
        "PASSWORD": "",
        "HOST": "localhost",
    }
}

# Pengaturan database untuk deployment (komentar dulu)
# DATABASES = {
#     "default": dj_database_url.config(
#         default=os.environ.get("DATABASE_URL"),
#         conn_max_age=600
#     )
# }

# -------------------------------------
# Validasi Kata Sandi
# -------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------
# Internasionalisasi
# -------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------
# File Statis (CSS, JS, Gambar)
# -------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# -------------------------------------
# File Media (Upload pengguna)
# -------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------
# Tipe default untuk primary key di model
# -------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
