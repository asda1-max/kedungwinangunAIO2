# CLAUDE.md - Project Reference (Updated)

**Project**: Desa Kedungwinangun AIO  
**Type**: Flask Web Application (Desa Digital / E-Government)  
**Location**: C:\Productivity\Coding\Projects\kedungwinangunAIO  
**Port**: 5209 (default)  
**Last Updated**: 9 Juli 2026

---

## Quick Start

```bash
cd C:\Productivity\Coding\Projects\kedungwinangunAIO
pip install -r requirements.txt
python app.py
# Opens: http://localhost:5209
```

---

## Architecture

### Tech Stack
```
Backend:    Python 3.12 + Flask 3.0+
Database:   SQLite3 (file: database.db)
Frontend:   HTML5 + Tailwind CSS 3.x + Vanilla JS + Alpine.js
PDF:        ReportLab 4.0+ (placeholder)
AI:         OpenRouter API (server-side)
Auth:       Werkzeug PBKDF2 hashing
```

### Directory Structure
```
├── app.py              # Entry point, blueprint registration, chatbot API, error handlers
├── config.py           # Config class, DEFAULT_CONFIG, NAV_LINKS, DUSUN_DATA, SQL_SCHEMA
├── models.py           # ALL DB operations - 2592 lines of models
├── database.py         # Database error handling + safe DB operations
├── errors.py           # Custom exceptions, decorators, validation helpers (873 lines)
├── routes/             # Route handlers (modular blueprints)
│   ├── __init__.py           # Blueprint exports
│   ├── public.py             # Legacy: monolithic public routes (50,852 bytes)
│   ├── public_auth.py        # Login, logout
│   ├── public_home.py        # Homepage / beranda
│   ├── public_berita.py      # Berita list, detail, komentar API
│   ├── public_pages.py       # Galeri, kontak, kritik saran, custom pages
│   ├── public_struktur.py    # Struktur organisasi, sejarah desa
│   ├── public_info.py        # Kependudukan, pengumuman, peta, transparansi
│   ├── public_aduan.py       # Aduan, program kerja, agenda
│   ├── admin.py              # Legacy: monolithic admin routes (102,408 bytes)
│   ├── admin_dashboard.py    # Dashboard, auth redirects
│   ├── admin_berita.py       # Berita CRUD
│   ├── admin_galeri.py       # Galeri CRUD + toggle
│   ├── admin_pages.py        # Pages, sejarah, config management
│   ├── admin_struktur.py     # Struktur CRUD + import/export/template
│   ├── admin_umkm.py        # UMKM CRUD + Google Maps location parser
│   ├── admin_potensi.py     # Potensi, kependudukan
│   ├── admin_pengumuman.py   # Pengumuman, APBDes CRUD
│   ├── admin_aduan.py        # Aduan, kritik saran, program kerja, agenda
│   ├── admin_accounts.py     # Account center, settings
│   └── admin_rtrw.py        # RT/RW locations management (separate blueprint)
├── templates/          # Jinja2 templates (30+ files)
│   ├── base.html             # Main layout with navbar, footer, dark mode
│   ├── index.html            # Homepage (68,635 bytes)
│   ├── berita.html           # News listing
│   ├── detail_berita.html    # News detail + comments
│   ├── galeri.html           # Photo gallery
│   ├── kontak.html           # Contact page
│   ├── aduan.html            # Complaint form
│   ├── kritik_saran.html     # Kritik dan saran form
│   ├── program_kerja.html    # Work programs
│   ├── agenda.html           # Village agenda
│   ├── transparansi.html     # APBDes transparency
│   ├── info_kependudukan.html # Demographics
│   ├── peta_interaktif.html  # Interactive map
│   ├── sejarah.html          # Village history
│   ├── struktur.html         # Organization structure
│   ├── struktur_detail.html  # Person detail
│   ├── pengumuman.html       # Announcements
│   ├── login.html            # Unified login
│   ├── page.html             # Dynamic pages
│   ├── cek_aduan.html        # Check complaint status
│   ├── error.html            # Error page
│   ├── admin/                # 40+ admin templates
│   ├── partials/             # Navbar, footer, chatbot, dark-mode
│   └── dinas/                # Dinas templates
├── static/
│   ├── styles.css            # Main CSS (846 lines)
│   ├── dark-mode.js          # Dark mode script
│   └── data/geojson          # Peta interaktif GeoJSON
├── geojson/                  # GeoJSON files for map layers
└── uploads/                  # User uploads (KTP, KK, berita, galeri, dll)
```

