# Desa Kedungwinangun AIO — Complete Codebase Map for AI

## 1. PROJECT OVERVIEW
Flask 3.0 + SQLite3 web app for Indonesian village (desa) digital services.
- Port: 5209
- Language: Indonesian (UI), English (code comments)
- Auth: Werkzeug PBKDF2 hashing, session-based
- Frontend: Tailwind CSS 3.x + Alpine.js + Vanilla JS
- AI Chatbot: OpenRouter API (server-side, API key in .env)
- Maps: Leaflet.js + GeoJSON layers
- PDF: ReportLab 4.0+
- No ORM — raw SQLite3 with `sqlite3.Row` (dict-like rows)

## 2. DIRECTORY TREE (Key Files Only)

```
kedungwinangunAIO/
├── app.py                          # 555 lines — Entry point, blueprints, chatbot, error handlers
├── config.py                       # 258 lines — Flask Config, DEFAULT_CONFIG, NAV_LINKS, DUSUN_DATA, SQL_SCHEMA
├── models.py                       # 2965 lines — ALL database CRUD functions (NO SQLAlchemy)
├── database.py                     # 557 lines — DB error handling, context managers, safe wrappers
├── errors.py                       # 873 lines — Custom exceptions, auth decorators, validators
├── fix_models.py                   # 37 lines — Scans models.py for SQL syntax bugs
├── testai.py                       # 16 lines — Anthropic SDK test script
├── requirements.txt                # Flask>=3.0, Werkzeug>=3.0, python-dotenv, reportlab, Pillow
├── .env                            # OPENROUTER_API_KEY
├── database.db                     # SQLite file
├── routes/
│   ├── __init__.py                 # 61 lines — Blueprint registry (legacy + modular)
│   ├── public.py                   # LEGACY monolithic public routes (53KB)
│   ├── admin.py                    # LEGACY monolithic admin routes (105KB)
│   ├── public_auth.py              # Login/logout with brute-force protection
│   ├── public_home.py              # Homepage / beranda
│   ├── public_berita.py            # News list, detail, comments API
│   ├── public_pages.py             # Galeri, kontak, kritik-saran, custom pages
│   ├── public_struktur.py          # Struktur organisasi, sejarah
│   ├── public_info.py              # Kependudukan, pengumuman, peta, transparansi
│   ├── public_aduan.py             # Aduan, program kerja, agenda, e-library
│   ├── admin_dashboard.py          # Dashboard, auth redirects
│   ├── admin_berita.py             # Berita CRUD
│   ├── admin_galeri.py             # Galeri CRUD + toggle
│   ├── admin_pages.py              # Config, pages, sejarah management
│   ├── admin_struktur.py           # Struktur CRUD + CSV import/export/template
│   ├── admin_umkm.py               # UMKM CRUD + Google Maps URL parser
│   ├── admin_potensi.py            # Potensi desa + kependudukan CRUD
│   ├── admin_pengumuman.py         # Pengumuman + APBDes CRUD
│   ├── admin_aduan.py              # Aduan, kritik-saran, program kerja, agenda CRUD
│   ├── admin_accounts.py           # Account center + settings
│   ├── admin_rtrw.py               # RT/RW locations CRUD (separate blueprint)
│   └── admin_ebook.py              # E-book CRUD (separate blueprint)
├── templates/
│   ├── base.html                   # Main layout (34KB) — Tailwind, Alpine, dark mode, Inter font
│   ├── index.html                  # Homepage (67KB) — standalone HTML (NOT extending base)
│   ├── berita.html, detail_berita.html
│   ├── galeri.html, kontak.html
│   ├── aduan.html, cek_aduan.html
│   ├── kritik_saran.html
│   ├── program_kerja.html, agenda.html
│   ├── transparansi.html, pengumuman.html
│   ├── info_kependudukan.html, peta_interaktif.html (53KB)
│   ├── sejarah.html, struktur.html, struktur_detail.html
│   ├── e_library.html, e_library_detail.html
│   ├── login.html, page.html, error.html
│   ├── admin/                       # 40+ admin templates
│   │   ├── base.html                # Admin layout (47KB)
│   │   ├── dashboard.html, config.html, settings.html
│   │   ├── account_center.html, account_detail.html, account_create.html
│   │   ├── berita.html, add_berita.html, edit_berita.html
│   │   ├── galeri.html, add_galeri.html, edit_galeri.html
│   │   ├── pages.html, add_page.html, edit_page.html
│   │   ├── sejarah.html, add_sejarah.html, edit_sejarah.html
│   │   ├── struktur.html, add_struktur.html, edit_struktur.html
│   │   ├── umkm.html, add_umkm.html, edit_umkm.html
│   │   ├── potensi.html, add_potensi.html, edit_potensi.html
│   │   ├── pengumuman.html, add_pengumuman.html, edit_pengumuman.html
│   │   ├── apbdes.html, add_apbdes.html, edit_apbdes.html
│   │   ├── aduan.html, aduan_detail.html
│   │   ├── kritik_saran.html
│   │   ├── program_kerja.html, add_program_kerja.html, edit_program_kerja.html
│   │   ├── agenda.html, add_agenda.html, edit_agenda.html
│   │   ├── kependudukan.html
│   │   ├── lokasi_rtrw.html, add_lokasi_rtrw.html, edit_lokasi_rtrw.html
│   │   ├── ebook.html, add_ebook.html, edit_ebook.html
│   │   └── login.html
│   ├── dinas/                       # 5 dinas templates
│   │   ├── base.html (22KB), dashboard.html, pending_users.html, all_users.html, user_detail.html
│   └── partials/
│       ├── navbar.html (24KB), footer.html (12KB)
│       ├── chatbot.html (31KB) — Alpine.js chatbot widget
│       └── dark-mode.html
├── static/
│   ├── styles.css (21KB), design-system.css (13KB), dark-mode.css, dark-mode.js
│   ├── tailwind.js (CDN fallback)
│   └── data/geojson/
├── geojson/                         # 12 GeoJSON files
│   ├── batas_desa_wgs84.geojson, batas_desa.geojson
│   ├── DusunRWKedungwinangun_wgs84.geojson
│   ├── BlokKedungwinangun_wgs84.geojson, BlokKedungwinangun.geojson
│   ├── PBTKedungwinangun_wgs84.geojson, PBTKedungwinangun.geojson
│   ├── rtrw_kedungwinangun.geojson
│   ├── umkm_kedungwinangun.geojson
│   └── Batas Desa Kedungwinangun_BPN*.geojson (2 files + .qmd)
├── foto/                            # RT/RW location photos (PLANG_*, RUMAH_*)
├── contoh_webgis/                   # Sample WebGIS (geojson + index.html)
├── uploads/                         # User uploads, CSV templates
│   ├── ebook/                       # PDF files + cover images
│   ├── contoh_struktur_organisasi.csv
│   └── struktur_organisasi_kedungwinangun.csv
├── PLAN.md                          # 7-phase redesign plan (FASE 1-7)
├── ui_plan_update.md                # UI design system reference
├── roles.md                         # Role permissions matrix
└── CLAUDE.md                        # Project reference for Claude AI
```

