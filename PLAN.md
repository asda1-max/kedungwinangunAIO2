# Plan: Redesain Total Sistem Desa Kedungwinangun AIO

## RINGKASAN EKSEKUTIF

Project besar yang terdiri dari:
1. **HAPUS** Sistem Surat + Login NIK (cleanup total)
2. **TAMBAH** Fitur-fitur baru yang immersive

---

## FASE 1: HAPUS SISTEM SURAT + LOGIN NIK

### Files to DELETE Entirely:
```
routes/user.py
routes/dinas.py
templates/user/surat_permohonan.html
templates/dinas/permohonan_list.html
templates/dinas/permohonan_detail.html
templates/user/register.html
templates/user/login.html
templates/user/dashboard.html
templates/user/base.html
pdf_generator.py
```

### Files to MODIFY:

#### `routes/public.py`
- Remove: warga/NIK login tab (lines 115-135)
- Remove: `/layanan` route (lines 320-368)
- Remove: `/surat_info` route (lines 314-317)
- Remove imports: `get_user_by_nik`, `verify_user`

#### `models.py`
- Remove table schemas: `permohonan_acc`, `jenis_surat`, `permohonan_surat`
- Remove functions:
  - `get_user_by_nik()`
  - `approve_user()`, `reject_user()`
  - `create_permohonan_acc()`
  - `get_all_jenis_surat()`, `get_jenis_surat_by_id()`
  - `create_permohonan_surat()`
  - `get_permohonan_surat_by_user()`
  - `get_all_permohonan_surat()`
  - `get_pending_permohonan_surat()`
  - `get_permohonan_detail()`
  - `approve_permohonan_surat()`
  - `reject_permohonan_surat()`

#### `config.py`
- Remove `/layanan` dari NAV_LINKS
- Remove `DEFAULT_JENIS_SURAT`
- Remove SQL schema for surat tables

#### `templates/login.html`
- Remove warga/NIK login tab (lines 480-502)

#### `templates/dinas/dashboard.html`
- Remove "Permohonan Surat Pending" section (lines 129-185)

#### `templates/dinas/base.html`
- Remove "Permohonan Surat" sidebar menu (lines 434-441)

#### `errors.py`
- Remove `warga_required()` decorator
- Remove `validate_nik()` function

#### `app.py`
- Update comments/docstrings
- Remove DinasBlueprint registration

### Database Migration:
```sql
DROP TABLE IF EXISTS permohonan_acc;
DROP TABLE IF EXISTS jenis_surat;
DROP TABLE IF EXISTS permohonan_surat;
```

---

## FASE 2: SEJARAH DESA (IMMERSIVE)

### Database - New Table `sejarah_desa`:
```sql
CREATE TABLE IF NOT EXISTS sejarah_desa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT NOT NULL,
    sub_judul TEXT,
    konten TEXT,
    kategori TEXT DEFAULT 'sejarah',
    tahun_dari INTEGER,
    tahun_sampai INTEGER,
    gambar_url TEXT,
    gambar_alt TEXT,
    video_url TEXT,
    aktif INTEGER DEFAULT 1,
    urutan INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Admin CRUD (routes/admin.py):
- GET/POST `/admin/sejarah` - List semua
- GET/POST `/admin/sejarah/add` - Tambah
- GET/POST `/admin/sejarah/edit/<id>` - Edit
- POST `/admin/sejarah/delete/<id>` - Hapus
- POST `/admin/sejarah/reorder` - Urutkan

### Admin Templates:
- `templates/admin/sejarah.html` - Timeline list
- `templates/admin/add_sejarah.html` - Form dengan Rich Text Editor
- `templates/admin/edit_sejarah.html` - Edit form

### Public Route:
- GET `/sejarah` - Timeline immersive dengan:
  - Parallax hero section
  - Timeline interaktif (scroll-triggered animations)
  - Era/periode cards
  - Video embed support
  - Parallax image backgrounds

---

## FASE 3: STRUKTUR DESA (TUNGGU DATA BU SEKDES)

### Status: PENDING - Perlu data dari Bu Sekdes

### Implementation setelah dapat data:
1. Admin CRUD untuk struktur organisasi
2. Public page dengan org chart interaktif
3. Animated hierarchy tree

---

## FASE 4: MAP UMKM + MAP INTERAKTIF (w/ Ilma)

### Static Data:
- `static/data/umkm.geojson` - Lokasi UMKM
- `static/data/population.json` - Data populasi per dusun

### Enhancements to peta_interaktif.html:
- New layer: "UMKM" dengan category filter
- Popup dengan detail bisnis
- "Ilma" feature: Glow/animation pada marker penting
- Filter by dusun
- Legend interaktif

### Admin for UMKM (optional):
- CRUD UMKM locations
- Import from CSV

---

## FASE 5: ARTIKEL + FACEBOOK SHARE

### Modifications to berita system:

#### Database - Add to `berita`:
```sql
ALTER TABLE berita ADD COLUMN video_url TEXT;
ALTER TABLE berita ADD COLUMN facebook_share INTEGER DEFAULT 1;
```

#### templates/detail_berita.html:
- Add Open Graph meta tags:
```html
<meta property="og:title" content="{{ artikel.judul }}">
<meta property="og:description" content="{{ artikel.excerpt }}">
<meta property="og:image" content="{{ artikel.gambar_url }}">
<meta property="og:url" content="{{ request.url }}">
<meta property="og:type" content="article">
```

- Add Share buttons:
```html
<div class="share-section">
    <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.url }}"
       target="_blank" class="btn-facebook">
        📘 Bagikan ke Facebook
    </a>
    <a href="https://wa.me/?text={{ artikel.judul }}%20{{ request.url }}"
       target="_blank" class="btn-whatsapp">
        💬 WhatsApp
    </a>
