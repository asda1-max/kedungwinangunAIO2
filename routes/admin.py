"""
Admin Routes
Berisi route-route untuk panel administrasi website

Error Handling:
    Menggunakan decorators dari errors.py:
    - admin_required: Proteksi route admin only
    - safe_handler: Handle semua error dalam route
    - flash_error: Flash error messages
"""

import os
import re
import uuid
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, send_from_directory
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import (
    get_all_berita,
    get_berita_by_id,
    add_berita,
    update_berita,
    delete_berita,
    get_all_config,
    update_config,
    get_user_by_id,
    get_all_galeri,
    get_galeri_by_id,
    add_galeri,
    update_galeri,
    delete_galeri,
    toggle_galeri_aktif,
    get_all_pages,
    get_page_by_id,
    add_page,
    update_page,
    delete_page,
    toggle_page_active,
    get_all_users,
    get_user_stats,
    update_user_data,
    update_user_role,
    update_user_password,
    delete_user_account,
    create_staff_account,
    # Potensi Desa
    get_all_potensi,
    get_potensi_by_id,
    add_potensi,
    update_potensi,
    delete_potensi,
    toggle_potensi_aktif,
    # Sejarah Desa
    get_all_sejarah,
    get_sejarah_by_id,
    add_sejarah,
    update_sejarah,
    delete_sejarah,
    toggle_sejarah_aktif,
    # Struktur Organisasi
    get_all_struktur,
    get_struktur_by_kategori,
    get_struktur_by_id,
    add_struktur,
    update_struktur,
    delete_struktur,
    toggle_struktur_aktif,
    batch_import_struktur,
    # UMKM
    get_all_umkm,
    get_umkm_by_id,
    add_umkm,
    update_umkm,
    delete_umkm,
    toggle_umkm_aktif,
    # Kependudukan
    get_all_kependudukan,
    update_kependudukan,
    # Kritik dan Saran
    get_all_kritik_saran,
    get_kritik_saran_stats,
    mark_kritik_saran_read,
    delete_kritik_saran,
    # Aduan
    get_all_aduan,
    get_aduan_by_id,
    add_aduan,
    update_aduan,
    delete_aduan,
    respond_aduan,
    get_aduan_stats,
    # Program Kerja
    get_all_program_kerja,
    get_program_kerja_by_id,
    add_program_kerja,
    update_program_kerja,
    delete_program_kerja,
    toggle_program_kerja_aktif,
    # Agenda
    get_all_agenda,
    get_agenda_by_id,
    add_agenda,
    update_agenda,
    delete_agenda,
    toggle_agenda_aktif,
)
from errors import admin_required, flash_error
from config import Config

# File upload helpers
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    """Save uploaded file and return the URL/path"""
    if file and file.filename and allowed_image(file.filename):
        # Create unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        # Create upload directory
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder) if subfolder else Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Return relative URL path
        if subfolder:
            return f"/uploads/{subfolder}/{filename}"
        return f"/uploads/{filename}"
    return None
import logging

