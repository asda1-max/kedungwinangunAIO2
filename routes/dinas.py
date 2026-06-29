"""
Dinas Routes
Berisi route-route untuk panel petugas dinas
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import json

from models import (
    get_user_by_id,
    get_pending_users,
    get_all_warga,
    approve_user,
    reject_user,
    get_all_permohonan_surat,
    get_pending_permohonan_surat,
    get_permohonan_detail,
    approve_permohonan_surat,
    reject_permohonan_surat,
)

dinas_bp = Blueprint('dinas', __name__, url_prefix='/dinas')


# ── Decorators ─────────────────────────────────────────────────────────

def dinas_required(f):
    """Decorator untuk proteksi route (hanya dinas & admin)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('user.login'))
        user = get_user_by_id(session.get('user_id'))
        if not user or user['role'] not in ['admin', 'dinas']:
            flash('Anda tidak memiliki akses ke halaman ini!', 'error')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────────────────

@dinas_bp.route("/dashboard")
@dinas_required
def dashboard():
    """Dashboard dinas"""
    pending_users = get_pending_users()
    pending_permits = get_pending_permohonan_surat()
    all_permits = get_all_permohonan_surat()

    stats = {
        'pending_users': len(pending_users),
        'pending_permits': len(pending_permits),
        'total_permits': len(all_permits),
        'approved_permits': len([p for p in all_permits if p['status'] == 'approved']),
        'rejected_permits': len([p for p in all_permits if p['status'] == 'rejected']),
    }

    return render_template(
        "dinas/dashboard.html",
        pending_users=pending_users[:5],  # Limit for display
        pending_permits=pending_permits[:5],
        stats=stats
    )


# ── User Management ────────────────────────────────────────────────────

@dinas_bp.route("/users/pending")
@dinas_required
def pending_users():
    """Halaman daftar user pending"""
    users = get_pending_users()
    return render_template("dinas/pending_users.html", users=users)


@dinas_bp.route("/users/all")
@dinas_required
def all_users():
    """Halaman semua warga"""
    users = get_all_warga()
    return render_template("dinas/all_users.html", users=users)


@dinas_bp.route("/users/approve/<int:user_id>", methods=['POST'])
@dinas_required
def approve_user_route(user_id):
    """Setujui pendaftaran user"""
    approve_user(user_id, session.get('user_id'))
    flash('Pendaftaran berhasil disetujui!', 'success')
    return redirect(url_for('dinas.pending_users'))


@dinas_bp.route("/users/reject/<int:user_id>", methods=['POST'])
@dinas_required
def reject_user_route(user_id):
    """Tolak pendaftaran user"""
    catatan = request.form.get('catatan', '')
    reject_user(user_id, session.get('user_id'), catatan)
    flash('Pendaftaran ditolak.', 'info')
    return redirect(url_for('dinas.pending_users'))


# ── Permohonan Surat Management ───────────────────────────────────────

@dinas_bp.route("/permohonan")
@dinas_required
def permohonan_list():
    """Halaman daftar permohonan surat"""
    permits = get_all_permohonan_surat()
    return render_template("dinas/permohonan_list.html", permits=permits)


@dinas_bp.route("/permohonan/detail/<int:permit_id>")
@dinas_required
def permohonan_detail(permit_id):
    """Halaman detail permohonan surat"""
    permit = get_permohonan_detail(permit_id)

    if not permit:
        flash('Permohonan tidak ditemukan!', 'error')
        return redirect(url_for('dinas.permohonan_list'))

    # Parse JSON data
    permit['data_json_parsed'] = json.loads(permit['data_json']) if permit['data_json'] else {}

    return render_template("dinas/permohonan_detail.html", permit=permit)


@dinas_bp.route("/permohonan/approve/<int:permit_id>", methods=['POST'])
@dinas_required
def approve_permit_route(permit_id):
    """Setujui permohonan surat"""
    nomor_surat = request.form.get('nomor_surat', '')
    catatan = request.form.get('catatan', '')

    if not nomor_surat:
        flash('Nomor surat harus diisi!', 'error')
        return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))

    approve_permohonan_surat(permit_id, session.get('user_id'), nomor_surat, catatan)
    flash('Permohonan surat disetujui!', 'success')
    return redirect(url_for('dinas.permohonan_list'))


@dinas_bp.route("/permohonan/reject/<int:permit_id>", methods=['POST'])
@dinas_required
def reject_permit_route(permit_id):
    """Tolak permohonan surat"""
    catatan = request.form.get('catatan', '')
    reject_permohonan_surat(permit_id, session.get('user_id'), catatan)
    flash('Permohonan surat ditolak.', 'info')
    return redirect(url_for('dinas.permohonan_list'))
