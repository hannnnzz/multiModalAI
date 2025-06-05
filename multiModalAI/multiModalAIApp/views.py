import os
import locale
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import base64
from datetime import timedelta, datetime, time
from io import BytesIO
from collections import OrderedDict, Counter
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from calendar import month_name
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.timezone import now as dj_now
from xhtml2pdf import pisa
from .models import UploadedImage


# Mapping Nama Kelas → Deskripsi, Treatment, dan Prevention
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

# Load Model CNN

model_path = os.path.join(settings.BASE_DIR, 'model', 'model_mobilenettv.h5')  
model = load_model(model_path)

''' # Load Model TFLite (Deployment)
# path ke .tflite
tflite_model_path = os.path.join(settings.BASE_DIR, 'model', 'model_mobilenettv.tflite')
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Ambil detail input/output
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
'''

# Mapping Hasil Prediksi ke Nama Penyakit
disease_classes = ['Antraknosa', 'Bercak Daun', 'Keriting Daun', 'Fusarium', 'Sehat', 'Serangga', 'Penyakit Kuning']

# Set Locale ke Bahasa Indonesia Supaya Nama Hari dan Bulannya Bahasa Indonesia
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')  # Linux/MacOS
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Indonesian_indonesia.1252')  # Windows
    except locale.Error:
        pass  # Apabila gagal ke default (Bahasa Inggris)

# Helper Konversi Tanggal String 'YYYY-MM-DD' Menjadi Nama Hari Bahasa Indonesia
def get_day_name(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%A')  # Contoh: 'Senin', 'Selasa', dst

# Helper Untuk Mengubah Angka Bulan ke Nama Bulan Indonesia
def get_month_name(month_num):
    dt = datetime(2000, month_num, 1)
    return dt.strftime('%B')  # Contoh: 'Januari', 'Februari', dst

# Fungsi Untuk Mengambil Halaman Utama
def home(request):
    if not request.user.is_authenticated:
        return redirect('/signin')

    # Ambil 3 Gambar Terbaru yang diupload Oleh User
    images = UploadedImage.objects.filter(user=request.user)
    total = images.count()
    recent_images = images.order_by('-uploaded_at')[:3]

    # Hitung Upload per Hari Selama 7 Hari Terakhir
    today = timezone.now().date()
    days_range = [today - timedelta(days=i) for i in range(6, -1, -1)]

    # OrderedDict untuk menyimpan jumlah upload per hari
    uploads_per_day = OrderedDict()
    for day in days_range:
        start_dt = timezone.make_aware(datetime.combine(day, time.min))
        end_dt = timezone.make_aware(datetime.combine(day, time.max))
        count = images.filter(uploaded_at__range=(start_dt, end_dt)).count()
        uploads_per_day[day.strftime('%Y-%m-%d')] = count

    total_uploads_last_7_days = sum(uploads_per_day.values())

    # Hitung Jumlah Kemunculan Setiap disease_name
    raw_labels = list(images.values_list('disease_name', flat=True))
    disease_counter = Counter(name for name in raw_labels if name)

    # Pie Chart: Persentase tiap Penyakit
    labels = list(disease_counter.keys())
    values = [
        round((disease_counter[label] / total) * 100, 2) if total > 0 else 0
        for label in labels
    ]

    # Bar Chart: Jumlah Deteksi tiap Penyakit
    bar_labels = labels
    bar_counts = [disease_counter[label] for label in bar_labels]

    # Ringkasan Bulanan
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    month_display = get_month_name(current_month)

    # Menggunakan Filter untuk Mendapatkan Gambar yang diupload pada Bulan dan Tahun Ini
    monthly_images = images.filter(uploaded_at__month=current_month, uploaded_at__year=current_year)
    monthly_total = monthly_images.count()

    # Hitung Jumlah Penyakit yang Terdeteksi pada Bulan ini
    monthly_raw_labels = list(monthly_images.values_list('disease_name', flat=True))
    monthly_counter = Counter(name for name in monthly_raw_labels if name)
    monthly_disease_count = sum(monthly_counter.values())

    # Ambil 3 Penyakit Paling Umum pada Bulan Ini
    top_3 = monthly_counter.most_common(3)
    top_3_data = [
        {
            'name': name,
            'percentage': round((count / monthly_disease_count) * 100, 2) if monthly_disease_count else 0
        }
        for name, count in top_3
    ]

    # Hitung Hari Paling Aktif dan Paling Sepi Upload, Dalam Bentuk Nama Hari Bahasa Indonesia
    most_active_day_date = max(uploads_per_day.items(), key=lambda x: x[1])[0] if uploads_per_day else None
    least_active_day_date = min(uploads_per_day.items(), key=lambda x: x[1])[0] if uploads_per_day else None

    most_active_day = get_day_name(most_active_day_date) if most_active_day_date else '—'
    least_active_day = get_day_name(least_active_day_date) if least_active_day_date else '—'

    # Siapkan Context untuk Render Template
    context = {
        'img': images,
        'recent_images': recent_images,
        'uploads_per_day_keys': list(uploads_per_day.keys()),
        'uploads_per_day_values': list(uploads_per_day.values()),
        'total_uploads_last_7_days': total_uploads_last_7_days,
        'chart_data': {
            'labels': labels,
            'values': values,
        },
        'bar_chart_data': {
            'labels': bar_labels,
            'values': bar_counts,
        },
        'monthly_summary': { 
            'now': dj_now(),
            'month': month_display,
            'total_upload': monthly_total,
            'disease_detected': monthly_disease_count,
            'most_common': top_3_data[0]['name'] if top_3_data else '—',
            'top_diseases': top_3_data,
            'most_active_day': most_active_day,
            'least_active_day': least_active_day,
        }
    }

    return render(request, 'home.html', context)

# Fungsi Untuk Mengambil Halaman Login
# Jika Sudah Login, Redirect ke Home
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

# Fungsi Untuk Mengambil Halaman Signout
# Jika Sudah Logout, Redirect ke Login
def signout(request):
    logout(request)
    return redirect('/signin')

# Fungsi Untuk Mengambil Halaman Signup
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

# Fungsi Untuk Mengambil Halaman Upload
# Jika Sudah Upload, Redirect ke History
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
def upload(request):
    if request.method == 'POST' and request.FILES.get('pic'):
        image_file = request.FILES['pic']

        # Cek Ekstensi File
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            messages.error(request, "Format file tidak didukung. Harap upload file gambar (JPG, PNG, BMP, dll).")
            return redirect('/upload')  # atau halaman upload kamu
        
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        file_path = fs.path(filename)

        # Proses Prediksi Gambar
        img = image.load_img(file_path, target_size=(224, 224))  # Sesuaikan ukuran model kamu
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalisasi ukuran
        
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)
        disease_name = f"{disease_classes[predicted_class]}"

        # Simpan ke Database
        UploadedImage.objects.create(
            user=request.user,
            pic=filename,
            disease_name=disease_name
        )
        
        messages.success(request, "Upload dan prediksi berhasil!")
        return redirect('/upload')

    return render(request, 'upload.html')  # Redirect ke history

