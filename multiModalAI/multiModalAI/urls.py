"""
Konfigurasi URL untuk proyek multiModalAI.

`urlpatterns` digunakan untuk mengarahkan URL ke fungsi view.
Dokumentasi: https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from multiModalAIApp.views import (
    home, signin, signout, signup,
    upload, history, export_pdf,
    detail, delete,
)

# Daftar URL utama aplikasi
urlpatterns = [
    path('admin/', admin.site.urls),

    # Halaman utama
    path('', home, name='home'),
    path('home/', home, name='home'),

    # Autentikasi pengguna
    path('signin/', signin, name='login'),
    path('signout/', signout, name='logout'),
    path('signup/', signup, name='signup'),

    # Fitur aplikasi
    path('upload/', upload, name='upload'),
    path('history/', history, name='history'),
    path('export/', export_pdf, name='export_pdf'),
    path('detail/<int:image_id>/', detail, name='detail'),
    path('delete/<int:image_id>/', delete, name='delete'),
]

# Penanganan file media selama pengembangan
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Tambahan konfigurasi untuk produksi (jika DEBUG = False)
if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Tambahkan custom error page jika diperlukan
# handler404 = 'multiModalAIApp.views.custom_404_view'