## 3. BLUEPRINT ARCHITECTURE (app.py:67-72)

```
app.py registers 4 blueprints:
├── public_bp     (from routes.public)      — All public routes: /, /berita, /login, etc.
├── admin_bp      (from routes.admin)       — All admin routes: /admin/*
├── admin_rtrw_bp (from routes.admin_rtrw)  — RT/RW: /admin/rtrw/*
└── ebook_bp      (from routes.admin_ebook) — E-Library: /admin/ebook/*
```

The modular files (routes/public_*.py, routes/admin_*.py) are IMPORTED in __init__.py but NOT REGISTERED in app.py. The LEGACY monolithic files (routes/public.py, routes/admin.py) are what actually handle requests. Modular files serve as reference/refactoring targets.

## 4. DATABASE — 18 Tables

All created in `models.py:init_database()` (line 171). Schema defined as raw SQL `executescript()`.

| # | Table | Purpose | Key Columns | Defined At |
|---|-------|---------|-------------|-----------|
| 1 | `users` | All users (admin/dinas/penduduk) | id, nik, username, nip, nama_lengkap, password_hash, role, status | models.py:183 |
| 2 | `berita` | News articles | judul, excerpt, kategori, gambar_url, video_url, facebook_auto_post, unggulan | models.py:203 |
| 3 | `sejarah_desa` | Village history timeline | judul, sub_judul, konten, tahun_dari, tahun_sampai, gambar_url | models.py:221 |
| 4 | `config` | Website key-value config | key, value | models.py:240 |
| 5 | `galeri` | Photo gallery | judul, deskripsi, kategori, gambar_url, aktif | models.py:246 |
| 6 | `pages` | Dynamic custom pages | title, slug, content, icon, order_num, active | models.py:258 |
| 7 | `komentar` | News comments (nested) | berita_id, parent_id, user_id, nama_pengirim, konten | models.py:271 |
| 8 | `struktur_organisasi` | Village org structure | kategori, nama, jabatan, nik, dusun, rt, rw, foto_url, status | models.py:285 |
| 9 | `umkm` | UMKM businesses | nama, kategori, pemiliki_nama, alamat, latitude, longitude, foto_url | models.py:312 |
| 10 | `kependudukan` | Demographics data | kategori, label, jumlah, satuan, tahun | models.py:336 |
| 11 | `pengumuman` | Announcements | judul, isi, kategori, is_penting, lampiran, author, aktif | models.py:348 |
| 12 | `apbdes` | Budget items | tahun, jenis, nama, icon, jumlah, deskripsi | models.py:362 |
| 13 | `apbdes_summary` | Budget totals | tahun, total_pendapatan, total_belanja, pembiayaan_net | models.py:374 |
| 14 | `potensi_desa` | Village potentials | nama, kategori, deskripsi, gambar_url, icon, aktif | models.py:386 |
| 15 | `kritik_saran` | Kritik dan saran | nama, subjek, isi, kategori, is_read | models.py:399 |
| 16 | `aduan` | Complaints | nomor_aduan (unique), nama, judul, kategori, status, tanggapan | models.py:415 |
| 17 | `program_kerja` | Work programs | judul, kategori, tahun, target, realiasi, anggaran, status | models.py:440 |
| 18 | `login_attempts` | Brute-force protection | identifier, ip_address, attempted_at, success | models.py:458 |
| 19 | `agenda` | Village events | judul, deskripsi, tanggal_mulai, tanggal_selesai, waktu, lokasi, status | models.py:467 |
| 20 | `lokasi_rtrw` | RT/RW locations | jenis, rw, rt, nama_ketua, latitude, longitude, aktif | models.py:487 |
| 21 | `ebook` | E-Library | judul, penulis, file_path, cover_url, kategori, download_count | models.py:504 |

## 5. COMPLETE PUBLIC ROUTES (public_bp)

