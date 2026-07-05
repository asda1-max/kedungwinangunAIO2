"""
User Routes (Warga/Penduduk)
Berisi route-route untuk panel warga

Error Handling:
    Menggunakan decorators dari errors.py:
    - login_required: Proteksi route warga
    - warga_required: Proteksi route khusus warga
    - flash_error: Flash error messages
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.utils import secure_filename
import os
import uuid
import json

from models import (
    get_user_by_id,
    get_all_jenis_surat,
    get_permohonan_surat_by_user,
    register_user,
    verify_user,
)
from errors import flash_error, ValidationError
import logging

# Setup logging
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)

# Upload config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Decorators ─────────────────────────────────────────────────────────

def login_required(f):
    """Decorator untuk proteksi route warga/dinas"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash_error('Silakan login terlebih dahulu.')
            return redirect(url_for('public.login') + '#warga')

        role = session.get('user_role')
        if role not in ['warga', 'dinas', 'penduduk']:
            flash_error('Anda tidak memiliki akses ke halaman ini.')
            return redirect(url_for('public.index'))

        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ─────────────────────────────────────────────────────────

@user_bp.route("/register", methods=['GET', 'POST'])
def register():
    """Halaman registrasi warga"""
    if session.get('user_logged_in'):
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        nik = request.form.get('nik', '').strip()
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        email = request.form.get('email', '').strip()
        no_telepon = request.form.get('no_telepon', '').strip()
        alamat = request.form.get('alamat', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not nik:
            flash_error('NIK wajib diisi!')
            return redirect(request.url)

        if not nama_lengkap:
            flash_error('Nama lengkap wajib diisi!')
            return redirect(request.url)

        if len(nik) != 16:
            flash_error('NIK harus 16 digit!')
            return redirect(request.url)

        if not nik.isdigit():
            flash_error('NIK harus berupa angka!')
            return redirect(request.url)

        if len(password) < 6:
            flash_error('Password minimal 6 karakter!')
            return redirect(request.url)

        if password != confirm_password:
            flash_error('Password tidak cocok!')
            return redirect(request.url)

        # Handle file upload
        ktp_path = None
        kk_path = None

        try:
            if 'ktp_file' in request.files:
                ktp_file = request.files['ktp_file']
                if ktp_file and ktp_file.filename and allowed_file(ktp_file.filename):
                    ext = ktp_file.filename.rsplit('.', 1)[1].lower()
                    filename = f"ktp_{nik}_{uuid.uuid4().hex[:8]}.{ext}"
                    ktp_file.save(os.path.join(UPLOAD_FOLDER, filename))
                    ktp_path = filename

            if 'kk_file' in request.files:
                kk_file = request.files['kk_file']
                if kk_file and kk_file.filename and allowed_file(kk_file.filename):
                    ext = kk_file.filename.rsplit('.', 1)[1].lower()
                    filename = f"kk_{nik}_{uuid.uuid4().hex[:8]}.{ext}"
                    kk_file.save(os.path.join(UPLOAD_FOLDER, filename))
                    kk_path = filename

            success, message = register_user(nik, nama_lengkap, email, no_telepon, alamat, password, ktp_path, kk_path)

            if success:
                flash(message, 'success')
                return redirect(url_for('public.login') + '#warga')
            else:
                flash_error(message)
                return redirect(request.url)

        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            flash_error('Terjadi kesalahan saat registrasi. Silakan coba lagi.')
            return redirect(request.url)

    return render_template("user/register.html")


@user_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Redirect to unified login"""
    return redirect(url_for('public.login') + '#warga')


@user_bp.route("/logout")
def logout():
    """Logout"""
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('public.index'))


# ── Dashboard Routes ────────────────────────────────────────────────────

@user_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard warga"""
    try:
        user = get_user_by_id(session.get('user_id'))

        if not user:
            flash_error('User tidak ditemukan. Silakan login ulang.')
            session.clear()
            return redirect(url_for('public.login'))

        permohonan_list = get_permohonan_surat_by_user(session.get('user_id'))
        return render_template("user/dashboard.html", user=user, permohonan_list=permohonan_list)

    except Exception as e:
        logger.error(f"Error loading user dashboard: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat dashboard')
        return redirect(url_for('public.index'))


# ── Surat Routes ───────────────────────────────────────────────────────

@user_bp.route("/surat/permohonan", methods=['GET', 'POST'])
@login_required
def permohonan_surat():
    """Form permohonan surat"""
    try:
        jenis_surat = get_all_jenis_surat()

        if request.method == 'POST':
            from models import create_permohonan_surat

            jenis_id = request.form.get('jenis_surat_id', '')

            if not jenis_id:
                flash_error('Pilih jenis surat terlebih dahulu!')
                return redirect(request.url)

            data = {}
            for key, value in request.form.items():
                if key not in ['jenis_surat_id']:
                    data[key] = value

            result = create_permohonan_surat(session.get('user_id'), jenis_id, json.dumps(data))

            if result:
                flash('Permohonan surat berhasil diajukan! Mohon tunggu persetujuan.', 'success')
            else:
                flash_error('Terjadi kesalahan saat mengajukan permohonan. Silakan coba lagi.')

            return redirect(url_for('user.dashboard'))

        return render_template("user/surat_permohonan.html", jenis_surat=jenis_surat)

    except Exception as e:
        logger.error(f"Error in permohonan_surat: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman permohonan surat')
        return redirect(url_for('user.dashboard'))
