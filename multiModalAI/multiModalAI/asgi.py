# Konfigurasi ASGI untuk proyek multiModalAI

# Modul ini menyiapkan callable ASGI bernama `application`
# yang digunakan oleh server ASGI untuk menjalankan aplikasi Django.
# Dokumentasi resmi: https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/

import os
from django.core.asgi import get_asgi_application

# Menentukan pengaturan default Django untuk proyek ini
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiModalAI.settings")

# Membuat instance aplikasi ASGI
application = get_asgi_application()