| URL | Methods | Function | Template | File |
|-----|---------|----------|----------|------|
| `/` | GET | `index` | index.html | public_home.py |
| `/login` | GET,POST | `login` | login.html | public_auth.py |
| `/logout` | GET | `logout` | redirect / | public_auth.py |
| `/csrf-token` | GET | `get_csrf_token` | JSON | public_auth.py |
| `/berita` | GET | `berita` | berita.html | public_berita.py |
| `/berita/<int:id>` | GET | `detail_berita` | detail_berita.html | public_berita.py |
| `/api/berita/<int:id>/komentar` | GET | `api_get_komentar` | JSON | public_berita.py |
| `/api/berita/<int:id>/komentar` | POST | `api_post_komentar` | JSON | public_berita.py |
| `/api/berita/<int:id>/komentar/<int:cid>` | DELETE | `api_delete_komentar` | JSON | public_berita.py |
| `/galeri` | GET | `galeri` | galeri.html | public_pages.py |
| `/kontak` | GET | `kontak` | kontak.html | public_pages.py |
| `/kritik-saran` | GET,POST | `kritik_saran` | kritik_saran.html | public_pages.py |
| `/api/kritik-saran` | POST | `api_kritik_saran` | JSON | public_pages.py |
| `/page/<slug>` | GET | `view_page` | page.html | public_pages.py |
| `/struktur` | GET | `struktur` | struktur.html | public_struktur.py |
| `/struktur/<int:id>` | GET | `struktur_detail` | struktur_detail.html | public_struktur.py |
| `/sejarah` | GET | `sejarah` | sejarah.html | public_struktur.py |
| `/info-kependudukan` | GET | `info_kependudukan` | info_kependudukan.html | public_info.py |
| `/pengumuman` | GET | `pengumuman` | pengumuman.html | public_info.py |
| `/peta-interaktif` | GET | `peta_interaktif` | peta_interaktif.html | public_info.py |
| `/api/umkm/geojson` | GET | `api_umkm_geojson` | JSON | public_info.py |
| `/transparansi` | GET | `transparansi` | transparansi.html | public_info.py |
| `/aduan` | GET,POST | `aduan` | aduan.html | public_aduan.py |
| `/aduan/cek` | GET,POST | `cek_aduan` | cek_aduan.html | public_aduan.py |
| `/program-kerja` | GET | `program_kerja` | program_kerja.html | public_aduan.py |
| `/agenda` | GET | `agenda` | agenda.html | public_aduan.py |
| `/e-library` | GET | `e_library` | e_library.html | public_aduan.py |
| `/e-library/<int:id>` | GET | `e_library_detail` | e_library_detail.html | public_aduan.py |
| `/e-library/<int:id>/download` | GET | `e_library_download` | redirect | public_aduan.py |

## 6. COMPLETE ADMIN ROUTES (admin_bp, prefix: /admin)

All protected with `@admin_required` decorator (session check for role='admin').

| URL | Function | Template |
|-----|----------|----------|
| `/admin/login` | `login` | redirect to public login |
| `/admin/logout` | `logout` | redirect |
| `/admin/dashboard` | `dashboard` | admin/dashboard.html |
| `/admin/config` | `config` (GET,POST) | admin/config.html |
| `/admin/settings` | `settings` (GET,POST) | admin/settings.html |
| `/admin/accounts` | `account_center` | admin/account_center.html |
| `/admin/accounts/user/<int:id>` | `account_detail` (GET,POST) | admin/account_detail.html |
| `/admin/accounts/user/delete/<int:id>` | `account_delete` (POST) | redirect |
| `/admin/accounts/create` | `account_create` (GET,POST) | admin/account_create.html |
| `/admin/berita/add` | `add_berita_route` (GET,POST) | admin/add_berita.html |
| `/admin/berita/edit/<int:id>` | `edit_berita_route` (GET,POST) | admin/edit_berita.html |
| `/admin/berita/delete/<int:id>` | `delete_berita_route` (POST) | redirect |
| `/admin/galeri` | `galeri` | admin/galeri.html |
| `/admin/galeri/add` | `add_galeri_route` (GET,POST) | admin/add_galeri.html |
| `/admin/galeri/edit/<int:id>` | `edit_galeri_route` (GET,POST) | admin/edit_galeri.html |
| `/admin/galeri/delete/<int:id>` | `delete_galeri_route` (POST) | redirect |
| `/admin/galeri/toggle/<int:id>` | `toggle_galeri_route` (POST) | redirect |
| `/admin/sejarah` | `sejarah` | admin/sejarah.html |
| `/admin/sejarah/add` | `add_sejarah_route` (GET,POST) | admin/add_sejarah.html |
| `/admin/sejarah/edit/<int:id>` | `edit_sejarah_route` (GET,POST) | admin/edit_sejarah.html |
| `/admin/sejarah/delete/<int:id>` | `delete_sejarah_route` (POST) | redirect |
| `/admin/sejarah/toggle/<int:id>` | `toggle_sejarah_route` (POST) | redirect |
| `/admin/pages` | `pages` | admin/pages.html |
| `/admin/pages/add` | `add_page_route` (GET,POST) | admin/add_page.html |
| `/admin/pages/edit/<int:id>` | `edit_page_route` (GET,POST) | admin/edit_page.html |
| `/admin/pages/delete/<int:id>` | `delete_page_route` (POST) | redirect |
| `/admin/pages/toggle/<int:id>` | `toggle_page_route` (POST) | redirect |
| `/admin/struktur` | `struktur` | admin/struktur.html |
| `/admin/struktur/add` | `add_struktur_route` (GET,POST) | admin/add_struktur.html |
| `/admin/struktur/edit/<int:id>` | `edit_struktur_route` (GET,POST) | admin/edit_struktur.html |
| `/admin/struktur/delete/<int:id>` | `delete_struktur_route` (POST) | redirect |
| `/admin/struktur/toggle/<int:id>` | `toggle_struktur_route` (POST) | redirect |
| `/admin/struktur/import` | `import_struktur` (POST) | JSON/redirect |
| `/admin/struktur/export` | `export_struktur` (GET) | CSV download |
| `/admin/struktur/template` | `download_struktur_template` (GET) | CSV download |
| `/admin/umkm` | `umkm` | admin/umkm.html |
| `/admin/umkm/add` | `add_umkm_route` (GET,POST) | admin/add_umkm.html |
| `/admin/umkm/edit/<int:id>` | `edit_umkm_route` (GET,POST) | admin/edit_umkm.html |
| `/admin/umkm/delete/<int:id>` | `delete_umkm_route` (POST) | redirect |
| `/admin/umkm/toggle/<int:id>` | `toggle_umkm_route` (POST) | redirect |
| `/admin/umkm/parse-location` | `parse_umkm_location` (POST) | JSON |
| `/admin/kependudukan` | `kependudukan` (GET,POST) | admin/kependudukan.html |
| `/admin/pengumuman` | `pengumuman` | admin/pengumuman.html |
| `/admin/pengumuman/add` | `add_pengumuman_route` (GET,POST) | admin/add_pengumuman.html |
| `/admin/pengumuman/edit/<int:id>` | `edit_pengumuman_route` (GET,POST) | admin/edit_pengumuman.html |
| `/admin/pengumuman/delete/<int:id>` | `delete_pengumuman_route` (POST) | redirect |
| `/admin/pengumuman/toggle/<int:id>` | `toggle_pengumuman_route` (POST) | redirect |
| `/admin/apbdes` | `apbdes` | admin/apbdes.html |
| `/admin/apbdes/add` | `add_apbdes_route` (GET,POST) | admin/add_apbdes.html |
| `/admin/apbdes/edit/<int:id>` | `edit_apbdes_route` (GET,POST) | admin/edit_apbdes.html |
| `/admin/apbdes/delete/<int:id>` | `delete_apbdes_route` (POST) | redirect |
| `/admin/potensi` | `potensi` | admin/potensi.html |
| `/admin/potensi/add` | `add_potensi_route` (GET,POST) | admin/add_potensi.html |
| `/admin/potensi/edit/<int:id>` | `edit_potensi_route` (GET,POST) | admin/edit_potensi.html |
| `/admin/potensi/delete/<int:id>` | `delete_potensi_route` (POST) | redirect |
| `/admin/potensi/toggle/<int:id>` | `toggle_potensi_route` (POST) | redirect |
| `/admin/kritik-saran` | `kritik_saran` | admin/kritik_saran.html |
| `/admin/kritik-saran/read/<int:id>` | `read_kritik_saran` (POST) | redirect |
| `/admin/kritik-saran/delete/<int:id>` | `delete_kritik_saran_route` (POST) | redirect |
| `/admin/aduan` | `aduan` | admin/aduan.html |
| `/admin/aduan/<int:id>` | `aduan_detail` (GET,POST) | admin/aduan_detail.html |
| `/admin/aduan/delete/<int:id>` | `delete_aduan_route` (POST) | redirect |
| `/admin/program-kerja` | `program_kerja` | admin/program_kerja.html |
| `/admin/program-kerja/add` | `add_program_kerja_route` (GET,POST) | admin/add_program_kerja.html |
| `/admin/program-kerja/edit/<int:id>` | `edit_program_kerja_route` (GET,POST) | admin/edit_program_kerja.html |
| `/admin/program-kerja/delete/<int:id>` | `delete_program_kerja_route` (POST) | redirect |
| `/admin/program-kerja/toggle/<int:id>` | `toggle_program_kerja_route` (POST) | redirect |
| `/admin/agenda` | `agenda` | admin/agenda.html |
| `/admin/agenda/add` | `add_agenda_route` (GET,POST) | admin/add_agenda.html |
| `/admin/agenda/edit/<int:id>` | `edit_agenda_route` (GET,POST) | admin/edit_agenda.html |
| `/admin/agenda/delete/<int:id>` | `delete_agenda_route` (POST) | redirect |
| `/admin/agenda/toggle/<int:id>` | `toggle_agenda_route` (POST) | redirect |
| `/admin/rtrw/` (admin_rtrw_bp) | `index` | admin/lokasi_rtrw.html |
| `/admin/rtrw/add` | `add` (GET,POST) | admin/add_lokasi_rtrw.html |
| `/admin/rtrw/edit/<int:id>` | `edit` (GET,POST) | admin/edit_lokasi_rtrw.html |
| `/admin/rtrw/delete/<int:id>` | `delete` | redirect |
| `/admin/rtrw/toggle/<int:id>` | `toggle` | redirect |
| `/admin/rtrw/api/geojson` | `api_geojson` | JSON |
| `/admin/ebook` (ebook_bp) | `ebook_index` | admin/ebook.html |
| `/admin/ebook/add` | `ebook_add` (GET,POST) | admin/add_ebook.html |
| `/admin/ebook/edit/<int:id>` | `ebook_edit` (GET,POST) | admin/edit_ebook.html |
| `/admin/ebook/delete/<int:id>` | `ebook_delete` (POST) | redirect |
| `/admin/ebook/toggle/<int:id>` | `ebook_toggle` (POST) | redirect |

