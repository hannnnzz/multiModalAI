from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models

# Model untuk menyimpan gambar yang diupload
class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to='uploads/')
    disease_name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.uploaded_at}"
