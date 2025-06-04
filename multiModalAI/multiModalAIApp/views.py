import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import base64
import datetime
from io import BytesIO
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
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
from django.utils import timezone
from datetime import timedelta

# Mapping nama kelas → deskripsi, treatment, dan prevention
disease_info = {
    'Antraknosa': {
        'name': 'Antraknosa',
        'description': (
            'Penyakit Antraknosa pada tanaman biasanya ditandai dengan munculnya '
            'bintik‐bintik hitam atau bolong pada daun akibat infeksi jamur. Daun akan '
            'tampak “mata ikan” dan mudah rontok jika tidak diatasi.'
        ),
        'treatment': (
            'Semprot fungisida berbahan aktif tembaga (contoh: FungisidaX) setiap 7–10 hari '
            'sekali, terutama saat curah hujan tinggi.'
        ),
        'prevention': (
            '- Jaga kelembapan di lapangan: hindari genangan air, pastikan jarak tanam cukup, '
            'dan sirkulasi udara lancar.\n'
            '- Sanitasi tanaman: pangkas dan buang daun/daun yang bolong atau “terbakar” akibat jamur, '
            'bersihkan sisa tanaman di pangkal batang.\n'
            '- Gunakan fungisida berbahan aktif tembaga secara periodik (7–10 hari sekali).\n'
            '- Perbaiki sistem drainase agar media tanam tidak tergenang.'
        )
    },
    'Bercak Daun': {
        'name': 'Bercak Daun',
        'description': (
            'Bercak Daun disebabkan oleh beberapa jenis jamur/bakteri, menimbulkan bercak cokelat '
            'atau hitam di permukaan daun. Jika parah, daun mengering dan rontok.'
        ),
        'treatment': (
            'Semprot fungisida tembaga (misalnya mancozeb) dengan konsentrasi 0.2% setiap 10 hari. '
            'Potong dan buang daun yang sudah parah agar tidak menyebar.'
        ),
        'prevention': (
            '- Kendalikan kelembapan dan sirkulasi udara: hindari penyiraman langsung ke daun, '
            'siramlah di pagi hari agar daun cepat kering, dan jaga jarak tanam.\n'
            '- Sanitasi daun yang bernoda/parah: potong dan buang secara rutin.\n'
            '- Semprot fungisida ber‐bahan tembaga secara periodik (10 hari sekali).\n'
            '- Pastikan drainase lapang baik agar media tanam tidak lembap berlebihan.'
        )
    },
    'Keriting Daun': {
        'name': 'Keriting Daun',
        'description': (
            'Keriting Daun adalah gejala daun keriting pada cabai, umumnya disebabkan oleh virus '
            'yang ditularkan oleh kutu daun atau vektor serupa. Daun menjadi kerdil dan '
            'pertumbuhan tanaman terhambat.'
        ),
        'treatment': (
            'Semprot insektisida berbahan aktif imidakloprid atau abamektin untuk mengendalikan kutu '
            'dan vektor lainnya. Gunakan varietas tahan virus jika tersedia.'
        ),
        'prevention': (
            '- Pakailah varietas tahan virus (jika ada).\n'
            '- Gunakan benih/bibit bebas virus (clean seed).\n'
            '- Kontrol vektor: semprot insektisida (imidakloprid/abamektin) secara berkala, '
            'dan pasang perangkap kuning untuk kutu daun.\n'
            '- Isolasi tanaman baru: tanam di lokasi terpisah atau periksa gejala sebelum dimasukkan ke kebun.'
        )
    },
    'Fusarium': {
        'name': 'Fusarium',
        'description': (
            'Fusarium wilt (Fusarium oxysporum) menyebabkan batang layu dari pangkal, daun '
            'menguning, dan akhirnya mati. Infeksi terjadi melalui akar yang terkontaminasi jamur.'
        ),
        'treatment': (
            'Semprot fungisida sistemik (contoh: Triazole) dan aplikasikan kapur pertanian '
            'untuk menaikkan pH tanah, sehingga jamur Fusarium kurang berkembang.'
        ),
        'prevention': (
            '- Rotasi tanaman: hindari menanam cabai atau tanaman Solanaceae di lahan yang sama '
            'setidaknya satu musim.\n'
            '- Perbaiki drainase: pastikan lahan tidak tergenang air agar akar tidak lembap.\n'
            '- Gunakan benih/steril media tanam: pilih bibit bebas penyakit (certified seed).\n'
            '- Pengapuran tanah: aplikasikan kapur pertanian untuk menaikkan pH (± 6,5–7).'
        )
    },
    'Sehat': {
        'name': 'Sehat',
        'description': (
            'Tanaman tampak sehat, tidak ada gejala penyakit atau hama. Daun hijau segar, batang kokoh.'
        ),
        'treatment': (
            'Tidak perlu pengobatan khusus. Lakukan perawatan dan pemupukan standar agar tanaman tetap prima.'
        ),
        'prevention': (
            '- Pemupukan NPK seimbang secara rutin untuk pertumbuhan daun dan buah.\n'
            '- Rotasi tanaman dan sanitasi lahan: bersihkan gulma dan sisa‐sisa tanaman.\n'
            '- Pantau kelembapan media tanam: hindari kelebihan air.\n'
            '- Cek tanaman secara berkala, segera ambil tindakan bila ada gejala awal penyakit atau hama.'
        )
    },
    'Serangga': {
        'name': 'Serangan Hama',
        'description': (
            'Serangan hama seperti ulat, lalat buah, kutu putih, kutu hitam menyebabkan daun '
            'atau buah rusak, berlubang, dan kondisi tanaman melemah.'
        ),
        'treatment': (
            'Semprot insektisida nabati (ekstrak neem) atau insektisida kimia standar sesuai dosis '
            'untuk memberantas hama yang menyerang.'
        ),
        'prevention': (
            '- Semprot insektisida biasa secara rutin (sesuai dosis) untuk ulat, lalat buah, '
            'kutu putih/putih, dan kutu hitam.\n'
            '- Pasang perangkap kuning atau perangkap jeruk untuk kutu putih.\n'
            '- Tanam tanaman perangkap (companion planting) yang dapat menarik hama menjauh dari cabai.\n'
            '- Sanitasi buah/daun terinfeksi: buang buah yang ada ulat di dalamnya dan daun penuh kutu.'
        )
    },
    'Penyakit Kuning': {
        'name': 'Kuning Daun',
        'description': (
            'Daun menguning bisa disebabkan oleh kekurangan nutrisi (klorosis) atau infeksi virus '
            '(sering disebut penyakit kuning/bule). Jika virus, biasanya berasal dari benih atau vektor.'
        ),
        'treatment': (
            'Tambahkan pupuk nitrogen (N) jika karena kekurangan nutrisi, semprot mikro‐nutrien '
            '(Fe, Mg) untuk mencegah klorosis, atau pisahkan tanaman terinfeksi jika virus terdeteksi.'
        ),
        'prevention': (
            '- Gunakan bibit/bibit bebas virus (clean seed) atau varietas toleran virus.\n'
            '- Pupuk NPK seimbang dan semprot mikro‐nutrien (zat besi, magnesium) bila perlu.\n'
            '- Perbaiki drainase agar akar mendapat oksigen dan tidak tergenang.\n'
            '- Singkirkan daun yang terlalu kuning parah agar sumber infeksi (jika virus) tidak menyebar.'
        )
    },
}