## 7. API ENDPOINTS (app.py + routes)

| Endpoint | Method | Returns | Location |
|----------|--------|---------|----------|
| `/api/berita` | GET | JSON: all news | app.py:311 |
| `/api/berita/<id>/komentar` | GET | JSON: comment tree | public_berita.py |
| `/api/berita/<id>/komentar` | POST | JSON: create comment | public_berita.py |
| `/api/berita/<id>/komentar/<cid>` | DELETE | JSON: delete comment | public_berita.py |
| `/api/umkm/geojson` | GET | GeoJSON FeatureCollection | public_info.py |
| `/api/kritik-saran` | POST | JSON: submit kritik/saran | public_pages.py |
| `/admin/umkm/parse-location` | POST | JSON: parse Google Maps URL | admin_umkm.py |
| `/admin/struktur/export` | GET | CSV download | admin_struktur.py |
| `/admin/struktur/template` | GET | CSV download | admin_struktur.py |
| `/admin/rtrw/api/geojson` | GET | GeoJSON FeatureCollection | admin_rtrw.py |
| `/api/chat` | POST | JSON: chatbot response | app.py:438 |
| `/health` | GET | JSON: health check | app.py:320 |
| `/csrf-token` | GET | JSON: CSRF token | public_auth.py |

## 8. AUTH SYSTEM

### 8.1 User Roles (config.py:155)
```python
ROLES = {'admin': 'Administrator', 'dinas': 'Petugas Dinas', 'penduduk': 'Penduduk'}
```

### 8.2 Default Accounts (config.py:166)
| Login ID | Name | Password | Role | Login Field |
|----------|------|----------|------|-------------|
| `admin` | Administrator | `adminkedungwinangun` | admin | username |
| `admin001` | Administrator 2 | `adminadmin` | admin | username |
| `199001012020011001` | Petugas Dinas | `dinas123` | dinas | nip |