</div>
```

#### templates/admin/add_berita.html:
- Add "Video URL" field
- Add "Enable Facebook Share" toggle
- Add "Auto-post to Facebook" option (advanced)

---

## FASE 6: INFO KEPENDUDUDKAN

### Database - New Table `kependudukan`:
```sql
CREATE TABLE IF NOT EXISTS kependudukan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategori TEXT NOT NULL,
    label TEXT NOT NULL,
    nilai INTEGER DEFAULT 0,
    satuan TEXT,
    tahun INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Admin CRUD:
- `/admin/kependudukan` - Manage stats
- Import/Export CSV support

### Public Page `/info-kependudukan`:
- Dashboard cards dengan animasi counter
- Charts (using Chart.js):
  - Populasi per dusun (bar chart)
  - Jenis kelamin (pie chart)
  - Usia produktif (donut chart)
- Summary statistics
- Source attribution

### Admin Dashboard Update:
- Show real user count dari database
- Show approved users count
- Show registrations by dusun

---

## FASE 7: VIDEO INTEGRATION IN GALLERY

### New Table `video_galeri`:
```sql
CREATE TABLE IF NOT EXISTS video_galeri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT NOT NULL,
    deskripsi TEXT,
    video_url TEXT NOT NULL,
    thumbnail_url TEXT,
    aktif INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Admin CRUD:
- `/admin/video-galeri` - Manage videos
- YouTube/Vimeo URL parsing
- Thumbnail extraction

### Templates:
- `templates/admin/video_galeri.html`
- `templates/video.html` (public video gallery)

### Public Gallery Enhancement:
- Tab navigation: Gambar | Video
- Video player dengan lightbox
- Lazy loading untuk performance

---

## IMPLEMENTATION ORDER

```
Week 1:
├── FASE 1: Hapus Sistem Surat + Login NIK
├── FASE 2: Sejarah Desa
└── FASE 3: (TUNGGU DATA)

Week 2:
├── FASE 5: Artikel + Facebook Share
├── FASE 7: Video Integration
└── FASE 4: Map UMKM

Week 3:
├── FASE 6: Info Kependudukan
└── FASE 3: Struktur Desa (jika data sudah ada)
```

---

## ESTIMASI Effort

| Fase | Complexity | Files |
|------|------------|-------|
| FASE 1 | High (deletion) | ~10 files |
| FASE 2 | Medium | ~5 files |
| FASE 4 | Medium | ~3 files |
| FASE 5 | Low | ~2 files |
| FASE 6 | Medium | ~4 files |
| FASE 7 | Medium | ~4 files |

---

## CATATAN

- FASE 3 (Struktur Desa) menunggu data dari Bu Sekdes
- Semua fitur baru harus responsive (mobile-first)
- Tailwind CSS sudah digunakan - continue dengan pattern yang sama
- Test setiap fase sebelum lanjut ke fase berikutnya
