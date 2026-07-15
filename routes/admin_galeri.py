"""
Admin Galeri Routes
Part of admin.py refactoring
"""

import logging
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from config import Config, compress_and_save_image

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated_function


def flash_error(msg):
    flash(msg, 'error')


def allowed_image(filename):
    ALLOWED_EXTENSIONS = Config.ALLOWED_IMAGE_EXT
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder=''):
    """Save uploaded image with WebP compression.
    If image > 2MB, apply extreme compression by reducing resolution."""
    if not file or not file.filename or not allowed_image(file.filename):
        return None

    upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder) if subfolder else Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)

    file.seek(0)
    file_bytes = file.read()

    try:
        filename, _ = compress_and_save_image(file_bytes, upload_dir)
    except Exception:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_bytes)

    if subfolder:
        return f"/uploads/{subfolder}/{filename}"
    return f"/uploads/{filename}"


# ── Galeri Management ────────────────────────────────────────────────────

@admin_bp.route("/galeri")
@admin_required
def galeri():
    """Halaman manajemen galeri"""
    from models import get_all_galeri

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
    from models import add_galeri

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
    from models import get_galeri_by_id, update_galeri

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
    from models import delete_galeri

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
    from models import toggle_galeri_aktif

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