### 8.3 Login Flow (public_auth.py)
1. POST to `/login` with `{login_id, password, role}`
2. Route: if role='admin' → `get_user_by_username(login_id)`, if role='dinas' → `get_user_by_nip(login_id)`
3. Verify password with `check_password_hash()`
4. Brute-force protection: records in `login_attempts` table, locks after Config.MAX_LOGIN_ATTEMPTS (5) in Config.LOGIN_LOCKOUT_MINUTES (15)
5. Sets session vars: user_id, user_role, user_nama, user_logged_in

### 8.4 Session Pattern
```python
session.get('user_id')
session.get('user_role')       # 'admin' | 'dinas'
session.get('user_nama')
session.get('user_logged_in')  # True/False
```

### 8.5 Auth Decorators (errors.py)
```python
@admin_required      # session['user_role'] == 'admin'
@dinas_required      # session['user_role'] in ['admin', 'dinas']
@login_required      # session.get('user_logged_in')
@require_role('admin', 'dinas')  # specific roles
```

## 9. MODELS REFERENCE (models.py — 2965 lines)

### 9.1 Connection Pattern (models.py:49)
```python
from models import get_db_connection
conn = get_db_connection()  # sqlite3.Row (dict-like)
cursor = conn.cursor()
# ... queries ...
conn.close()
```

### 9.2 Complete Function Index

**Config** (models.py:562-618):
- `get_config(key, default)` → str
- `get_all_config()` → dict
- `update_config(key, value)` → bool
- `get_desa_info()` → dict

**Auth/Users** (models.py:625-982):
- `get_user_by_username(username)` → dict|None (admin login)
- `get_user_by_nip(nip)` → dict|None (dinas login)
- `get_user_by_id(user_id)` → dict|None
- `register_user(nik, nama, email, telp, alamat, password, ktp_path, kk_path)` → (bool, msg)
- `get_pending_users()` → list
- `get_all_warga()` → list
- `get_all_warga_approved()` → list
- `get_all_users()` → list
- `get_users_by_role(role)` → list
- `get_user_stats()` → dict {total, by_role, by_status}
- `update_user_data(user_id, data)` → bool
- `update_user_role(user_id, new_role, updated_by)` → bool
- `update_user_password(user_id, new_password)` → bool
- `delete_user_account(user_id)` → bool
- `create_staff_account(login_id, nama, password, role)` → (bool, result)

**Berita** (models.py:989-1059):
- `get_all_berita()` → list
- `get_berita_by_id(id)` → dict|None
- `add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan)` → bool
- `update_berita(id, ...)` → bool
- `delete_berita(id)` → bool

**Sejarah** (models.py:1066-1159):
- `get_all_sejarah(aktif=None)` → list
- `get_sejarah_by_id(id)` → dict|None
- `add_sejarah(judul, konten, kategori, tahun_dari, tahun_sampai, gambar_url, ...)` → bool
- `update_sejarah(id, ...)` → bool
- `delete_sejarah(id)` → bool
- `toggle_sejarah_aktif(id)` → bool

**Galeri** (models.py:1166-1251):
- `get_all_galeri(aktif=None)` → list
- `get_galeri_by_id(id)` → dict|None
- `add_galeri(judul, gambar_url, deskripsi, kategori, gambar_alt)` → bool
- `update_galeri(id, ...)` → bool
- `delete_galeri(id)` → bool
- `toggle_galeri_aktif(id)` → bool

**Pages** (models.py:1258-1371):
- `get_all_pages()` → list (active only)
- `get_all_pages_admin()` → list (all)
- `get_page_by_slug(slug)` → dict|None
- `get_page_by_id(id)` → dict|None
- `add_page(title, slug, content, icon)` → bool
- `update_page(id, ...)` → bool
- `delete_page(id)` → bool
- `toggle_page_active(id)` → bool

**Komentar** (models.py:1378-1468):
- `get_komentar_by_berita(berita_id)` → list (flat)
- `build_comment_tree(flat_comments)` → list (nested tree)
- `create_komentar(berita_id, konten, nama_pengirim, parent_id, user_id)` → bool
- `delete_komentar(id)` → bool
- `get_komentar_by_id(id)` → dict|None
- `count_komentar_by_berita(berita_id)` → int

**Struktur Organisasi** (models.py:1475-1683):
- `get_all_struktur(aktif=None)` → list
- `get_struktur_by_kategori(kategori, aktif=None)` → list
- `get_struktur_by_id(id)` → dict|None
- `add_struktur(kategori, nama, jabatan, deskripsi, nik, dusun, rt, rw, ...)` → bool
- `update_struktur(id, ...)` → bool
- `delete_struktur(id)` → bool
- `toggle_struktur_aktif(id)` → bool
- `batch_import_struktur(csv_data)` → dict {success, errors, total}
- Valid categories: perangkat, bpd, pkk, karang_taruna, rt, rw

**UMKM** (models.py:1690-1831):
- `get_all_umkm(aktif=None, kategori=None)` → list
- `get_umkm_by_id(id)` → dict|None
- `add_umkm(nama, kategori, deskripsi, pemiliki_nama, alamat, dusun, latitude, longitude, ...)` → bool
- `update_umkm(id, ...)` → bool
- `delete_umkm(id)` → bool
- `toggle_umkm_aktif(id)` → bool
- `get_umkm_for_geojson(aktif=1)` → GeoJSON FeatureCollection
- Categories: makanan, minuman, kerajinan, jasa, pertanian, peternakan, perikanan, umum

**Pengumuman** (models.py:1839-1942):
- `get_all_pengumuman(aktif=None)` → list
- `get_pengumuman_by_id(id)` → dict|None
- `add_pengumuman(judul, isi, kategori, is_penting, lampiran, author)` → bool
- `update_pengumuman(id, ...)` → bool
- `delete_pengumuman(id)` → bool
- `toggle_pengumuman_aktif(id)` → bool

