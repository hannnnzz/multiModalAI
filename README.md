## 1. Clone Repository & Setup Local
git clone https://github.com/username/project-ini.git 
cd project-ini 
pip install django mysqlclient 
(Setup Database Local Masing-Masing") 
python manage.py migrate                               

## 2. Step Sebelum Coding
(Menggeser progress di Canban Board) 
git branch nama_fitur 
git checkout nama_fitur 
(lakukan coding di editor / IDE kamu) 
git add . 
git commit -m "deskripsi singkat perubahan" 
git push -u origin nama_fitur

## 3. Update dari Upstream (jika sudah pernah clone) 
git fetch 
git pull

## 4. Create Pull Request (manual di GitHub) 
Buka halaman repo di GitHub 
Klik “Compare & pull request” 
Isi title & description, lalu Create Pull Request

## 5. Review & Merge (Admin) 
(Approval → Merge → Delete branch via GitHub UI)

## 6. Jalankan Server Development 
python manage.py runserver