# Fungsi Untuk Menghapus Gambar
def delete(request, image_id):
    image = get_object_or_404(UploadedImage, id=image_id)

    # Pastikan Hanya Pemilik Gambar yang Bisa Menghapus
    if request.user == image.user:
        image.pic.delete()  # Hapus File dari Sistem
        image.delete()  # Hapus Data dari Database
    return redirect('/history')

# Fungsi Untuk Mengambil Halaman history
def history(request):
    filter_days = request.GET.get('days')
    filter_disease = request.GET.get('disease')

    images = UploadedImage.objects.filter(user=request.user)

    # Filter Berdasarkan Hari Terakhir diupload
    if filter_days and filter_days.isdigit():
        days = int(filter_days)
        cutoff_date = timezone.now() - timedelta(days=days)
        images = images.filter(uploaded_at__gte=cutoff_date)

    # Filter Berdasarkan Nama Penyakit
    if filter_disease and filter_disease != '':
        images = images.filter(disease_name__iexact=filter_disease)

    # Urutkan Berdasarkan Waktu Upload Terbaru
    images = images.order_by('-uploaded_at')

    # Ambil Semua Penyakit Dari disease_info, format (key, name)
    disease_list = [(key, disease_info[key]['name']) for key in sorted(disease_info.keys())]

    context = {
        'img': images,
        'filter_days': filter_days,
        'filter_disease': filter_disease,
        'disease_list': disease_list,
    }

    return render(request, 'history.html', context)

# Fungsi Untuk Mengambil Halaman detail
def detail(request, image_id):
    # Ambil Objek UploadedImage Milik User
    image_obj = get_object_or_404(UploadedImage, id=image_id, user=request.user)

    # Ambil Nama Penyakit dari Objek
    raw_name = image_obj.disease_name
    label = raw_name.rsplit(' (', 1)[0]  

    # Ambil Info dari Mapping, Jika Tidak Ditemukan, Pakai Fallback Generic
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

# Fungsi untuk Mengekspor PDF
def export_pdf(request):
    images = UploadedImage.objects.filter(user=request.user).order_by('-uploaded_at')

    # Konversi Gambar ke base64 + Tambahkan Treatment
    for img in images:
        # Convert Gambar ke base64
        img_path = os.path.join(settings.MEDIA_ROOT, img.pic.name)
        with default_storage.open(img_path, "rb") as image_file:
            img.base64 = base64.b64encode(image_file.read()).decode('utf-8')

        # Tambahkan Rekomendasi Treatment Berdasarkan disease_name
        img.treatment = disease_info.get(img.disease_name, {}).get(
            'treatment', 'Belum ada rekomendasi.')

    # Siapkan Template untuk PDF
    template_path = 'export_pdf_template.html'
    context = {
        'img': images,
        'user': request.user,
        'export_date': datetime.now().strftime("%d %B %Y, %H:%M")
    }

    # Render Template ke HTML
    template = get_template(template_path)
    html = template.render(context)

    # Buat PDF dari HTML
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Riwayat_Deteksi.pdf"'

    # Gunakan xhtml2pdf untuk mengkonversi HTML ke PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF', content_type='text/plain')

    return response

# Fungsi untuk 404 Untuk Deployment
#def custom_404_view(request, exception):
#   return render(request, '404.html', status=404)