**APBDes** (models.py:1949-2060):
- `get_apbdes_by_tahun(tahun)` → list (grouped by jenis: pendapatan, belanja, pembiayaan)
- `get_apbdes_summary(tahun)` → dict|None (total_pendapatan, total_belanja, pembiayaan_net)
- `get_apbdes_by_id(id)` → dict|None
- `add_apbdes_item(tahun, jenis, nama, jumlah, icon, deskripsi)` → bool
- `update_apbdes_item(id, ...)` → bool
- `delete_apbdes_item(id)` → bool
- `save_apbdes_summary(tahun, total_pendapatan, total_belanja, pembiayaan_net)` → bool
- `get_available_tahun()` → list

**Potensi Desa** (models.py:2067-2149):
- `get_all_potensi()` → list
- `get_potensi_by_id(id)` → dict|None
- `add_potensi(nama, kategori, deskripsi, gambar_url, icon, aktif)` → bool
- `update_potensi(id, ...)` → bool
- `delete_potensi(id)` → bool
- `toggle_potensi_aktif(id)` → bool

**Kependudukan** (models.py:2152-2179):
- `get_all_kependudukan()` → list
- `update_kependudukan(kategori, label, jumlah, satuan, tahun)` → bool

**Kritik Saran** (models.py:2186-2261):
- `add_kritik_saran(nama, subjek, isi, email, telepon, kategori)` → bool
- `get_all_kritik_saran(include_read=True)` → list
- `get_kritik_saran_stats()` → dict {total, unread, kritik, saran}
- `mark_kritik_saran_read(id)` → bool
- `delete_kritik_saran(id)` → bool
- Categories: kritik, saran, pertanyaan, lainnya

**Aduan** (models.py:2268-2403):
- `get_all_aduan(aktif=None, status=None)` → list
- `get_aduan_by_id(id)` → dict|None
- `get_aduan_by_nomor(nomor_aduan)` → dict|None
- `add_aduan(nama, judul, deskripsi, kategori, email, telepon, nik, ...)` → (bool, nomor_aduan)
- `update_aduan(id, ...)` → bool
- `delete_aduan(id)` → bool
- `respond_aduan(id, catatan, responded_by)` → bool
- `get_aduan_stats()` → dict {total, menunggu, ditanggapi, selesai}
- Categories: infrastruktur, lingkungan, kesehatan, pendidikan, keamanan, pelecehan, korupsi, lainnya
- Status: menunggu, diterima, dalam_proses, selesai, ditolak

**Program Kerja** (models.py:2410-2508):
- `get_all_program_kerja(aktif=None, tahun=None)` → list
- `get_program_kerja_by_id(id)` → dict|None
- `add_program_kerja(judul, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status)` → bool
- `update_program_kerja(id, ...)` → bool
- `delete_program_kerja(id)` → bool
- `toggle_program_kerja_aktif(id)` → bool
- Status: rencana, berlangsung, selesai

**Agenda** (models.py:2516-2622):
- `get_all_agenda(aktif=None, status=None, tahun=None)` → list
- `get_agenda_by_id(id)` → dict|None
- `add_agenda(judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu, lokasi, icon, ...)` → bool
- `update_agenda(id, ...)` → bool
- `delete_agenda(id)` → bool
- `toggle_agenda_aktif(id)` → bool
- Status: akan_datang, sedang_berlangsung, selesai, dibatalkan
- Categories: umum, kegiatan, rapat, musyawarah, pembangunan, kesehatan, pendidikan

**Lokasi RT/RW** (models.py:2629-2775):
- `get_all_lokasi_rtrw(aktif=None)` → list
- `get_lokasi_rtrw_by_id(id)` → dict|None
- `add_lokasi_rtrw(jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude)` → int|None
- `update_lokasi_rtrw(id, jenis, rw, rt, nama_ketua, ...)` → bool
- `delete_lokasi_rtrw(id)` → bool
- `toggle_lokasi_rtrw_aktif(id)` → bool
- `get_lokasi_rtrw_geojson()` → GeoJSON FeatureCollection (with foto_url)
- `_get_foto_url(jenis, rw, rt)` → str (auto-matches PLANG_*/RUMAH_* photos in /foto/)
- `get_all_locations_geojson(aktif=1)` → unified GeoJSON from rtrw + struktur

**E-Library** (models.py:2819-2925):
- `get_all_ebook(aktif=None)` → list
- `get_ebook_by_id(id)` → dict|None
- `add_ebook(judul, file_path, penulis, deskripsi, kategori, cover_url, tahun, halaman, bahasa)` → int|None
- `update_ebook(id, ...)` → bool
- `delete_ebook(id)` → bool
- `toggle_ebook_aktif(id)` → bool
- `increment_ebook_download(id)` → bool

**Login Attempts** (models.py:680-747):
- `record_login_attempt(identifier, ip_address, success)` → bool
- `get_recent_login_attempts(identifier, ip_address, window_minutes)` → int
- `is_login_locked(identifier, ip_address, max_attempts, window_minutes)` → bool
- `clear_login_attempts(identifier)` → bool
- `clean_old_login_attempts(days)` → bool

### 9.3 Location Category Mappings (models.py:2928-2965)
```python
LOKASI_KATEGORI_LABELS = {'RT': 'Rumah Ketua RT', 'RW': 'Rumah Ketua RW', 'perangkat': 'Perangkat Desa', ...}
LOKASI_KATEGORI_ICONS = {'RT': '🏠', 'RW': '🏛️', 'perangkat': '👔', ...}
LOKASI_KATEGORI_COLORS = {'RT': '#457b9d', 'RW': '#264653', 'perangkat': '#1b4332', ...}
```

## 10. CHATBOT SYSTEM (app.py:376-538)

### Architecture:
- `POST /api/chat` receives `{messages: [{role, content}], model?: string}`
- Server builds dynamic system prompt with RT/RW data + Perangkat Desa data from DB
- Tries models in order: deepseek-v4-flash (free) → nemotron-3-ultra → gemma-4-26b → openrouter/free
- Falls through on: 429 (rate limit), 503 (unavailable), network errors
- API key stored ONLY in .env (`OPENROUTER_API_KEY`), never exposed to client