---

## Database

### Connection Pattern
```python
from models import get_db_connection
conn = get_db_connection()  # Returns sqlite3.Row dict-like rows
cursor = conn.cursor()
# ... queries ...
conn.close()
```

### Tables (16 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | All users (admin/dinas/penduduk) | id, nik, username, nip, nama_lengkap, password_hash, role, status |
| `berita` | News articles | judul, excerpt, kategori, badge_class, gambar_url, video_url, facebook_auto_post, unggulan |
| `sejarah_desa` | Village history timeline | judul, sub_judul, konten, tahun_dari, tahun_sampai, gambar_url |
| `config` | Website config | key, value |
| `galeri` | Photos | judul, deskripsi, kategori, gambar_url, aktif |
| `pages` | Dynamic pages | title, slug, content, icon, order_num, active |
| `komentar` | News comments | berita_id, parent_id, user_id, nama_pengirim, konten |
| `struktur_organisasi` | Village org structure | kategori, nama, jabatan, nik, alamat, telepon, foto_url, status |
| `pengumuman` | Announcements | judul, isi, kategori, is_penting, lampiran, author, aktif |
| `apbdes` | Budget items | tahun, jenis, nama, icon, jumlah, deskripsi |
| `apbdes_summary` | Budget summary | tahun, total_pendapatan, total_belanja, pembiayaan_net |
| `umkm` | UMKM listings | nama, kategori, pemiliki_nama, alamat, latitude, longitude, foto_url |
| `kependudukan` | Demographics data | kategori, label, jumlah, satuan, tahun |
| `potensi_desa` | Village potentials | nama, kategori, deskripsi, gambar_url, icon |
| `aduan` | Complaint system | nomor_aduan, nama, email, telepon, nik, judul, kategori, lokasi, status, tanggapan |
| `kritik_saran` | Kritik dan saran | nama, email, telepon, subjek, kategori, isi, is_read, is_responded |
| `program_kerja` | Work programs | judul, kategori, tahun, target, realiasi, anggaran, icon, status, aktif |
| `agenda` | Village events | judul, deskripsi, tanggal_mulai, tanggal_selesai, waktu, lokasi, icon, status |
| `lokasi_rtrw` | RT/RW locations | jenis, rw, rt, nama_ketua, wilayah, alamat, latitude, longitude |

---

## Routes Architecture

### Blueprint Registration (app.py)
```python
from routes import public_bp, admin_bp, admin_rtrw_bp
app.register_blueprint(public_bp)     # Public routes: /, /berita, /login, dll
app.register_blueprint(admin_bp)      # Admin routes: /admin/*
app.register_blueprint(admin_rtrw_bp) # RT/RW: /admin/rtrw/*
```

### Public Routes (public_bp, prefix: /)

| Route | Template | Description |
|-------|---------|-------------|
| `/` | index.html | Homepage, berita carousel, potensi, pengumuman |
| `/login` | login.html | Unified login (admin/dinas tabs) |
| `/logout` | - | Clear session and redirect |
| `/berita` | berita.html | News listing with pagination |
| `/berita/<id>` | detail_berita.html | News detail + comments |
| `/sejarah` | sejarah.html | Village history timeline |
| `/info-kependudukan` | info_kependimento.html | Demographics with charts |
| `/struktur` | struktur.html | Village organization chart |
| `/struktur/<id>` | struktur_detail.html | Person detail page |
| `/galeri` | galeri.html | Photo gallery |
| `/kontak` | kontak.html | Contact info |
| `/pengumuman` | pengumuman.html | Announcements listing |
| `/transparansi` | transparansi.html | APBDes transparency |
| `/peta-interaktif` | peta_interaktif.html | Interactive map with UMKM markers |
| `/page/<slug>` | page.html | Dynamic pages |
| `/aduan` | aduan.html | Complaint form |
| `/aduan/cek` | cek_aduan.html | Check complaint status |
| `/kritik-saran` | kritik_saran.html | Kritik dan saran form |
| `/program-kerja` | program_kerja.html | Work programs listing |
| `/agenda` | agenda.html | Village agenda/calendar |
| `/api/berita` | - | JSON: all news |
| `/api/berita/<id>/komentar` | - | GET/POST/DELETE comments |
| `/api/umkm/geojson` | - | GeoJSON for interactive map |
| `/api/kritik-saran` | - | POST kritik/saran (JSON) |

