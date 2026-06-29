"""
User Routes (Warga/Penduduk)
Berisi route-route untuk panel warga
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

user_bp = Blueprint('user', __name__)

# Upload config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Decorators ─────────────────────────────────────────────────────────

def login_required(f):
    """Decorator untuk proteksi route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('user.login'))
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
        if len(nik) != 16:
            flash('NIK harus 16 digit!', 'error')
            return redirect(url_for('user.register'))

        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'error')
            return redirect(url_for('user.register'))

        if password != confirm_password:
            flash('Password tidak cocok!', 'error')
            return redirect(url_for('user.register'))

        # Handle file upload
        ktp_path = None
        kk_path = None

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
            return redirect(url_for('user.login'))
        else:
            flash(message, 'error')

    return render_template("user/register.html")


@user_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Halaman login warga/dinas"""
    if session.get('user_logged_in'):
        if session.get('user_role') in ['admin', 'dinas']:
            return redirect(url_for('dinas.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        nik = request.form.get('nik', '').strip()
        password = request.form.get('password', '')

        user = verify_user(nik, password)

        if user:
            session['user_logged_in'] = True
            session['user_id'] = user['id']
            session['user_nama'] = user['nama_lengkap']
            session['user_role'] = user['role']
            session['user_nik'] = user['nik']

            if user['role'] in ['admin', 'dinas']:
                return redirect(url_for('dinas.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            existing = get_user_by_id(nik)
            if existing and existing['status'] == 'pending':
                flash('Akun Anda belum disetujui. Mohon tunggu konfirmasi.', 'warning')
            else:
                flash('NIK atau password salah!', 'error')

    return render_template("user/login.html")


@user_bp.route("/logout")
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('public.index'))


# ── Dashboard Routes ────────────────────────────────────────────────────

@user_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard warga"""
    user = get_user_by_id(session.get('user_id'))
    permohonan_list = get_permohonan_surat_by_user(session.get('user_id'))
    return render_template("user/dashboard.html", user=user, permohonan_list=permohonan_list)


# ── Surat Routes ───────────────────────────────────────────────────────

@user_bp.route("/surat/permohonan", methods=['GET', 'POST'])
@login_required
def permohonan_surat():
    """Form permohonan surat"""
    jenis_surat = get_all_jenis_surat()

    if request.method == 'POST':
        from models import create_permohonan_surat

        jenis_id = request.form.get('jenis_surat_id', '')
        data = {}
        for key, value in request.form.items():
            if key not in ['jenis_surat_id']:
                data[key] = value

        create_permohonan_surat(session.get('user_id'), jenis_id, json.dumps(data))
        flash('Permohonan surat berhasil diajukan! Mohon tunggu persetujuan.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template("user/surat_permohonan.html", jenis_surat=jenis_surat)
