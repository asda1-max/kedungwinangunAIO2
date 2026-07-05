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
├── pdf_generator.py    # PDF generation per surat type
├── routes/
│   ├── public.py       # Blueprint 'public_bp' - website publik
│   ├── admin.py        # Blueprint 'admin_bp' - /admin/*
│   ├── user.py         # Blueprint 'user_bp' - warga
│   └── dinas.py        # Blueprint 'dinas_bp' - /dinas/*
├── templates/          # Jinja2 templates
│   ├── index.html, berita.html, galeri.html, kontak.html
│   ├── admin/          # 23 admin templates
│   ├── dinas/          # 7 dinas templates
│   └── user/           # 4 user templates
├── static/
│   ├── styles.css
│   └── data/geojson     # Peta interaktif
└── uploads/            # User uploads (KTP, KK)
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
| `users` | All users (admin/dinas/penduduk) | id, nik, nama_lengkap, password_hash, role, status |
| `permohonan_acc` | Registration approvals | user_id, status |
| `jenis_surat` | Letter types catalog | kode, nama, required_docs |
| `permohonan_surat` | Letter requests | user_id, jenis_surat_id, status, nomor_surat |
| `berita` | News articles | judul, excerpt, kategori, unggulan |
| `config` | Website config | key, value |
| `galeri` | Photos | judul, gambar_url, aktif |
| `pages` | Dynamic pages | title, slug, content |
| `komentar` | News comments | berita_id, parent_id, konten |
| `struktur_organisasi` | Village org structure | kategori, nama, jabatan |
| `pengumuman` | Announcements | judul, isi, is_penting |
| `apbdes` | Budget items | tahun, jenis, nama, jumlah |

---

## Routes Reference

### Pattern: Blueprint Decorators

```python
# Protected route example
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session.get('user_id'))
    return render_template("admin/dashboard.html", user=user)
```

### Public Routes (public_bp)
| Route | Template | Description |
|-------|---------|-------------|
| `/` | index.html | Homepage, berita carousel |
| `/login` | login.html | Unified login (admin/dinas/warga tabs) |
| `/berita` | berita.html | News listing |
| `/berita/<id>` | detail_berita.html | News detail + comments |
| `/layanan` | user/surat_permohonan.html | Submit letter request |
| `/galeri` | galeri.html | Photo gallery |
| `/kontak` | kontak.html | Contact info |
| `/pengumuman` | pengumuman.html | Announcements |
| `/struktur` | struktur.html | Village org chart |
| `/transparansi` | transparansi.html | APBDes transparency |
| `/peta-interaktif` | peta_interaktif.html | Interactive map |
| `/page/<slug>` | page.html | Dynamic pages |
| `/api/berita` | - | JSON: all news |
| `/api/chat` | - | POST: chatbot AI |
| `/api/berita/<id>/komentar` | - | GET/POST/DELETE comments |

### Admin Routes (admin_bp, prefix: /admin)
| Route | Template | Description |
|-------|---------|-------------|
| `/dashboard` | admin/dashboard.html | Stats |
| `/berita/add` | admin/add_berita.html | Create news |
| `/berita/edit/<id>` | admin/edit_berita.html | Edit news |
| `/config` | admin/config.html | Website settings |
| `/galeri` | admin/galeri.html | Photo management |
| `/pages` | admin/pages.html | Dynamic pages CRUD |
| `/struktur` | admin/struktur.html | Org structure CRUD |
| `/pengumuman` | admin/pengumuman.html | Announcements CRUD |
| `/apbdes` | admin/apbdes.html | Budget management |
| `/settings` | admin/settings.html | Admin account |

### User Routes (user_bp, no prefix)
| Route | Template | Description |
|-------|---------|-------------|
| `/register` | user/register.html | Registration form |
| `/dashboard` | user/dashboard.html | Letter history |
| `/surat/permohonan` | user/surat_permohonan.html | Submit request |

### Dinas Routes (dinas_bp, prefix: /dinas)
| Route | Template | Description |
|-------|---------|-------------|
| `/dashboard` | dinas/dashboard.html | Pending counts |
| `/users/pending` | dinas/pending_users.html | Pending registrations |
| `/users/all` | dinas/all_users.html | All warga |
| `/users/detail/<id>` | dinas/user_detail.html | Preview + docs |
| `/permohonan` | dinas/permohonan_list.html | All letter requests |
| `/permohonan/detail/<id>` | dinas/permohonan_detail.html | Request details |
| `/surat/generate-pdf/<id>` | - | Download PDF |

---

## Models Reference

### Session Pattern
```python
session.get('user_id')
session.get('user_role')      # 'admin' | 'dinas' | 'penduduk'
session.get('user_nama')
session.get('user_logged_in')  # True/False
```

