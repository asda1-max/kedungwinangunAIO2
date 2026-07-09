# Desa Kedungwinangun AIO

Website resmi Desa Kedungwinangun - Sistem Informasi Desa Digital Terintegrasi.

**Lokasi:** Kec. Klirong, Kab. Kebumen, Jawa Tengah  
**Port Default:** 5209

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py

# Buka browser
http://localhost:5209
```

---

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.12 + Flask 3.0+ |
| Database | SQLite3 |
| Frontend | HTML5 + Tailwind CSS 3.x + Vanilla JS |
| PDF | ReportLab 4.0+ |
| AI Chatbot | OpenRouter API (server-side) |
| Auth | Werkzeug PBKDF2 hashing |

---

## Struktur Direktori

```
├── app.py                    # Flask app factory + blueprints
├── config.py                 # Config class + konstanta
├── models.py                 # Semua operasi database
├── database.py               # Error handling + safe DB ops
├── errors.py                 # Error handlers, decorators, validators
├── routes/
│   ├── public*.py            # Routes publik (modular)
│   └── admin*.py             # Routes admin (modular)
├── templates/                # Jinja2 templates
│   ├── admin/                # 27+ template admin
│   └── partials/             # Navbar, footer, chatbot, dark-mode
├── static/
│   ├── styles.css
│   └── images/
└── uploads/                  # File upload (KTP, KK, berita, galeri, dll)
```

---

## Fitur Utama

### Publik
- **Beranda** - Hero, carousel berita, potensi desa, statistik
- **Berita** - Daftar & detail berita dengan komentar
- **Galeri** - Galeri foto desa
- **Struktur Organisasi** - Peta organisasi desa
- **Sejarah Desa** - Timeline sejarah Kedungwinangun
- **Kependudukan** - Data demografis dengan chart
- **Pengumuman** - Pengumuman terbaru
- **Transparansi** - APBDes (Anggaran Pendapatan Belanja Desa)
- **Peta Interaktif** - Peta UMKM dan lokasi desa
- **Aduan** - Sistem kritik dan saran
- **Program Kerja** - Daftar program kerja desa
- **Agenda** - Agenda kegiatan desa
- **Chatbot AI** - Asisten virtual (OpenRouter)

### Admin Panel (`/admin`)
- Dashboard dengan statistik
- Manajemen berita
- Manajemen galeri
- Manajemen halaman dinamis
- Manajemen struktur organisasi (support import/export CSV)
- Manajemen UMKM + Google Maps parser
- Manajemen potensi desa
- Manajemen pengumuman
- Manajemen APBDes
- Manajemen kependudukan
- Manajemen aduan
- Manajemen program kerja
- Manajemen agenda
- Account center (multi-role: admin/dinas/penduduk)
- Konfigurasi website

---

## Default Login

| Role | Login ID | Password |
|------|----------|----------|
| Admin | `admin` | `adminkedungwinangun` |
| Admin 2 | `admin001` | `adminadmin` |
| Dinas | `199001012020011001` | `dinas123` |

---

## Database

Database SQLite (`database.db`) dengan tabel:

| Tabel | Deskripsi |
|-------|-----------|
| `users` | Semua user (admin/dinas/penduduk) |
| `berita` | Artikel berita |
| `config` | Konfigurasi website |
| `galeri` | Foto galeri |
| `pages` | Halaman dinamis |
| `komentar` | Komentar berita |
| `struktur_organisasi` | Struktur organisasi |
| `sejarah_desa` | Timeline sejarah |
| `pengumuman` | Pengumuman |
| `apbdes` | Item APBDes |
| `apbdes_summary` | Ringkasan APBDes |
| `umkm` | Daftar UMKM |
| `kependudukan` | Data demografis |
| `potensi_desa` | Potensi desa |
| `aduan` | Sistem aduan |
| `program_kerja` | Program kerja |
| `agenda` | Agenda kegiatan |
| `kritik_saran` | Kritik dan saran |

---

## API Endpoints

```
GET  /api/berita              # JSON semua berita
GET  /api/berita/<id>/komentar # Komentar berita
POST /api/berita/<id>/komentar # Tambah komentar
POST /api/chat                # Chatbot AI
GET  /api/umkm/geojson        # GeoJSON untuk peta interaktif
```

---

## Environment Variables

```env
OPENROUTER_API_KEY=sk-or-v1-...    # Required untuk chatbot
SECRET_KEY=...                      # Flask session secret
DATABASE_NAME=database.db
PORT=5209
```

---

## Struktur Organisasi Categories

```
perangkat, bpd, pkk, karang_taruna, rt, rw
```

---

## UMKM Categories

```
makanan 🍜 | minuman 🥤 | kerajinan 🎨 | jasa 🔧
pertanian 🌾 | peternakan 🐔 | perikanan 🐟 | umum 🏪
```

---

## 6 Dinas di Kedungwinangun

1. Dumont Kedungwaru
2. Perna
3. Sasak
4. Entak
5. Grewing
6. Pedana

---

## Instalasi Manual

```bash
# 1. Clone/download proyek
cd kedungwinangunAIO

# 2. Buat virtual environment (opsional tapi disarankan)
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
# atau: .venv\Scripts\activate  # Windows (CMD/PowerShell)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy .env.example ke .env (jika ada)
# cp .env.example .env

# 5. Jalankan
python app.py
```

---

## Production Notes

1. Gunakan web server (Nginx + Gunicorn) untuk production
2. Untuk skala besar, migrate ke PostgreSQL/MySQL
3. Gunakan cloud storage (AWS S3) untuk file upload
4. Wajib HTTPS untuk keamanan data
5. Set `FLASK_ENV=production`

---

## Lisensi

Open source untuk pelayanan masyarakat desa.

---

*Website ini dikembangkan untuk meningkatkan transparansi dan pelayanan publik di Desa Kedungwinangun.*
