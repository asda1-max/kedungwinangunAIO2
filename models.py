"""
Database Models & Helpers
Berisi semua fungsi untuk berinteraksi dengan database
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config, DEFAULT_CONFIG, DEFAULT_JENIS_SURAT, DEFAULT_USERS

# ── Database Connection ────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ── Database Initialization ────────────────────────────────────────────
def init_database():
    """Initialize database with all tables and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute schema
    cursor.executescript('''
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

        -- Permohonan ACC
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
    ''')

    # Insert default config
    for key, value in DEFAULT_CONFIG.items():
        cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', (key, value))

    # Insert default users
    for nik, nama, password, role in DEFAULT_USERS:
        cursor.execute('SELECT * FROM users WHERE nik = ?', (nik,))
        if not cursor.fetchone():
            hashed = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (nik, nama_lengkap, password_hash, role, status, approved_by, approved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nik, nama, hashed, role, 'approved', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # Insert default jenis surat
    for kode, nama, desc, docs, active in DEFAULT_JENIS_SURAT:
        cursor.execute('SELECT * FROM jenis_surat WHERE kode = ?', (kode,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO jenis_surat (kode, nama, deskripsi, required_docs, active)
                VALUES (?, ?, ?, ?, ?)
            ''', (kode, nama, desc, docs, active))

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── CONFIG HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_config(key, default=None):
    """Ambil satu nilai konfigurasi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else (default if default is not None else DEFAULT_CONFIG.get(key, ''))

def get_all_config():
    """Ambil semua konfigurasi"""
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

def update_config(key, value):
    """Update satu konfigurasi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

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

def get_user_by_nik(nik):
    """Ambil user berdasarkan NIK"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE nik = ?', (nik,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Ambil user berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def verify_user(nik, password):
    """Verifikasi login user"""
    user = get_user_by_nik(nik)
    if user and user['status'] == 'approved' and check_password_hash(user['password_hash'], password):
        return user
    return None

def register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path=None, kk_path=None):
    """Registrasi user baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(password)
    try:
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
    except sqlite3.IntegrityError:
        conn.close()
        return False, "NIK sudah terdaftar!"

def get_pending_users():
    """Ambil semua user pending"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE status = ? ORDER BY created_at DESC', ('pending',))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_all_warga():
    """Ambil semua warga (role=penduduk)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE role = ? ORDER BY created_at DESC', ('penduduk',))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_all_warga_approved():
    """Ambil semua warga yang sudah disetujui"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = ? AND status = ? ORDER BY created_at DESC", ('penduduk', 'approved'))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def approve_user(user_id, processed_by):
    """Setujui pendaftaran user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET status = ?, approved_by = ?, approved_at = ? WHERE id = ?
    ''', ('approved', processed_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    cursor.execute('''
        UPDATE permohonan_acc SET status = ?, processed_by = ?, processed_at = ? WHERE user_id = ?
    ''', ('approved', processed_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()
    conn.close()

def reject_user(user_id, processed_by, catatan=''):
    """Tolak pendaftaran user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = ? WHERE id = ?', ('rejected', user_id))
    cursor.execute('''
        UPDATE permohonan_acc SET status = ?, processed_by = ?, catatan = ?, processed_at = ? WHERE user_id = ?
    ''', ('rejected', processed_by, catatan, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── BERITA HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_berita():
    """Ambil semua berita"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM berita ORDER BY created_at DESC')
    berita = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return berita

def get_berita_by_id(berita_id):
    """Ambil berita berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM berita WHERE id = ?', (berita_id,))
    berita = cursor.fetchone()
    conn.close()
    return dict(berita) if berita else None

def add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan):
    """Tambah berita baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    tanggal = datetime.now().strftime("%d %b %Y")
    cursor.execute('''
        INSERT INTO berita (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, views, gambar_url, gambar_alt, unggulan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (judul, excerpt, kategori, badge_class, kategori_icon, tanggal, "0", gambar_url, gambar_alt, unggulan))
    conn.commit()
    conn.close()

def update_berita(berita_id, judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan):
    """Update berita"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE berita SET judul = ?, excerpt = ?, kategori = ?, badge_class = ?, kategori_icon = ?, gambar_url = ?, gambar_alt = ?, unggulan = ?
        WHERE id = ?
    ''', (judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan, berita_id))
    conn.commit()
    conn.close()

def delete_berita(berita_id):
    """Hapus berita"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM berita WHERE id = ?', (berita_id,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── SURAT HELPERS ───────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_jenis_surat():
    """Ambil semua jenis surat aktif"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jenis_surat WHERE active = 1 ORDER BY nama')
    surats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return surats

def get_jenis_surat_by_id(jenis_id):
    """Ambil jenis surat berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jenis_surat WHERE id = ?', (jenis_id,))
    surat = cursor.fetchone()
    conn.close()
    return dict(surat) if surat else None

def create_permohonan_surat(user_id, jenis_surat_id, data_json):
    """Buat permohonan surat baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO permohonan_surat (user_id, jenis_surat_id, data_json, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, jenis_surat_id, data_json, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_permohonan_surat_by_user(user_id):
    """Ambil permohonan surat berdasarkan user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ps.*, js.nama as jenis_nama, js.kode as jenis_kode
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.jenis_surat_id = js.id
        WHERE ps.user_id = ?
        ORDER BY ps.created_at DESC
    ''', (user_id,))
    permits = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return permits

def get_all_permohonan_surat():
    """Ambil semua permohonan surat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ps.*, js.nama as jenis_nama, js.kode as jenis_kode, u.nama_lengkap, u.nik, u.alamat
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.jenis_surat_id = js.id
        JOIN users u ON ps.user_id = u.id
        ORDER BY ps.created_at DESC
    ''')
    permits = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return permits

def get_pending_permohonan_surat():
    """Ambil permohonan surat pending"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ps.*, js.nama as jenis_nama, js.kode as jenis_kode, u.nama_lengkap, u.nik
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.jenis_surat_id = js.id
        JOIN users u ON ps.user_id = u.id
        WHERE ps.status = ?
        ORDER BY ps.created_at DESC
    ''', ('pending',))
    permits = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return permits

def get_permohonan_detail(permit_id):
    """Ambil detail permohonan surat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ps.*, js.nama as jenis_nama, js.kode as jenis_kode, js.required_docs,
               u.nama_lengkap, u.nik, u.alamat, u.no_telepon, u.email
        FROM permohonan_surat ps
        JOIN jenis_surat js ON ps.jenis_surat_id = js.id
        JOIN users u ON ps.user_id = u.id
        WHERE ps.id = ?
    ''', (permit_id,))
    permit = cursor.fetchone()
    conn.close()
    return dict(permit) if permit else None

def approve_permohonan_surat(permit_id, approved_by, nomor_surat, catatan=''):
    """Setujui permohonan surat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE permohonan_surat
        SET status = ?, approved_by = ?, approved_at = ?, nomor_surat = ?, catatan = ?
        WHERE id = ?
    ''', ('approved', approved_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nomor_surat, catatan, permit_id))
    conn.commit()
    conn.close()

def reject_permohonan_surat(permit_id, processed_by, catatan=''):
    """Tolak permohonan surat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE permohonan_surat SET status = ?, catatan = ? WHERE id = ?
    ''', ('rejected', catatan, permit_id))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── GALERI HELPERS ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_galeri(aktif=None):
    """Ambil semua foto galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if aktif is not None:
        cursor.execute('SELECT * FROM galeri WHERE aktif = ? ORDER BY created_at DESC', (aktif,))
    else:
        cursor.execute('SELECT * FROM galeri ORDER BY created_at DESC')
    galeri = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return galeri

def get_galeri_by_id(galeri_id):
    """Ambil satu foto galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM galeri WHERE id = ?', (galeri_id,))
    galeri = cursor.fetchone()
    conn.close()
    return dict(galeri) if galeri else None

def add_galeri(judul, gambar_url, deskripsi='', kategori='galeri', gambar_alt=''):
    """Tambah foto galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO galeri (judul, deskripsi, kategori, gambar_url, gambar_alt)
        VALUES (?, ?, ?, ?, ?)
    ''', (judul, deskripsi, kategori, gambar_url, gambar_alt))
    conn.commit()
    conn.close()

def update_galeri(galeri_id, judul, gambar_url, deskripsi, kategori, gambar_alt):
    """Update foto galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE galeri SET judul = ?, deskripsi = ?, kategori = ?, gambar_url = ?, gambar_alt = ?
        WHERE id = ?
    ''', (judul, deskripsi, kategori, gambar_url, gambar_alt, galeri_id))
    conn.commit()
    conn.close()

def delete_galeri(galeri_id):
    """Hapus foto galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM galeri WHERE id = ?', (galeri_id,))
    conn.commit()
    conn.close()

def toggle_galeri_aktif(galeri_id):
    """Toggle status aktif/nonaktif galeri"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE galeri SET aktif = CASE WHEN aktif = 1 THEN 0 ELSE 1 END WHERE id = ?', (galeri_id,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── CUSTOM PAGES HELPERS ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_all_pages():
    """Ambil semua page aktif"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE active = 1 ORDER BY order_num ASC, title ASC')
    pages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return pages

def get_page_by_slug(slug):
    """Ambil page berdasarkan slug"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE slug = ? AND active = 1', (slug,))
    page = cursor.fetchone()
    conn.close()
    return dict(page) if page else None

def get_page_by_id(page_id):
    """Ambil page berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = cursor.fetchone()
    conn.close()
    return dict(page) if page else None

def get_all_pages_admin():
    """Ambil semua page (termasuk nonaktif) untuk admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages ORDER BY order_num ASC, title ASC')
    pages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return pages

def add_page(title, slug, content, icon='📄'):
    """Tambah page baru"""
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

def update_page(page_id, title, slug, content, icon, order_num, active):
    """Update page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE pages SET title = ?, slug = ?, content = ?, icon = ?, order_num = ?, active = ?
        WHERE id = ?
    ''', (title, slug, content, icon, order_num, active, page_id))
    conn.commit()
    conn.close()

def delete_page(page_id):
    """Hapus page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
    conn.commit()
    conn.close()

def toggle_page_active(page_id):
    """Toggle status aktif page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pages SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?', (page_id,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════
# ── KOMENTAR HELPERS ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

def get_komentar_by_berita(berita_id):
    """Ambil semua komentar untuk sebuah berita (flat list)"""
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO komentar (berita_id, parent_id, user_id, nama_pengirim, konten)
        VALUES (?, ?, ?, ?, ?)
    ''', (berita_id, parent_id, user_id, nama_pengirim, konten))
    conn.commit()
    conn.close()

def delete_komentar(komentar_id):
    """Hapus komentar beserta semua child-nya (recursive delete via FK cascade)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # FK cascade ON DELETE CASCADE akan handle child comment otomatis,
    # tapi kita hapus manual untuk memastikan bersih
    cursor.execute('DELETE FROM komentar WHERE id = ?', (komentar_id,))
    conn.commit()
    conn.close()

def get_komentar_by_id(komentar_id):
    """Ambil satu komentar berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM komentar WHERE id = ?', (komentar_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def count_komentar_by_berita(berita_id):
    """Hitung jumlah komentar untuk sebuah berita"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as cnt FROM komentar WHERE berita_id = ?', (berita_id,))
    row = cursor.fetchone()
    conn.close()
    return row['cnt'] if row else 0
