"""
Konfigurasi WSGI untuk proyek multiModalAI.

File ini menyediakan objek WSGI yang bernama `application`,
yang digunakan oleh server seperti Gunicorn atau uWSGI
untuk menjalankan proyek Django ini.

Dokumentasi: https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Menetapkan modul settings default untuk proyek ini
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiModalAI.settings")

# Membuat instance aplikasi WSGI
application = get_wsgi_application()
