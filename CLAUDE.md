# CLAUDE.md - Project Reference

## Project Identity

**Name**: Desa Kedungwinangun AIO  
**Type**: Flask Web Application (Desa Digital / E-Government)  
**Location**: c:/Productivity/Coding/Projects/kedungwinangunAIO/  
**Port**: 5209 (default)

---

## Quick Start

```bash
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
Frontend:   HTML5 + Tailwind CSS 3.x + Vanilla JS
PDF:        ReportLab 4.0+
AI:         OpenRouter API (server-side)
Auth:       Werkzeug PBKDF2 hashing
```

### Directory Structure
```
├── app.py              # Flask app factory + blueprints registration
├── config.py           # Config class + DEFAULT_CONFIG dict
├── models.py           # All DB operations (get_db_connection, helpers)
├── database.py          # Database error handling + safe DB operations
├── errors.py            # Error handlers, decorators, validation helpers
├── pdf_generator.py    # PDF generation (placeholder - not implemented)
├── routes/
│   ├── __init__.py     # Blueprint exports
│   ├── public.py       # Blueprint 'public_bp' - website publik
│   └── admin.py        # Blueprint 'admin_bp' - /admin/*
├── templates/          # Jinja2 templates
│   ├── index.html, berita.html, galeri.html, kontak.html
│   ├── admin/          # 27 admin templates
│   ├── partials/       # Navbar, footer, chatbot, dark-mode
│   └── user/           # User templates
├── static/
│   ├── styles.css
│   ├── dark-mode.js
│   ├── images/
│   └── data/geojson    # Peta interaktif GeoJSON
└── uploads/            # User uploads (KTP, KK, berita, galeri, dll)
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

### Tables
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | All users (admin/dinas/penduduk) | id, nik, username, nip, nama_lengkap, password_hash, role, status |
| `berita` | News articles | judul, excerpt, kategori, badge_class, gambar_url, video_url, facebook_auto_post, unggulan |
| `config` | Website config | key, value |
| `galeri` | Photos | judul, deskripsi, kategori, gambar_url, aktif |
| `pages` | Dynamic pages | title, slug, content, icon, order_num, active |
| `komentar` | News comments | berita_id, parent_id, user_id, nama_pengirim, konten |
| `struktur_organisasi` | Village org structure | kategori, nama, jabatan, nik, alamat, telepon, foto_url, status |
| `sejarah_desa` | Village history timeline | judul, sub_judul, konten, tahun_dari, tahun_sampai, gambar_url |
| `pengumuman` | Announcements | judul, isi, kategori, is_penting, lampiran, author, aktif |
| `apbdes` | Budget items | tahun, jenis, nama, icon, jumlah, deskripsi |
| `apbdes_summary` | Budget summary | tahun, total_pendapatan, total_belanja, pembiayaan_net |
| `umkm` | UMKM listings | nama, kategori, pemiliki_nama, alamat, latitude, longitude, foto_url |
| `kependudukan` | Demographics data | kategori, label, jumlah, satuan, tahun |
| `potensi_desa` | Village potentials | nama, kategori, deskripsi, gambar_url, icon |
| `permohonan_acc` | Registration approvals | user_id, status, created_at |

---

## Routes Reference

### Pattern: Blueprint Decorators

```python
# Protected route example
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    user = get_user_by_id(session.get('user_id'))
    return render_template("admin/dashboard.html", user=user)