# Load model sekali di awal

model_path = os.path.join(settings.BASE_DIR, 'model', 'model_mobilenettv.h5')  
model = load_model(model_path)

'''
# path ke .tflite
tflite_model_path = os.path.join(settings.BASE_DIR, 'model', 'model_mobilenettv.tflite')
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Ambil detail input/output
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
'''

# Mapping hasil prediksi ke nama penyakit
disease_classes = ['Antraknosa', 'Bercak Daun', 'Keriting Daun', 'Fusarium', 'Sehat', 'Serangga', 'Penyakit Kuning']

# Fungsi yang dipanggil ke URLS

# Fungsi untuk mengambil halaman utama
def home(request):
    if not request.user.is_authenticated:
        return redirect('/signin')

    images = UploadedImage.objects.filter(user=request.user)
    total = images.count()
    recent_images = images.order_by('-uploaded_at')[:3]

    # Ambil daftar penyakit yang pernah diupload user ini (distinct)
    labels = list(images.values_list('disease_name', flat=True).distinct())

    values = []
    for label in labels:
        count = images.filter(disease_name__iexact=label).count()
        if total > 0:
            values.append(round(count / total * 100, 2))
        else:
            values.append(0)

    context = {
        'img': images,
        'recent_images': recent_images,
        'chart_data': {
            'labels': labels,
            'values': values,
        }
    }
    return render(request, 'home.html', context)

