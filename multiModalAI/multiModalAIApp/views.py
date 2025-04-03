import os
import base64
import datetime
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import UploadedImage
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        pr=UploadedImage.objects.all().filter(user=request.user)
        c={"img":pr}
        return render(request,"home.html",context=c)
    else:
        return redirect('/signin')

def signin(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST["password"]
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect ke home setelah login berhasil
            else:
                messages.error(request, "Username atau password salah! Silakan coba lagi.")
                return redirect('/signin')

        return render(request, "login.html")

def signout(request):
    logout(request)
    return redirect('/signin')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confpassword = request.POST['confirmpassword']

        if password == confpassword:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username sudah digunakan! Coba yang lain.")
                return redirect('/signup')
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                login(request, user)
                messages.success(request, "Akun berhasil dibuat! Selamat datang, {}.".format(username))
                return redirect('/')  # Redirect ke home setelah signup berhasil
        else:
            messages.error(request, "Password tidak cocok! Silakan coba lagi.")
            return redirect('/signup')

    return render(request, "signup.html")
    
def upload(request):
    if request.method == 'POST' and request.FILES.get('pic'):
        image = request.FILES['pic']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        # Simpan gambar ke database dengan user
        UploadedImage.objects.create(user=request.user, pic=filename)

        return redirect('/home')  # Redirect ke halaman utama

    # Ambil semua gambar yang diupload user saat ini, urutkan terbaru dulu
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    return render(request, 'upload.html', {'img': images})

def delete(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)

    # Pastikan hanya pemilik gambar yang bisa menghapus (jika ingin fitur ini)
    if request.user == image.user:
        image.pic.delete()  # Hapus file dari sistem
        image.delete()  # Hapus data dari database
    return redirect('/home')

def history(request):
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'history.html', {'img': images})

def detail(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id, user=request.user)
    return render(request, 'detail.html', {'image': image})

def export_pdf(request):
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')

    # Konversi gambar ke base64
    for img in images:
        img_path = os.path.join(settings.MEDIA_ROOT, img.pic.name)
        with default_storage.open(img_path, "rb") as image_file:
            img.base64 = base64.b64encode(image_file.read()).decode('utf-8')

    template_path = 'export_pdf_template.html'
    context = {
        'img': images,
        'user': request.user,
        'export_date': datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Riwayat_Deteksi.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF', content_type='text/plain')

    return response