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
                penulis TEXT DEFAULT 'Admin Desa Kedungwinangun',
                unggulan INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            -- Struktur Organisasi
            CREATE TABLE IF NOT EXISTS struktur_organisasi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategori TEXT NOT NULL,
                nama TEXT NOT NULL,
                jabatan TEXT,
                status TEXT,
                icon TEXT,
                no_urut INTEGER DEFAULT 0,
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
        ''')

        # Insert default config
        for key, value in DEFAULT_CONFIG.items():
            cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))

        # Insert default users (updated: admin uses username, dinas uses nip)
        for login_id, nama, password, role in DEFAULT_USERS:
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
        "jumlah_dusun": 6,
        "jumlah_kasi": 3,
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

def verify_user(nik, password):
    """Verifikasi login user"""
    user = get_user_by_nik(nik)
    if user and user['status'] == 'approved' and check_password_hash(user['password_hash'], password):
        return user
    return None

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

def add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan):
    """Tambah berita baru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        tanggal = datetime.now().strftime("%d %b %Y")
        cursor.execute('''
            INSERT INTO berita (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, views, gambar_url, gambar_alt, unggulan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, "0", gambar_url, gambar_alt, unggulan))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding berita: {str(e)}")
        return False

def update_berita(berita_id, judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan):
    """Update berita"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE berita SET judul = ?, excerpt = ?, kategori = ?, badge_class = ?, kategori_icon = ?, gambar_url = ?, gambar_alt = ?, unggulan = ?
            WHERE id = ?
        ''', (judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan, berita_id))
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

def get_all_struktur():
    """Ambil semua struktur organisasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM struktur_organisasi ORDER BY kategori, no_urut ASC')
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting all struktur: {str(e)}")
        return []

def get_struktur_by_kategori(kategori):
    """Ambil struktur berdasarkan kategori"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
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

def add_struktur(kategori, nama, jabatan='', status='', icon=''):
    """Tambah struktur organisasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get max order in kategori
        cursor.execute('SELECT MAX(no_urut) as max_order FROM struktur_organisasi WHERE kategori = ?', (kategori,))
        row = cursor.fetchone()
        max_order = (row['max_order'] or 0) + 1

        cursor.execute('''
            INSERT INTO struktur_organisasi (kategori, nama, jabatan, status, icon, no_urut)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (kategori, nama, jabatan, status, icon, max_order))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding struktur: {str(e)}")
        return False

def update_struktur(struktur_id, kategori, nama, jabatan, status, icon, no_urut):
    """Update struktur organisasi"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE struktur_organisasi SET kategori = ?, nama = ?, jabatan = ?, status = ?, icon = ?, no_urut = ?
            WHERE id = ?
        ''', (kategori, nama, jabatan, status, icon, no_urut, struktur_id))
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
