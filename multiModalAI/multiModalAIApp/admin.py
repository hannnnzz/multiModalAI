from django.contrib import admin
from .models import UploadedImage

# Registrasi model UploadedImage ke halaman admin Django.
# Dengan ini, model dapat dikelola melalui antarmuka admin.

admin.site.register(UploadedImage)