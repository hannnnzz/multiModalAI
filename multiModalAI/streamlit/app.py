import os
import sys

# Arahkan ke folder project (yang berisi manage.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

# Set modul settings Django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'multiModalAI.settings'

# Inisialisasi Django
import django
django.setup()

from multiModalAIApp.models import UploadedImage
import streamlit as st
from PIL import Image

st.title("Dashboard Gambar yang Diupload dari Django")

images = UploadedImage.objects.all()

for img in images:
    st.write(f"User: {img.user.username} | Waktu: {img.uploaded_at} | Penyakit: {img.disease_name}")

    img_path = os.path.join(BASE_DIR, 'media', str(img.pic))
    if os.path.exists(img_path):
        image = Image.open(img_path)
        st.image(image, caption=img.disease_name, width=300)
    else:
        st.warning(f"Gambar tidak ditemukan: {img_path}")
