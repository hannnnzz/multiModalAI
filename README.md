# ─── 1. Clone Repository & Setup Local ─────────────────────────────────────────
git clone https://github.com/username/project-ini.git   # clone repo
cd project-ini                                         # masuk ke folder project
pip install django mysqlclient                         # install dependencies
# (Setup Database Local Masing-Masing"
python manage.py migrate                               # apply migrations

# ─── 2. Step Sebelum Coding ─────────────────────────────────────
# (Menggeser progress di Canban Board)
git branch nama_fitur				       # buat branch baru 
git checkout nama_fitur                                # pindah branch
# (lakukan coding di editor / IDE kamu)
git add .                                              # stage semua perubahan
git commit -m "deskripsi singkat perubahan"            # commit dengan pesan
git push -u origin nama_fitur                          # push branch baru ke remote

# ─── 3. Update dari Upstream (jika sudah pernah clone) ─────────────────────────
git fetch                                              # ambil info branch & tag baru
git pull                                               # merge update dari remote

# ─── 5. Create Pull Request (manual di GitHub) ─────────────────────────────────
# → Buka halaman repo di GitHub
# → Klik “Compare & pull request”
# → Isi title & description, lalu Create Pull Request

# ─── 6. Review & Merge (Admin) ─────────────────────────────────────────────────
# (Approval → Merge → Delete branch via GitHub UI)

# ─── 7. Jalankan Server Development ────────────────────────────────────────────
python manage.py runserver                              # start Django dev server (default: http://127.0.0.1:8000/)
