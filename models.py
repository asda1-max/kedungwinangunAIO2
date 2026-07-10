"""
Database Models & Helpers
Berisi semua fungsi untuk berinteraksi dengan database

Error Handling:
    Semua error handling database sudah menggunakan database.py
    Import dari: from database import DatabaseError, db_fetch_one, db_fetch_all, etc.
"""

import sqlite3
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config, DEFAULT_CONFIG, DEFAULT_USERS
from database import (
    DatabaseError,
    db_fetch_one,
    db_fetch_all,
    db_execute,
    get_db_connection,
    get_db_error_message,
)

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# ── Database Error Handling ──────────────────────────────────────────────

def handle_db_error(error, operation="database operation", conn=None):
    """
    Handle database error dengan logging dan cleanup

    Args:
        error: Exception yang terjadi
        operation: Deskripsi operasi yang gagal
        conn: Database connection untuk cleanup

    Returns:
        str: User-friendly error message
    """
    return get_db_error_message(error)


# ── Database Connection ────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ── Database Migration ──────────────────────────────────────────────────
def migrate_database():
    """Migrate database schema from old version (NIK-based) to new version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Add new columns if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            logger.info("Added 'username' column to users table")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN nip TEXT")
            logger.info("Added 'nip' column to users table")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Migrate existing admin accounts (old nik -> username)
        cursor.execute("UPDATE users SET username = nik WHERE role = 'admin' AND username IS NULL")
        migrated_admins = cursor.rowcount

        # Migrate existing dinas accounts (old nik -> nip)
        cursor.execute("UPDATE users SET nip = nik WHERE role = 'dinas' AND nip IS NULL")
        migrated_dinas = cursor.rowcount

        # ── NEW TABLES MIGRATION ────────────────────────────────────────
        
        # Aduan table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aduan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_aduan TEXT UNIQUE,
                nama TEXT NOT NULL,
                email TEXT,
                telepon TEXT,
                nik TEXT,
                alamat TEXT,
                dusun TEXT,
                judul TEXT NOT NULL,
                kategori TEXT DEFAULT 'infrastruktur',
                lokasi TEXT,
                isi TEXT NOT NULL,
                lampiran TEXT,
                status TEXT DEFAULT 'pending',
                tanggapan TEXT,
                responded_by INTEGER,
                responded_at TIMESTAMP,
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Table 'aduan' ready")

        # Program Kerja table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS program_kerja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT DEFAULT 'pembangunan',
                tahun INTEGER,
                tahun_mulai INTEGER,
                tahun_selesai INTEGER,
                target TEXT,
                realiasi TEXT,
                sasaran TEXT,
                anggaran INTEGER DEFAULT 0,
                icon TEXT DEFAULT '📋',
                deskripsi TEXT,
                status TEXT DEFAULT 'rencana',
                progress INTEGER DEFAULT 0,
                aktif INTEGER DEFAULT 1,
                urutan INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Table 'program_kerja' ready")

        # Agenda table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                deskripsi TEXT,
                tanggal DATE NOT NULL,
                tanggal_mulai DATE,
                waktu TEXT,
                lokasi TEXT,
                icon TEXT DEFAULT '📅',
                kategori TEXT DEFAULT 'umum',
                penanggung_jawab TEXT,
                peserta TEXT,
                status TEXT DEFAULT 'akan_datang',
                urutan INTEGER DEFAULT 0,
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Table 'agenda' ready")
        
        conn.commit()
        conn.close()

        if migrated_admins > 0 or migrated_dinas > 0:
            logger.info(f"Migrated {migrated_admins} admin(s) and {migrated_dinas} dinas account(s)")
        else:
            logger.info("No migration needed or all accounts already migrated")

        return True
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        return False

# ── Database Initialization ────────────────────────────────────────────
def init_database():
    """Initialize database with all tables and default data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Run migration first
        migrate_database()

        # Execute schema
        cursor.executescript('''
            -- Users Table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT,
                username TEXT,
                nip TEXT,
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
                video_url TEXT,
                penulis TEXT DEFAULT 'Admin Desa Kedungwinangun',
                unggulan INTEGER DEFAULT 0,
                facebook_auto_post INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Sejarah Desa
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

            -- Config
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            -- Galeri
            CREATE TABLE IF NOT EXISTS galeri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                deskripsi TEXT,
                kategori TEXT DEFAULT 'galeri',
                gambar_url TEXT NOT NULL,
                gambar_alt TEXT,
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            -- Komentar Berita
            CREATE TABLE IF NOT EXISTS komentar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                berita_id INTEGER NOT NULL,
                parent_id INTEGER,
                user_id INTEGER,
                nama_pengirim TEXT NOT NULL,
                konten TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (berita_id) REFERENCES berita(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES komentar(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            -- Struktur Organisasi (Enhanced)
            CREATE TABLE IF NOT EXISTS struktur_organisasi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategori TEXT NOT NULL,
                nama TEXT NOT NULL,
                jabatan TEXT,
                deskripsi TEXT,
                nik TEXT,
                alamat TEXT,
                dusun TEXT,
                rt TEXT,
                rw TEXT,
                telepon TEXT,
                email TEXT,
                foto_url TEXT,
                sk_url TEXT,
                no_sk TEXT,
                tanggal_sk TEXT,
                masa_jabatan TEXT,
                status TEXT DEFAULT 'Aktif',
                icon TEXT,
                no_urut INTEGER DEFAULT 0,
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- UMKM (Usaha Mikro Kecil Menengah)
            CREATE TABLE IF NOT EXISTS umkm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                deskripsi TEXT,
                kategori TEXT DEFAULT 'umum',
                pemiliki_nama TEXT,
                pemiliki_kontak TEXT,
                alamat TEXT,
                dusun TEXT,
                rt TEXT,
                rw TEXT,
                latitude REAL,
                longitude REAL,
                foto_url TEXT,
                produk_jasa TEXT,
                harga_range TEXT,
                jam_operasional TEXT,
                aktif INTEGER DEFAULT 1,
                urutan INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Info Kependudukan
            CREATE TABLE IF NOT EXISTS kependudukan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategori TEXT NOT NULL,
                label TEXT NOT NULL,
                jumlah INTEGER DEFAULT 0,
                satuan TEXT DEFAULT 'orang',
                tahun INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Pengumuman
            CREATE TABLE IF NOT EXISTS pengumuman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                isi TEXT NOT NULL,
                kategori TEXT DEFAULT 'umum',
                is_penting INTEGER DEFAULT 0,
                lampiran TEXT,
                author TEXT DEFAULT 'Pemerintahan Desa',
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- APBDes
            CREATE TABLE IF NOT EXISTS apbdes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tahun INTEGER NOT NULL,
                jenis TEXT NOT NULL,
                nama TEXT NOT NULL,
                icon TEXT DEFAULT '📄',
                jumlah INTEGER DEFAULT 0,
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- APBDes Summary
            CREATE TABLE IF NOT EXISTS apbdes_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tahun INTEGER NOT NULL,
                total_pendapatan INTEGER DEFAULT 0,
                total_belanja INTEGER DEFAULT 0,
                pembiayaan_net INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Potensi Desa
            CREATE TABLE IF NOT EXISTS potensi_desa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL,
                deskripsi TEXT,
                gambar_url TEXT,
                icon TEXT,
                aktif INTEGER DEFAULT 1,
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

            -- Aduan Publik
            CREATE TABLE IF NOT EXISTS aduan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_aduan TEXT UNIQUE,
                nama TEXT NOT NULL,
                email TEXT,
                telepon TEXT,
                nik TEXT,
                alamat TEXT,
                dusun TEXT,
                judul TEXT NOT NULL,
                kategori TEXT DEFAULT 'infrastruktur',
                lokasi TEXT,
                deskripsi TEXT NOT NULL,
                lampiran_url TEXT,
                status TEXT DEFAULT 'menunggu',
                prioritas TEXT DEFAULT 'normal',
                responded_by INTEGER,
                responded_at TIMESTAMP,
                catatan TEXT,
                aktif INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Program Kerja Desa
            CREATE TABLE IF NOT EXISTS program_kerja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                deskripsi TEXT,
                kategori TEXT DEFAULT 'pembangunan',
                tahun INTEGER,
                target TEXT,
                realiasi TEXT,
                anggaran TEXT,
                icon TEXT DEFAULT '📋',
                status TEXT DEFAULT 'berlangsung',
                aktif INTEGER DEFAULT 1,
                urutan INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Login Attempts (Brute Force Protection)
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 0
            );

            -- Agenda Desa (Timeline)
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                deskripsi TEXT,
                kategori TEXT DEFAULT 'kegiatan',
                tanggal_mulai DATE,
                tanggal_selesai DATE,
                waktu TEXT,
                lokasi TEXT,
                icon TEXT DEFAULT '📅',
                penanggung_jawab TEXT,
                peserta TEXT,
                status TEXT DEFAULT 'akan_datang',
                aktif INTEGER DEFAULT 1,
                urutan INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Insert default config
        for key, value in DEFAULT_CONFIG.items():
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))

        # Insert default users (updated: admin uses username, dinas uses nip)
        for login_id, nama, password, role in DEFAULT_USERS:
            # Check if user already exists based on role type
            if role == 'admin':
                cursor.execute('SELECT * FROM users WHERE username = ?', (login_id,))
            elif role == 'dinas':
                cursor.execute('SELECT * FROM users WHERE nip = ?', (login_id,))
            else:
                cursor.execute('SELECT * FROM users WHERE role = ?', (role,))
            
            if not cursor.fetchone():
                hashed = generate_password_hash(password)
                if role == 'admin':
                    cursor.execute('''
                        INSERT INTO users (username, nama_lengkap, password_hash, role, status, approved_by, approved_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (login_id, nama, hashed, role, 'approved', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                elif role == 'dinas':
                    cursor.execute('''
                        INSERT INTO users (nip, nama_lengkap, password_hash, role, status, approved_by, approved_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (login_id, nama, hashed, role, 'approved', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


# ════════════════════════════════════════════════════════════════════════
# ── CONFIG HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_config(key, default=None):
    """Ambil satu nilai konfigurasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else (default if default is not None else DEFAULT_CONFIG.get(key, ''))
    except Exception as e:
        logger.error(f"Error getting config '{key}': {str(e)}")
        return default if default is not None else DEFAULT_CONFIG.get(key, '')

def get_all_config():
    """Ambil semua konfigurasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM config')
        rows = cursor.fetchall()
        conn.close()
        config = {row['key']: row['value'] for row in rows}
        # Fill missing keys with defaults
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except Exception as e:
        logger.error(f"Error getting all config: {str(e)}")
        return DEFAULT_CONFIG.copy()

def update_config(key, value):
    """Update satu konfigurasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating config '{key}': {str(e)}")
        return False

def get_desa_info():
    """Ambil info desa untuk template"""
    return {
        "nama": get_config("website_nama", DEFAULT_CONFIG["website_nama"]),
        "tagline": get_config("website_tagline", DEFAULT_CONFIG["website_tagline"]),
        "deskripsi": get_config("website_deskripsi", DEFAULT_CONFIG["website_deskripsi"]),
        "jumlah_dusun": 8,
        "jumlah_kadus": 6,
        "jumlah_kasi": 3,
        "jumlah_kaur": 3,
        "jumlah_sekdes": 1,
        "jumlah_kepala_desa": 1,
    }


# ════════════════════════════════════════════════════════════════════════
# ── USER HELPERS ───────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_user_by_username(username):
    """Ambil user berdasarkan username (untuk admin)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # First try username field
        cursor.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, 'admin'))
        user = cursor.fetchone()
        # Fallback: check old nik field for admin (backward compatibility)
        if not user:
            cursor.execute('SELECT * FROM users WHERE nik = ? AND role = ?', (username, 'admin'))
            user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}")
        return None

def get_user_by_nip(nip):
    """Ambil user berdasarkan NIP (untuk dinas)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # First try nip field
        cursor.execute('SELECT * FROM users WHERE nip = ? AND role = ?', (nip, 'dinas'))
        user = cursor.fetchone()
        # Fallback: check old nik field for dinas (backward compatibility)
        if not user:
            cursor.execute('SELECT * FROM users WHERE nik = ? AND role = ?', (nip, 'dinas'))
            user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user by NIP: {str(e)}")
        return None

def get_user_by_id(user_id):
    """Ambil user berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {str(e)}")
        return None



# ════════════════════════════════════════════════════════════════════════
# ── LOGIN ATTEMPT HELPERS (Brute Force Protection) ─────────────────────
# ════════════════════════════════════════════════════════════════════════

def record_login_attempt(identifier, ip_address, success=False):
    """Catat percobaan login ke database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO login_attempts (identifier, ip_address, success, attempted_at)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        ''', (identifier, ip_address, 1 if success else 0))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error recording login attempt: {str(e)}")
        return False

def get_recent_login_attempts(identifier, ip_address, window_minutes=15):
    """Hitung jumlah percobaan login gagal dalam window tertentu"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM login_attempts
            WHERE success = 0
            AND identifier = ?
            AND ip_address = ?
            AND attempted_at > datetime('now', 'localtime', ?)
        ''', (identifier, ip_address, f'-{window_minutes} minutes'))
        row = cursor.fetchone()
        conn.close()
        return row['count'] if row else 0
    except Exception as e:
        logger.error(f"Error counting login attempts: {str(e)}")
        return 0

def is_login_locked(identifier, ip_address, max_attempts=5, window_minutes=15):
    """Cek apakah login terkunci karena terlalu banyak gagal"""
    attempts = get_recent_login_attempts(identifier, ip_address, window_minutes)
    return attempts >= max_attempts

def clear_login_attempts(identifier):
    """Hapus catatan percobaan login setelah berhasil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM login_attempts WHERE identifier = ?', (identifier,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error clearing login attempts: {str(e)}")
        return False

def clean_old_login_attempts(days=7):
    """Hapus percobaan login yang sudah lama (maintenance)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM login_attempts
            WHERE attempted_at < datetime('now', 'localtime', ?)
        ''', (f'-{days} days',))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error cleaning old login attempts: {str(e)}")
        return False


def register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path=None, kk_path=None):
    """Registrasi user baru"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (nik, nama_lengkap, email, no_telepon, alamat, password_hash, ktp_path, kk_path, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nik, nama_lengkap, email, no_telepon, alamat, hashed, ktp_path, kk_path, 'penduduk', 'pending'))
        user_id = cursor.lastrowid

        # Create approval record
        cursor.execute('''
            INSERT INTO permohonan_acc (user_id, status, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()
        return True, "Pendaftaran berhasil! Mohon tunggu persetujuan dari petugas dinas."
    except sqlite3.IntegrityError as e:
        if conn:
            conn.rollback()
            conn.close()
        msg = handle_db_error(e, "register_user")
        return False, msg
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"Error registering user: {str(e)}")
        return False, "Terjadi kesalahan saat registrasi. Silakan coba lagi."

def get_pending_users():
    """Ambil semua user pending"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE status = ? ORDER BY created_at DESC', ('pending',))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting pending users: {str(e)}")
        return []

def get_all_warga():
    """Ambil semua warga (role=penduduk)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', ('penduduk',))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting all warga: {str(e)}")
        return []

def get_all_warga_approved():
    """Ambil semua warga yang sudah disetujui"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE role = ? AND status = ? ORDER BY created_at DESC", ('penduduk', 'approved'))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting approved warga: {str(e)}")
        return []

# ════════════════════════════════════════════════════════════════════════
# ── ACCOUNT CENTER HELPERS ─────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_users():
    """Ambil semua user (admin, dinas, penduduk)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY role, created_at DESC')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

def get_users_by_role(role):
    """Ambil user berdasarkan role"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', (role,))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting users by role {role}: {str(e)}")
        return []

def get_user_stats():
    """Ambil statistik user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        stats = {}
        # Total users
        cursor.execute('SELECT COUNT(*) as count FROM users')
        stats['total'] = cursor.fetchone()['count']
        # By role
        cursor.execute('SELECT role, COUNT(*) as count FROM users GROUP BY role')
        stats['by_role'] = {row['role']: row['count'] for row in cursor.fetchall()}
        # By status
        cursor.execute('SELECT status, COUNT(*) as count FROM users GROUP BY status')
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        conn.close()
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return {'total': 0, 'by_role': {}, 'by_status': {}}

def update_user_data(user_id, data):
    """Update data user (bukan role)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Build update query dynamically
        allowed_fields = ['nama_lengkap', 'email', 'no_telepon', 'alamat']
        updates = []
        values = []
        for key, value in data.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if updates:
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating user data {user_id}: {str(e)}")
        return False

def update_user_role(user_id, new_role, updated_by):
    """Update role user"""
    try:
        if new_role not in ['admin', 'dinas', 'penduduk']:
            return False
        conn = get_db_connection()
        cursor = conn.cursor()
        # Set status to approved automatically when promoted
        cursor.execute('''
            UPDATE users SET role = ?, status = 'approved', approved_by = ?, approved_at = ? WHERE id = ?
        ''', (new_role, updated_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating user role {user_id}: {str(e)}")
        return False

def update_user_password(user_id, new_password):
    """Update password user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating user password {user_id}: {str(e)}")
        return False

def delete_user_account(user_id):
    """Hapus user account"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if user has any permits
        cursor.execute('SELECT COUNT(*) as count FROM permohonan_surat WHERE user_id = ?', (user_id,))
        if cursor.fetchone()['count'] > 0:
            # Just mark as rejected instead of deleting
            cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('deleted', user_id))
        else:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return False

def create_staff_account(login_id, nama_lengkap, password, role):
    """Buat akun admin/dinas baru langsung tanpa approval"""
    try:
        if role not in ['admin', 'dinas']:
            return False, "Role tidak valid"

        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = generate_password_hash(password)

        if role == 'admin':
            cursor.execute('''
                INSERT INTO users (username, nama_lengkap, password_hash, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (login_id, nama_lengkap, hashed, role, 'approved', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        elif role == 'dinas':
            cursor.execute('''
                INSERT INTO users (nip, nama_lengkap, password_hash, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (login_id, nama_lengkap, hashed, role, 'approved', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError as e:
        logger.error(f"Login ID already exists: {login_id}")
        return False, "ID Login sudah terdaftar"
    except Exception as e:
        logger.error(f"Error creating staff account: {str(e)}")
        return False, str(e)


# ════════════════════════════════════════════════════════════════════════
# ── BERITA HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_berita():
    """Ambil semua berita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM berita ORDER BY created_at DESC')
        berita = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return berita
    except Exception as e:
        logger.error(f"Error getting all berita: {str(e)}")
        return []

def get_berita_by_id(berita_id):
    """Ambil berita berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM berita WHERE id = ?', (berita_id,))
        berita = cursor.fetchone()
        conn.close()
        return dict(berita) if berita else None
    except Exception as e:
        logger.error(f"Error getting berita {berita_id}: {str(e)}")
        return None

def add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url='', facebook_auto_post=0, unggulan=0):
    """Tambah berita baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        tanggal = datetime.now().strftime("%d %b %Y")
        cursor.execute('''
            INSERT INTO berita (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, views, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, "0", gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding berita: {str(e)}")
        return False

def update_berita(berita_id, judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url='', facebook_auto_post=0, unggulan=0):
    """Update berita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE berita SET judul = ?, excerpt = ?, kategori = ?, badge_class = ?, kategori_icon = ?, gambar_url = ?, gambar_alt = ?, video_url = ?, facebook_auto_post = ?, unggulan = ?
            WHERE id = ?
        ''', (judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan, berita_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating berita {berita_id}: {str(e)}")
        return False

def delete_berita(berita_id):
    """Hapus berita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM berita WHERE id = ?', (berita_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting berita {berita_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── SEJARAH DESA HELPERS ──────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_sejarah(aktif=None):
    """Ambil semua entries sejarah desa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM sejarah_desa WHERE aktif = ? ORDER BY urutan ASC, tahun_dari ASC', (aktif,))
        else:
            cursor.execute('SELECT * FROM sejarah_desa ORDER BY urutan ASC, tahun_dari ASC')
        sejarah = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sejarah
    except Exception as e:
        logger.error(f"Error getting all sejarah: {str(e)}")
        return []

def get_sejarah_by_id(sejarah_id):
    """Ambil satu entry sejarah berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sejarah_desa WHERE id = ?', (sejarah_id,))
        sejarah = cursor.fetchone()
        conn.close()
        return dict(sejarah) if sejarah else None
    except Exception as e:
        logger.error(f"Error getting sejarah {sejarah_id}: {str(e)}")
        return None

def add_sejarah(judul, konten, kategori='sejarah', tahun_dari=None, tahun_sampai=None,
                gambar_url='', gambar_alt='', video_url='', sub_judul='', urutan=0):
    """Tambah entry sejarah baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sejarah_desa (judul, sub_judul, konten, kategori, tahun_dari, tahun_sampai,
                                    gambar_url, gambar_alt, video_url, aktif, urutan, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
        ''', (judul, sub_judul, konten, kategori, tahun_dari, tahun_sampai, gambar_url, gambar_alt,
              video_url, urutan, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding sejarah: {str(e)}")
        return False

def update_sejarah(sejarah_id, judul, konten, kategori='sejarah', tahun_dari=None, tahun_sampai=None,
                   gambar_url='', gambar_alt='', video_url='', sub_judul='', aktif=1, urutan=0):
    """Update entry sejarah"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sejarah_desa
            SET judul = ?, sub_judul = ?, konten = ?, kategori = ?, tahun_dari = ?, tahun_sampai = ?,
                gambar_url = ?, gambar_alt = ?, video_url = ?, aktif = ?, urutan = ?, updated_at = ?
            WHERE id = ?
        ''', (judul, sub_judul, konten, kategori, tahun_dari, tahun_sampai, gambar_url, gambar_alt,
              video_url, aktif, urutan, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sejarah_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating sejarah {sejarah_id}: {str(e)}")
        return False

def delete_sejarah(sejarah_id):
    """Hapus entry sejarah"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sejarah_desa WHERE id = ?', (sejarah_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting sejarah {sejarah_id}: {str(e)}")
        return False

def toggle_sejarah_aktif(sejarah_id):
    """Toggle aktif status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE sejarah_desa SET aktif = NOT aktif WHERE id = ?', (sejarah_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling sejarah {sejarah_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── GALERI HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_galeri(aktif=None):
    """Ambil semua foto galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM galeri WHERE aktif = ? ORDER BY created_at DESC', (aktif,))
        else:
            cursor.execute('SELECT * FROM galeri ORDER BY created_at DESC')
        galeri = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return galeri
    except Exception as e:
        logger.error(f"Error getting all galeri: {str(e)}")
        return []

def get_galeri_by_id(galeri_id):
    """Ambil satu foto galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM galeri WHERE id = ?', (galeri_id,))
        galeri = cursor.fetchone()
        conn.close()
        return dict(galeri) if galeri else None
    except Exception as e:
        logger.error(f"Error getting galeri {galeri_id}: {str(e)}")
        return None

def add_galeri(judul, gambar_url, deskripsi='', kategori='galeri', gambar_alt=''):
    """Tambah foto galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO galeri (judul, deskripsi, kategori, gambar_url, gambar_alt)
            VALUES (?, ?, ?, ?, ?)
        ''', (judul, deskripsi, kategori, gambar_url, gambar_alt))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding galeri: {str(e)}")
        return False

def update_galeri(galeri_id, judul, gambar_url, deskripsi, kategori, gambar_alt):
    """Update foto galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE galeri SET judul = ?, deskripsi = ?, kategori = ?, gambar_url = ?, gambar_alt = ?
            WHERE id = ?
        ''', (judul, deskripsi, kategori, gambar_url, gambar_alt, galeri_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating galeri {galeri_id}: {str(e)}")
        return False

def delete_galeri(galeri_id):
    """Hapus foto galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM galeri WHERE id = ?', (galeri_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting galeri {galeri_id}: {str(e)}")
        return False

def toggle_galeri_aktif(galeri_id):
    """Toggle status aktif/nonaktif galeri"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE galeri SET aktif = CASE WHEN aktif = 1 THEN 0 ELSE 1 END WHERE id = ?', (galeri_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling galeri {galeri_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── CUSTOM PAGES HELPERS ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_pages():
    """Ambil semua page aktif"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE active = 1 ORDER BY order_num ASC, title ASC')
        pages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pages
    except Exception as e:
        logger.error(f"Error getting all pages: {str(e)}")
        return []

def get_page_by_slug(slug):
    """Ambil page berdasarkan slug"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE slug = ? AND active = 1', (slug,))
        page = cursor.fetchone()
        conn.close()
        return dict(page) if page else None
    except Exception as e:
        logger.error(f"Error getting page by slug '{slug}': {str(e)}")
        return None

def get_page_by_id(page_id):
    """Ambil page berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = cursor.fetchone()
        conn.close()
        return dict(page) if page else None
    except Exception as e:
        logger.error(f"Error getting page by id {page_id}: {str(e)}")
        return None

def get_all_pages_admin():
    """Ambil semua page (termasuk nonaktif) untuk admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages ORDER BY order_num ASC, title ASC')
        pages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pages
    except Exception as e:
        logger.error(f"Error getting all pages admin: {str(e)}")
        return []

def add_page(title, slug, content, icon='📄'):
    """Tambah page baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get max order
        cursor.execute('SELECT MAX(order_num) as max_order FROM pages')
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1

        cursor.execute('''
            INSERT INTO pages (title, slug, content, icon, order_num, active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (title, slug, content, icon, max_order))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding page: {str(e)}")
        return False

def update_page(page_id, title, slug, content, icon, order_num, active):
    """Update page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pages SET title = ?, slug = ?, content = ?, icon = ?, order_num = ?, active = ?
            WHERE id = ?
        ''', (title, slug, content, icon, order_num, active, page_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating page {page_id}: {str(e)}")
        return False

def delete_page(page_id):
    """Hapus page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting page {page_id}: {str(e)}")
        return False

def toggle_page_active(page_id):
    """Toggle status aktif page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE pages SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?', (page_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling page {page_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── KOMENTAR HELPERS ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_komentar_by_berita(berita_id):
    """Ambil semua komentar untuk sebuah berita (flat list)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT k.*, u.nama_lengkap, u.role
            FROM komentar k
            LEFT JOIN users u ON k.user_id = u.id
            WHERE k.berita_id = ?
            ORDER BY k.created_at ASC
        ''', (berita_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting komentar for berita {berita_id}: {str(e)}")
        return []

def build_comment_tree(flat_comments):
    """Konversi flat list komentar -> nested tree untuk rendering Reddit-style"""
    lookup = {}
    for c in flat_comments:
        lookup[c['id']] = {**c, 'children': []}
    roots = []
    for comment in flat_comments:
        node = lookup[comment['id']]
        if comment['parent_id'] is None:
            roots.append(node)
        else:
            parent = lookup.get(comment['parent_id'])
            if parent:
                parent['children'].append(node)
    return roots

def create_komentar(berita_id, konten, nama_pengirim, parent_id=None, user_id=None):
    """Buat komentar baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO komentar (berita_id, parent_id, user_id, nama_pengirim, konten)
            VALUES (?, ?, ?, ?, ?)
        ''', (berita_id, parent_id, user_id, nama_pengirim, konten))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating komentar: {str(e)}")
        return False

def delete_komentar(komentar_id):
    """Hapus komentar beserta semua child-nya (recursive delete via FK cascade)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # FK cascade ON DELETE CASCADE akan handle child comment otomatis,
        # tapi kita hapus manual untuk memastikan bersih
        cursor.execute('DELETE FROM komentar WHERE id = ?', (komentar_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting komentar {komentar_id}: {str(e)}")
        return False

def get_komentar_by_id(komentar_id):
    """Ambil satu komentar berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM komentar WHERE id = ?', (komentar_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting komentar {komentar_id}: {str(e)}")
        return None

def count_komentar_by_berita(berita_id):
    """Hitung jumlah komentar untuk sebuah berita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as cnt FROM komentar WHERE berita_id = ?', (berita_id,))
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0
    except Exception as e:
        logger.error(f"Error counting komentar for berita {berita_id}: {str(e)}")
        return 0


# ════════════════════════════════════════════════════════════════════════
# ── STRUKTUR ORGANISASI HELPERS ───────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_struktur(aktif=None):
    """Ambil semua struktur organisasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM struktur_organisasi WHERE aktif = ? ORDER BY kategori, no_urut ASC', (aktif,))
        else:
            cursor.execute('SELECT * FROM struktur_organisasi ORDER BY kategori, no_urut ASC')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all struktur: {str(e)}")
        return []

def get_struktur_for_geojson(aktif=1):
    """Get struktur organisasi data formatted as GeoJSON features (only those with coordinates)"""
    try:
        items = get_all_struktur(aktif=aktif)
        features = []
        for item in items:
            if item.get('latitude') and item.get('longitude'):
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [item['longitude'], item['latitude']]
                    },
                    'properties': {
                        'id': item['id'],
                        'nama': item['nama'],
                        'jabatan': item['jabatan'] or '',
                        'kategori': item['kategori'] or '',
                        'nik': item['nik'] or '',
                        'alamat': item['alamat'] or '',
                        'dusun': item['dusun'] or '',
                        'telepon': item['telepon'] or '',
                        'email': item['email'] or '',
                        'foto_url': item['foto_url'] or '',
                    }
                })
        return {'type': 'FeatureCollection', 'features': features}
    except Exception as e:
        logger.error(f"Error getting struktur geojson: {str(e)}")
        return {'type': 'FeatureCollection', 'features': []}

def get_struktur_by_kategori(kategori, aktif=None):
    """Ambil struktur berdasarkan kategori"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM struktur_organisasi WHERE kategori = ? AND aktif = ? ORDER BY no_urut ASC', (kategori, aktif))
        else:
            cursor.execute('SELECT * FROM struktur_organisasi WHERE kategori = ? ORDER BY no_urut ASC', (kategori,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting struktur by kategori '{kategori}': {str(e)}")
        return []

def get_struktur_by_id(struktur_id):
    """Ambil satu struktur berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM struktur_organisasi WHERE id = ?', (struktur_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting struktur by id {struktur_id}: {str(e)}")
        return None

def add_struktur(kategori, nama, jabatan='', deskripsi='', nik='', alamat='', dusun='', rt='', rw='',
                 telepon='', email='', foto_url='', sk_url='', no_sk='', tanggal_sk='', masa_jabatan='', status='Aktif', icon='', aktif=1):
    """Tambah struktur organisasi dengan detail lengkap"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(no_urut) as max_order FROM struktur_organisasi WHERE kategori = ?', (kategori,))
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1

        cursor.execute('''
            INSERT INTO struktur_organisasi (kategori, nama, jabatan, deskripsi, nik, alamat, dusun, rt, rw,
                telepon, email, foto_url, sk_url, no_sk, tanggal_sk, masa_jabatan, status, icon, no_urut, aktif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (kategori, nama, jabatan, deskripsi, nik, alamat, dusun, rt, rw,
              telepon, email, foto_url, sk_url, no_sk, tanggal_sk, masa_jabatan, status, icon, max_order, aktif))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding struktur: {str(e)}")
        return False

def update_struktur(struktur_id, kategori, nama, jabatan='', deskripsi='', nik='', alamat='', dusun='', rt='', rw='',
                   telepon='', email='', foto_url='', sk_url='', no_sk='', tanggal_sk='', masa_jabatan='',
                   status='Aktif', icon='', aktif=1, no_urut=0):
    """Update struktur organisasi dengan detail lengkap"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE struktur_organisasi SET kategori = ?, nama = ?, jabatan = ?, deskripsi = ?,
                nik = ?, alamat = ?, dusun = ?, rt = ?, rw = ?, telepon = ?, email = ?,
                foto_url = ?, sk_url = ?, no_sk = ?, tanggal_sk = ?, masa_jabatan = ?,
                status = ?, icon = ?, aktif = ?, no_urut = ?, updated_at = ?
            WHERE id = ?
        ''', (kategori, nama, jabatan, deskripsi, nik, alamat, dusun, rt, rw,
              telepon, email, foto_url, sk_url, no_sk, tanggal_sk, masa_jabatan,
              status, icon, aktif, no_urut, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), struktur_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating struktur {struktur_id}: {str(e)}")
        return False

def delete_struktur(struktur_id):
    """Hapus struktur organisasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM struktur_organisasi WHERE id = ?', (struktur_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting struktur {struktur_id}: {str(e)}")
        return False

def batch_import_struktur(csv_data):
    """Batch import struktur organisasi dari CSV string"""
    import csv
    import io
    results = {'success': 0, 'errors': [], 'total': 0}
    
    try:
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        results['total'] = len(rows)
        
        for i, row in enumerate(rows):
            try:
                # Required fields
                kategori = row.get('kategori', '').strip().lower()
                nama = row.get('nama', '').strip()
                
                if not nama:
                    results['errors'].append(f"Baris {i+2}: Nama wajib diisi")
                    continue
                
                if kategori not in ['perangkat', 'bpd', 'pkk', 'karang_taruna', 'rt', 'rw']:
                    results['errors'].append(f"Baris {i+2}: Kategori '{kategori}' tidak valid")
                    continue
                
                # Optional fields
                jabatan = row.get('jabatan', '').strip()
                nik = row.get('nik', '').strip()
                alamat = row.get('alamat', '').strip()
                dusun = row.get('dusun', '').strip()
                rt = row.get('rt', '').strip()
                rw = row.get('rw', '').strip()
                telepon = row.get('telepon', '').strip()
                email = row.get('email', '').strip()
                status = row.get('status', 'Aktif').strip()
                aktif = 1 if row.get('aktif', '1').strip() in ['1', 'true', 'yes', 'aktif'] else 0
                
                add_struktur(
                    kategori=kategori,
                    nama=nama,
                    jabatan=jabatan,
                    nik=nik,
                    alamat=alamat,
                    dusun=dusun,
                    rt=rt,
                    rw=rw,
                    telepon=telepon,
                    email=email,
                    status=status,
                    aktif=aktif
                )
                results['success'] += 1
                
            except Exception as e:
                results['errors'].append(f"Baris {i+2}: {str(e)}")
        
        return results
        
    except Exception as e:
        results['errors'].append(f"Error parsing CSV: {str(e)}")
        return results

def toggle_struktur_aktif(struktur_id):
    """Toggle aktif status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE struktur_organisasi SET aktif = NOT aktif WHERE id = ?', (struktur_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling struktur {struktur_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── UMKM HELPERS ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_umkm(aktif=None, kategori=None):
    """Ambil semua data UMKM"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM umkm WHERE 1=1'
        params = []
        if aktif is not None:
            query += ' AND aktif = ?'
            params.append(aktif)
        if kategori:
            query += ' AND kategori = ?'
            params.append(kategori)
        query += ' ORDER BY urutan ASC, nama ASC'
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all umkm: {str(e)}")
        return []

def get_umkm_by_id(umkm_id):
    """Ambil satu UMKM berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM umkm WHERE id = ?', (umkm_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting umkm {umkm_id}: {str(e)}")
        return None

def add_umkm(nama, kategori='umum', deskripsi='', pemiliki_nama='', pemiliki_kontak='',
              alamat='', dusun='', rt='', rw='', latitude=None, longitude=None,
              foto_url='', produk_jasa='', harga_range='', jam_operasional=''):
    """Tambah data UMKM baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(urutan) as max_order FROM umkm')
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1
        cursor.execute('''
            INSERT INTO umkm (nama, kategori, deskripsi, pemiliki_nama, pemiliki_kontak,
                alamat, dusun, rt, rw, latitude, longitude, foto_url, produk_jasa,
                harga_range, jam_operasional, aktif, urutan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (nama, kategori, deskripsi, pemiliki_nama, pemiliki_kontak,
              alamat, dusun, rt, rw, latitude, longitude, foto_url, produk_jasa,
              harga_range, jam_operasional, max_order))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding umkm: {str(e)}")
        return False

def update_umkm(umkm_id, nama, kategori='umum', deskripsi='', pemiliki_nama='', pemiliki_kontak='',
                alamat='', dusun='', rt='', rw='', latitude=None, longitude=None,
                foto_url='', produk_jasa='', harga_range='', jam_operasional='',
                aktif=1, urutan=0):
    """Update data UMKM"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE umkm SET nama = ?, kategori = ?, deskripsi = ?, pemiliki_nama = ?,
                pemiliki_kontak = ?, alamat = ?, dusun = ?, rt = ?, rw = ?,
                latitude = ?, longitude = ?, foto_url = ?, produk_jasa = ?,
                harga_range = ?, jam_operasional = ?, aktif = ?, urutan = ?,
                updated_at = ?
            WHERE id = ?
        ''', (nama, kategori, deskripsi, pemiliki_nama, pemiliki_kontak,
              alamat, dusun, rt, rw, latitude, longitude, foto_url, produk_jasa,
              harga_range, jam_operasional, aktif, urutan,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"), umkm_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating umkm {umkm_id}: {str(e)}")
        return False

def delete_umkm(umkm_id):
    """Hapus data UMKM"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM umkm WHERE id = ?', (umkm_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting umkm {umkm_id}: {str(e)}")
        return False

def toggle_umkm_aktif(umkm_id):
    """Toggle aktif status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE umkm SET aktif = NOT aktif WHERE id = ?', (umkm_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling umkm {umkm_id}: {str(e)}")
        return False

def get_umkm_for_geojson(aktif=1):
    """Get UMKM data formatted as GeoJSON features"""
    try:
        items = get_all_umkm(aktif=aktif)
        features = []
        for item in items:
            if item.get('latitude') and item.get('longitude'):
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [item['longitude'], item['latitude']]
                    },
                    'properties': {
                        'id': item['id'],
                        'nama': item['nama'],
                        'kategori': item['kategori'],
                        'deskripsi': item['deskripsi'] or '',
                        'pemiliki': item['pemiliki_nama'] or '',
                        'alamat': item['alamat'] or '',
                        'dusun': item['dusun'] or '',
                        'kontak': item['pemiliki_kontak'] or '',
                        'foto': item['foto_url'] or '',
                        'harga': item['harga_range'] or '',
                    }
                })
        return {'type': 'FeatureCollection', 'features': features}
    except Exception as e:
        logger.error(f"Error getting geojson: {str(e)}")
        return {'type': 'FeatureCollection', 'features': []}



# ════════════════════════════════════════════════════════════════════════
# ── PENGUMUMAN HELPERS ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_pengumuman(aktif=None):
    """Ambil semua pengumuman"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM pengumuman WHERE aktif = ? ORDER BY created_at DESC', (aktif,))
        else:
            cursor.execute('SELECT * FROM pengumuman ORDER BY created_at DESC')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all pengumuman: {str(e)}")
        return []

# KEPENDUDUKAN
def update_kependudukan(kategori, label, jumlah, satuan='orang', tahun=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM kependudukan WHERE kategori = ? AND label = ?', (kategori, label))
        existing = cursor.fetchone()
        if existing:
            cursor.execute('UPDATE kependudukan SET jumlah = ?, satuan = ?, tahun = ? WHERE kategori = ? AND label = ?', (jumlah, satuan, tahun, kategori, label))
        else:
            cursor.execute('INSERT INTO kependudukan (kategori, label, jumlah, satuan, tahun) VALUES (?, ?, ?, ?, ?)', (kategori, label, jumlah, satuan, tahun))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error('Error updating kependudukan')
        return False

def get_pengumuman_by_id(pengumuman_id):
    """Ambil satu pengumuman berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pengumuman WHERE id = ?', (pengumuman_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting pengumuman {pengumuman_id}: {str(e)}")
        return None

def add_pengumuman(judul, isi, kategori='umum', is_penting=0, lampiran='', author='Pemerintahan Desa'):
    """Tambah pengumuman baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pengumuman (judul, isi, kategori, is_penting, lampiran, author)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (judul, isi, kategori, is_penting, lampiran, author))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding pengumuman: {str(e)}")
        return False

def update_pengumuman(pengumuman_id, judul, isi, kategori, is_penting, lampiran, author):
    """Update pengumuman"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pengumuman SET judul = ?, isi = ?, kategori = ?, is_penting = ?, lampiran = ?, author = ?
            WHERE id = ?
        ''', (judul, isi, kategori, is_penting, lampiran, author, pengumuman_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating pengumuman {pengumuman_id}: {str(e)}")
        return False

def delete_pengumuman(pengumuman_id):
    """Hapus pengumuman"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pengumuman WHERE id = ?', (pengumuman_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting pengumuman {pengumuman_id}: {str(e)}")
        return False

def toggle_pengumuman_aktif(pengumuman_id):
    """Toggle status aktif pengumuman"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE pengumuman SET aktif = CASE WHEN aktif = 1 THEN 0 ELSE 1 END WHERE id = ?', (pengumuman_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling pengumuman {pengumuman_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── APBDes HELPERS ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_apbdes_by_tahun(tahun):
    """Ambil semua data APBDes untuk tahun tertentu"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apbdes WHERE tahun = ? ORDER BY jenis, id ASC', (tahun,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting APBDes for tahun {tahun}: {str(e)}")
        return []

def get_apbdes_summary(tahun):
    """Ambil summary APBDes untuk tahun tertentu"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apbdes_summary WHERE tahun = ?', (tahun,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting APBDes summary for tahun {tahun}: {str(e)}")
        return None

def get_apbdes_by_id(apbdes_id):
    """Ambil satu item APBDes berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM apbdes WHERE id = ?', (apbdes_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting APBDes item {apbdes_id}: {str(e)}")
        return None

def add_apbdes_item(tahun, jenis, nama, jumlah, icon='', deskripsi=''):
    """Tambah item APBDes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO apbdes (tahun, jenis, nama, jumlah, icon, deskripsi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tahun, jenis, nama, jumlah, icon, deskripsi))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding APBDes item: {str(e)}")
        return False

def update_apbdes_item(apbdes_id, tahun, jenis, nama, jumlah, icon, deskripsi):
    """Update item APBDes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE apbdes SET tahun = ?, jenis = ?, nama = ?, jumlah = ?, icon = ?, deskripsi = ?
            WHERE id = ?
        ''', (tahun, jenis, nama, jumlah, icon, deskripsi, apbdes_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating APBDes item {apbdes_id}: {str(e)}")
        return False

def delete_apbdes_item(apbdes_id):
    """Hapus item APBDes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM apbdes WHERE id = ?', (apbdes_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting APBDes item {apbdes_id}: {str(e)}")
        return False

def save_apbdes_summary(tahun, total_pendapatan, total_belanja, pembiayaan_net):
    """Simpan/update summary APBDes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO apbdes_summary (tahun, total_pendapatan, total_belanja, pembiayaan_net)
            VALUES (?, ?, ?, ?)
        ''', (tahun, total_pendapatan, total_belanja, pembiayaan_net))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving APBDes summary: {str(e)}")
        return False

def get_available_tahun():
    """Ambil daftar tahun yang ada di APBDes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT tahun FROM apbdes ORDER BY tahun DESC')
        rows = cursor.fetchall()
        conn.close()
        return [row['tahun'] for row in rows]
    except Exception as e:
        logger.error(f"Error getting available tahun: {str(e)}")
        return []


# ════════════════════════════════════════════════════════════════════════
# ── POTENSI DESA ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_potensi():
    """Ambil semua potensi desa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM potensi_desa ORDER BY kategori, id DESC')
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data
    except Exception as e:
        logger.error(f"Error getting all potensi: {str(e)}")
        return []

def get_potensi_by_id(potensi_id):
    """Ambil potensi berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM potensi_desa WHERE id = ?', (potensi_id,))
        data = cursor.fetchone()
        conn.close()
        return dict(data) if data else None
    except Exception as e:
        logger.error(f"Error getting potensi {potensi_id}: {str(e)}")
        return None

def add_potensi(nama, kategori, deskripsi, gambar_url, icon, aktif=1):
    """Tambah potensi desa baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO potensi_desa (nama, kategori, deskripsi, gambar_url, icon, aktif)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nama, kategori, deskripsi, gambar_url, icon, aktif))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding potensi: {str(e)}")
        return False

def update_potensi(potensi_id, nama, kategori, deskripsi, gambar_url, icon, aktif):
    """Update potensi desa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE potensi_desa SET nama = ?, kategori = ?, deskripsi = ?, gambar_url = ?, icon = ?, aktif = ?
            WHERE id = ?
        ''', (nama, kategori, deskripsi, gambar_url, icon, aktif, potensi_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating potensi {potensi_id}: {str(e)}")
        return False

def delete_potensi(potensi_id):
    """Hapus potensi desa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM potensi_desa WHERE id = ?', (potensi_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting potensi {potensi_id}: {str(e)}")
        return False

def toggle_potensi_aktif(potensi_id):
    """Toggle status aktif/nonaktif potensi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE potensi_desa SET aktif = NOT aktif WHERE id = ?', (potensi_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling potensi {potensi_id}: {str(e)}")
        return False


def get_all_kependudukan():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kependudukan ORDER BY kategori, label')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting kependudukan: {str(e)}")
        return []

def update_kependudukan(kategori, label, jumlah, satuan='orang', tahun=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM kependudukan WHERE kategori = ? AND label = ?', (kategori, label))
        existing = cursor.fetchone()
        if existing:
            cursor.execute('UPDATE kependudukan SET jumlah = ?, satuan = ?, tahun = ? WHERE kategori = ? AND label = ?', (jumlah, satuan, tahun, kategori, label))
        else:
            cursor.execute('INSERT INTO kependudukan (kategori, label, jumlah, satuan, tahun) VALUES (?, ?, ?, ?, ?)', (kategori, label, jumlah, satuan, tahun))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating kependudukan: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── KRITIK DAN SARAN ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def add_kritik_saran(nama, subjek, isi, email=None, telepon=None, kategori='kritik'):
    """Tambah kritik/saran baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO kritik_saran (nama, email, telepon, subjek, kategori, isi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nama, email, telepon, subjek, kategori, isi))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding kritik_saran: {str(e)}")
        return False

def get_all_kritik_saran(include_read=True):
    """Ambil semua kritik/saran"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if include_read:
            cursor.execute('SELECT * FROM kritik_saran ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM kritik_saran WHERE is_read = 0 ORDER BY created_at DESC')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting kritik_saran: {str(e)}")
        return []

def get_kritik_saran_stats():
    """Ambil statistik kritik/saran"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM kritik_saran')
        total = cursor.fetchone()['total'] or 0
        cursor.execute('SELECT COUNT(*) as unread FROM kritik_saran WHERE is_read = 0')
        unread = cursor.fetchone()['unread'] or 0
        cursor.execute('SELECT COUNT(*) as kritik FROM kritik_saran WHERE kategori = ?', ('kritik',))
        kritik = cursor.fetchone()['kritik'] or 0
        cursor.execute('SELECT COUNT(*) as saran FROM kritik_saran WHERE kategori = ?', ('saran',))
        saran = cursor.fetchone()['saran'] or 0
        conn.close()
        return {'total': total, 'unread': unread, 'kritik': kritik, 'saran': saran}
    except Exception as e:
        logger.error(f"Error getting kritik_saran stats: {str(e)}")
        return {'total': 0, 'unread': 0, 'kritik': 0, 'saran': 0}

def mark_kritik_saran_read(ks_id):
    """Tandai kritik/saran sudah dibaca"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE kritik_saran SET is_read = 1 WHERE id = ?', (ks_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error marking kritik_saran read: {str(e)}")
        return False

def delete_kritik_saran(ks_id):
    """Hapus kritik/saran"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM kritik_saran WHERE id = ?', (ks_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting kritik_saran: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── ADUAN PUBLIK ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_aduan(aktif=None, status=None):
    """Ambil semua aduan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM aduan WHERE 1=1'
        params = []
        if aktif is not None:
            query += ' AND aktif = ?'
            params.append(aktif)
        if status:
            query += ' AND status = ?'
            params.append(status)
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all aduan: {str(e)}")
        return []

def get_aduan_by_id(aduan_id):
    """Ambil satu aduan berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM aduan WHERE id = ?', (aduan_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting aduan {aduan_id}: {str(e)}")
        return None

def get_aduan_by_nomor(nomor_aduan):
    """Ambil aduan berdasarkan nomor"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM aduan WHERE nomor_aduan = ?', (nomor_aduan,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting aduan by nomor: {str(e)}")
        return None

def add_aduan(nama, judul, deskripsi, kategori='infrastruktur', email=None, telepon=None, nik=None,
              alamat=None, dusun=None, lokasi=None, lampiran_url=None):
    """Tambah aduan baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Generate nomor aduan: KDGW-ADUAN-YYYYMMDD-XXXX
        import uuid
        from datetime import datetime
        nomor = f"KDGW-ADUAN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        cursor.execute('''
            INSERT INTO aduan (nomor_aduan, nama, email, telepon, nik, alamat, dusun, judul,
                             kategori, lokasi, isi, lampiran)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nomor, nama, email, telepon, nik, alamat, dusun, judul, kategori, lokasi, deskripsi, lampiran_url))
        conn.commit()
        conn.close()
        return True, nomor
    except Exception as e:
        logger.error(f"Error adding aduan: {str(e)}")
        return False, None

def update_aduan(aduan_id, judul, deskripsi, kategori, lokasi, status, prioritas, catatan):
    """Update aduan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE aduan SET judul = ?, isi = ?, kategori = ?, lokasi = ?, 
                           status = ?, tanggapan = ?
            WHERE id = ?
        ''', (judul, deskripsi, kategori, lokasi, status, catatan, aduan_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating aduan {aduan_id}: {str(e)}")
        return False

def delete_aduan(aduan_id):
    """Hapus aduan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM aduan WHERE id = ?', (aduan_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting aduan {aduan_id}: {str(e)}")
        return False

def respond_aduan(aduan_id, catatan, responded_by):
    """Respon aduan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE aduan SET status = 'ditanggapi', tanggapan = ?, 
                           responded_by = ?, responded_at = ?
            WHERE id = ?
        ''', (catatan, responded_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), aduan_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error responding aduan {aduan_id}: {str(e)}")
        return False

def get_aduan_stats():
    """Ambil statistik aduan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM aduan')
        total = cursor.fetchone()['total'] or 0
        cursor.execute('SELECT COUNT(*) as menunggu FROM aduan WHERE status = ?', ('menunggu',))
        menunggu = cursor.fetchone()['menunggu'] or 0
        cursor.execute('SELECT COUNT(*) as ditanggapi FROM aduan WHERE status = ?', ('ditanggapi',))
        ditanggapi = cursor.fetchone()['ditanggapi'] or 0
        cursor.execute('SELECT COUNT(*) as selesai FROM aduan WHERE status = ?', ('selesai',))
        selesai = cursor.fetchone()['selesai'] or 0
        conn.close()
        return {'total': total, 'menunggu': menunggu, 'ditanggapi': ditanggapi, 'selesai': selesai}
    except Exception as e:
        logger.error(f"Error getting aduan stats: {str(e)}")
        return {'total': 0, 'menunggu': 0, 'ditanggapi': 0, 'selesai': 0}


# ════════════════════════════════════════════════════════════════════════
# ── PROGRAM KERJA DESA ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_program_kerja(aktif=None, tahun=None):
    """Ambil semua program kerja"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM program_kerja WHERE 1=1'
        params = []
        if aktif is not None:
            query += ' AND aktif = ?'
            params.append(aktif)
        if tahun:
            query += ' AND tahun = ?'
            params.append(tahun)
        query += ' ORDER BY urutan ASC, tahun DESC, id DESC'
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all program_kerja: {str(e)}")
        return []

def get_program_kerja_by_id(program_id):
    """Ambil satu program kerja berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM program_kerja WHERE id = ?', (program_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting program_kerja {program_id}: {str(e)}")
        return None

def add_program_kerja(nama, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status, aktif=1):
    """Tambah program kerja baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(urutan) as max_order FROM program_kerja')
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1

        cursor.execute('''
            INSERT INTO program_kerja (nama, deskripsi, kategori, tahun, target, realiasi,
                                      anggaran, icon, status, aktif, urutan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nama, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status, aktif, max_order))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding program_kerja: {str(e)}")
        return False

def update_program_kerja(program_id, nama, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status, aktif, urutan):
    """Update program kerja"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE program_kerja SET nama = ?, deskripsi = ?, kategori = ?, tahun = ?,
                                   target = ?, realiasi = ?, anggaran = ?, icon = ?,
                                   status = ?, aktif = ?, urutan = ?, updated_at = ?
            WHERE id = ?
        ''', (nama, deskripsi, kategori, tahun, target, realiasi, anggaran, icon, status, aktif, urutan,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"), program_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating program_kerja {program_id}: {str(e)}")
        return False

def delete_program_kerja(program_id):
    """Hapus program kerja"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM program_kerja WHERE id = ?', (program_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting program_kerja {program_id}: {str(e)}")
        return False

def toggle_program_kerja_aktif(program_id):
    """Toggle status aktif program kerja"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE program_kerja SET aktif = NOT aktif WHERE id = ?', (program_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling program_kerja {program_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── AGENDA DESA (TIMELINE) ───────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_agenda(aktif=None, status=None, tahun=None):
    """Ambil semua agenda"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM agenda WHERE 1=1'
        params = []
        if aktif is not None:
            query += ' AND aktif = ?'
            params.append(aktif)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if tahun:
            query += ' AND strftime("%Y", tanggal_mulai) = ?'
            params.append(str(tahun))
        query += ' ORDER BY tanggal_mulai ASC, urutan ASC'
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all agenda: {str(e)}")
        return []

def get_agenda_by_id(agenda_id):
    """Ambil satu agenda berdasarkan ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM agenda WHERE id = ?', (agenda_id,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except Exception as e:
        logger.error(f"Error getting agenda {agenda_id}: {str(e)}")
        return None

def add_agenda(judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu, lokasi,
               icon, penanggung_jawab, peserta, status, aktif=1):
    """Tambah agenda baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(urutan) as max_order FROM agenda')
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1

        cursor.execute('''
            INSERT INTO agenda (judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu,
                              lokasi, icon, penanggung_jawab, peserta, status, aktif, urutan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu, lokasi,
              icon, penanggung_jawab, peserta, status, aktif, max_order))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding agenda: {str(e)}")
        return False

def update_agenda(agenda_id, judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu,
                  lokasi, icon, penanggung_jawab, peserta, status, aktif, urutan):
    """Update agenda"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE agenda SET judul = ?, deskripsi = ?, kategori = ?,
                           tanggal_mulai = ?, tanggal_selesai = ?, waktu = ?, lokasi = ?, icon = ?,
                           penanggung_jawab = ?, peserta = ?, status = ?, aktif = ?,
                           urutan = ?
            WHERE id = ?
        ''', (judul, deskripsi, kategori, tanggal_mulai, tanggal_selesai, waktu, lokasi,
              icon, penanggung_jawab, peserta, status, aktif, urutan, agenda_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating agenda {agenda_id}: {str(e)}")
        return False

def delete_agenda(agenda_id):
    """Hapus agenda"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM agenda WHERE id = ?', (agenda_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting agenda {agenda_id}: {str(e)}")
        return False

def toggle_agenda_aktif(agenda_id):
    """Toggle status aktif agenda"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE agenda SET aktif = NOT aktif WHERE id = ?', (agenda_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling agenda {agenda_id}: {str(e)}")
        return False


# ════════════════════════════════════════════════════════════════════════
# ── LOKASI RT/RW HELPERS ──────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_lokasi_rtrw(aktif=None):
    """Ambil semua data lokasi RT/RW"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if aktif is not None:
            cursor.execute('SELECT * FROM lokasi_rtrw WHERE aktif = ? ORDER BY jenis, rw, rt', (aktif,))
        else:
            cursor.execute('SELECT * FROM lokasi_rtrw ORDER BY jenis, rw, rt')
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting lokasi_rtrw: {str(e)}")
        return []

def get_lokasi_rtrw_by_id(lokasi_id):
    """Ambil satu lokasi RT/RW by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lokasi_rtrw WHERE id = ?', (lokasi_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    except Exception as e:
        logger.error(f"Error getting lokasi_rtrw {lokasi_id}: {str(e)}")
        return None

def add_lokasi_rtrw(jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif=1):
    """Tambah lokasi RT/RW"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lokasi_rtrw (jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        logger.error(f"Error adding lokasi_rtrw: {str(e)}")
        return None

def update_lokasi_rtrw(lokasi_id, jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif):
    """Update lokasi RT/RW"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE lokasi_rtrw SET jenis=?, rw=?, rt=?, nama_ketua=?, jabatan=?, wilayah=?, 
            alamat=?, no_hp=?, latitude=?, longitude=?, aktif=?
            WHERE id=?
        ''', (jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp, latitude, longitude, aktif, lokasi_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error updating lokasi_rtrw {lokasi_id}: {str(e)}")
        return False

def delete_lokasi_rtrw(lokasi_id):
    """Hapus lokasi RT/RW"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lokasi_rtrw WHERE id = ?', (lokasi_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error deleting lokasi_rtrw {lokasi_id}: {str(e)}")
        return False

def toggle_lokasi_rtrw_aktif(lokasi_id):
    """Toggle status aktif lokasi RT/RW"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE lokasi_rtrw SET aktif = NOT aktif WHERE id = ?', (lokasi_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error toggling lokasi_rtrw {lokasi_id}: {str(e)}")
        return False

def get_lokasi_rtrw_geojson():
    """Get semua lokasi RT/RW sebagai GeoJSON FeatureCollection"""
    locations = get_all_lokasi_rtrw(aktif=1)
    features = []
    for loc in locations:
        if loc.get('latitude') and loc.get('longitude'):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(loc['longitude']), float(loc['latitude'])]
                },
                "properties": {
                    "id": loc['id'],
                    "jenis": loc.get('jenis', ''),
                    "rw": loc.get('rw', ''),
                    "rt": loc.get('rt', ''),
                    "nama_ketua": loc.get('nama_ketua', ''),
                    "jabatan": loc.get('jabatan', ''),
                    "wilayah": loc.get('wilayah', ''),
                    "alamat": loc.get('alamat', ''),
                    "no_hp": loc.get('no_hp', ''),
                    "source": "rtrw"  # marker for filtering
                }
            })
    return {"type": "FeatureCollection", "features": features}


def get_all_locations_geojson(aktif=1):
    """
    Get ALL locations from all sources as unified GeoJSON FeatureCollection.
    Sources:
    - RT/RW from lokasi_rtrw table
    - Perangkat Desa, BPD, PKK, Karang Taruna from struktur_organisasi table
    """
    features = []
    
    # 1. Get RT/RW locations
    rtrw_data = get_lokasi_rtrw_geojson()
    features.extend(rtrw_data.get('features', []))
    
    # 2. Get Struktur Organisasi locations (Perangkat Desa, BPD, PKK, dll)
    struktur_data = get_struktur_for_geojson(aktif=aktif)
    for feat in struktur_data.get('features', []):
        # Map struktur properties to unified format
        p = feat['properties']
        features.append({
            "type": "Feature",
            "geometry": feat['geometry'],
            "properties": {
                "id": f"struktur_{p['id']}",
                "jenis": p.get('kategori', 'perangkat'),
                "nama": p.get('nama', ''),
                "jabatan": p.get('jabatan', ''),
                "kategori": p.get('kategori', ''),
                "nik": p.get('nik', ''),
                "alamat": p.get('alamat', ''),
                "telepon": p.get('telepon', ''),
                "email": p.get('email', ''),
                "foto_url": p.get('foto_url', ''),
                "source": "struktur"
            }
        })
    
    return {"type": "FeatureCollection", "features": features}


# Kategori mapping untuk peta
LOKASI_KATEGORI_LABELS = {
    # Dari lokasi_rtrw
    'RT': 'Rumah Ketua RT',
    'RW': 'Rumah Ketua RW',
    # Dari struktur_organisasi
    'perangkat': 'Perangkat Desa',
    'bpd': 'BPD',
    'pkk': 'PKK',
    'karang_taruna': 'Karang Taruna',
    'rt': 'RT',
    'rw': 'RW',
    'lembaga': 'Lembaga Desa',
}

LOKASI_KATEGORI_ICONS = {
    'RT': '🏠',
    'RW': '🏛️',
    'perangkat': '👔',
    'bpd': '📋',
    'pkk': '👩',
    'karang_taruna': '🧑',
    'rt': '🏠',
    'rw': '🏛️',
    'lembaga': '🏢',
}

LOKASI_KATEGORI_COLORS = {
    'RT': '#457b9d',
    'RW': '#264653',
    'perangkat': '#1b4332',
    'bpd': '#7c3aed',
    'pkk': '#ec4899',
    'karang_taruna': '#f59e0b',
    'rt': '#457b9d',
    'rw': '#264653',
    'lembaga': '#6366f1',
}
