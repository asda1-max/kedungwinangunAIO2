"""
Admin Account Center & Settings Routes
Part of admin.py refactoring
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

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
# ── ACCOUNT CENTER ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/accounts")
@admin_required
def account_center():
    """Halaman Account Center - Kelola semua akun"""
    from models import get_all_users, get_user_stats

    try:
        # Filter by role if specified
        role_filter = request.args.get('role', 'all')
        status_filter = request.args.get('status', 'all')
        search = request.args.get('search', '').strip()

        users = get_all_users()
        stats = get_user_stats()

        # Apply filters
        if role_filter != 'all':
            users = [u for u in users if u['role'] == role_filter]
        if status_filter != 'all':
            users = [u for u in users if u['status'] == status_filter]
        if search:
            search = search.lower()
            users = [u for u in users if
                     search in u.get('nama_lengkap', '').lower() or
                     search in u.get('nik', '').lower() or
                     search in u.get('email', '').lower()]

        return render_template(
            "admin/account_center.html",
            users=users,
            stats=stats,
            role_filter=role_filter,
            status_filter=status_filter,
            search=search
        )
    except Exception as e:
        logger.error(f"Error in account_center: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat Account Center')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/accounts/user/<int:user_id>", methods=['GET', 'POST'])
@admin_required
def account_detail(user_id):
    """Detail & Edit user"""
    from models import get_user_by_id, update_user_data, update_user_password, update_user_role

    try:
        user = get_user_by_id(user_id)
        if not user:
            flash_error('User tidak ditemukan!')
            return redirect(url_for('admin.account_center'))

        if request.method == 'POST':
            action = request.form.get('action', '')

            if action == 'update_data':
                # Update user data
                data = {
                    'nama_lengkap': request.form.get('nama_lengkap', '').strip(),
                    'email': request.form.get('email', '').strip(),
                    'no_telepon': request.form.get('no_telepon', '').strip(),
                    'alamat': request.form.get('alamat', '').strip(),
                }
                if update_user_data(user_id, data):
                    flash('Data user berhasil diperbarui!', 'success')
                else:
                    flash_error('Gagal memperbarui data user.')

            elif action == 'update_password':
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                if new_password != confirm_password:
                    flash_error('Password baru tidak cocok!')
                    return redirect(url_for('admin.account_detail', user_id=user_id))
                if len(new_password) < 6:
                    flash_error('Password minimal 6 karakter!')
                    return redirect(url_for('admin.account_detail', user_id=user_id))
                if update_user_password(user_id, new_password):
                    flash('Password berhasil diperbarui!', 'success')
                else:
                    flash_error('Gagal memperbarui password.')

            elif action == 'change_role':
                new_role = request.form.get('new_role', '')
                if new_role in ['admin', 'dinas', 'penduduk']:
                    if update_user_role(user_id, new_role, session.get('user_id')):
                        flash(f'Role berhasil diubah ke {new_role}!', 'success')
                    else:
                        flash_error('Gagal mengubah role.')

            return redirect(url_for('admin.account_detail', user_id=user_id))

        return render_template("admin/account_detail.html", user=user)
    except Exception as e:
        logger.error(f"Error in account_detail {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat data user')
        return redirect(url_for('admin.account_center'))


@admin_bp.route("/accounts/user/delete/<int:user_id>", methods=['POST'])
@admin_required
def account_delete(user_id):
    """Hapus user"""
    from models import delete_user_account

    try:
        # Prevent self-deletion
        if user_id == session.get('user_id'):
            flash_error('Tidak dapat menghapus akun sendiri!')
            return redirect(url_for('admin.account_center'))

        if delete_user_account(user_id):
            flash('User berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus user.')
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus user')
    return redirect(url_for('admin.account_center'))


@admin_bp.route("/accounts/create", methods=['GET', 'POST'])
@admin_required
def account_create():
    """Buat akun admin/dinas baru"""
    from models import create_staff_account

    try:
        if request.method == 'POST':
            login_id = request.form.get('login_id', '').strip()
            nama_lengkap = request.form.get('nama_lengkap', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            role = request.form.get('role', '')

            # Validation
            if not login_id or not nama_lengkap or not password or not role:
                flash_error('Semua field harus diisi!')
                return redirect(url_for('admin.account_create'))

            if password != confirm_password:
                flash_error('Password tidak cocok!')
                return redirect(url_for('admin.account_create'))

            if len(password) < 6:
                flash_error('Password minimal 6 karakter!')
                return redirect(url_for('admin.account_create'))

            if role not in ['admin', 'dinas']:
                flash_error('Role tidak valid!')
                return redirect(url_for('admin.account_create'))

            success, result = create_staff_account(login_id, nama_lengkap, password, role)
            if success:
                flash(f'Akun {role} berhasil dibuat!', 'success')
                return redirect(url_for('admin.account_center'))
            else:
                flash_error(result)
                return redirect(url_for('admin.account_create'))

        return render_template("admin/account_create.html")
    except Exception as e:
        logger.error(f"Error in account_create: {str(e)}")
        flash_error('Terjadi kesalahan saat membuat akun')
        return redirect(url_for('admin.account_center'))


# ── Settings ────────────────────────────────────────────────────────────

@admin_bp.route("/settings", methods=['GET', 'POST'])
@admin_required
def settings():
    """Halaman pengaturan akun admin"""
    from models import get_user_by_id, get_db_connection

    try:
        user = get_user_by_id(session.get('user_id'))

        if request.method == 'POST':
            new_username = request.form.get('new_username', '').strip()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            # Verify current password
            if not check_password_hash(user['password_hash'], current_password):
                flash_error('Password saat ini salah!')
                return redirect(url_for('admin.settings'))

            # Prepare update
            updates = {}
            if new_username and new_username != user['nik']:
                updates['nik'] = new_username

            if new_password:
                if new_password != confirm_password:
                    flash_error('Password baru tidak cocok!')
                    return redirect(url_for('admin.settings'))
                if len(new_password) < 6:
                    flash_error('Password minimal 6 karakter!')
                    return redirect(url_for('admin.settings'))
                updates['password_hash'] = generate_password_hash(new_password)

            # Execute updates
            if updates:
                conn = get_db_connection()
                cursor = conn.cursor()
                set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
                cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', (*updates.values(), user['id']))
                conn.commit()
                conn.close()

                # Update session
                if 'nik' in updates:
                    session['user_nik'] = updates['nik']
                flash('Pengaturan berhasil disimpan!', 'success')
            else:
                flash('Tidak ada perubahan.', 'info')

            return redirect(url_for('admin.settings'))

        return render_template("admin/settings.html", user=user)
    except Exception as e:
        logger.error(f"Error in settings page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat pengaturan')
        return redirect(url_for('admin.dashboard'))