### System Prompt (app.py:411):
- NAMA KADES: Moh Baequni
- Website context: Desa Kedungwinangun, Kec. Klirong, Kebumen, Jawa Tengah
- Dynamic RT/RW list + Perangkat Desa injected at runtime
- Instructions: Bahasa Indonesia informal, max 3-4 paragraphs, use emojis sparingly

## 11. ERROR HANDLING (errors.py — 873 lines)

### Exception Hierarchy:
```
AppError (base)
├── DatabaseError — DB operations
├── ValidationError — Input validation
├── NotFoundError — 404
├── UnauthorizedError — 401
├── ForbiddenError — 403
├── FileError — File operations
└── APIError — API endpoints
```

### Decorators:
- `@safe_handler` — wraps routes to catch all errors, with optional fallback_url
- `@safe_handler(fallback_url='/admin/dashboard')` — redirect on error
- `@api_handler` — for JSON API routes with consistent error formatting
- `@require_json` — ensures request has JSON body

### Response Helpers:
- `flash_error(message, category)` — flash message with validation
- `json_error_response(message, status_code, error_code, extra)` → tuple
- `json_success_response(message, data, status_code)` → tuple
- `render_error_page(error_code, title, message, back_url)` → template
- `handle_db_error(error, operation, rollback_conn)` → (bool, message)

### Validation:
- `validate_required(data, required_fields, prefix)` → (bool, msg)
- `validate_email(email)` → (bool, msg)
- `validate_password(password, min_length)` → (bool, msg)
- `validate_phone(phone)` → (bool, msg)
- `validate_url(url, required)` → (bool, msg)
- `validate_integer(value, field_name, min, max)` → (bool, msg)

## 12. DATABASE LAYER (database.py — 557 lines)

### Connection:
- `get_db_connection()` → sqlite3.Connection with row_factory=sqlite3.Row
- `@contextmanager with_db_connection()` — auto-close context manager
- `DatabaseError`, `DatabaseConnectionError`, `DatabaseQueryError`, `DatabaseValidationError`

### Safe Wrappers:
- `db_execute(query, params, conn, commit, return_lastrowid, return_rowcount)` → varies
- `db_fetch_one(query, params, conn)` → dict|None
- `db_fetch_all(query, params, conn)` → list of dicts

### Decorators:
- `@db_operation('name')` — wrap function with DB error handling
- `@safe_db_operation(default_return=[])` — return default on error
- `@db_transaction` — auto commit/rollback

### Batch Helpers:
- `db_batch_insert(table, fields, values, conn)` → row count
- `check_unique(conn, table, field, value, exclude_id)` → bool
- `check_foreign_key(conn, table, field, value)` → bool

## 13. FILE UPLOAD SYSTEM

