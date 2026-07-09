"""
Admin Potensi & Kependudukan Routes
Part of admin.py refactoring
"""

import logging
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps

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
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder=''):
    from config import Config
    if file and file.filename and allowed_image(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder) if subfolder else Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        if subfolder:
            return f"/uploads/{subfolder}/{filename}"
        return f"/uploads/{filename}"
    return None


# ════════════════════════════════════════════════════════════════════════
# ── KEPENDUDUKAN MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/kependudukan", methods=['GET', 'POST'])
@admin_required
def kependudukan():
    """Halaman manage kependudukan dengan charts"""
    from models import get_all_kependudukan, update_kependudukan

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
# ── POTENSI DESA MANAGEMENT ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/potensi")
@admin_required
def potensi():
    """Halaman manajemen potensi desa"""
    from models import get_all_potensi

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
    from models import add_potensi

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
    from models import get_potensi_by_id, update_potensi

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
    from models import delete_potensi

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
    from models import toggle_potensi_aktif

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
