"""
Admin UMKM Routes
Part of admin.py refactoring
"""

import logging
import os
import uuid
import re
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, current_app
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


# ── UMKM Management ─────────────────────────────────────────────────────

@admin_bp.route("/umkm")
@admin_required
def umkm():
    """Halaman manajemen UMKM"""
    from models import get_all_umkm

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
            result['nama'] = urllib.parse.unquote(place_match.group(1).replace('+', ' ')) if 'urllib' in dir() else place_match.group(1).replace('+', ' ')
        
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
    from models import add_umkm

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
            foto_file = request.files.get('foto_file')
            if foto_file and foto_file.filename:
                upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'umkm')
                os.makedirs(upload_dir, exist_ok=True)
                foto_file.seek(0)
                file_bytes = foto_file.read()
                try:
                    filename, _ = compress_and_save_image(file_bytes, upload_dir)
                except Exception:
                    ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                    filename = f"{uuid.uuid4().hex}.{ext}"
                    with open(os.path.join(upload_dir, filename), 'wb') as f:
                        f.write(file_bytes)
                foto_url = f'/uploads/umkm/{filename}'
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
    from models import get_umkm_by_id, update_umkm

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
            foto_file = request.files.get('foto_file')
            if foto_file and foto_file.filename:
                upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'umkm')
                os.makedirs(upload_dir, exist_ok=True)
                foto_file.seek(0)
                file_bytes = foto_file.read()
                try:
                    filename, _ = compress_and_save_image(file_bytes, upload_dir)
                except Exception:
                    ext = foto_file.filename.rsplit('.', 1)[1].lower() if '.' in foto_file.filename else 'jpg'
                    filename = f"{uuid.uuid4().hex}.{ext}"
                    with open(os.path.join(upload_dir, filename), 'wb') as f:
                        f.write(file_bytes)
                foto_url = f'/uploads/umkm/{filename}'
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
    from models import delete_umkm

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
    from models import toggle_umkm_aktif

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
