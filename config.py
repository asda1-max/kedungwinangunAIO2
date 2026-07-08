"""
Konfigurasi Aplikasi Desa Kedungwinangun
Berisi konstanta, konfigurasi default, dan settings aplikasi
"""

from datetime import datetime
import os

# ── Flask Configuration ──────────────────────────────────────────────────
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kdgwinangun_secret_key_2026'
    DB_NAME = os.environ.get('DATABASE_NAME') or 'database.db'

    # Upload Settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Session
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# ── Default Config (Database) ────────────────────────────────────────────
DEFAULT_CONFIG = {
    # Website Info
    "website_nama": "Desa Kedungwinangun",
    "website_tagline": "Selamat datang di website Kami",
    "website_deskripsi": "Eksplor semua tentang desa Kedungwinangun disini",
    "website_meta_description": "Website resmi Desa Kedungwinangun, Klirong, Kebumen",

    # Berita Settings
    "berita_tampil_di_beranda": "6",
    "berita_unggulan_tampil": "3",
    "berita_tampil_di_halaman": "12",
    "berita_tampilkan_views": "1",
    "berita_tampilkan_tanggal": "1",
    "berita_carousel_stacks": "2",

    # Homepage Sections
    "tampilkan_maps": "1",
    "tampilkan_statistik": "1",
    "tampilkan_daftar_dusun": "1",
    "tampilkan_hero": "1",

    # Kontak
    "kontak_whatsapp": "",
    "kontak_telepon": "",
    "kontak_email": "",
    "alamat_desa": "Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, Jawa Tengah",

    # Sosial Media
    "sosial_facebook": "",
    "sosial_instagram": "",
    "sosial_twitter": "",

    # Footer
    "footer_copyright": f"© {datetime.now().year} Desa Kedungwinangun. Hak Cipta Dilindungi.",
}

# ── Nav Links (Static) ─────────────────────────────────────────────────
NAV_LINKS = [
    {"label": "Beranda", "href": "/", "active": True},
    {"label": "Sejarah", "href": "/sejarah", "active": False},
    {"label": "Kependudukan", "href": "/info-kependudukan", "active": False},
    {"label": "Pengumuman", "href": "/pengumuman", "active": False},
    {"label": "Berita", "href": "/berita", "active": False},
    {"label": "Galeri", "href": "/galeri", "active": False},
    {"label": "Kontak", "href": "/kontak", "active": False},
]

# ── Data Static ────────────────────────────────────────────────────────
DUSUN_DATA = [
    {"nama": "Dusun Kedungwaru", "delay": "0.05s"},
    {"nama": "Dusun Perna", "delay": "0.12s"},
    {"nama": "Dusun Sasak", "delay": "0.19s"},
    {"nama": "Dusun Entak", "delay": "0.26s"},
    {"nama": "Dusun Grewing", "delay": "0.33s"},
    {"nama": "Dusun Pedana", "delay": "0.40s"},
]

MAPS_EMBED_URL = (
    "https://maps.google.com/maps?q=Kedungwinangun,+Klirong,+Kebumen"
    "&t=&z=13&ie=UTF8&iwloc=&output=embed"
)

# ── Role Definitions ───────────────────────────────────────────────────
ROLES = {
    'admin': 'Administrator',
    'dinas': 'Petugas Dinas',
    'penduduk': 'Penduduk'
}

# ── Default Users ───────────────────────────────────────────────────────
# Format: (login_id, nama_lengkap, password, role)
# - admin: username, nip: null
# - dinas: username: null, nip
# - warga: nik, username: null, nip: null
DEFAULT_USERS = [
    ('admin', 'Administrator', 'adminkedungwinangun', 'admin'),      # Admin: login pakai username
    ('admin001', 'Administrator 2', 'adminadmin', 'admin'),          # Admin 2
    ('199001012020011001', 'Petugas Dinas', 'dinas123', 'dinas'),  # Dinas: login pakai NIP
]

# ── SQL Schema ─────────────────────────────────────────────────────────
SQL_SCHEMA = '''
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nik TEXT UNIQUE NOT NULL,
    nama_lengkap TEXT NOT NULL,
    email TEXT,
    no_telepon TEXT,
    alamat TEXT,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'penduduk',
    status TEXT DEFAULT 'pending',
    ktp_path TEXT,
    kk_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER,
    approved_at TIMESTAMP
);

-- Berita
CREATE TABLE IF NOT EXISTS berita (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT NOT NULL,
    excerpt TEXT,
    kategori TEXT,
    badge_class TEXT DEFAULT 'badge-green',
    kategori_icon TEXT DEFAULT '📰',
    tanggal TEXT,
    views TEXT DEFAULT '0',
    gambar_url TEXT,
    gambar_alt TEXT,
    penulis TEXT DEFAULT 'Admin Desa Kedungwinangun',
    unggulan INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Config
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Pages (Custom Pages)
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    icon TEXT DEFAULT '📄',
    order_num INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Kritik dan Saran
CREATE TABLE IF NOT EXISTS kritik_saran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    email TEXT,
    telepon TEXT,
    subjek TEXT NOT NULL,
    kategori TEXT DEFAULT 'kritik',
    isi TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    is_responded INTEGER DEFAULT 0,
    responded_by INTEGER,
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