### Auth Helpers
```python
from models import (
    verify_user,           # (nik, password) -> user or None
    get_user_by_nik,       # (nik) -> dict or None
    get_user_by_id,        # (id) -> dict or None
)
```

### Auth Decorators
```python
@login_required           # admin_bp - admin only
@dinas_required           # dinas_bp - admin OR dinas
# For user routes, check: session.get('user_role') == 'penduduk'
```

### User Management
```python
register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path, kk_path)
approve_user(user_id, processed_by)
reject_user(user_id, processed_by, catatan)
```

### Letter Management
```python
get_all_jenis_surat()                     # Active letter types
create_permohonan_surat(user_id, jenis_surat_id, data_json)  # data_json is JSON string
get_permohonan_surat_by_user(user_id)
get_all_permohonan_surat()
get_pending_permohonan_surat()
approve_permohonan_surat(permit_id, approved_by, nomor_surat, catatan)
reject_permohonan_surat(permit_id, processed_by, catatan)
```

### News Management
```python
get_all_berita()
get_berita_by_id(id)
add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan)
update_berita(id, ...)
delete_berita(id)
```

### Config
```python
get_config(key, default)
get_all_config()               # Returns dict of all config
update_config(key, value)
```

---

## Letter Types (Jenis Surat)

| Kode | Nama | Required Docs |
|------|------|---------------|
| SKU | Surat Keterangan Usaha | ktp,kk |
| SKTM | Surat Keterangan Tidak Mampu | ktp,kk,surat_keterangan_rt |
| SKCK | Surat Pengantar SKCK | ktp |
| DOMISILI | Surat Keterangan Domisili | ktp,kk |
| BELUM_NIKAH | Surat Keterangan Belum Menikah | ktp,kk,surat_keterangan_rt |
| LAHIR | Surat Keterangan Kelahiran | ktp_ayah,ktp_ibu,kk,surat_keterangan_bidan |
| MATI | Surat Keterangan Kematian | ktp_almarhum,kk,surat_keterangan_kades |

### PDF Generation
```python
from pdf_generator import generate_surat_pdf
# Signature: generate_surat_pdf(kode_surat, data, nomor_surat, tanggal_surat)
# Returns: BytesIO buffer
```

---

## Roles

| Role | Login Method | Can Do |
|------|-------------|--------|
| `admin` | NIK: ADMIN001, Pass: adminkedungwinangun | Website content management |
| `dinas` | NIK: DINAS001, Pass: dinas123 | Verify warga, approve letters |
| `penduduk` | NIK: 16 digits, Pass: self-set | Register, submit letters |

### Default Nav Links (config.py)
```python
NAV_LINKS = [
    {"label": "Beranda", "href": "/"},
    {"label": "Layanan Surat", "href": "/layanan"},
    {"label": "Pengumuman", "href": "/pengumuman"},
    {"label": "Berita", "href": "/berita"},
    {"label": "Kontak", "href": "/kontak"},
]
```

### Village Info (config.py)
```python
DUSUN_DATA = ["Kedungwaru", "Perna", "Sasak", "Entak", "Grewing", "Pedana"]
KADES = "Moh Baequni"
LOCATION = "Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, Jawa Tengah"
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
```

### Redirect with Next
```python
return redirect(url_for('user.register', next=url_for('public.layanan')))
```

### JSON Response
```python
from flask import jsonify
return jsonify({"success": True, "data": ...})
```

### File Upload
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Comment System
```python
get_komentar_by_berita(berita_id)     # Flat list
build_comment_tree(flat_comments)     # Nested tree
create_komentar(berita_id, konten, nama_pengirim, parent_id, user_id)
```

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `app.py` | Entry point, blueprints, chatbot endpoint |
| `config.py` | Config class, NAV_LINKS, DUSUN_DATA, SQL_SCHEMA |
| `models.py` | ALL database operations - look here first |
| `routes/public.py` | Public website routes |
| `routes/admin.py` | Admin panel routes |
| `routes/dinas.py` | Dinas verification routes |
| `routes/user.py` | Warga registration/login |
| `pdf_generator.py` | Letter PDF templates |

---

## Village Constants (config.py)

```python
# Default users
DEFAULT_USERS = [
    ('ADMIN001', 'Administrator', 'adminkedungwinangun', 'admin'),
    ('DINAS001', 'Petugas Dinas', 'dinas123', 'dinas'),
]

# Nav links shown in header
NAV_LINKS = [...]

# 6 villages (dusun)
DUSUN_DATA = [
    {"nama": "Dusun Kedungwaru", "delay": "0.05s"},
    {"nama": "Dusun Perna", "delay": "0.12s"},
    ...
]

# Maps embed URL
MAPS_EMBED_URL = "https://maps.google.com/maps?q=Kedungwinangun,+Klirong,+Kebumen..."
```
