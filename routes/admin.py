"""
Admin Routes
Berisi route-route untuk panel administrasi website
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    get_all_berita,
    get_berita_by_id,
    add_berita,
    update_berita,
    delete_berita,
    get_all_config,
    update_config,
    get_user_by_nik,
    get_user_by_id,
    get_all_galeri,
    get_galeri_by_id,
    add_galeri,
    update_galeri,
    delete_galeri,
    toggle_galeri_aktif,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Decorators ─────────────────────────────────────────────────────────

def login_required(f):
    """Decorator untuk proteksi route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ─────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Halaman login admin"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Check against admin001 user with admin role
        user = get_user_by_nik(username)
        if user and user['role'] == 'admin' and check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['user_id'] = user['id']
            session['user_nama'] = user['nama_lengkap']
            session['user_nik'] = user['nik']
            session['user_role'] = user['role']
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Username atau password salah!', 'error')

    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    """Logout admin"""
    session.clear()
    return redirect(url_for('public.index'))


# ── Dashboard ──────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard admin"""
    berita_list = get_all_berita()
    return render_template(
        "admin/dashboard.html",
        berita_list=berita_list,
        total_berita=len(berita_list),
        berita_unggulan=len([b for b in berita_list if b.get('unggulan') == 1])
    )


# ── Berita Management ───────────────────────────────────────────────────

@admin_bp.route("/berita/add", methods=['GET', 'POST'])
@login_required
def add_berita_route():
    """Form tambah berita"""
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        kategori = request.form.get('kategori', 'Berita')
        badge_class = request.form.get('badge_class', 'badge-green')
        kategori_icon = request.form.get('kategori_icon', '📰')
        gambar_url = request.form.get('gambar_url', '').strip()
        gambar_alt = request.form.get('gambar_alt', '').strip()
        unggulan = 1 if request.form.get('unggulan') else 0

        if judul:
            add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan)
            flash('Berita berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Judul berita harus diisi!', 'error')

    return render_template("admin/add_berita.html")


