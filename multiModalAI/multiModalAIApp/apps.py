# Konfigurasi aplikasi Django untuk multiModalAIApp

from django.apps import AppConfig

class MultimodalaiappConfig(AppConfig):
    # Menentukan jenis field default untuk primary key pada model
    default_auto_field = "django.db.models.BigAutoField"

    # Nama aplikasi sesuai dengan folder app
    name = "multiModalAIApp"