### Admin Routes (admin_bp, prefix: /admin)

| Route | Template | Description |
|-------|---------|-------------|
| `/admin/login` | - | Redirect to unified login |
| `/admin/logout` | - | Admin logout |
| `/admin/dashboard` | admin/dashboard.html | Stats overview |
| `/admin/config` | admin/config.html | Website settings |
| `/admin/settings` | admin/settings.html | Admin account settings |
| `/admin/accounts` | admin/account_center.html | All users management |
| `/admin/accounts/user/<id>` | admin/account_detail.html | User edit/detail |
| `/admin/accounts/create` | admin/account_create.html | Create admin/dinas account |
| `/admin/accounts/user/delete/<id>` | - | Delete user |
| `/admin/berita/add` | admin/add_berita.html | Create news |
| `/admin/berita/edit/<id>` | admin/edit_berita.html | Edit news |
| `/admin/berita/delete/<id>` | - | Delete news |
| `/admin/galeri` | admin/galeri.html | Photo management |
| `/admin/galeri/add` | admin/add_galeri.html | Add photo |
| `/admin/galeri/edit/<id>` | admin/edit_galeri.html | Edit photo |
| `/admin/galeri/delete/<id>` | - | Delete photo |
| `/admin/galeri/toggle/<id>` | - | Toggle photo status |
| `/admin/pages` | admin/pages.html | Dynamic pages CRUD |
| `/admin/pages/add` | admin/add_page.html | Add page |
| `/admin/pages/edit/<id>` | admin/edit_page.html | Edit page |
| `/admin/pages/delete/<id>` | - | Delete page |
| `/admin/pages/toggle/<id>` | - | Toggle page status |
| `/admin/sejarah` | admin/sejarah.html | Village history management |
| `/admin/sejarah/add` | admin/add_sejarah.html | Add history entry |
| `/admin/sejarah/edit/<id>` | admin/edit_sejarah.html | Edit history entry |
| `/admin/sejarah/delete/<id>` | - | Delete history entry |
| `/admin/sejarah/toggle/<id>` | - | Toggle entry status |
| `/admin/struktur` | admin/struktur.html | Organization structure CRUD |
| `/admin/struktur/add` | admin/add_struktur.html | Add structure member |
| `/admin/struktur/edit/<id>` | admin/edit_struktur.html | Edit structure member |
| `/admin/struktur/delete/<id>` | - | Delete structure member |
| `/admin/struktur/toggle/<id>` | - | Toggle member status |
| `/admin/struktur/import` | - | Batch import from CSV |
| `/admin/struktur/export` | - | Export all data to CSV |
| `/admin/struktur/template` | - | Download CSV template |
| `/admin/umkm` | admin/umkm.html | UMKM management |
| `/admin/umkm/add` | admin/add_umkm.html | Add UMKM |
| `/admin/umkm/edit/<id>` | admin/edit_umkm.html | Edit UMKM |
| `/admin/umkm/delete/<id>` | - | Delete UMKM |
| `/admin/umkm/toggle/<id>` | - | Toggle UMKM status |
| `/admin/umkm/parse-location` | - | Parse Google Maps URL to coordinates |
| `/admin/potensi` | admin/potensi.html | Village potentials CRUD |
| `/admin/potensi/add` | admin/add_potensi.html | Add potential |
| `/admin/potensi/edit/<id>` | admin/edit_potensi.html | Edit potential |
| `/admin/potensi/delete/<id>` | - | Delete potential |
| `/admin/potensi/toggle/<id>` | - | Toggle potential status |
| `/admin/kependudukan` | admin/kependudukan.html | Demographics management |
| `/admin/pengumuman` | admin/pengumuman.html | Announcements CRUD |
| `/admin/pengumuman/add` | admin/add_pengumuman.html | Add announcement |
| `/admin/pengumuman/edit/<id>` | admin/edit_pengumuman.html | Edit announcement |
| `/admin/pengumuman/delete/<id>` | - | Delete announcement |
| `/admin/pengumuman/toggle/<id>` | - | Toggle announcement status |
| `/admin/apbdes` | admin/apbdes.html | Budget management |
| `/admin/apbdes/add` | admin/add_apbdes.html | Add budget item |
| `/admin/apbdes/edit/<id>` | admin/edit_apbdes.html | Edit budget item |
| `/admin/apbdes/delete/<id>` | - | Delete budget item |
| `/admin/kritik-saran` | admin/kritik_saran.html | Kritik dan saran management |
| `/admin/kritik-saran/read/<id>` | - | Mark as read |
| `/admin/kritik-saran/delete/<id>` | - | Delete kritik/saran |
| `/admin/aduan` | admin/aduan.html | Complaint management |
| `/admin/aduan/<id>` | admin/aduan_detail.html | Complaint detail + response |
| `/admin/aduan/delete/<id>` | - | Delete complaint |
| `/admin/program-kerja` | admin/program_kerja.html | Work programs management |
| `/admin/program-kerja/add` | admin/add_program_kerja.html | Add work program |
| `/admin/program-kerja/edit/<id>` | admin/edit_program_kerja.html | Edit work program |
| `/admin/program-kerja/delete/<id>` | - | Delete work program |
| `/admin/program-kerja/toggle/<id>` | - | Toggle work program status |
| `/admin/agenda` | admin/agenda.html | Agenda management |
| `/admin/agenda/add` | admin/add_agenda.html | Add agenda |
| `/admin/agenda/edit/<id>` | admin/edit_agenda.html | Edit agenda |
| `/admin/agenda/delete/<id>` | - | Delete agenda |
| `/admin/agenda/toggle/<id>` | - | Toggle agenda status |

