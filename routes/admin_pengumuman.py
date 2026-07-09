"""
Admin Pengumuman & APBDes Routes
Part of admin.py refactoring
"""

import logging
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


# ════════════════════════════════════════════════════════════════════════
# ── PENGUMUMAN MANAGEMENT ──────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/pengumuman")
@admin_required
def pengumuman():
    """Halaman manajemen pengumuman"""
    from models import get_all_pengumuman

    try:
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
    from models import add_pengumuman

    try:
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
    from models import get_pengumuman_by_id, update_pengumuman

    try:
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
    from models import delete_pengumuman

    try:
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
    from models import toggle_pengumuman_aktif

    try:
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
    from models import get_apbdes_by_tahun, get_apbdes_summary, get_available_tahun
    from datetime import datetime

    try:
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
    from models import add_apbdes_item
    from datetime import datetime

    try:
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
    from models import get_apbdes_by_id, update_apbdes_item

    try:
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
    from models import delete_apbdes_item

    try:
        result = delete_apbdes_item(apbdes_id)
        if result:
            flash('Item berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus item. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting apbdes {apbdes_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus item')
    return redirect(url_for('admin.apbdes'))
