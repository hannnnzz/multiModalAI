from django.db import models
from django.contrib.auth.models import User

# Model untuk menyimpan gambar yang diunggah oleh pengguna
class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relasi ke pengguna yang mengunggah
    pic = models.ImageField(upload_to='uploads/')             # Lokasi penyimpanan gambar
    disease_name = models.CharField(max_length=255, blank=True, null=True)  # Nama penyakit (jika ada)
    uploaded_at = models.DateTimeField(auto_now_add=True)     # Waktu unggah otomatis

    def __str__(self):
        return f"Image {self.id} - {self.uploaded_at}"        # Representasi string objek