### RT/RW Routes (admin_rtrw_bp, prefix: /admin/rtrw)

| Route | Template | Description |
|-------|---------|-------------|
| `/admin/rtrw/` | admin/lokasi_rtrw.html | List all RT/RW locations |
| `/admin/rtrw/add` | admin/add_lokasi_rtrw.html | Add RT/RW location |
| `/admin/rtrw/edit/<id>` | admin/edit_lokasi_rtrw.html | Edit RT/RW location |
| `/admin/rtrw/delete/<id>` | - | Delete RT/RW location |
| `/admin/rtrw/toggle/<id>` | - | Toggle RT/RW status |
| `/admin/rtrw/api/geojson` | - | Get all locations as GeoJSON |

---

## Models Reference

### Session Pattern
```python
session.get('user_id')
session.get('user_role')      # 'admin' | 'dinas' | 'penduduk'
session.get('user_nama')
session.get('user_nik')
session.get('user_logged_in') # True/False
```

### Auth Helpers
```python
from models import (
    verify_user,           # (nik, password) -> user or None
    get_user_by_id,        # (id) -> dict or None
    get_user_by_username,  # (username) -> dict or None  # for admin
    get_user_by_nip,       # (nip) -> dict or None       # for dinas
)
```

### Auth Decorators (from errors.py)
```python
@admin_required        # admin only
@dinas_required        # admin OR dinas
@login_required        # any logged-in user
@require_role(*roles) # specific roles
```

### User Management
```python
register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path, kk_path)
get_pending_users()
get_all_warga()
get_all_warga_approved()
get_all_users()                      # all admin/dinas/penduduk
get_user_stats()                     # returns {total, by_role, by_status}
update_user_data(user_id, data)
update_user_role(user_id, new_role, updated_by)
update_user_password(user_id, new_password)
delete_user_account(user_id)
create_staff_account(login_id, nama_lengkap, password, role)  # admin/dinas only
```

### News Management
```python
get_all_berita()
get_berita_by_id(id)
add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan)
update_berita(...)
delete_berita(id)
```

### Sejarah Desa
```python
get_all_sejarah(aktif=None)
get_sejarah_by_id(id)
add_sejarah(judul, sub_judul, konten, kategori, tahun_dari, tahun_sampai, gambar_url, ...)
update_sejarah(id, ...)
delete_sejarah(id)
toggle_sejarah_aktif(id)
```

### Galeri
```python
get_all_galeri(aktif=None)
get_galeri_by_id(id)
add_galeri(judul, gambar_url, deskripsi, kategori, gambar_alt)
update_galeri(id, ...)
delete_galeri(id)
toggle_galeri_aktif(id)
```

### Pages
```python
get_all_pages()          # active only
get_all_pages_admin()    # all including inactive
get_page_by_slug(slug)
get_page_by_id(id)
add_page(title, slug, content, icon)
update_page(id, ...)
delete_page(id)
toggle_page_active(id)
```

