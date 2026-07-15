"""
Admin Routes - Lokasi RT/RW Management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
from models import (
    get_all_lokasi_rtrw, get_lokasi_rtrw_by_id, add_lokasi_rtrw,
    update_lokasi_rtrw, delete_lokasi_rtrw, toggle_lokasi_rtrw_aktif
)

admin_rtrw_bp = Blueprint('admin_rtrw', __name__, url_prefix='/admin/rtrw')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('user_logged_in') or session.get('user_role') not in ['admin', 'dinas']:
            flash('Silakan login terlebih dahulu', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@admin_rtrw_bp.route('/')
@admin_required
def index():
    """List all RT/RW locations"""
    locations = get_all_lokasi_rtrw()
    return render_template('admin/lokasi_rtrw.html', locations=locations)

@admin_rtrw_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """Add new RT/RW location"""
    if request.method == 'POST':
        jenis = request.form.get('jenis', '').strip()
        rw = request.form.get('rw', '').strip()
        rt = request.form.get('rt', '').strip()
        nama_ketua = request.form.get('nama_ketua', '').strip()
        jabatan = request.form.get('jabatan', '').strip()
        wilayah = request.form.get('wilayah', '').strip()
        alamat = request.form.get('alamat', '').strip()
        no_hp = request.form.get('no_hp', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        latitude = float(lat) if lat else None
        longitude = float(lng) if lng else None
        
        if not jenis:
            flash('Jenis (RT/RW) wajib diisi', 'error')
            return redirect(url_for('admin_rtrw.add'))
        
        result = add_lokasi_rtrw(
            jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp,
            latitude, longitude
        )
        
        if result:
            flash('Lokasi RT/RW berhasil ditambahkan', 'success')
            return redirect(url_for('admin_rtrw.index'))
        else:
            flash('Gagal menambahkan lokasi', 'error')
    
    return render_template('admin/add_lokasi_rtrw.html')

@admin_rtrw_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    """Edit RT/RW location"""
    location = get_lokasi_rtrw_by_id(id)
    if not location:
        flash('Lokasi tidak ditemukan', 'error')
        return redirect(url_for('admin_rtrw.index'))
    
    if request.method == 'POST':
        jenis = request.form.get('jenis', '').strip()
        rw = request.form.get('rw', '').strip()
        rt = request.form.get('rt', '').strip()
        nama_ketua = request.form.get('nama_ketua', '').strip()
        jabatan = request.form.get('jabatan', '').strip()
        wilayah = request.form.get('wilayah', '').strip()
        alamat = request.form.get('alamat', '').strip()
        no_hp = request.form.get('no_hp', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        latitude = float(lat) if lat else None
        longitude = float(lng) if lng else None
        aktif = 1 if request.form.get('aktif') else 0
        
        if not jenis:
            flash('Jenis (RT/RW) wajib diisi', 'error')
            return redirect(url_for('admin_rtrw.edit', id=id))
        
        result = update_lokasi_rtrw(
            id, jenis, rw, rt, nama_ketua, jabatan, wilayah, alamat, no_hp,
            latitude, longitude, aktif
        )
        
        if result:
            flash('Lokasi RT/RW berhasil diupdate', 'success')
            return redirect(url_for('admin_rtrw.index'))
        else:
            flash('Gagal mengupdate lokasi', 'error')
    
    return render_template('admin/edit_lokasi_rtrw.html', location=location)

@admin_rtrw_bp.route('/delete/<int:id>')
@admin_required
def delete(id):
    """Delete RT/RW location"""
    result = delete_lokasi_rtrw(id)
    if result:
        flash('Lokasi RT/RW berhasil dihapus', 'success')
    else:
        flash('Gagal menghapus lokasi', 'error')
    return redirect(url_for('admin_rtrw.index'))

@admin_rtrw_bp.route('/toggle/<int:id>')
@admin_required
def toggle(id):
    """Toggle RT/RW location active status"""
    result = toggle_lokasi_rtrw_aktif(id)
    if result:
        flash('Status berhasil diubah', 'success')
    else:
        flash('Gagal mengubah status', 'error')
    return redirect(url_for('admin_rtrw.index'))

@admin_rtrw_bp.route('/api/geojson')
@admin_required
def api_geojson():
    """Get all locations as GeoJSON (for admin map preview)"""
    from models import get_lokasi_rtrw_geojson
    return jsonify(get_lokasi_rtrw_geojson())