# Fungsi untuk mengambil halaman login
# Jika sudah login, redirect ke home
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

# Fungsi untuk mengambil halaman signout
# Jika sudah logout, redirect ke login
def signout(request):
    logout(request)
    return redirect('/signin')

# Fungsi untuk mengambil halaman signup
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

# Fungsi untuk mengambil halaman upload
# Jika sudah upload, redirect ke history
def upload(request):
    if request.method == 'POST' and request.FILES.get('pic'):
        image_file = request.FILES['pic']
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        file_path = fs.path(filename)

        # Prediksi gambar
        img = image.load_img(file_path, target_size=(224, 224))  # Sesuaikan ukuran model kamu
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalisasi jika modelmu pakai itu
        
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)
        
        '''
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], img_array.astype(input_details[0]['dtype']))
        # Jalankan inference
        interpreter.invoke()
        # Ambil output
        pred = interpreter.get_tensor(output_details[0]['index'])
        predicted_class = np.argmax(pred)
        confidence = np.max(pred) * 100
        '''
        
        disease_name = f"{disease_classes[predicted_class]}"


        # Simpan ke database
        UploadedImage.objects.create(
            user=request.user,
            pic=filename,
            disease_name=disease_name
        )

        return redirect('/history')  # Redirect ke history

    # Ambil semua gambar user saat ini, terbaru dulu
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    return render(request, 'upload.html', {'img': images})

# Fungsi untuk menghapus gambar
def delete(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)

    # Pastikan hanya pemilik gambar yang bisa menghapus (jika ingin fitur ini)
    if request.user == image.user:
        image.pic.delete()  # Hapus file dari sistem
        image.delete()  # Hapus data dari database
    return redirect('/history')

# Fungsi untuk mengambil halaman history
def history(request):
    filter_days = request.GET.get('days')
    filter_disease = request.GET.get('disease')

    images = UploadedImage.objects.filter(user=request.user)

    if filter_days and filter_days.isdigit():
        days = int(filter_days)
        cutoff_date = timezone.now() - timedelta(days=days)
        images = images.filter(uploaded_at__gte=cutoff_date)

    if filter_disease and filter_disease != '':
        images = images.filter(disease_name__iexact=filter_disease)

    images = images.order_by('-uploaded_at')

    # Ambil semua penyakit dari disease_info, format (key, name)
    disease_list = [(key, disease_info[key]['name']) for key in sorted(disease_info.keys())]

    context = {
        'img': images,
        'filter_days': filter_days,
        'filter_disease': filter_disease,
        'disease_list': disease_list,
    }

    return render(request, 'history.html', context)

# Fungsi untuk mengambil halaman detail
def detail(request, image_id):
    # Ambil objek UploadedImage milik user
    image_obj = get_object_or_404(UploadedImage, id=image_id, user=request.user)

    # Contoh value image_obj.disease_name: "Antraknosa (95.34%)"
    raw_name = image_obj.disease_name
    # Potong label hingga sebelum " ("
    label = raw_name.rsplit(' (', 1)[0]  # → "Antraknosa"

    # Ambil info dari mapping, jika tidak ditemukan, pakai fallback generic
    info = disease_info.get(label, {
        'name': label,
        'description': 'Informasi belum tersedia.',
        'treatment': 'Tidak ada rekomendasi khusus.',
        'prevention': 'Tidak ada pencegahan khusus.'
    })

    context = {
        'image': image_obj,
        'info': info,
    }
    return render(request, 'detail.html', context)

# Fungsi untuk mengekspor PDF
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