### Komentar
```python
get_komentar_by_berita(berita_id)     # flat list
build_comment_tree(flat_comments)    # nested tree for rendering
create_komentar(berita_id, konten, nama_pengirim, parent_id, user_id)
delete_komentar(komentar_id)
get_komentar_by_id(id)
count_komentar_by_berita(berita_id)
```

### Struktur Organisasi
```python
get_all_struktur(aktif=None)
get_struktur_by_kategori(kategori, aktif=None)
get_struktur_by_id(id)
add_struktur(kategori, nama, jabatan, deskripsi, nik, alamat, dusun, rt, rw, ...)
update_struktur(id, ...)
delete_struktur(id)
toggle_struktur_aktif(id)
batch_import_struktur(csv_data)  # Batch import dari CSV string
```

### Batch Import Struktur CSV
```python
# CSV format:
kategori,nama,jabatan,nik,alamat,dusun,rt,rw,telepon,email,status,aktif
perangkat,Moh. Baequni,Kepala Desa,,,,,001,001,,,Aktif,1
rw,Wawan Setiawan,Ketua RW 01,,Jl. Rw 01,Kedungwaru,001,001,,,Aktif,1
rt,Joko Pranowo,Ketua RT 01 RW 01,,Jl. Rt 01,Kedungwaru,001,001,,,Aktif,1

# Kategori valid: perangkat, bpd, pkk, karang_taruna, rt, rw
# Routes: /admin/struktur/import, /admin/struktur/export, /admin/struktur/template
```

### UMKM
```python
get_all_umkm(aktif=None, kategori=None)
get_umkm_by_id(id)
add_umkm(nama, kategori, deskripsi, pemiliki_nama, pemiliki_kontak, alamat, dusun, ...)
update_umkm(id, ...)
delete_umkm(id)
toggle_umkm_aktif(id)
get_umkm_for_geojson(aktif=1)  # returns GeoJSON FeatureCollection
```

### UMKM Google Maps Parser
```python
# POST /admin/umkm/parse-location
# Body: {"maps_url": "https://maps.google.com/..."}
# Response: {"success": true, "latitude": -7.7004, "longitude": 109.6432, "nama": "Toko Kita"}
#
# Supported URL formats:
# - @lat,lng format: https://maps.google.com/@-7.7004,109.6432,15z
# - place format: https://maps.google.com/place/Toko+Kita/@...
# - query format: https://maps.google.com?q=-7.7004,109.6432
# - Short URLs: https://maps.app.goo.gl/... (auto-resolved)
```

### Struktur Foto Upload
```python
# Both add_struktur and edit_struktur routes support:
# - foto_file: Upload file (multipart/form-data)
# - foto_url: External URL
# Priority: foto_file > foto_url
# Upload path: static/uploads/struktur/
```

### Kependudukan
```python
get_all_kependudukan()
update_kependudukan(kategori, label, jumlah, satuan, tahun)
```

### Potensi Desa
```python
get_all_potensi()
get_potensi_by_id(id)
add_potensi(nama, kategori, deskripsi, gambar_url, icon)
update_potensi(id, ...)
delete_potensi(id)
toggle_potensi_aktif(id)
```

### APBDes
```python
get_apbdes_by_tahun(tahun)
get_apbdes_summary(tahun)
get_apbdes_by_id(id)
add_apbdes_item(tahun, jenis, nama, jumlah, icon, deskripsi)
update_apbdes_item(id, ...)
delete_apbdes_item(id)
save_apbdes_summary(tahun, total_pendapatan, total_belanja, pembiayaan_net)
get_available_tahun()
```

### Kritik dan Saran
```python
get_all_kritik_saran(include_read=False)
get_kritik_saran_stats()
mark_kritik_saran_read(ks_id)
delete_kritik_saran(ks_id)
add_kritik_saran(nama, subjek, isi, email=None, telepon=None, kategori='kritik')
```

### Lokasi RT/RW
```python
get_all_lokasi_rtrw()
get_lokasi_rtrw_by_id(id)
add_lokasi_rtrw(jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude)
update_lokasi_rtrw(id, jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif)
delete_lokasi_rtrw(id)
toggle_lokasi_rtrw_aktif(id)
get_lokasi_rtrw_geojson()  # Returns GeoJSON FeatureCollection
```

