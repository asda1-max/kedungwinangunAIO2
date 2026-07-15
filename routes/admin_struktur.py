"""
Admin Struktur Organisasi Routes
Part of admin.py refactoring
"""

import logging
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, Response, current_app
from functools import wraps
import csv
import io
from config import compress_and_save_image

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


# ── Struktur Organisasi Management ──────────────────────────────────────

@admin_bp.route("/struktur")
@admin_required
def struktur():
    """Halaman manajemen struktur organisasi"""
    from models import get_all_struktur

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
    from models import add_struktur

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
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'struktur')
                os.makedirs(upload_dir, exist_ok=True)
                foto_file.seek(0)
                file_bytes = foto_file.read()
                try:
                    filename, _ = compress_and_save_image(file_bytes, upload_dir, 'struktur_')
                except Exception:
                    ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                    filename = f"struktur_{uuid.uuid4().hex}.{ext}"
                    with open(os.path.join(upload_dir, filename), 'wb') as f:
                        f.write(file_bytes)
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
    from models import get_struktur_by_id, update_struktur
    from flask import current_app

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
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'struktur')
                os.makedirs(upload_dir, exist_ok=True)
                foto_file.seek(0)
                file_bytes = foto_file.read()
                try:
                    filename, _ = compress_and_save_image(file_bytes, upload_dir, 'struktur_')
                except Exception:
                    ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                    filename = f"struktur_{uuid.uuid4().hex}.{ext}"
                    with open(os.path.join(upload_dir, filename), 'wb') as f:
                        f.write(file_bytes)
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
    from models import delete_struktur

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
    from models import toggle_struktur_aktif

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
    from models import batch_import_struktur

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
    from models import get_all_struktur

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