@admin_bp.route("/berita/edit/<int:berita_id>", methods=['GET', 'POST'])
@login_required
def edit_berita_route(berita_id):
    """Form edit berita"""
    berita = get_berita_by_id(berita_id)
    if not berita:
        flash('Berita tidak ditemukan!', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        kategori = request.form.get('kategori', 'Berita')
        badge_class = request.form.get('badge_class', 'badge-green')
        kategori_icon = request.form.get('kategori_icon', '📰')
        gambar_url = request.form.get('gambar_url', '').strip()
        gambar_alt = request.form.get('gambar_alt', '').strip()
        unggulan = 1 if request.form.get('unggulan') else 0

        if judul:
            update_berita(berita_id, judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, unggulan)
            flash('Berita berhasil diperbarui!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Judul berita harus diisi!', 'error')

    return render_template("admin/edit_berita.html", berita=berita)


@admin_bp.route("/berita/delete/<int:berita_id>", methods=['POST'])
@login_required
def delete_berita_route(berita_id):
    """Hapus berita"""
    delete_berita(berita_id)
    flash('Berita berhasil dihapus!', 'success')
    return redirect(url_for('admin.dashboard'))


# ── Config Management ──────────────────────────────────────────────────

@admin_bp.route("/config", methods=['GET', 'POST'])
@login_required
def config():
    """Halaman konfigurasi website"""
    config_data = get_all_config()

    if request.method == 'POST':
        # Website Info
        update_config("website_nama", request.form.get('website_nama', ''))
        update_config("website_tagline", request.form.get('website_tagline', ''))
        update_config("website_deskripsi", request.form.get('website_deskripsi', ''))
        update_config("website_meta_description", request.form.get('website_meta_description', ''))

        # Berita Settings
        update_config("berita_tampil_di_beranda", request.form.get('berita_tampil_di_beranda', '6'))
        update_config("berita_unggulan_tampil", request.form.get('berita_unggulan_tampil', '3'))
        update_config("berita_carousel_stacks", request.form.get('berita_carousel_stacks', '2'))
        update_config("berita_tampil_di_halaman", request.form.get('berita_tampil_di_halaman', '12'))
        update_config("berita_tampilkan_views", '1' if request.form.get('berita_tampilkan_views') else '0')
        update_config("berita_tampilkan_tanggal", '1' if request.form.get('berita_tampilkan_tanggal') else '0')

        # Homepage Sections
        update_config("tampilkan_maps", '1' if request.form.get('tampilkan_maps') else '0')
        update_config("tampilkan_statistik", '1' if request.form.get('tampilkan_statistik') else '0')
        update_config("tampilkan_daftar_dusun", '1' if request.form.get('tampilkan_daftar_dusun') else '0')
        update_config("tampilkan_hero", '1' if request.form.get('tampilkan_hero') else '0')

        # Kontak
        update_config("kontak_whatsapp", request.form.get('kontak_whatsapp', ''))
        update_config("kontak_telepon", request.form.get('kontak_telepon', ''))
        update_config("kontak_email", request.form.get('kontak_email', ''))
        update_config("alamat_desa", request.form.get('alamat_desa', ''))

        # Sosial Media
        update_config("sosial_facebook", request.form.get('sosial_facebook', ''))
        update_config("sosial_instagram", request.form.get('sosial_instagram', ''))
        update_config("sosial_twitter", request.form.get('sosial_twitter', ''))

        # Footer
        update_config("footer_copyright", request.form.get('footer_copyright', ''))

        flash('Pengaturan berhasil disimpan!', 'success')
        return redirect(url_for('admin.config'))

    return render_template("admin/config.html", config=config_data)


# ── Settings ────────────────────────────────────────────────────────────

@admin_bp.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    """Halaman pengaturan akun admin"""
    user = get_user_by_id(session.get('user_id'))

    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            flash('Password saat ini salah!', 'error')
            return redirect(url_for('admin.settings'))

        # Prepare update
        updates = {}
        if new_username and new_username != user['nik']:
            updates['nik'] = new_username

        if new_password:
            if new_password != confirm_password:
                flash('Password baru tidak cocok!', 'error')
                return redirect(url_for('admin.settings'))
            if len(new_password) < 6:
                flash('Password minimal 6 karakter!', 'error')
                return redirect(url_for('admin.settings'))
            updates['password_hash'] = generate_password_hash(new_password)

        # Execute updates
        if updates:
            conn = __import__('models').get_db_connection()
            cursor = conn.cursor()
            set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
            cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', (*updates.values(), user['id']))
            conn.commit()
            conn.close()

            # Update session
            if 'nik' in updates:
                session['user_nik'] = updates['nik']
            flash('Pengaturan berhasil disimpan!', 'success')
        else:
            flash('Tidak ada perubahan.', 'info')

        return redirect(url_for('admin.settings'))

    return render_template("admin/settings.html", user=user)


# ── Galeri Management ────────────────────────────────────────────────────

@admin_bp.route("/galeri")
@login_required
def galeri():
    """Halaman manajemen galeri"""
    galeri_list = get_all_galeri()
    return render_template(
        "admin/galeri.html",
        galeri_list=galeri_list,
        total_galeri=len(galeri_list)
    )


@admin_bp.route("/galeri/add", methods=['GET', 'POST'])
@login_required
def add_galeri_route():
    """Form tambah galeri"""
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        kategori = request.form.get('kategori', 'galeri')
        gambar_url = request.form.get('gambar_url', '').strip()
        gambar_alt = request.form.get('gambar_alt', '').strip()

        if judul and gambar_url:
            add_galeri(judul, gambar_url, deskripsi, kategori, gambar_alt)
            flash('Foto berhasil ditambahkan ke galeri!', 'success')
            return redirect(url_for('admin.galeri'))
        else:
            flash('Judul dan URL gambar harus diisi!', 'error')

    return render_template("admin/add_galeri.html")


@admin_bp.route("/galeri/edit/<int:galeri_id>", methods=['GET', 'POST'])
@login_required
def edit_galeri_route(galeri_id):
    """Form edit galeri"""
    galeri = get_galeri_by_id(galeri_id)
    if not galeri:
        flash('Foto tidak ditemukan!', 'error')
        return redirect(url_for('admin.galeri'))

    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        kategori = request.form.get('kategori', 'galeri')
        gambar_url = request.form.get('gambar_url', '').strip()
        gambar_alt = request.form.get('gambar_alt', '').strip()

        if judul and gambar_url:
            update_galeri(galeri_id, judul, gambar_url, deskripsi, kategori, gambar_alt)
            flash('Foto berhasil diperbarui!', 'success')
            return redirect(url_for('admin.galeri'))
        else:
            flash('Judul dan URL gambar harus diisi!', 'error')

    return render_template("admin/edit_galeri.html", galeri=galeri)


@admin_bp.route("/galeri/delete/<int:galeri_id>", methods=['POST'])
@login_required
def delete_galeri_route(galeri_id):
    """Hapus galeri"""
    delete_galeri(galeri_id)
    flash('Foto berhasil dihapus dari galeri!', 'success')
    return redirect(url_for('admin.galeri'))


@admin_bp.route("/galeri/toggle/<int:galeri_id>", methods=['POST'])
@login_required
def toggle_galeri_route(galeri_id):
    """Toggle status aktif/nonaktif galeri"""
    toggle_galeri_aktif(galeri_id)
    flash('Status galeri berhasil diubah!', 'success')
    return redirect(url_for('admin.galeri'))