### Config
```python
get_config(key, default)
get_all_config()               # Returns dict of all config
update_config(key, value)
get_desa_info()               # Returns {nama, tagline, deskripsi, jumlah_dusun, ...}
```

### Aduan (Complaints)
```python
get_all_aduan(aktif=None, status=None)
get_aduan_by_id(aduan_id)
get_aduan_by_nomor(nomor_aduan)
add_aduan(nama, judul, deskripsi, kategori, email, telepon, nik, ...)
update_aduan(aduan_id, judul, deskripsi, kategori, lokasi, status, prioritas, catatan)
delete_aduan(aduan_id)
respond_aduan(aduan_id, tanggapan, responded_by)
get_aduan_stats()
```

### Program Kerja (Work Programs)
```python
get_all_program_kerja(aktif=None, tahun=None)
get_program_kerja_by_id(program_id)
add_program_kerja(judul, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status)
update_program_kerja(program_id, judul, deskripsi, kategori, tahun, target, realiasi, ...)
delete_program_kerja(program_id)
toggle_program_kerja_aktif(program_id)
```

### Agenda
```python
get_all_agenda(aktif=None, status=None, tahun=None)
get_agenda_by_id(agenda_id)
add_agenda(judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu, lokasi, icon, ...)
update_agenda(agenda_id, judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, ...)
delete_agenda(agenda_id)
toggle_agenda_aktif(agenda_id)
```

---

## Roles

| Role | Login ID | Password | Can Do |
|------|----------|----------|--------|
| `admin` | `admin` | `adminkedungwinangun` | Full admin panel access |
| `admin` | `admin001` | `adminadmin` | Full admin panel access |
| `dinas` | `199001012020011001` | `dinas123` | Verify warga, approve letters, admin panel |
| `penduduk` | NIK (16 digits) | self-set | Register, submit letters |

### Role Permissions

| Feature | Guest | Penduduk | Dinas | Admin |
|---------|:-----:|:--------:|:-----:|:-----:|
| View Homepage | YES | YES | YES | YES |
| View Berita | YES | YES | YES | YES |
| View Galeri | YES | YES | YES | YES |
| View Kontak | YES | YES | YES | YES |
| Submit Aduan | YES | YES | YES | YES |
| Submit Kritik/Saran | YES | YES | YES | YES |
| Register | NO | YES | NO | NO |
| Submit Letter | NO | YES | NO | NO |
| View Status Letter | NO | YES | YES | NO |
| Approve Registration | NO | NO | YES | NO |
| Approve/Reject Letter | NO | NO | YES | NO |
| View All Warga | NO | NO | YES | NO |
| Manage Berita | NO | NO | NO | YES |
| Manage Galeri | NO | NO | NO | YES |
| Manage Config | NO | NO | NO | YES |
| Manage Account | NO | NO | NO | YES |

---

## Village Constants (config.py)

### Nav Links
```python
NAV_LINKS = [
    {"label": "Beranda", "href": "/", "active": True},
    {"label": "Sejarah", "href": "/sejarah", "active": False},
    {"label": "Kependudukan", "href": "/info-kependudukan", "active": False},
    {"label": "Pengumuman", "href": "/pengumuman", "active": False},
    {"label": "Berita", "href": "/berita", "active": False},
    {"label": "Galeri", "href": "/galeri", "active": False},
    {"label": "Kontak", "href": "/kontak", "active": False},
    {"label": "Lainnya", "href": "#", "active": False, "is_dropdown": True},
]
```

### 6 Villages (Dusun)
```python
DUSUN_DATA = [
    {"nama": "Dusun Kedungwaru", "delay": "0.05s"},
    {"nama": "Dusun Perna", "delay": "0.12s"},
    {"nama": "Dusun Sasak", "delay": "0.19s"},
    {"nama": "Dusun Entak", "delay": "0.26s"},
    {"nama": "Dusun Grewing", "delay": "0.33s"},
    {"nama": "Dusun Pedana", "delay": "0.40s"},
]
```

### Map Embed URL
```python
MAPS_EMBED_URL = "https://maps.google.com/maps?q=Kedungwinangun,+Klirong,+Kebumen&t=&z=13&ie=UTF8&iwloc=&output=embed"
```

### Default Map Coordinates (Interaktif Peta)
```python
MAP_CENTER_LAT = -7.7004775
MAP_CENTER_LNG = 109.6432848
MAP_DEFAULT_ZOOM = 15
```

---