```

### Public Routes (public_bp)
| Route | Template | Description |
|-------|---------|-------------|
| `/` | index.html | Homepage, berita carousel, potensi, pengumuman |
| `/login` | login.html | Unified login (admin/dinas tabs) |
| `/logout` | - | Clear session and redirect |
| `/berita` | berita.html | News listing with pagination |
| `/berita/<id>` | detail_berita.html | News detail + comments |
| `/sejarah` | sejarah.html | Village history timeline |
| `/info-kependudukan` | info_kependudukan.html | Demographics with charts |
| `/struktur` | struktur.html | Village organization chart |
| `/struktur/<id>` | struktur_detail.html | Person detail page |
| `/galeri` | galeri.html | Photo gallery |
| `/kontak` | kontak.html | Contact info |
| `/pengumuman` | pengumuman.html | Announcements listing |
| `/transparansi` | transparansi.html | APBDes transparency |
| `/peta-interaktif` | peta_interaktif.html | Interactive map with UMKM markers |
| `/page/<slug>` | page.html | Dynamic pages |
| `/api/berita` | - | JSON: all news |
| `/api/berita/<id>/komentar` | - | GET/POST/DELETE comments |
| `/api/umkm/geojson` | - | GeoJSON for interactive map |

### Admin Routes (admin_bp, prefix: /admin)
| Route | Template | Description |
|-------|---------|-------------|
| `/dashboard` | admin/dashboard.html | Stats overview |
| `/login` | - | Redirect to unified login |
| `/logout` | - | Admin logout |
| `/config` | admin/config.html | Website settings |
| `/settings` | admin/settings.html | Admin account settings |
| `/accounts` | admin/account_center.html | All users management |
| `/accounts/user/<id>` | admin/account_detail.html | User edit/detail |
| `/accounts/create` | admin/account_create.html | Create admin/dinas account |
| `/berita/add` | admin/add_berita.html | Create news |
| `/berita/edit/<id>` | admin/edit_berita.html | Edit news |
| `/berita/delete/<id>` | - | Delete news |
| `/galeri` | admin/galeri.html | Photo management |
| `/galeri/add` | admin/add_galeri.html | Add photo |
| `/galeri/edit/<id>` | admin/edit_galeri.html | Edit photo |
| `/galeri/delete/<id>` | - | Delete photo |
| `/galeri/toggle/<id>` | - | Toggle photo status |
| `/pages` | admin/pages.html | Dynamic pages CRUD |
| `/pages/add` | admin/add_page.html | Add page |
| `/pages/edit/<id>` | admin/edit_page.html | Edit page |
| `/pages/delete/<id>` | - | Delete page |
| `/pages/toggle/<id>` | - | Toggle page status |
| `/struktur` | admin/struktur.html | Organization structure CRUD |
| `/struktur/add` | admin/add_struktur.html | Add structure member |
| `/struktur/edit/<id>` | admin/edit_struktur.html | Edit structure member |
| `/struktur/delete/<id>` | - | Delete structure member |
| `/struktur/toggle/<id>` | - | Toggle member status |
| `/sejarah` | admin/sejarah.html | Village history management |
| `/sejarah/add` | admin/add_sejarah.html | Add history entry |
| `/sejarah/edit/<id>` | admin/edit_sejarah.html | Edit history entry |
| `/sejarah/delete/<id>` | - | Delete history entry |
| `/sejarah/toggle/<id>` | - | Toggle entry status |
| `/pengumuman` | admin/pengumuman.html | Announcements CRUD |
| `/pengumuman/add` | admin/add_pengumuman.html | Add announcement |
| `/pengumuman/edit/<id>` | admin/edit_pengumuman.html | Edit announcement |
| `/pengumuman/delete/<id>` | - | Delete announcement |
| `/pengumuman/toggle/<id>` | - | Toggle announcement status |
| `/apbdes` | admin/apbdes.html | Budget management |
| `/apbdes/add` | admin/add_apbdes.html | Add budget item |
| `/apbdes/edit/<id>` | admin/edit_apbdes.html | Edit budget item |
| `/apbdes/delete/<id>` | - | Delete budget item |
| `/umkm` | admin/umkm.html | UMKM management |
| `/umkm/add` | admin/add_umkm.html | Add UMKM |
| `/umkm/edit/<id>` | admin/edit_umkm.html | Edit UMKM |
| `/umkm/delete/<id>` | - | Delete UMKM |
| `/umkm/toggle/<id>` | - | Toggle UMKM status |
| `/kependudukan` | admin/kependudukan.html | Demographics management |
| `/potensi` | admin/potensi.html | Village potentials CRUD |
| `/potensi/add` | admin/add_potensi.html | Add potential |
| `/potensi/edit/<id>` | admin/edit_potensi.html | Edit potential |
| `/potensi/delete/<id>` | - | Delete potential |
| `/potensi/toggle/<id>` | - | Toggle potential status |

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
@require_role(*roles)  # specific roles
```

