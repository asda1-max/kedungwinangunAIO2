"""
Admin E-Library Routes
CRUD for ebook management
"""

import logging
import os
import uuid
import mimetypes
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_from_directory
from functools import wraps
from config import Config

logger = logging.getLogger(__name__)
ebook_bp = Blueprint('ebook', __name__, url_prefix='/admin')


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


def allowed_pdf(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


def allowed_cover(filename):
    ALLOWED = Config.ALLOWED_IMAGE_EXT
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def save_pdf_file(file):
    if not file or not file.filename or not allowed_pdf(file.filename):
        logger.warning(f"save_pdf_file skipped: file={bool(file)}, filename='{getattr(file, 'filename', '')}'")
        return None
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'ebook')
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"save_pdf_file: failed to create dir {upload_dir}: {str(e)}")
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    try:
        file.save(filepath)
    except Exception as e:
        logger.error(f"save_pdf_file: failed to save {filepath}: {str(e)}")
        return None
    return f"/uploads/ebook/{filename}"


def save_cover_image(file):
    if not file or not file.filename or not allowed_cover(file.filename):
        return None
    from config import compress_and_save_image
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'ebook')
    os.makedirs(upload_dir, exist_ok=True)
    file.seek(0)
    file_bytes = file.read()
    try:
        filename, _ = compress_and_save_image(file_bytes, upload_dir, filename_prefix='cover_')
    except Exception:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"cover_{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_bytes)
    return f"/uploads/ebook/{filename}"


@ebook_bp.route('/ebook')
@admin_required
def ebook_index():
    from models import get_all_ebook
    try:
        ebook_list = get_all_ebook()
        return render_template('admin/ebook.html', ebook_list=ebook_list, total=len(ebook_list))
    except Exception as e:
        logger.error(f"Error loading ebook page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman e-library')
        return redirect(url_for('admin.dashboard'))


@ebook_bp.route('/ebook/add', methods=['GET', 'POST'])
@admin_required
def ebook_add():
    from models import add_ebook
    try:
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            penulis = request.form.get('penulis', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'umum')
            tahun = request.form.get('tahun', '').strip()
            halaman = request.form.get('halaman', 0, type=int) or 0
            bahasa = request.form.get('bahasa', 'Indonesia').strip()

            file_path = ''
            pdf_file = request.files.get('file_path')
            if pdf_file and pdf_file.filename:
                file_path = save_pdf_file(pdf_file)
            if not file_path:
                file_path = request.form.get('file_url', '').strip()

            cover_url = ''
            cover_file = request.files.get('cover_file')
            if cover_file and cover_file.filename:
                cover_url = save_cover_image(cover_file)
            if not cover_url:
                cover_url = request.form.get('cover_url', '').strip()

            if not judul:
                flash_error('Judul buku wajib diisi!')
                return redirect(request.url)

            if not file_path:
                flash_error('File PDF wajib diupload atau URL wajib diisi!')
                return redirect(request.url)

            result = add_ebook(judul, file_path, penulis, deskripsi, kategori,
                              cover_url, tahun, halaman, bahasa)
            if result:
                flash('Buku berhasil ditambahkan ke e-library!', 'success')
                return redirect(url_for('ebook.ebook_index'))
            else:
                flash_error('Gagal menyimpan ke database. Periksa log untuk detail.')
                return redirect(request.url)

        return render_template('admin/add_ebook.html')
    except Exception as e:
        logger.error(f"Error in ebook_add: {str(e)}", exc_info=True)
        flash_error('Terjadi kesalahan: ' + str(e)[:100])
        return redirect(url_for('ebook.ebook_index'))


@ebook_bp.route('/ebook/edit/<int:ebook_id>', methods=['GET', 'POST'])
@admin_required
def ebook_edit(ebook_id):
    from models import get_ebook_by_id, update_ebook
    try:
        ebook = get_ebook_by_id(ebook_id)
        if not ebook:
            flash_error('Buku tidak ditemukan!')
            return redirect(url_for('ebook.ebook_index'))

        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            penulis = request.form.get('penulis', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'umum')
            tahun = request.form.get('tahun', '').strip()
            halaman = request.form.get('halaman', 0, type=int) or 0
            bahasa = request.form.get('bahasa', 'Indonesia').strip()

            file_path = ebook['file_path']
            pdf_file = request.files.get('file_path')
            if pdf_file and pdf_file.filename:
                new_path = save_pdf_file(pdf_file)
                if new_path:
                    file_path = new_path

            cover_url = ebook['cover_url'] or ''
            cover_file = request.files.get('cover_file')
            if cover_file and cover_file.filename:
                new_cover = save_cover_image(cover_file)
                if new_cover:
                    cover_url = new_cover
            if not cover_url:
                cover_url = request.form.get('cover_url', '').strip()

            if not judul:
                flash_error('Judul buku wajib diisi!')
                return redirect(request.url)
            if not file_path:
                flash_error('File PDF tidak ditemukan. Upload ulang atau isi URL.')
                return redirect(request.url)

            result = update_ebook(ebook_id, judul, file_path, penulis, deskripsi,
                                 kategori, cover_url, tahun, halaman, bahasa)
            if result:
                flash('Buku berhasil diperbarui!', 'success')
                return redirect(url_for('ebook.ebook_index'))
            else:
                flash_error('Gagal memperbarui buku. Periksa log untuk detail.')
                return redirect(request.url)

        return render_template('admin/edit_ebook.html', ebook=ebook)
    except Exception as e:
        logger.error(f"Error in ebook_edit {ebook_id}: {str(e)}", exc_info=True)
        flash_error('Terjadi kesalahan: ' + str(e)[:100])
        return redirect(url_for('ebook.ebook_index'))


@ebook_bp.route('/ebook/delete/<int:ebook_id>', methods=['POST'])
@admin_required
def ebook_delete(ebook_id):
    from models import delete_ebook
    try:
        result = delete_ebook(ebook_id)
        if result:
            flash('Buku berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus buku.')
    except Exception as e:
        logger.error(f"Error deleting ebook {ebook_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus buku')
    return redirect(url_for('ebook.ebook_index'))


@ebook_bp.route('/ebook/toggle/<int:ebook_id>', methods=['POST'])
@admin_required
def ebook_toggle(ebook_id):
    from models import toggle_ebook_aktif
    try:
        result = toggle_ebook_aktif(ebook_id)
        if result:
            flash('Status buku berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status buku.')
    except Exception as e:
        logger.error(f"Error toggling ebook {ebook_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('ebook.ebook_index'))