## Struktur Organisasi Categories
```python
PERANGKAT_DESA = ["perangkat", "bpd", "pkk", "karang_taruna", "rt", "rw"]

kategori_labels = {
    'perangkat': 'Perangkat Desa',
    'bpd': 'BPD',
    'pkk': 'PKK',
    'karang_taruna': 'Karang Taruna',
    'rt': 'RT',
    'rw': 'RW',
}
```

---

## UMKM Categories
```python
kategori_labels = {
    'makanan': 'Makanan',
    'minuman': 'Minuman',
    'kerajinan': 'Kerajinan',
    'jasa': 'Jasa',
    'pertanian': 'Pertanian',
    'peternakan': 'Peternakan',
    'perikanan': 'Perikanan',
    'umum': 'Umum',
}
```

---

## APBDes Jenis
```python
APBDES_JENIS = ['pendapatan', 'belanja', 'pembiayaan']
```

## Aduan Categories
```python
ADUAN_KATEGORI = {
    'infrastruktur': 'Infrastruktur',
    'lingkungan': 'Lingkungan',
    'kesehatan': 'Kesehatan',
    'pendidikan': 'Pendidikan',
    'keamanan': 'Keamanan',
    'pelecehan': 'Pelecehan/Kekerasan',
    'korupsi': 'Korupsi',
    'lainnya': 'Lainnya',
}

ADUAN_STATUS = {
    'menunggu': 'Menunggu',
    'diterima': 'Diterima',
    'dalam_proses': 'Dalam Proses',
    'selesai': 'Selesai',
    'ditolak': 'Ditolak',
}
```

## Kritik Saran Categories
```python
KRITIK_KATEGORI = {
    'kritik': 'Kritik',
    'saran': 'Saran',
    'pertanyaan': 'Pertanyaan',
    'lainnya': 'Lainnya',
}
```

## Program Kerja Status
```python
PROGRAM_STATUS = {
    'rencana': 'Rencana',
    'berlangsung': 'Berlangsung',
    'selesai': 'Selesai',
}
```

## Agenda Status
```python
AGENDA_STATUS = {
    'akan_datang': 'Akan Datang',
    'sedang_berlangsung': 'Sedang Berlangsung',
    'selesai': 'Selesai',
    'dibatalkan': 'Dibatalkan',
}

AGENDA_KATEGORI = {
    'umum': 'Umum',
    'kegiatan': 'Kegiatan',
    'rapat': 'Rapat',
    'musyawarah': 'Musyawarah',
    'pembangunan': 'Pembangunan',
    'kesehatan': 'Kesehatan',
    'pendidikan': 'Pendidikan',
}
```

---

## API Reference

### Chatbot (Server-side OpenRouter)
```
POST /api/chat
Body: {"messages": [{"role": "user", "content": "..."}], "model": "..."}
Response: {"text": "...", "model": "..."}
```

Models tried in order:
1. `nvidia/nemotron-3-ultra-550b-a55b:free`
2. `google/gemma-4-26b-a4b-it:free`
3. `openrouter/free`

### Health Check
```
GET /health
Response: {"status": "healthy", "app": "Desa Kedungwinangun"}
```

### Comment API
```
GET /api/berita/<id>/komentar
POST /api/berita/<id>/komentar  (JSON: {konten, parent_id?, nama_pengirim?})
DELETE /api/berita/<id>/komentar/<komentar_id>
```

### UMKM GeoJSON API
```
GET /api/umkm/geojson
Response: GeoJSON FeatureCollection
```

### Kritik Saran API
```
POST /api/kritik-saran  (JSON: {nama, email?, telepon?, subjek, kategori, isi})
```

---

## Environment Variables

```env
OPENROUTER_API_KEY=sk-or-v1-...    # Required for chatbot
SECRET_KEY=...                      # Flask session secret
DATABASE_NAME=database.db
PORT=5209
```

---

## Common Patterns

### Flash Messages
```python
from flask import flash
flash('Message text', 'success')   # Green
flash('Message text', 'error')     # Red
flash('Message text', 'info')      # Blue
flash('Message text', 'warning')   # Yellow
```

### JSON Response
```python
from flask import jsonify
return jsonify({"success": True, "data": ...})
return jsonify({"success": False, "error": "message"}), 400
```

### File Upload
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Save uploaded file
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and allowed_image(file.filename):
        # Use save_uploaded_file() from admin.py or implement custom
        pass
