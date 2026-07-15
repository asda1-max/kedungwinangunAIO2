"""
Admin Berita Routes
Part of admin.py refactoring
"""

import logging
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from functools import wraps
from config import Config, compress_and_save_image

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin login"""
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


# ── Berita Management ────────────────────────────────────────────────────

@admin_bp.route("/berita/add", methods=['GET', 'POST'])
@admin_required
def add_berita_route():
    """Form tambah berita"""
    from models import add_berita

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
    from models import get_berita_by_id, update_berita

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
    from models import delete_berita

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