### User Management
```python
register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path, kk_path)
get_pending_users()
get_all_warga()
get_all_warga_approved()
get_all_users()                      # all admin/dinas/penduduk
get_user_stats()                    # returns {total, by_role, by_status}
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

### Config
```python
get_config(key, default)
get_all_config()               # Returns dict of all config
update_config(key, value)
get_desa_info()               # Returns {nama, tagline, deskripsi, jumlah_dusun, ...}
```

---

## Struktur Organisasi Categories
```python
PERANGKAT_DESA = ["perangkat", "bpd", "pkk", "karang_taruna", "rt", "rw"]
```

---

## Village Constants (config.py)

### Nav Links
```python
NAV_LINKS = [
    {"label": "Beranda", "href": "/"},
    {"label": "Sejarah", "href": "/sejarah"},
    {"label": "Kependudukan", "href": "/info-kependudukan"},
    {"label": "Pengumuman", "href": "/pengumuman"},
    {"label": "Berita", "href": "/berita"},
    {"label": "Galeri", "href": "/galeri"},
    {"label": "Kontak", "href": "/kontak"},
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

### Default Users
```python
DEFAULT_USERS = [
    ('admin', 'Administrator', 'adminkedungwinangun', 'admin'),           # Admin login
    ('199001012020011001', 'Petugas Dinas', 'dinas123', 'dinas'),        # Dinas login (NIP)
]
```

### Map Embed URL
```python
MAPS_EMBED_URL = "https://maps.google.com/maps?q=Kedungwinangun,+Klirong,+Kebumen&t=&z=13&ie=UTF8&iwloc=&output=embed"
```

---

## Roles

| Role | Login ID | Password | Can Do |
|------|----------|----------|--------|
| `admin` | `admin` | `adminkedungwinangun` | Full admin panel access |
| `dinas` | `199001012020011001` | `dinas123` | Verify warga, approve letters, admin panel |
| `penduduk` | NIK (16 digits) | self-set | Register, submit letters |

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
    flash_error,               # Flash error message
    json_error_response,       # JSON error response
    json_success_response,     # JSON success response
    ValidationError,           # Custom exception
    NotFoundError,             # Custom exception
    safe_handler,              # Decorator with error handling
    validate_required,         # Validate required fields
    validate_email,            # Validate email format
    validate_phone,            # Validate Indonesian phone
)
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `app.py` | Entry point, blueprints, chatbot endpoint, error handlers |
| `config.py` | Config class, NAV_LINKS, DUSUN_DATA, SQL_SCHEMA, DEFAULT_USERS |
| `models.py` | ALL database operations - look here first |
| `database.py` | Database error handling, safe DB operations |
| `errors.py` | Custom exceptions, decorators, validation helpers |
| `routes/public.py` | Public website routes (login, berita, galeri, dll) |
| `routes/admin.py` | Admin panel routes (all CRUD operations) |

---

## UMKM Categories
```python
kategori_labels = {
    'makanan': '🍜 Makanan',
    'minuman': '🥤 Minuman',
    'kerajinan': '🎨 Kerajinan',
    'jasa': '🔧 Jasa',
    'pertanian': '🌾 Pertanian',
    'peternakan': '🐔 Peternakan',
    'perikanan': '🐟 Perkins',
    'umum': '🏪 Umum',
}
```

---

## APBDes Jenis
```python
APBDES_JENIS = ['pendapatan', 'belanja', 'pembiayaan']
```

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