```

### Error Handlers (errors.py)
```python
from errors import (
    AppError, DatabaseError, ValidationError, NotFoundError, UnauthorizedError, ForbiddenError,
    flash_error, json_error_response, json_success_response,
    admin_required, dinas_required, login_required, require_role,
    validate_required, validate_email, validate_password, validate_phone,
    render_error_page, safe_handler,
)
```

---

## Key Files to Know

| File | Size | Purpose |
|------|------|---------|
| `app.py` | 454 lines | Entry point, blueprints, chatbot endpoint, error handlers |
| `config.py` | 202 lines | Config class, NAV_LINKS, DUSUN_DATA, SQL_SCHEMA, DEFAULT_USERS |
| `models.py` | 2592 lines | ALL database operations - look here first |
| `database.py` | - | Database error handling, safe DB operations |
| `errors.py` | 873 lines | Custom exceptions, decorators, validation helpers |
| `routes/__init__.py` | 60 lines | Blueprint exports |
| `routes/public.py` | 50,852 bytes | Legacy: monolithic public routes |
| `routes/admin.py` | 102,408 bytes | Legacy: monolithic admin routes |
| `templates/base.html` | 33,713 bytes | Main layout with navbar, footer, dark mode |
| `templates/index.html` | 68,635 bytes | Homepage |
| `static/styles.css` | 846 lines | Main CSS |

---

## Website Config Keys (DEFAULT_CONFIG)

```python
# Website Info
website_nama, website_tagline, website_deskripsi, website_meta_description

# Berita Settings
berita_tampil_di_beranda, berita_unggulan_tampil, berita_tampil_di_halaman
berita_tampilkan_views, berita_tampilkan_tanggal, berita_carousel_stacks

# Homepage Sections
tampilkan_maps, tampilkan_statistik, tampilkan_daftar_dusun, tampilkan_hero

# Kontak
kontak_whatsapp, kontak_telepon, kontak_email, alamat_desa

# Sosial Media
sosial_facebook, sosial_instagram, sosial_twitter

# Footer
footer_copyright
```

---

## GeoJSON Layers

### UMKM GeoJSON
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "id": 1,
        "nama": "Toko Kelontong",
        "kategori": "makanan",
        "alamat": "Jl. Desa No. 1",
        "pemiliki": "Budi"
      }
    }
  ]
}
```

### RT/RW GeoJSON
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "id": 1,
        "jenis": "RT",
        "rw": "01",
        "rt": "01",
        "nama_ketua": "Joko",
        "alamat": "Jl. RT 01"
      }
    }
  ]
}
```

---

## Legacy Files (Maintained for Compatibility)

The following files are maintained but routes have been refactored into modular files:

- `routes/public.py` - Original monolithic public routes (still used by app.py)
- `routes/admin.py` - Original monolithic admin routes (still used by app.py)

New modular files provide the same functionality in smaller, more maintainable chunks.

---

## UI Design System

### Color Palette
```
Primary:   #155C1B (Forest Green)
Accent:    #73AA0F (Light Green)
Dark:      #0f3d14 (Darker Green)
Muted:     #5B8A4E (Muted Green)
```

### Typography
```
Font: Inter (Google Fonts)
Weights: 400, 500, 600, 700, 800
```

### Dark Mode
Dark mode is implemented in `templates/base.html` with Tailwind CSS `dark:` classes and custom CSS overrides.

---

## UI Plan Update Reference

For UI redesign guidelines, see `ui_plan_update.md` which contains:

1. **Design Foundation** - CSS Variables, Typography Scale, Spacing System
2. **Layout System** - Centric Grid, Container Max-Widths, Page Structure Patterns
3. **Component Library** - Buttons, Cards, Forms, Navigation, Alerts, Tables
4. **Page Specifications** - Homepage, Berita, Galeri, Struktur, Aduan, Program Kerja, Transparansi
5. **Admin Panel** - Dashboard, Form Pages, CRUD Pages
6. **Dark Mode** - Color Overrides
7. **Responsive Breakpoints** - Grid Columns by Breakpoint
8. **Animations** - Allowed Animations, Transition Guidelines
9. **Emoji Guide** - Emoji Replacement Guide
10. **Accessibility** - Contrast, Focus States, Semantic HTML
11. **Implementation Checklist** - Phases 1-6

---

*Last updated: 9 Juli 2026*
