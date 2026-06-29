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
    {"label": "Layanan Surat", "href": "/layanan", "active": False},
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

# ── Surat Katalog Default ──────────────────────────────────────────────
DEFAULT_JENIS_SURAT = [
    ('SKU', 'Surat Keterangan Usaha', 'Surat keterangan untuk pelaku usaha mikro dan kecil', 'ktp,kk', 1),
    ('SKTM', 'Surat Keterangan Tidak Mampu', 'Surat keterangan untuk keluarga kurang mampu', 'ktp,kk,surat_keterangan_rt', 1),
    ('SKCK', 'Surat Pengantar SKCK', 'Surat pengantar untuk membuat SKCK', 'ktp', 1),
    ('DOMISILI', 'Surat Keterangan Domisili', 'Surat keterangan tempat tinggal', 'ktp,kk', 1),
    ('BELUM_NIKAH', 'Surat Keterangan Belum Menikah', 'Surat keterangan belum pernah menikah', 'ktp,kk,surat_keterangan_rt', 1),
    ('LAHIR', 'Surat Keterangan Kelahiran', 'Surat keterangan bayi yang lahir', 'ktp_ayah,ktp_ibu,kk,surat_keterangan_bidan', 1),
    ('MATI', 'Surat Keterangan Kematian', 'Surat keterangan seseorang telah meninggal', 'ktp_almarhum,kk,surat_keterangan_kades', 1),
]

# ── Default Users ───────────────────────────────────────────────────────
DEFAULT_USERS = [
    ('ADMIN001', 'Administrator', 'adminkedungwinangun', 'admin'),
    ('DINAS001', 'Petugas Dinas', 'dinas123', 'dinas'),
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

-- Permohonan ACC (Registration Approvals)
CREATE TABLE IF NOT EXISTS permohonan_acc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    catatan TEXT,
    processed_by INTEGER,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Jenis Surat
CREATE TABLE IF NOT EXISTS jenis_surat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT UNIQUE NOT NULL,
    nama TEXT NOT NULL,
    deskripsi TEXT,
    required_docs TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permohonan Surat
CREATE TABLE IF NOT EXISTS permohonan_surat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    jenis_surat_id INTEGER NOT NULL,
    nomor_surat TEXT,
    data_json TEXT,
    status TEXT DEFAULT 'pending',
    catatan TEXT,
    file_surat TEXT,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (jenis_surat_id) REFERENCES jenis_surat (id)
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
'''
