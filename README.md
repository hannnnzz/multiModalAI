## 1. Clone Repository & Setup Local
```bash
git clone https://github.com/username/project-ini.git   
cd project-ini   
pip install django mysqlclient
```
(Setup Database Local Masing-Masing")   
```bash
python manage.py migrate                   
```

## 2. Step Sebelum Coding    
(Menggeser progress di Canban Board)    
```bash
git branch nama_fitur    
git checkout nama_fitur
```
(lakukan coding di editor / IDE kamu) lalu untuk Push lakukan ini    
Buat .gitignore
```bash
# Byte‑compiled / cache
__pycache__/
**/__pycache__/
*.py[cod]
*~

# Virtual environments
.venv/
multiModalAI/env/

# SQLite database
db.sqlite3
*.sqlite3-journal

# Django logs, local settings, test cache
*.log
local_settings.py
.pytest_cache/

# Media uploads (user‑uploaded files)
media/

# ML model files (jika model besar disimpan di sini)
model/

# IDE/editor
.vscode/
.idea/
*.sw?
# macOS
.DS_Store
# Windows
Thumbs.db

# Misc
all‑files.txt
```
```bash
git add .    
git commit -m "deskripsi singkat perubahan"    
git push -u origin nama_fitur    
```

## 3. Update dari Upstream (jika sudah pernah clone)     
```bash
git fetch   
git pull    
```

## 4. Create Pull Request (manual di GitHub)    
Buka halaman repo di GitHub    
Klik “Compare & pull request”    
Isi title & description, lalu Create Pull Request    

## 5. Review & Merge (Admin)    
(Approval → Merge → Delete branch via GitHub UI)    

## 6. Jalankan Server Development    
```bash
python manage.py runserver    
```
## 7. Tambahan Streamlit
```bash
pip install streamlit
streamlit run streamlit/app.py
```    
Pastikan Run Streamlit di terminal berbeda