### Config (config.py:16-28):
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}  # General
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}  # Images
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB threshold for compression
```

### Image Compression (config.py:40):
- `compress_and_save_image(file_bytes, upload_dir, filename_prefix)` → (filename, filepath)
- If >2MB: resize to max 1200px dimension, WebP quality 60
- If <=2MB: WebP quality 80
- All images converted to WebP format

### Upload Routes (app.py:328-347):
- `/uploads/<path:filename>` — serve uploaded files (KTP, KK, etc.)
- `/foto/<path:filename>` — serve RT/RW photos from /foto/ directory

### Common Helper Functions (found in admin route files):
- `allowed_image(filename)` — checks against ALLOWED_IMAGE_EXT
- `save_uploaded_file(file, subfolder)` — saves to uploads/{subfolder}/ with WebP compression
- `allowed_pdf(filename)` — checks .pdf extension (admin_ebook.py)
- `save_pdf_file(file)` — saves PDF to uploads/ebook/
- `save_cover_image(file)` — saves WebP cover to uploads/ebook/

## 14. GEOSPATIAL SYSTEM

### GeoJSON Files (12 files in /geojson/):
| File | Type | Description |
|------|------|-------------|
| batas_desa_wgs84.geojson | Polygon | Village boundary |
| DusunRWKedungwinangun_wgs84.geojson | MultiPolygon | Hamlet boundaries |
| BlokKedungwinangun_wgs84.geojson | MultiPolygon | Land blocks |
| PBTKedungwinangun_wgs84.geojson | Polygon | PBT area |
| rtrw_kedungwinangun.geojson | Point | RT/RW locations |
| umkm_kedungwinangun.geojson | Point | UMKM locations |
| Batas Desa Kedungwinangun_BPN_wgs84.geojson | Polygon | BPN certified boundary |

### GeoJSON Serving (app.py:351-373):
- `/geojson/<path:filename>` — serves with `application/geo+json` MIME type + CORS header

### API Endpoints:
- `/api/umkm/geojson` — UMKM points from DB (models.py:get_umkm_for_geojson)
- `/admin/rtrw/api/geojson` — RT/RW points from DB (models.py:get_lokasi_rtrw_geojson)
- `get_all_locations_geojson()` — unified: rtrw + struktur (models.py:2778)

### Google Maps URL Parser (admin_umkm.py):
- `POST /admin/umkm/parse-location` with `{maps_url: "..."}`
- Handles: @lat,lng format, place format, query format, short URLs (auto-resolved)

### Map Coordinates (config.py):
```python
MAP_CENTER_LAT = -7.7004775
MAP_CENTER_LNG = 109.6432848
MAP_DEFAULT_ZOOM = 15
```

### RT/RW Photo Auto-Matching (models.py:2718-2745):
```python
# Convention: /foto/PLANG_RT{rt}_RW{rw}.jpg or RUMAH_RT{rt}_RW{rw}.jpg
# For RW: /foto/PLANG_RW{rw}.jpg or RUMAH_RW{rw}.jpg
```

## 15. UI / DESIGN SYSTEM

### Colors (base.html):
```css
--desa-dark: #155C1B;     /* Forest Green */
--desa-mid: #2A6726;      /* Medium Green */
--desa-light: #73AA0F;    /* Light Green */
--desa-muted: #5B8A4E;    /* Muted Green */
--desa-dark2: #0f3d14;    /* Darker Green */
```

### Typography: Inter (Google Fonts), weights 400-800.

### Dark Mode:
- Toggle via `dark` class on `<body>` in dark-mode.js
- Tailwind `dark:` classes + CSS custom properties overrides
- Persisted in localStorage

### Frameworks:
- Tailwind CSS 3.x (CDN: `cdn.tailwindcss.com` + local fallback)
- Alpine.js (CDN)
- Chart.js for statistics (info_kependudukan.html)
- Leaflet.js for interactive map (peta_interaktif.html) with OpenStreetMap tiles

## 16. TEMPLATE STRUCTURE

### Base Templates:
- `base.html` — Public layout (navbar + footer + chatbot + dark mode)
- `admin/base.html` — Admin layout (sidebar + navbar)
- `dinas/base.html` — Dinas layout (sidebar + navbar)

### INCLUDE hierarchy:
- `base.html` → includes `partials/navbar.html`, `partials/footer.html`, `partials/chatbot.html`, `partials/dark-mode.html`
- `index.html` — STANDALONE (does NOT extend base.html, has its own full `<head>`)

### Chatbot Widget (partials/chatbot.html — 31KB):
- Alpine.js component with toggle, message history, typing indicator
- Sends POST to `/api/chat` with CSRF token
- Supports Enter to send, scroll-to-bottom auto

## 17. CONFIGURATION

### Website Config (database table `config`, DEFAULT_CONFIG in config.py:74):
- website_nama, website_tagline, website_deskripsi, website_meta_description
- berita_tampil_di_beranda (default: 6), berita_unggulan_tampil (3), berita_tampil_di_halaman (12)
- berita_tampilkan_views (1), berita_tampilkan_tanggal (1), berita_carousel_stacks (2)
- tampilkan_maps (1), tampilkan_statistik (1), tampilkan_daftar_dusun (1), tampilkan_hero (1)
- kontak_whatsapp, kontak_telepon, kontak_email, alamat_desa
- sosial_facebook, sosial_instagram, sosial_twitter, sosial_tiktok
- footer_copyright

### Dusun Data (config.py:140):
6 hamlets: Karangmiri, Dungwaru, Perna & Sasak, Entak, Grewing, Pedana & Pagak

## 18. SECURITY

### Headers (app.py:228-261):
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Cache-Control: no-store for admin/login paths
- Content-Security-Policy: relaxed for CDN/Google Maps/OpenRouter
- Permissions-Policy: restricted features

### Brute-Force Protection (models.py:680-747):
- Login attempts recorded in `login_attempts` table
- Configurable: MAX_LOGIN_ATTEMPTS=5, LOGIN_LOCKOUT_MINUTES=15, LOGIN_ATTEMPT_WINDOW=15
- Lockout based on identifier + IP address within rolling window

### CSRF (app.py:268):
- Random token generated per session, injected into templates
- Used by chatbot and AJAX endpoints (not all forms)

## 19. REDESIGN PLAN (PLAN.md)

### Current Status:
- FASE 1: Hapus Sistem Surat + Login NIK — Planned
- FASE 2: Sejarah Desa immersive — Planned
- FASE 3: Struktur Desa org chart — PENDING (waiting data from Bu Sekdes)
- FASE 4: Map UMKM + Peta Interaktif — Planned
- FASE 5: Artikel + Facebook Share — Planned
- FASE 6: Info Kependudukan with charts — Planned
- FASE 7: Video Integration — Planned

### FASE 1 Cleanup Target:
Delete files: routes/user.py, routes/dinas.py, templates/user/*, templates/dinas/permohonan*.html, pdf_generator.py
Remove from: NAV_LINKS (/layanan), models.py (surat functions), login.html (warga tab), errors.py (warga_required)

## 20. KEY ARCHITECTURAL NOTES

1. **Monolithic files (public.py, admin.py) are the actual handlers** — modular files are imports only, NOT registered
2. **No SQLAlchemy** — all DB via raw SQL + sqlite3.Row
3. **No class-based views** — all route handlers are functions
4. **Duplicate helper functions** — each public_*.py independently defines `get_desa_info_with_maps()` and `set_nav_active()` with slight variations
5. **index.html is standalone** — does NOT extend base.html, has its own full head section
6. **Session-based auth** — no JWT, no OAuth, no API tokens
7. **OpenRouter API key in .env** — chatbot only works if OPENROUTER_API_KEY is set
8. **CSRF only for AJAX** — most forms don't have CSRF protection
9. **File naming for RT/RW photos** — convention-based: PLANG_RT{rt}_RW{rw}.jpg or RUMAH_RT{rt}_RW{rw}.jpg (and RW variants)
10. **Dual blueprint system** — legacy monolithic + modular (for future migration)

## 21. FILE SIZE REFERENCE (For Prioritization)

| File | Lines | Size | What to Know |
|------|-------|------|-------------|
| models.py | 2965 | ~120KB | ALL CRUD functions — single largest file |
| routes/admin.py | ~1000+ | 105KB | Legacy monolithic admin routes |
| routes/public.py | ~700+ | 53KB | Legacy monolithic public routes |
| templates/index.html | — | 67KB | Homepage (standalone, not extending base) |
| templates/base.html | — | 34KB | Main layout |
| templates/partials/chatbot.html | — | 31KB | Alpine.js chatbot widget |
| templates/peta_interaktif.html | — | 53KB | Interactive map with Leaflet |
| errors.py | 873 | ~30KB | Custom exceptions, decorators, validators |
| database.py | 557 | ~20KB | DB error handling, safe wrappers |
| app.py | 555 | ~20KB | Entry point, chatbot, error handlers |
| config.py | 258 | ~10KB | Config, constants, SQL schema |

## 22. QUICK COMMANDS

```bash
# Run
python app.py                     # Dev server on http://localhost:5209

# Default login
Username: admin | Password: adminkedungwinangun

# Install
pip install -r requirements.txt   # Flask, Werkzeug, python-dotenv, reportlab, Pillow
```