# Setup logging
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Auth Routes ─────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Redirect to unified login"""
    return redirect(url_for('public.login'))


@admin_bp.route("/logout")
def logout():
    """Logout admin"""
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('public.index'))


# ── Dashboard ──────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Dashboard admin"""
    try:
        berita_list = get_all_berita()
        return render_template(
            "admin/dashboard.html",
            berita_list=berita_list,
            total_berita=len(berita_list),
            berita_unggulan=len([b for b in berita_list if b.get('unggulan') == 1])
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat dashboard')
        return redirect(url_for('public.index'))


# ── Berita Management ────────────────────────────────────────────────────

@admin_bp.route("/berita/add", methods=['GET', 'POST'])
@admin_required
def add_berita_route():
    """Form tambah berita"""
    try:
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            kategori = request.form.get('kategori', 'Berita')
            badge_class = request.form.get('badge_class', 'badge-green')
            kategori_icon = request.form.get('kategori_icon', '')
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            facebook_auto_post = 1 if request.form.get('facebook_auto_post') else 0
            unggulan = 1 if request.form.get('unggulan') else 0

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'berita')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not judul:
                flash_error('Judul berita harus diisi!')
                return redirect(request.url)

            result = add_berita(judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan)
            if result:
                flash('Berita berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash_error('Gagal menambahkan berita. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_berita.html")
    except Exception as e:
        logger.error(f"Error in add_berita_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form berita')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/berita/edit/<int:berita_id>", methods=['GET', 'POST'])
@admin_required
def edit_berita_route(berita_id):
    """Form edit berita"""
    try:
        berita = get_berita_by_id(berita_id)
        if not berita:
            flash_error('Berita tidak ditemukan!')
            return redirect(url_for('admin.dashboard'))

        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            kategori = request.form.get('kategori', 'Berita')
            badge_class = request.form.get('badge_class', 'badge-green')
            kategori_icon = request.form.get('kategori_icon', '')
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            facebook_auto_post = 1 if request.form.get('facebook_auto_post') else 0
            unggulan = 1 if request.form.get('unggulan') else 0

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'berita')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not judul:
                flash_error('Judul berita harus diisi!')
                return redirect(request.url)

            result = update_berita(berita_id, judul, excerpt, kategori, badge_class, kategori_icon, gambar_url, gambar_alt, video_url, facebook_auto_post, unggulan)
            if result:
                flash('Berita berhasil diperbarui!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash_error('Gagal memperbarui berita. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_berita.html", berita=berita)
    except Exception as e:
        logger.error(f"Error in edit_berita_route {berita_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form berita')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/berita/delete/<int:berita_id>", methods=['POST'])
@admin_required
def delete_berita_route(berita_id):
    """Hapus berita"""
    try:
        result = delete_berita(berita_id)
        if result:
            flash('Berita berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus berita. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting berita {berita_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus berita')
    return redirect(url_for('admin.dashboard'))


# ── Config Management ──────────────────────────────────────────────────

@admin_bp.route("/config", methods=['GET', 'POST'])
@admin_required
def config():
    """Halaman konfigurasi website"""
    try:
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
            update_config("sosial_tiktok", request.form.get('sosial_tiktok', ''))

            # Footer
            update_config("footer_copyright", request.form.get('footer_copyright', ''))

            flash('Pengaturan berhasil disimpan!', 'success')
            return redirect(url_for('admin.config'))

        return render_template("admin/config.html", config=config_data)
    except Exception as e:
        logger.error(f"Error in config page: {str(e)}")
        flash_error('Terjadi kesalahan saat menyimpan pengaturan')
        return redirect(url_for('admin.dashboard'))


# ── Settings ────────────────────────────────────────────────────────────

@admin_bp.route("/settings", methods=['GET', 'POST'])
@admin_required
def settings():
    """Halaman pengaturan akun admin"""
    try:
        user = get_user_by_id(session.get('user_id'))

        if request.method == 'POST':
            new_username = request.form.get('new_username', '').strip()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            # Verify current password
            if not check_password_hash(user['password_hash'], current_password):
                flash_error('Password saat ini salah!')
                return redirect(url_for('admin.settings'))

            # Prepare update
            updates = {}
            if new_username and new_username != user['nik']:
                updates['nik'] = new_username

            if new_password:
                if new_password != confirm_password:
                    flash_error('Password baru tidak cocok!')
                    return redirect(url_for('admin.settings'))
                if len(new_password) < 6:
                    flash_error('Password minimal 6 karakter!')
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
    except Exception as e:
        logger.error(f"Error in settings page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat pengaturan')
        return redirect(url_for('admin.dashboard'))


# ════════════════════════════════════════════════════════════════════════
# ── ACCOUNT CENTER ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/accounts")
@admin_required
def account_center():
    """Halaman Account Center - Kelola semua akun"""
    try:
        # Filter by role if specified
        role_filter = request.args.get('role', 'all')
        status_filter = request.args.get('status', 'all')
        search = request.args.get('search', '').strip()

        users = get_all_users()
        stats = get_user_stats()

        # Apply filters
        if role_filter != 'all':
            users = [u for u in users if u['role'] == role_filter]
        if status_filter != 'all':
            users = [u for u in users if u['status'] == status_filter]
        if search:
            search = search.lower()
            users = [u for u in users if
                     search in u.get('nama_lengkap', '').lower() or
                     search in u.get('nik', '').lower() or
                     search in u.get('email', '').lower()]

        return render_template(
            "admin/account_center.html",
            users=users,
            stats=stats,
            role_filter=role_filter,
            status_filter=status_filter,
            search=search
        )
    except Exception as e:
        logger.error(f"Error in account_center: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat Account Center')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/accounts/user/<int:user_id>", methods=['GET', 'POST'])
@admin_required
def account_detail(user_id):
    """Detail & Edit user"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash_error('User tidak ditemukan!')
            return redirect(url_for('admin.account_center'))

        if request.method == 'POST':
            action = request.form.get('action', '')

            if action == 'update_data':
                # Update user data
                data = {
                    'nama_lengkap': request.form.get('nama_lengkap', '').strip(),
                    'email': request.form.get('email', '').strip(),
                    'no_telepon': request.form.get('no_telepon', '').strip(),
                    'alamat': request.form.get('alamat', '').strip(),
                }
                if update_user_data(user_id, data):
                    flash('Data user berhasil diperbarui!', 'success')
                else:
                    flash_error('Gagal memperbarui data user.')

            elif action == 'update_password':
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                if new_password != confirm_password:
                    flash_error('Password baru tidak cocok!')
                    return redirect(url_for('admin.account_detail', user_id=user_id))
                if len(new_password) < 6:
                    flash_error('Password minimal 6 karakter!')
                    return redirect(url_for('admin.account_detail', user_id=user_id))
                if update_user_password(user_id, new_password):
                    flash('Password berhasil diperbarui!', 'success')
                else:
                    flash_error('Gagal memperbarui password.')

            elif action == 'change_role':
                new_role = request.form.get('new_role', '')
                if new_role in ['admin', 'dinas', 'penduduk']:
                    if update_user_role(user_id, new_role, session.get('user_id')):
                        flash(f'Role berhasil diubah ke {new_role}!', 'success')
                    else:
                        flash_error('Gagal mengubah role.')

            return redirect(url_for('admin.account_detail', user_id=user_id))

        return render_template("admin/account_detail.html", user=user)
    except Exception as e:
        logger.error(f"Error in account_detail {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat data user')
        return redirect(url_for('admin.account_center'))


@admin_bp.route("/accounts/user/delete/<int:user_id>", methods=['POST'])
@admin_required
def account_delete(user_id):
    """Hapus user"""
    try:
        # Prevent self-deletion
        if user_id == session.get('user_id'):
            flash_error('Tidak dapat menghapus akun sendiri!')
            return redirect(url_for('admin.account_center'))

        if delete_user_account(user_id):
            flash('User berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus user.')
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus user')
    return redirect(url_for('admin.account_center'))


@admin_bp.route("/accounts/create", methods=['GET', 'POST'])
@admin_required
def account_create():
    """Buat akun admin/dinas baru"""
    try:
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            nama_lengkap = request.form.get('nama_lengkap', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            role = request.form.get('role', '')

            # Validation
            if not login_id or not nama_lengkap or not password or not role:
                flash_error('Semua field harus diisi!')
                return redirect(url_for('admin.account_create'))

            if password != confirm_password:
                flash_error('Password tidak cocok!')
                return redirect(url_for('admin.account_create'))

            if len(password) < 6:
                flash_error('Password minimal 6 karakter!')
                return redirect(url_for('admin.account_create'))

            if role not in ['admin', 'dinas']:
                flash_error('Role tidak valid!')
                return redirect(url_for('admin.account_create'))

            success, result = create_staff_account(login_id, nama_lengkap, password, role)
            if success:
                flash(f'Akun {role} berhasil dibuat!', 'success')
                return redirect(url_for('admin.account_center'))
            else:
                flash_error(result)
                return redirect(url_for('admin.account_create'))

        return render_template("admin/account_create.html")
    except Exception as e:
        logger.error(f"Error in account_create: {str(e)}")
        flash_error('Terjadi kesalahan saat membuat akun')
        return redirect(url_for('admin.account_center'))


# ── Galeri Management ────────────────────────────────────────────────────

@admin_bp.route("/galeri")
@admin_required
def galeri():
    """Halaman manajemen galeri"""
    try:
        galeri_list = get_all_galeri()
        return render_template(
            "admin/galeri.html",
            galeri_list=galeri_list,
            total_galeri=len(galeri_list)
        )
    except Exception as e:
        logger.error(f"Error loading galeri page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman galeri')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/galeri/add", methods=['GET', 'POST'])
@admin_required
def add_galeri_route():
    """Form tambah galeri"""
    try:
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'galeri')
            gambar_alt = request.form.get('gambar_alt', '').strip()

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'galeri')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not judul or not gambar_url:
                flash_error('Judul dan gambar harus diisi!')
                return redirect(request.url)

            result = add_galeri(judul, gambar_url, deskripsi, kategori, gambar_alt)
            if result:
                flash('Foto berhasil ditambahkan ke galeri!', 'success')
                return redirect(url_for('admin.galeri'))
            else:
                flash_error('Gagal menambahkan foto. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_galeri.html")
    except Exception as e:
        logger.error(f"Error in add_galeri_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form galeri')
        return redirect(url_for('admin.galeri'))


@admin_bp.route("/galeri/edit/<int:galeri_id>", methods=['GET', 'POST'])
@admin_required
def edit_galeri_route(galeri_id):
    """Form edit galeri"""
    try:
        galeri = get_galeri_by_id(galeri_id)
        if not galeri:
            flash_error('Foto tidak ditemukan!')
            return redirect(url_for('admin.galeri'))

        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'galeri')
            gambar_alt = request.form.get('gambar_alt', '').strip()

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'galeri')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not judul or not gambar_url:
                flash_error('Judul dan gambar harus diisi!')
                return redirect(request.url)

            result = update_galeri(galeri_id, judul, gambar_url, deskripsi, kategori, gambar_alt)
            if result:
                flash('Foto berhasil diperbarui!', 'success')
                return redirect(url_for('admin.galeri'))
            else:
                flash_error('Gagal memperbarui foto. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_galeri.html", galeri=galeri)
    except Exception as e:
        logger.error(f"Error in edit_galeri_route {galeri_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form galeri')
        return redirect(url_for('admin.galeri'))


@admin_bp.route("/galeri/delete/<int:galeri_id>", methods=['POST'])
@admin_required
def delete_galeri_route(galeri_id):
    """Hapus galeri"""
    try:
        result = delete_galeri(galeri_id)
        if result:
            flash('Foto berhasil dihapus dari galeri!', 'success')
        else:
            flash_error('Gagal menghapus foto. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting galeri {galeri_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus foto')
    return redirect(url_for('admin.galeri'))


@admin_bp.route("/galeri/toggle/<int:galeri_id>", methods=['POST'])
@admin_required
def toggle_galeri_route(galeri_id):
    """Toggle status aktif/nonaktif galeri"""
    try:
        result = toggle_galeri_aktif(galeri_id)
        if result:
            flash('Status galeri berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status galeri.')
    except Exception as e:
        logger.error(f"Error toggling galeri {galeri_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status galeri')
    return redirect(url_for('admin.galeri'))


# ════════════════════════════════════════════════════════════════════════
# ── SEJARAH DESA MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/sejarah")
@admin_required
def sejarah():
    """Halaman list sejarah desa"""
    try:
        all_sejarah = get_all_sejarah()
        return render_template("admin/sejarah.html", sejarah_list=all_sejarah)
    except Exception as e:
        logger.error(f"Error loading sejarah page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman sejarah')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/sejarah/add", methods=['GET', 'POST'])
@admin_required
def add_sejarah_route():
    """Form tambah sejarah"""
    if request.method == 'POST':
        try:
            judul = request.form.get('judul', '').strip()
            sub_judul = request.form.get('sub_judul', '').strip()
            konten = request.form.get('konten', '').strip()
            kategori = request.form.get('kategori', 'sejarah').strip()
            tahun_dari = request.form.get('tahun_dari', '')
            tahun_sampai = request.form.get('tahun_sampai', '')
            gambar_url = request.form.get('gambar_url', '').strip()
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            urutan = int(request.form.get('urutan', 0))

            if not judul:
                flash_error('Judul wajib diisi!')
                return redirect(request.url)

            # Parse tahun
            tahun_dari_int = int(tahun_dari) if tahun_dari else None
            tahun_sampai_int = int(tahun_sampai) if tahun_sampai else None

            result = add_sejarah(
                judul=judul,
                sub_judul=sub_judul,
                konten=konten,
                kategori=kategori,
                tahun_dari=tahun_dari_int,
                tahun_sampai=tahun_sampai_int,
                gambar_url=gambar_url,
                gambar_alt=gambar_alt,
                video_url=video_url,
                urutan=urutan
            )

            if result:
                flash('Entry sejarah berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.sejarah'))
            else:
                flash_error('Gagal menambahkan sejarah!')
        except Exception as e:
            logger.error(f"Error adding sejarah: {str(e)}")
            flash_error('Terjadi kesalahan saat menambahkan sejarah')

    return render_template("admin/add_sejarah.html")


@admin_bp.route("/sejarah/edit/<int:sejarah_id>", methods=['GET', 'POST'])
@admin_required
def edit_sejarah_route(sejarah_id):
    """Form edit sejarah"""
    sejarah = get_sejarah_by_id(sejarah_id)
    if not sejarah:
        flash_error('Sejarah tidak ditemukan!')
        return redirect(url_for('admin.sejarah'))

    if request.method == 'POST':
        try:
            judul = request.form.get('judul', '').strip()
            sub_judul = request.form.get('sub_judul', '').strip()
            konten = request.form.get('konten', '').strip()
            kategori = request.form.get('kategori', 'sejarah').strip()
            tahun_dari = request.form.get('tahun_dari', '')
            tahun_sampai = request.form.get('tahun_sampai', '')
            gambar_url = request.form.get('gambar_url', '').strip()
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            aktif = 1 if request.form.get('aktif') else 0
            urutan = int(request.form.get('urutan', 0))

            if not judul:
                flash_error('Judul wajib diisi!')
                return redirect(request.url)

            tahun_dari_int = int(tahun_dari) if tahun_dari else None
            tahun_sampai_int = int(tahun_sampai) if tahun_sampai else None

            result = update_sejarah(
                sejarah_id=sejarah_id,
                judul=judul,
                sub_judul=sub_judul,
                konten=konten,
                kategori=kategori,
                tahun_dari=tahun_dari_int,
                tahun_sampai=tahun_sampai_int,
                gambar_url=gambar_url,
                gambar_alt=gambar_alt,
                video_url=video_url,
                aktif=aktif,
                urutan=urutan
            )

            if result:
                flash('Sejarah berhasil diupdate!', 'success')
                return redirect(url_for('admin.sejarah'))
            else:
                flash_error('Gagal update sejarah!')
        except Exception as e:
            logger.error(f"Error updating sejarah {sejarah_id}: {str(e)}")
            flash_error('Terjadi kesalahan saat update sejarah')

    return render_template("admin/edit_sejarah.html", sejarah=sejarah)


@admin_bp.route("/sejarah/delete/<int:sejarah_id>", methods=['POST'])
@admin_required
def delete_sejarah_route(sejarah_id):
    """Hapus sejarah"""
    try:
        result = delete_sejarah(sejarah_id)
        if result:
            flash('Sejarah berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus sejarah!')
    except Exception as e:
        logger.error(f"Error deleting sejarah {sejarah_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus sejarah')
    return redirect(url_for('admin.sejarah'))


@admin_bp.route("/sejarah/toggle/<int:sejarah_id>", methods=['POST'])
@admin_required
def toggle_sejarah_route(sejarah_id):
    """Toggle status aktif/nonaktif sejarah"""
    try:
        result = toggle_sejarah_aktif(sejarah_id)
        if result:
            flash('Status sejarah berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status sejarah!')
    except Exception as e:
        logger.error(f"Error toggling sejarah {sejarah_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status sejarah')
    return redirect(url_for('admin.sejarah'))


# ════════════════════════════════════════════════════════════════════════
# ── PAGES MANAGEMENT ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/pages")
@admin_required
def pages():
    """Halaman list pages"""
    try:
        all_pages = get_all_pages()
        return render_template("admin/pages.html", pages_list=all_pages)
    except Exception as e:
        logger.error(f"Error loading pages page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman pages')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/pages/add", methods=['GET', 'POST'])
@admin_required
def add_page_route():
    """Form tambah page"""
    try:
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
            content = request.form.get('content', '').strip()
            icon = request.form.get('icon', '📄').strip()

            if not title or not slug:
                flash_error('Judul dan slug harus diisi!')
                return redirect(request.url)

            # Check if slug exists
            existing = get_all_pages()
            slugs = [p['slug'] for p in existing]
            if slug in slugs:
                flash_error('Slug sudah digunakan! Gunakan slug lain.')
                return redirect(request.url)

            result = add_page(title, slug, content, icon)
            if result:
                flash('Page berhasil dibuat!', 'success')
                return redirect(url_for('admin.pages'))
            else:
                flash_error('Gagal membuat page. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_page.html")
    except Exception as e:
        logger.error(f"Error in add_page_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form page')
        return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/edit/<int:page_id>", methods=['GET', 'POST'])
@admin_required
def edit_page_route(page_id):
    """Form edit page"""
    try:
        page = get_page_by_id(page_id)
        if not page:
            flash_error('Page tidak ditemukan!')
            return redirect(url_for('admin.pages'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
            content = request.form.get('content', '').strip()
            icon = request.form.get('icon', '📄').strip()
            order_num = int(request.form.get('order_num', 0) or 0)
            active = 1 if request.form.get('active') else 0

            if not title or not slug:
                flash_error('Judul dan slug harus diisi!')
                return redirect(request.url)

            # Check if slug exists for other pages
            existing = get_all_pages()
            slugs = [p['slug'] for p in existing if p['id'] != page_id]
            if slug in slugs:
                flash_error('Slug sudah digunakan! Gunakan slug lain.')
                return redirect(request.url)

            result = update_page(page_id, title, slug, content, icon, order_num, active)
            if result:
                flash('Page berhasil diperbarui!', 'success')
                return redirect(url_for('admin.pages'))
            else:
                flash_error('Gagal memperbarui page. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_page.html", page=page)
    except Exception as e:
        logger.error(f"Error in edit_page_route {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form page')
        return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/delete/<int:page_id>", methods=['POST'])
@admin_required
def delete_page_route(page_id):
    """Hapus page"""
    try:
        result = delete_page(page_id)
        if result:
            flash('Page berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus page. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting page {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus page')
    return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/toggle/<int:page_id>", methods=['POST'])
@admin_required
def toggle_page_route(page_id):
    """Toggle status aktif/nonaktif page"""
    try:
        result = toggle_page_active(page_id)
        if result:
            flash('Status page berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status page.')
    except Exception as e:
        logger.error(f"Error toggling page {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status page')
    return redirect(url_for('admin.pages'))


# ════════════════════════════════════════════════════════════════════════
# ── STRUKTUR ORGANISASI MANAGEMENT ────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/struktur")
@admin_required
def struktur():
    """Halaman manajemen struktur organisasi"""
    try:
        struktur_list = get_all_struktur()

        # Group by kategori
        grouped = {}
        for item in struktur_list:
            kat = item['kategori']
            if kat not in grouped:
                grouped[kat] = []
            grouped[kat].append(item)

        return render_template("admin/struktur.html", struktur_list=struktur_list, grouped=grouped)
    except Exception as e:
        logger.error(f"Error loading struktur page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman struktur')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/struktur/add", methods=['GET', 'POST'])
@admin_required
def add_struktur_route():
    """Form tambah struktur organisasi"""
    if request.method == 'POST':
        try:
            kategori = request.form.get('kategori', '').strip()
            nama = request.form.get('nama', '').strip()
            jabatan = request.form.get('jabatan', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            nik = request.form.get('nik', '').strip()
            alamat = request.form.get('alamat', '').strip()
            dusun = request.form.get('dusun', '').strip()
            rt = request.form.get('rt', '').strip()
            rw = request.form.get('rw', '').strip()
            telepon = request.form.get('telepon', '').strip()
            email = request.form.get('email', '').strip()
            sk_url = request.form.get('sk_url', '').strip()
            no_sk = request.form.get('no_sk', '').strip()
            tanggal_sk = request.form.get('tanggal_sk', '').strip()
            masa_jabatan = request.form.get('masa_jabatan', '').strip()
            status = request.form.get('status', 'Aktif').strip()
            icon = request.form.get('icon', '').strip()

            # Handle foto upload
            foto_url = request.form.get('foto_url', '').strip()
            foto_file = request.files.get('foto_file')
            if foto_file and foto_file.filename:
                from werkzeug.utils import secure_filename
                import os
                import uuid
                
                ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                filename = f"struktur_{uuid.uuid4().hex}.{ext}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'struktur')
                os.makedirs(upload_dir, exist_ok=True)
                foto_path = os.path.join(upload_dir, filename)
                foto_file.save(foto_path)
                foto_url = f'/static/uploads/struktur/{filename}'

            if not kategori or not nama:
                flash_error('Kategori dan Nama harus diisi!')
                return redirect(request.url)

            result = add_struktur(
                kategori=kategori, nama=nama, jabatan=jabatan, deskripsi=deskripsi,
                nik=nik, alamat=alamat, dusun=dusun, rt=rt, rw=rw,
                telepon=telepon, email=email, foto_url=foto_url, sk_url=sk_url,
                no_sk=no_sk, tanggal_sk=tanggal_sk, masa_jabatan=masa_jabatan,
                status=status, icon=icon
            )
            if result:
                flash('Data struktur berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.struktur'))
            else:
                flash_error('Gagal menambahkan data struktur. Silakan coba lagi.')
                return redirect(request.url)
        except Exception as e:
            logger.error(f"Error in add_struktur: {str(e)}")
            flash_error('Terjadi kesalahan saat menyimpan data')

    return render_template("admin/add_struktur.html")


@admin_bp.route("/struktur/edit/<int:struktur_id>", methods=['GET', 'POST'])
@admin_required
def edit_struktur_route(struktur_id):
    """Form edit struktur organisasi"""
    item = get_struktur_by_id(struktur_id)
    if not item:
        flash_error('Data tidak ditemukan!')
        return redirect(url_for('admin.struktur'))

    if request.method == 'POST':
        try:
            kategori = request.form.get('kategori', '').strip()
            nama = request.form.get('nama', '').strip()
            jabatan = request.form.get('jabatan', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            nik = request.form.get('nik', '').strip()
            alamat = request.form.get('alamat', '').strip()
            dusun = request.form.get('dusun', '').strip()
            rt = request.form.get('rt', '').strip()
            rw = request.form.get('rw', '').strip()
            telepon = request.form.get('telepon', '').strip()
            email = request.form.get('email', '').strip()
            sk_url = request.form.get('sk_url', '').strip()
            no_sk = request.form.get('no_sk', '').strip()
            tanggal_sk = request.form.get('tanggal_sk', '').strip()
            masa_jabatan = request.form.get('masa_jabatan', '').strip()
            status = request.form.get('status', 'Aktif').strip()
            icon = request.form.get('icon', '').strip()
            aktif = 1 if request.form.get('aktif') else 0
            no_urut = int(request.form.get('no_urut', '0').strip())

            # Handle foto upload
            foto_url = request.form.get('foto_url', '').strip()
            foto_file = request.files.get('foto_file')
            if foto_file and foto_file.filename:
                from werkzeug.utils import secure_filename
                import os
                import uuid
                
                ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                filename = f"struktur_{uuid.uuid4().hex}.{ext}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'struktur')
                os.makedirs(upload_dir, exist_ok=True)
                foto_path = os.path.join(upload_dir, filename)
                foto_file.save(foto_path)
                foto_url = f'/static/uploads/struktur/{filename}'

            if not kategori or not nama:
                flash_error('Kategori dan Nama harus diisi!')
                return redirect(request.url)

            result = update_struktur(
                struktur_id=struktur_id, kategori=kategori, nama=nama, jabatan=jabatan,
                deskripsi=deskripsi, nik=nik, alamat=alamat, dusun=dusun, rt=rt, rw=rw,
                telepon=telepon, email=email, foto_url=foto_url, sk_url=sk_url,
                no_sk=no_sk, tanggal_sk=tanggal_sk, masa_jabatan=masa_jabatan,
                status=status, icon=icon, aktif=aktif, no_urut=no_urut
            )
            if result:
                flash('Data struktur berhasil diperbarui!', 'success')
                return redirect(url_for('admin.struktur'))
            else:
                flash_error('Gagal memperbarui data struktur. Silakan coba lagi.')
                return redirect(request.url)
        except Exception as e:
            logger.error(f"Error in edit_struktur: {str(e)}")
            flash_error('Terjadi kesalahan saat menyimpan data')

    return render_template("admin/edit_struktur.html", item=item)


@admin_bp.route("/struktur/delete/<int:struktur_id>", methods=['POST'])
@admin_required
def delete_struktur_route(struktur_id):
    """Hapus struktur organisasi"""
    try:
        result = delete_struktur(struktur_id)
        if result:
            flash('Data berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus data. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting struktur {struktur_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus data')
    return redirect(url_for('admin.struktur'))


@admin_bp.route("/struktur/toggle/<int:struktur_id>", methods=['POST'])
@admin_required
def toggle_struktur_route(struktur_id):
    """Toggle aktif/nonaktif struktur"""
    try:
        result = toggle_struktur_aktif(struktur_id)
        if result:
            flash('Status berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status!')
    except Exception as e:
        logger.error(f"Error toggling struktur {struktur_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('admin.struktur'))


@admin_bp.route("/struktur/import", methods=['POST'])
@admin_required
def import_struktur():
    """Batch import struktur dari CSV"""
    try:
        file = request.files.get('csv_file')
        if not file:
            flash_error('File CSV wajib diupload')
            return redirect(url_for('admin.struktur'))
        
        csv_content = file.read().decode('utf-8')
        if not csv_content.strip():
            flash_error('File CSV kosong')
            return redirect(url_for('admin.struktur'))
        
        results = batch_import_struktur(csv_content)
        
        if results['success'] > 0:
            flash(f'Berhasil import {results["success"]} dari {results["total"]} data!', 'success')
        
        if results['errors']:
            error_msg = f'<br>'.join(results['errors'][:10])
            if len(results['errors']) > 10:
                error_msg += f'<br>...dan {len(results["errors"]) - 10} error lainnya'
            flash(f'Error:<br>{error_msg}', 'warning')
        
        return redirect(url_for('admin.struktur'))
        
    except Exception as e:
        logger.error(f"Error importing struktur: {str(e)}")
        flash_error(f'Error import: {str(e)}')
        return redirect(url_for('admin.struktur'))


@admin_bp.route("/struktur/export")
@admin_required
def export_struktur():
    """Export struktur ke CSV"""
    from flask import Response
    import csv
    import io
    
    struktur_list = get_all_struktur()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['kategori', 'nama', 'jabatan', 'nik', 'alamat', 'dusun', 'rt', 'rw', 'telepon', 'email', 'status', 'aktif'])
    
    # Data
    for item in struktur_list:
        writer.writerow([
            item.get('kategori', ''),
            item.get('nama', ''),
            item.get('jabatan', ''),
            item.get('nik', ''),
            item.get('alamat', ''),
            item.get('dusun', ''),
            item.get('rt', ''),
            item.get('rw', ''),
            item.get('telepon', ''),
            item.get('email', ''),
            item.get('status', ''),
            item.get('aktif', 1)
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=struktur_organisasi.csv'}
    )


@admin_bp.route("/struktur/template")
@admin_required
def download_struktur_template():
    """Download template CSV"""
    from flask import Response
    import io
    
    template = """kategori,nama,jabatan,nik,alamat,dusun,rt,rw,telepon,email,status,aktif
perangkat,Johannes Sitepu,Kepala Desa,,Jl. Desa No.1,Kedungwaru,,001,,,Aktif,1
perangkat,Maria Sitanggang,Sekretaris Desa,,Jl. Desa No.1,Kedungwaru,,001,,,Aktif,1
bpd,Ahmad Dahlan,Ketua BPD,,Jl. Desa No.2,Kedungwaru,,001,,,Aktif,1
pkk,Siti Aminah,Ketua PKK,,Jl. Desa No.3,Kedungwaru,,001,,,Aktif,1
karang_taruna,Budi Santoso,Ketua Karang Taruna,,Jl. Desa No.4,Kedungwaru,,001,,,Aktif,1
rt,Sukarno,Ketua RT 01,,Jl. Desa No.5,Kedungwaru,001,001,,Aktif,1
rw,Hassan Basri,Ketua RW 01,,Jl. Desa No.6,Kedungwaru,,001,,,Aktif,1"""
    
    return Response(
        template,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=template_struktur.csv'}
    )


# ════════════════════════════════════════════════════════════════════════
# ── UMKM MANAGEMENT ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/umkm")
@admin_required
def umkm():
    """Halaman manajemen UMKM"""
    try:
        umkm_list = get_all_umkm()
        return render_template("admin/umkm.html", umkm_list=umkm_list)
    except Exception as e:
        logger.error(f"Error loading umkm page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/umkm/parse-location", methods=['POST'])
@admin_required
def parse_umkm_location():
    """Parse Google Maps link to extract location data"""
    from flask import jsonify
    
    maps_url = request.json.get('maps_url', '').strip()
    
    if not maps_url:
        return jsonify({'success': False, 'error': 'URL kosong'})
    
    result = {
        'success': False,
        'latitude': None,
        'longitude': None,
        'nama': '',
        'alamat': '',
        'error': ''
    }
    
    try:
        # Pattern 1: Short URL (maps.app.goo.gl) - try to resolve
        if 'maps.app.goo.gl' in maps_url or ('goo.gl' in maps_url.lower() and 'maps' in maps_url.lower()):
            try:
                import urllib.request
                req = urllib.request.Request(maps_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req, timeout=10)
                maps_url = response.url
            except Exception as e:
                # Short URL resolve failed - try to extract from original URL anyway
                pass
        
        # Pattern 1b: Marker coordinates !3d...!4d... format (HARUS PRIORITAS - ini lokasi marker)
        # Extract ALL !3d!4d patterns and take the LAST one (usually the clicked marker)
        coord_matches = list(re.finditer(r'!3d(-?[\d.]+)!4d(-?[\d.]+)', maps_url))
        if coord_matches:
            # Take the LAST !3d!4d match (most recent marker click)
            last_match = coord_matches[-1]
            lat_from_data = float(last_match.group(1))
            lng_from_data = float(last_match.group(2))
            # Validate it's reasonable coordinates for Indonesia
            if -12 <= lat_from_data <= -5 and 95 <= lng_from_data <= 145:
                result['latitude'] = lat_from_data
                result['longitude'] = lng_from_data
                result['success'] = True
        
        # Pattern 2: @lat,lng format (most common) - e.g., maps.google.com/@-7.698188,109.651742,15z
        # Only use if we don't have valid marker coords yet
        if not result['success']:
            match = re.search(r'@(-?[\d.]+),(-?[\d.]+)', maps_url)
            if match:
                result['latitude'] = float(match.group(1))
                result['longitude'] = float(match.group(2))
                result['success'] = True
        
        # Pattern 3: /data=...!3d...!4d... format (older style)
        if not result['success']:
            coord_match = re.search(r'!3d(-?[\d.]+)!4d(-?[\d.]+)', maps_url)
            if coord_match:
                result['latitude'] = float(coord_match.group(1))
                result['longitude'] = float(coord_match.group(2))
                result['success'] = True
        
        # Pattern 4: query=lat,lng format - e.g., ?query=-7.7004,109.6432
        if not result['success']:
            lat_lng_match = re.search(r'[?&]query=(-?[\d.]+),(-?[\d.]+)', maps_url)
            if lat_lng_match:
                result['latitude'] = float(lat_lng_match.group(1))
                result['longitude'] = float(lat_lng_match.group(2))
                result['success'] = True
        
        # Pattern 5: /place/Name format - e.g., /place/Toko+Kita/@...
        place_match = re.search(r'/place/([^/@?]+)', maps_url)
        if place_match:
            import urllib.parse
            result['nama'] = urllib.parse.unquote(place_match.group(1).replace('+', ' '))
        
        # Pattern 6: Extract name from anywhere in URL
        if not result['nama']:
            name_match = re.search(r'(?:q|query)=([^&]+)', maps_url)
            if name_match:
                result['nama'] = name_match.group(1).replace('+', ' ').replace('%20', ' ')
        
        if not result['success']:
            result['error'] = 'Koordinat tidak ditemukan. Pastikan link berisi koordinat (format @lat,lng atau query=lat,lng)'
        
        return jsonify(result)
        
    except Exception as e:
        result['error'] = str(e)
        return jsonify(result)


@admin_bp.route("/umkm/add", methods=['GET', 'POST'])
@admin_required
def add_umkm_route():
    """Form tambah UMKM"""
    if request.method == 'POST':
        try:
            nama = request.form.get('nama', '').strip()
            kategori = request.form.get('kategori', 'umum').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            pemiliki_nama = request.form.get('pemiliki_nama', '').strip()
            pemiliki_kontak = request.form.get('pemiliki_kontak', '').strip()
            alamat = request.form.get('alamat', '').strip()
            dusun = request.form.get('dusun', '').strip()
            rt = request.form.get('rt', '').strip()
            rw = request.form.get('rw', '').strip()
            lat = request.form.get('latitude', '').strip()
            lng = request.form.get('longitude', '').strip()
            foto_url = request.form.get('foto_url', '').strip()
            produk_jasa = request.form.get('produk_jasa', '').strip()
            harga_range = request.form.get('harga_range', '').strip()
            jam_operasional = request.form.get('jam_operasional', '').strip()

            latitude = float(lat) if lat else None
            longitude = float(lng) if lng else None

            if not nama:
                flash_error('Nama UMKM wajib diisi!')
                return redirect(request.url)

            result = add_umkm(
                nama=nama, kategori=kategori, deskripsi=deskripsi,
                pemiliki_nama=pemiliki_nama, pemiliki_kontak=pemiliki_kontak,
                alamat=alamat, dusun=dusun, rt=rt, rw=rw,
                latitude=latitude, longitude=longitude,
                foto_url=foto_url, produk_jasa=produk_jasa,
                harga_range=harga_range, jam_operasional=jam_operasional
            )
            if result:
                flash('Data UMKM berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.umkm'))
            else:
                flash_error('Gagal menambahkan data!')
        except Exception as e:
            logger.error(f"Error adding umkm: {str(e)}")
            flash_error('Terjadi kesalahan saat menyimpan data')
    return render_template("admin/add_umkm.html")


@admin_bp.route("/umkm/edit/<int:umkm_id>", methods=['GET', 'POST'])
@admin_required
def edit_umkm_route(umkm_id):
    """Form edit UMKM"""
    item = get_umkm_by_id(umkm_id)
    if not item:
        flash_error('Data tidak ditemukan!')
        return redirect(url_for('admin.umkm'))

    if request.method == 'POST':
        try:
            nama = request.form.get('nama', '').strip()
            kategori = request.form.get('kategori', 'umum').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            pemiliki_nama = request.form.get('pemiliki_nama', '').strip()
            pemiliki_kontak = request.form.get('pemiliki_kontak', '').strip()
            alamat = request.form.get('alamat', '').strip()
            dusun = request.form.get('dusun', '').strip()
            rt = request.form.get('rt', '').strip()
            rw = request.form.get('rw', '').strip()
            lat = request.form.get('latitude', '').strip()
            lng = request.form.get('longitude', '').strip()
            foto_url = request.form.get('foto_url', '').strip()
            produk_jasa = request.form.get('produk_jasa', '').strip()
            harga_range = request.form.get('harga_range', '').strip()
            jam_operasional = request.form.get('jam_operasional', '').strip()
            aktif = 1 if request.form.get('aktif') else 0
            urutan = int(request.form.get('urutan', 0))

            latitude = float(lat) if lat else None
            longitude = float(lng) if lng else None

            if not nama:
                flash_error('Nama wajib diisi!')
                return redirect(request.url)

            result = update_umkm(
                umkm_id=umkm_id, nama=nama, kategori=kategori, deskripsi=deskripsi,
                pemiliki_nama=pemiliki_nama, pemiliki_kontak=pemiliki_kontak,
                alamat=alamat, dusun=dusun, rt=rt, rw=rw,
                latitude=latitude, longitude=longitude,
                foto_url=foto_url, produk_jasa=produk_jasa,
                harga_range=harga_range, jam_operasional=jam_operasional,
                aktif=aktif, urutan=urutan
            )
            if result:
                flash('Data berhasil diperbarui!', 'success')
                return redirect(url_for('admin.umkm'))
            else:
                flash_error('Gagal memperbarui data!')
        except Exception as e:
            logger.error(f"Error updating umkm: {str(e)}")
            flash_error('Terjadi kesalahan saat menyimpan')

    return render_template("admin/edit_umkm.html", item=item)


@admin_bp.route("/umkm/delete/<int:umkm_id>", methods=['POST'])
@admin_required
def delete_umkm_route(umkm_id):
    """Hapus UMKM"""
    try:
        result = delete_umkm(umkm_id)
        if result:
            flash('Data berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus!')
    except Exception as e:
        logger.error(f"Error deleting umkm: {str(e)}")
        flash_error('Terjadi kesalahan')
    return redirect(url_for('admin.umkm'))


@admin_bp.route("/umkm/toggle/<int:umkm_id>", methods=['POST'])
@admin_required
def toggle_umkm_route(umkm_id):
    """Toggle aktif/nonaktif"""
    try:
        result = toggle_umkm_aktif(umkm_id)
        if result:
            flash('Status berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status!')
    except Exception as e:
        logger.error(f"Error toggling umkm: {str(e)}")
        flash_error('Terjadi kesalahan')
    return redirect(url_for('admin.umkm'))


# ════════════════════════════════════════════════════════════════════════
# ── KEPENDUDUKAN MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/kependudukan", methods=['GET', 'POST'])
@admin_required
def kependudukan():
    """Halaman manage kependudukan dengan charts"""
    try:
        all_data = get_all_kependudukan()
        # Build stats dict with hanya jumlah value
        stats = {}
        for item in all_data:
            key = item['label'].lower().replace(' ', '_')
            stats[key] = item.get('jumlah', 0)

        if request.method == 'POST':
            # Update all population data
            updates = [
                ('total', 'total_penduduk', request.form.get('total_penduduk', 0)),
                ('jk', 'laki_laki', request.form.get('laki_laki', 0)),
                ('jk', 'perempuan', request.form.get('perempuan', 0)),
                ('kk', 'jumlah_kk', request.form.get('jumlah_kk', 0)),
                ('produktif', 'usia_produktif_total', request.form.get('usia_produktif_total', 0)),
                ('produktif', 'pekerja', request.form.get('pekerja', 0)),
                ('produktif', 'pelajar', request.form.get('pelajar', 0)),
                ('produktif', 'irt', request.form.get('irt', 0)),
                ('non_produktif', 'usia_0_14', request.form.get('usia_0_14', 0)),
                ('non_produktif', 'usia_65_plus', request.form.get('usia_65_plus', 0)),
            ]
            for kategori, label, jumlah in updates:
                try:
                    update_kependudukan(kategori, label, int(jumlah) if jumlah else 0)
                except:
                    pass
            flash('Data kependudukan berhasil disimpan!', 'success')
            return redirect(url_for('admin.kependudukan'))

        return render_template("admin/kependudukan.html", stats=stats)
    except Exception as e:
        logger.error(f"Error kependudukan: {str(e)}")
        flash_error('Terjadi kesalahan')
        return redirect(url_for('admin.dashboard'))


# ════════════════════════════════════════════════════════════════════════
# ── PENGUMUMAN MANAGEMENT ──────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/pengumuman")
@admin_required
def pengumuman():
    """Halaman manajemen pengumuman"""
    try:
        from models import get_all_pengumuman
        pengumuman_list = get_all_pengumuman()
        return render_template("admin/pengumuman.html", pengumuman_list=pengumuman_list)
    except Exception as e:
        logger.error(f"Error loading pengumuman page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman pengumuman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/pengumuman/add", methods=['GET', 'POST'])
@admin_required
def add_pengumuman_route():
    """Form tambah pengumuman"""
    try:
        from models import add_pengumuman

        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            isi = request.form.get('isi', '').strip()
            kategori = request.form.get('kategori', 'umum')
            is_penting = 1 if request.form.get('is_penting') else 0
            lampiran = request.form.get('lampiran', '').strip()
            author = request.form.get('author', 'Pemerintahan Desa').strip()

            if not judul or not isi:
                flash_error('Judul dan Isi harus diisi!')
                return redirect(request.url)

            result = add_pengumuman(judul, isi, kategori, is_penting, lampiran, author)
            if result:
                flash('Pengumuman berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.pengumuman'))
            else:
                flash_error('Gagal menambahkan pengumuman. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_pengumuman.html")
    except Exception as e:
        logger.error(f"Error in add_pengumuman_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form pengumuman')
        return redirect(url_for('admin.pengumuman'))


@admin_bp.route("/pengumuman/edit/<int:pengumuman_id>", methods=['GET', 'POST'])
@admin_required
def edit_pengumuman_route(pengumuman_id):
    """Form edit pengumuman"""
    try:
        from models import get_pengumuman_by_id, update_pengumuman

        item = get_pengumuman_by_id(pengumuman_id)
        if not item:
            flash_error('Pengumuman tidak ditemukan!')
            return redirect(url_for('admin.pengumuman'))

        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            isi = request.form.get('isi', '').strip()
            kategori = request.form.get('kategori', 'umum')
            is_penting = 1 if request.form.get('is_penting') else 0
            lampiran = request.form.get('lampiran', '').strip()
            author = request.form.get('author', 'Pemerintahan Desa').strip()

            if not judul or not isi:
                flash_error('Judul dan Isi harus diisi!')
                return redirect(request.url)

            result = update_pengumuman(pengumuman_id, judul, isi, kategori, is_penting, lampiran, author)
            if result:
                flash('Pengumuman berhasil diperbarui!', 'success')
                return redirect(url_for('admin.pengumuman'))
            else:
                flash_error('Gagal memperbarui pengumuman. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_pengumuman.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_pengumuman_route {pengumuman_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form pengumuman')
        return redirect(url_for('admin.pengumuman'))


@admin_bp.route("/pengumuman/delete/<int:pengumuman_id>", methods=['POST'])
@admin_required
def delete_pengumuman_route(pengumuman_id):
    """Hapus pengumuman"""
    try:
        from models import delete_pengumuman
        result = delete_pengumuman(pengumuman_id)
        if result:
            flash('Pengumuman berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus pengumuman. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting pengumuman {pengumuman_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus pengumuman')
    return redirect(url_for('admin.pengumuman'))


@admin_bp.route("/pengumuman/toggle/<int:pengumuman_id>", methods=['POST'])
@admin_required
def toggle_pengumuman_route(pengumuman_id):
    """Toggle status aktif/nonaktif pengumuman"""
    try:
        from models import toggle_pengumuman_aktif
        result = toggle_pengumuman_aktif(pengumuman_id)
        if result:
            flash('Status pengumuman berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status pengumuman.')
    except Exception as e:
        logger.error(f"Error toggling pengumuman {pengumuman_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status pengumuman')
    return redirect(url_for('admin.pengumuman'))


# ════════════════════════════════════════════════════════════════════════
# ── APBDes MANAGEMENT ──────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/apbdes")
@admin_required
def apbdes():
    """Halaman manajemen APBDes"""
    try:
        from models import get_apbdes_by_tahun, get_apbdes_summary, get_available_tahun
        from datetime import datetime

        tahun_list = get_available_tahun()
        if not tahun_list:
            tahun_list = [datetime.now().year]

        tahun = request.args.get('tahun', tahun_list[0], type=int)
        apbdes_list = get_apbdes_by_tahun(tahun)
        summary = get_apbdes_summary(tahun)

        # Group by jenis
        grouped = {'pendapatan': [], 'belanja': [], 'pembiayaan': []}
        for item in apbdes_list:
            if item['jenis'] in grouped:
                grouped[item['jenis']].append(item)

        return render_template("admin/apbdes.html", apbdes_list=apbdes_list, grouped=grouped, summary=summary, tahun_list=tahun_list, tahun=tahun)
    except Exception as e:
        logger.error(f"Error loading apbdes page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman APBDes')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/apbdes/add", methods=['GET', 'POST'])
@admin_required
def add_apbdes_route():
    """Form tambah item APBDes"""
    try:
        from models import add_apbdes_item
        from datetime import datetime

        if request.method == 'POST':
            tahun = request.form.get('tahun', datetime.now().year, type=int)
            jenis = request.form.get('jenis', '').strip()
            nama = request.form.get('nama', '').strip()
            jumlah = request.form.get('jumlah', 0, type=int)
            icon = request.form.get('icon', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()

            if not jenis or not nama:
                flash_error('Jenis dan Nama harus diisi!')
                return redirect(request.url)

            result = add_apbdes_item(tahun, jenis, nama, jumlah, icon, deskripsi)
            if result:
                flash('Item APBDes berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.apbdes'))
            else:
                flash_error('Gagal menambahkan item. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_apbdes.html")
    except Exception as e:
        logger.error(f"Error in add_apbdes_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form APBDes')
        return redirect(url_for('admin.apbdes'))


@admin_bp.route("/apbdes/edit/<int:apbdes_id>", methods=['GET', 'POST'])
@admin_required
def edit_apbdes_route(apbdes_id):
    """Form edit item APBDes"""
    try:
        from models import get_apbdes_by_id, update_apbdes_item

        item = get_apbdes_by_id(apbdes_id)
        if not item:
            flash_error('Item tidak ditemukan!')
            return redirect(url_for('admin.apbdes'))

        if request.method == 'POST':
            tahun = request.form.get('tahun', 2026, type=int)
            jenis = request.form.get('jenis', '').strip()
            nama = request.form.get('nama', '').strip()
            jumlah = request.form.get('jumlah', 0, type=int)
            icon = request.form.get('icon', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()

            if not jenis or not nama:
                flash_error('Jenis dan Nama harus diisi!')
                return redirect(request.url)

            result = update_apbdes_item(apbdes_id, tahun, jenis, nama, jumlah, icon, deskripsi)
            if result:
                flash('Item APBDes berhasil diperbarui!', 'success')
                return redirect(url_for('admin.apbdes'))
            else:
                flash_error('Gagal memperbarui item. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_apbdes.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_apbdes_route {apbdes_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form APBDes')
        return redirect(url_for('admin.apbdes'))


@admin_bp.route("/apbdes/delete/<int:apbdes_id>", methods=['POST'])
@admin_required
def delete_apbdes_route(apbdes_id):
    """Hapus item APBDes"""
    try:
        from models import delete_apbdes_item
        result = delete_apbdes_item(apbdes_id)
        if result:
            flash('Item berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus item. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting apbdes {apbdes_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus item')
    return redirect(url_for('admin.apbdes'))


# ════════════════════════════════════════════════════════════════════════
# ── POTENSI DESA MANAGEMENT ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/potensi")
@admin_required
def potensi():
    """Halaman manajemen potensi desa"""
    try:
        potensi_list = get_all_potensi()

        # Group by kategori
        grouped = {}
        for item in potensi_list:
            kat = item.get('kategori', 'Lainnya')
            if kat not in grouped:
                grouped[kat] = []
            grouped[kat].append(item)

        return render_template("admin/potensi.html", potensi_list=potensi_list, grouped=grouped)
    except Exception as e:
        logger.error(f"Error loading potensi page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman potensi')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/potensi/add", methods=['GET', 'POST'])
@admin_required
def add_potensi_route():
    """Form tambah potensi desa"""
    try:
        if request.method == 'POST':
            nama = request.form.get('nama', '').strip()
            kategori = request.form.get('kategori', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            icon = request.form.get('icon', '').strip()

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'potensi')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not nama or not kategori:
                flash_error('Nama dan Kategori harus diisi!')
                return redirect(request.url)

            result = add_potensi(nama, kategori, deskripsi, gambar_url, icon)
            if result:
                flash('Potensi berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.potensi'))
            else:
                flash_error('Gagal menambahkan potensi. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_potensi.html")
    except Exception as e:
        logger.error(f"Error in add_potensi_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form potensi')
        return redirect(url_for('admin.potensi'))


@admin_bp.route("/potensi/edit/<int:potensi_id>", methods=['GET', 'POST'])
@admin_required
def edit_potensi_route(potensi_id):
    """Form edit potensi desa"""
    try:
        item = get_potensi_by_id(potensi_id)
        if not item:
            flash_error('Potensi tidak ditemukan!')
            return redirect(url_for('admin.potensi'))

        if request.method == 'POST':
            nama = request.form.get('nama', '').strip()
            kategori = request.form.get('kategori', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            icon = request.form.get('icon', '').strip()
            aktif = 1 if request.form.get('aktif') else 0

            # Handle image upload (file or URL)
            gambar_url = ''
            file = request.files.get('gambar_file')
            if file and file.filename:
                gambar_url = save_uploaded_file(file, 'potensi')
            if not gambar_url:
                gambar_url = request.form.get('gambar_url', '').strip()

            if not nama or not kategori:
                flash_error('Nama dan Kategori harus diisi!')
                return redirect(request.url)

            result = update_potensi(potensi_id, nama, kategori, deskripsi, gambar_url, icon, aktif)
            if result:
                flash('Potensi berhasil diperbarui!', 'success')
                return redirect(url_for('admin.potensi'))
            else:
                flash_error('Gagal memperbarui potensi. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_potensi.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_potensi_route {potensi_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form potensi')
        return redirect(url_for('admin.potensi'))


@admin_bp.route("/potensi/delete/<int:potensi_id>", methods=['POST'])
@admin_required
def delete_potensi_route(potensi_id):
    """Hapus potensi desa"""
    try:
        result = delete_potensi(potensi_id)
        if result:
            flash('Potensi berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus potensi. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting potensi {potensi_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus potensi')
    return redirect(url_for('admin.potensi'))


@admin_bp.route("/potensi/toggle/<int:potensi_id>", methods=['POST'])
@admin_required
def toggle_potensi_route(potensi_id):
    """Toggle status aktif/nonaktif potensi"""
    try:
        result = toggle_potensi_aktif(potensi_id)
        if result:
            flash('Status potensi berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status potensi.')
    except Exception as e:
        logger.error(f"Error toggling potensi {potensi_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status potensi')
    return redirect(url_for('admin.potensi'))


# ════════════════════════════════════════════════════════════════════════
# ── KRITIK DAN SARAN MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/kritik-saran")
@admin_required
def kritik_saran():
    """Halaman daftar kritik dan saran"""
    try:
        kritik_saran_list = get_all_kritik_saran(include_read=True)
        stats = get_kritik_saran_stats()
        
        return render_template(
            "admin/kritik_saran.html",
            kritik_saran_list=kritik_saran_list,
            stats=stats,
        )
    except Exception as e:
        logger.error(f"Error loading kritik_saran: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route("/kritik-saran/read/<int:ks_id>", methods=['POST'])
@admin_required
def read_kritik_saran(ks_id):
    """Tandai kritik/saran sudah dibaca"""
    try:
        result = mark_kritik_saran_read(ks_id)
        if result:
            flash('Kritik/saran ditandai sudah dibaca', 'success')
        else:
            flash_error('Gagal menandai kritik/saran')
    except Exception as e:
        logger.error(f"Error marking kritik_saran read {ks_id}: {str(e)}")
        flash_error('Terjadi kesalahan')
    return redirect(url_for('admin.kritik_saran'))

@admin_bp.route("/kritik-saran/delete/<int:ks_id>", methods=['POST'])
@admin_required
def delete_kritik_saran_route(ks_id):
    """Hapus kritik/saran"""
    try:
        result = delete_kritik_saran(ks_id)
        if result:
            flash('Kritik/saran berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus kritik/saran')
    except Exception as e:
        logger.error(f"Error deleting kritik_saran {ks_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.kritik_saran'))


# ════════════════════════════════════════════════════════════════════════
# ── ADUAN MANAGEMENT ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/aduan")
@admin_required
def aduan():
    """Halaman daftar aduan"""
    try:
        from models import get_all_aduan, get_aduan_stats
        aduan_list = get_all_aduan()
        stats = get_aduan_stats()
        
        # Filter
        status_filter = request.args.get('status', '')
        if status_filter:
            aduan_list = [a for a in aduan_list if a.get('status') == status_filter]
        
        return render_template(
            "admin/aduan.html",
            aduan_list=aduan_list,
            stats=stats,
            status_filter=status_filter,
        )
    except Exception as e:
        logger.error(f"Error loading aduan: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/aduan/<int:aduan_id>", methods=['GET', 'POST'])
@admin_required
def aduan_detail(aduan_id):
    """Detail aduan dan form respon"""
    try:
        from models import get_aduan_by_id, respond_aduan
        
        item = get_aduan_by_id(aduan_id)
        if not item:
            flash_error('Aduan tidak ditemukan!')
            return redirect(url_for('admin.aduan'))
        
        if request.method == 'POST':
            action = request.form.get('action', '')
            
            if action == 'respond':
                catatan = request.form.get('catatan', '').strip()
                logger.info(f"[ADUAN] respond action: aduan_id={aduan_id}, catatan length={len(catatan)}")
                if catatan:
                    result = respond_aduan(aduan_id, catatan, session.get('user_id'))
                    if result:
                        flash('Tanggapan berhasil dikirim!', 'success')
                    else:
                        logger.warning(f"[ADUAN] respond_aduan returned False for aduan_id={aduan_id}")
                        flash_error('Gagal mengirim tanggapan.')
                else:
                    flash_error('Catatan/tanggapan wajib diisi!')
            
            elif action == 'update_status':
                logger.info(f"[ADUAN] update_status action: aduan_id={aduan_id}")
                from models import update_aduan
                status = request.form.get('status', '')
                catatan = request.form.get('catatan', '').strip()
                judul = request.form.get('judul', item['judul'])
                isi = request.form.get('deskripsi', item.get('isi', ''))
                kategori = request.form.get('kategori', item['kategori'])
                lokasi = request.form.get('lokasi', item['lokasi'] or '')
                
                result = update_aduan(aduan_id, judul, isi, kategori, lokasi, status, None, catatan)
                if result:
                    flash('Status aduan berhasil diperbarui!', 'success')
                else:
                    logger.warning(f"[ADUAN] update_aduan returned False for aduan_id={aduan_id}")
                    flash_error('Gagal memperbarui status.')
            
            return redirect(url_for('admin.aduan_detail', aduan_id=aduan_id))
        
        return render_template("admin/aduan_detail.html", item=item)
    except Exception as e:
        logger.error(f"Error loading aduan detail {aduan_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.aduan'))


@admin_bp.route("/aduan/delete/<int:aduan_id>", methods=['POST'])
@admin_required
def delete_aduan_route(aduan_id):
    """Hapus aduan"""
    try:
        from models import delete_aduan
        result = delete_aduan(aduan_id)
        if result:
            flash('Aduan berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus aduan')
    except Exception as e:
        logger.error(f"Error deleting aduan {aduan_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.aduan'))


# ════════════════════════════════════════════════════════════════════════
# ── PROGRAM KERJA MANAGEMENT ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/program-kerja")
@admin_required
def program_kerja():
    """Halaman manajemen program kerja"""
    try:
        from models import get_all_program_kerja
        program_list = get_all_program_kerja()
        
        # Filter
        tahun_filter = request.args.get('tahun', type=int)
        if tahun_filter:
            program_list = [p for p in program_list if p.get('tahun') == tahun_filter]
        
        # Group by status
        grouped = {'rencana': [], 'berlangsung': [], 'selesai': []}
        for p in program_list:
            status = p.get('status', 'berlangsung')
            if status in grouped:
                grouped[status].append(p)
        
        return render_template(
            "admin/program_kerja.html",
            program_list=program_list,
            grouped=grouped,
            tahun_filter=tahun_filter,
        )
    except Exception as e:
        logger.error(f"Error loading program_kerja: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/program-kerja/add", methods=['GET', 'POST'])
@admin_required
def add_program_kerja_route():
    """Form tambah program kerja"""
    try:
        from models import add_program_kerja
        from datetime import datetime
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'pembangunan')
            tahun = request.form.get('tahun', datetime.now().year, type=int)
            target = request.form.get('target', '').strip()
            realiasi = request.form.get('realiasi', '').strip()
            anggaran = request.form.get('anggaran', '').strip()
            icon = request.form.get('icon', '📋').strip()
            status = request.form.get('status', 'berlangsung')
            
            if not judul:
                flash_error('Judul program kerja harus diisi!')
                return redirect(request.url)
            
            result = add_program_kerja(nama=judul, deskripsi=deskripsi, kategori=kategori, tahun=tahun, target=target, realiasi=realiasi, anggaran=anggaran, icon=icon, status=status)
            logger.info(f"[PROGRAM_KERJA] add_program_kerja called with: judul={judul}, kategori={kategori}, tahun={tahun}, status={status}")
            if result:
                flash('Program kerja berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.program_kerja'))
            else:
                logger.warning(f"[PROGRAM_KERJA] add_program_kerja returned False for judul={judul}")
                flash_error('Gagal menambahkan program kerja.')
                return redirect(request.url)
        
        return render_template("admin/add_program_kerja.html")
    except Exception as e:
        logger.error(f"Error in add_program_kerja_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/edit/<int:program_id>", methods=['GET', 'POST'])
@admin_required
def edit_program_kerja_route(program_id):
    """Form edit program kerja"""
    try:
        from models import get_program_kerja_by_id, update_program_kerja
        from datetime import datetime
        
        item = get_program_kerja_by_id(program_id)
        if not item:
            flash_error('Program kerja tidak ditemukan!')
            return redirect(url_for('admin.program_kerja'))
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'pembangunan')
            tahun = request.form.get('tahun', datetime.now().year, type=int)
            target = request.form.get('target', '').strip()
            realiasi = request.form.get('realiasi', '').strip()
            anggaran = request.form.get('anggaran', '').strip()
            icon = request.form.get('icon', '📋').strip()
            status = request.form.get('status', 'berlangsung')
            aktif = 1 if request.form.get('aktif') else 0
            urutan = request.form.get('urutan', 0, type=int)
            
            if not judul:
                flash_error('Judul program kerja harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[PROGRAM_KERJA] update_program_kerja called: id={program_id}, nama={judul}")
            result = update_program_kerja(program_id, nama=judul, deskripsi=deskripsi, kategori=kategori, tahun=tahun, target=target, realiasi=realiasi, anggaran=anggaran, icon=icon, status=status, aktif=aktif, urutan=urutan)
            if result:
                flash('Program kerja berhasil diperbarui!', 'success')
                return redirect(url_for('admin.program_kerja'))
            else:
                logger.warning(f"[PROGRAM_KERJA] update_program_kerja returned False for id={program_id}")
                flash_error('Gagal memperbarui program kerja.')
                return redirect(request.url)
        
        return render_template("admin/edit_program_kerja.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_program_kerja_route {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/delete/<int:program_id>", methods=['POST'])
@admin_required
def delete_program_kerja_route(program_id):
    """Hapus program kerja"""
    try:
        from models import delete_program_kerja
        result = delete_program_kerja(program_id)
        if result:
            flash('Program kerja berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus program kerja')
    except Exception as e:
        logger.error(f"Error deleting program_kerja {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/toggle/<int:program_id>", methods=['POST'])
@admin_required
def toggle_program_kerja_route(program_id):
    """Toggle status aktif program kerja"""
    try:
        from models import toggle_program_kerja_aktif
        result = toggle_program_kerja_aktif(program_id)
        if result:
            flash('Status program kerja berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status program kerja.')
    except Exception as e:
        logger.error(f"Error toggling program_kerja {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('admin.program_kerja'))


# ════════════════════════════════════════════════════════════════════════
# ── AGENDA MANAGEMENT ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/agenda")
@admin_required
def agenda():
    """Halaman manajemen agenda"""
    try:
        from models import get_all_agenda
        agenda_list = get_all_agenda()
        
        # Filter
        tahun_filter = request.args.get('tahun', type=int)
        status_filter = request.args.get('status', '')
        
        if tahun_filter:
            agenda_list = [a for a in agenda_list if a.get('tanggal_mulai') and str(tahun_filter) in str(a['tanggal_mulai'])]
        if status_filter:
            agenda_list = [a for a in agenda_list if a.get('status') == status_filter]
        
        return render_template(
            "admin/agenda.html",
            agenda_list=agenda_list,
            tahun_filter=tahun_filter,
            status_filter=status_filter,
        )
    except Exception as e:
        logger.error(f"Error loading agenda: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/agenda/add", methods=['GET', 'POST'])
@admin_required
def add_agenda_route():
    """Form tambah agenda"""
    try:
        from models import add_agenda
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'kegiatan')
            tanggal_mulai = request.form.get('tanggal_mulai', '')
            tanggal_selesai = request.form.get('tanggal_selesai', '')
            waktu = request.form.get('waktu', '').strip()
            lokasi = request.form.get('lokasi', '').strip()
            icon = request.form.get('icon', '📅').strip()
            penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
            peserta = request.form.get('peserta', '').strip()
            status = request.form.get('status', 'akan_datang')
            
            if not judul or not tanggal_mulai:
                flash_error('Judul dan Tanggal Mulai harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[AGENDA] add_agenda called: judul={judul}, tanggal={tanggal_mulai}")
            result = add_agenda(judul=judul, deskripsi=deskripsi, kategori=kategori, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai or None, waktu=waktu, lokasi=lokasi, icon=icon, penanggung_jawab=penanggung_jawab, peserta=peserta, status=status)
            if result:
                flash('Agenda berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.agenda'))
            else:
                logger.warning(f"[AGENDA] add_agenda returned False for judul={judul}")
                flash_error('Gagal menambahkan agenda.')
                return redirect(request.url)
        
        return render_template("admin/add_agenda.html")
    except Exception as e:
        logger.error(f"Error in add_agenda_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/edit/<int:agenda_id>", methods=['GET', 'POST'])
@admin_required
def edit_agenda_route(agenda_id):
    """Form edit agenda"""
    try:
        from models import get_agenda_by_id, update_agenda
        
        item = get_agenda_by_id(agenda_id)
        if not item:
            flash_error('Agenda tidak ditemukan!')
            return redirect(url_for('admin.agenda'))
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'kegiatan')
            tanggal_mulai = request.form.get('tanggal_mulai', '')
            tanggal_selesai = request.form.get('tanggal_selesai', '')
            waktu = request.form.get('waktu', '').strip()
            lokasi = request.form.get('lokasi', '').strip()
            icon = request.form.get('icon', '📅').strip()
            penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
            peserta = request.form.get('peserta', '').strip()
            status = request.form.get('status', 'akan_datang')
            aktif = 1 if request.form.get('aktif') else 0
            urutan = request.form.get('urutan', 0, type=int)
            
            if not judul or not tanggal_mulai:
                flash_error('Judul dan Tanggal Mulai harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[AGENDA] update_agenda called: id={agenda_id}, judul={judul}")
            result = update_agenda(agenda_id, judul=judul, deskripsi=deskripsi, kategori=kategori, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai or None, waktu=waktu, lokasi=lokasi, icon=icon, penanggung_jawab=penanggung_jawab, peserta=peserta, status=status, aktif=aktif, urutan=urutan)
            if result:
                flash('Agenda berhasil diperbarui!', 'success')
                return redirect(url_for('admin.agenda'))
            else:
                logger.warning(f"[AGENDA] update_agenda returned False for id={agenda_id}")
                flash_error('Gagal memperbarui agenda.')
                return redirect(request.url)
        
        return render_template("admin/edit_agenda.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_agenda_route {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/delete/<int:agenda_id>", methods=['POST'])
@admin_required
def delete_agenda_route(agenda_id):
    """Hapus agenda"""
    try:
        from models import delete_agenda
        result = delete_agenda(agenda_id)
        if result:
            flash('Agenda berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus agenda')
    except Exception as e:
        logger.error(f"Error deleting agenda {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/toggle/<int:agenda_id>", methods=['POST'])
@admin_required
def toggle_agenda_route(agenda_id):
    """Toggle status aktif agenda"""
    try:
        from models import toggle_agenda_aktif
        result = toggle_agenda_aktif(agenda_id)
        if result:
            flash('Status agenda berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status agenda.')
    except Exception as e:
        logger.error(f"Error toggling agenda {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('admin.agenda'))
