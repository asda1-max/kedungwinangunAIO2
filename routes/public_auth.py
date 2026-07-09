"""
Auth Routes - Login/Logout public pages
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import check_password_hash
from models import get_user_by_username, get_user_by_nip, get_desa_info, get_all_pages
from config import MAPS_EMBED_URL, DUSUN_DATA, NAV_LINKS
import logging

logger = logging.getLogger(__name__)
public_bp = Blueprint('public', __name__)


def get_desa_info_with_maps():
    """Get desa info with maps URL"""
    info = get_desa_info()
    info['maps_embed_url'] = MAPS_EMBED_URL
    info['dusun'] = DUSUN_DATA
    return info


# ── Unified Login Route ──────────────────────────────────────────────────

@public_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Unified login page for Admin, Dinas, and Warga"""
    from datetime import datetime

    # Redirect if already logged in
    if session.get('user_logged_in'):
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'dinas':
            return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'admin')

        if login_type == 'admin':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Username dan password wajib diisi!', 'error')
                return redirect(request.url)

            user = get_user_by_username(username)
            if user and user['role'] == 'admin' and check_password_hash(user['password_hash'], password):
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user.get('nik', '')
                session['user_role'] = user['role']
                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Username atau password salah!', 'error')

        elif login_type == 'dinas':
            nip = request.form.get('nip', '').strip()
            password = request.form.get('password', '')

            if not nip or not password:
                flash('NIP dan password wajib diisi!', 'error')
                return redirect(request.url)

            user = get_user_by_nip(nip)
            if user and user['role'] == 'dinas' and check_password_hash(user['password_hash'], password):
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user.get('nik', '')
                session['user_role'] = user['role']
                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('NIP atau password salah!', 'error')

    # Render login page
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        return render_template(
            "login.html",
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman. Silakan coba lagi.', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/logout")
def logout():
    """Logout route - clears session"""
    session.clear()
    flash('Anda telah keluar dari sistem.', 'info')
    return redirect(url_for('public.index'))
