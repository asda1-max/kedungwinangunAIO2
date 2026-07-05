"""
Dinas Routes
Berisi route-route untuk panel petugas dinas

Error Handling:
    Menggunakan decorators dari errors.py:
    - dinas_required: Proteksi route dinas/admin
    - flash_error: Flash error messages
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
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
    get_all_warga_approved,
)
from errors import dinas_required, flash_error, NotFoundError, ValidationError
import logging

# Setup logging
logger = logging.getLogger(__name__)

dinas_bp = Blueprint('dinas', __name__, url_prefix='/dinas')


# ── Dashboard ──────────────────────────────────────────────────────────

@dinas_bp.route("/dashboard")
@dinas_required
def dashboard():
    """Dashboard dinas"""
    try:
        pending_users = get_pending_users()
        pending_permits = get_pending_permohonan_surat()
        all_warga = get_all_warga_approved()

        return render_template(
            "dinas/dashboard.html",
            recent_pending_users=pending_users[:5],  # Limit for display
            recent_permits=pending_permits[:5],
            pending_users_count=len(pending_users),
            pending_permits_count=len(pending_permits),
            approved_count=len(all_warga),
            total_warga=len(all_warga),
        )
    except Exception as e:
        logger.error(f"Error loading dinas dashboard: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat dashboard')
        return redirect(url_for('public.index'))


# ── User Management ────────────────────────────────────────────────────

@dinas_bp.route("/users/pending")
@dinas_required
def pending_users():
    """Halaman daftar user pending"""
    try:
        users = get_pending_users()
        return render_template("dinas/pending_users.html", users=users)
    except Exception as e:
        logger.error(f"Error loading pending users: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat daftar user')
        return redirect(url_for('dinas.dashboard'))


@dinas_bp.route("/users/all")
@dinas_required
def all_users():
    """Halaman semua warga"""
    try:
        users = get_all_warga()
        return render_template("dinas/all_users.html", users=users)
    except Exception as e:
        logger.error(f"Error loading all users: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat daftar warga')
        return redirect(url_for('dinas.dashboard'))


@dinas_bp.route("/users/approve/<int:user_id>", methods=['POST'])
@dinas_required
def approve_user_route(user_id):
    """Setujui pendaftaran user"""
    try:
        result = approve_user(user_id, session.get('user_id'))
        if result:
            flash('Pendaftaran berhasil disetujui!', 'success')
        else:
            flash_error('Gagal menyetujui pendaftaran. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error approving user {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menyetujui pendaftaran')
    return redirect(url_for('dinas.pending_users'))


@dinas_bp.route("/users/reject/<int:user_id>", methods=['POST'])
@dinas_required
def reject_user_route(user_id):
    """Tolak pendaftaran user"""
    try:
        catatan = request.form.get('catatan', '')
        result = reject_user(user_id, session.get('user_id'), catatan)
        if result:
            flash('Pendaftaran ditolak.', 'info')
        else:
            flash_error('Gagal menolak pendaftaran. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error rejecting user {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menolak pendaftaran')
    return redirect(url_for('dinas.pending_users'))


@dinas_bp.route("/users/detail/<int:user_id>")
@dinas_required
def user_detail(user_id):
    """Halaman detail user pending dengan preview dokumen"""
    try:
        user = get_user_by_id(user_id)

        if not user:
            flash_error('User tidak ditemukan!')
            return redirect(url_for('dinas.pending_users'))

        return render_template("dinas/user_detail.html", user=user)
    except Exception as e:
        logger.error(f"Error loading user detail {user_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat detail user')
        return redirect(url_for('dinas.pending_users'))


@dinas_bp.route("/surat/generate-pdf/<int:permit_id>")
@dinas_required
def generate_surat_pdf(permit_id):
    """Generate dan download PDF surat"""
    try:
        from models import get_permohonan_detail

        permit = get_permohonan_detail(permit_id)

        if not permit:
            flash_error('Permohonan tidak ditemukan!')
            return redirect(url_for('dinas.permohonan_list'))

        if permit['status'] != 'approved':
            flash_error('Surat hanya bisa di-generate untuk permohonan yang sudah disetujui!')
            return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))

        if not permit.get('nomor_surat'):
            flash_error('Nomor surat belum diisi. Setujui permohonan terlebih dahulu!')
            return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))

        # Parse data
        try:
            data = json.loads(permit['data_json']) if permit['data_json'] else {}
        except json.JSONDecodeError:
            data = {}

        # Add user info to data
        data['nama'] = permit['nama_lengkap']
        data['nik'] = permit['nik']
        data['alamat'] = permit['alamat']

        # Generate PDF
        from pdf_generator import generate_surat_pdf as make_pdf

        tanggal_surat = permit['approved_at'] or permit['created_at']
        pdf_buffer = make_pdf(
            kode_surat=permit['jenis_kode'],
            data=data,
            nomor_surat=permit['nomor_surat'],
            tanggal_surat=tanggal_surat,
        )

        # Create filename
        filename = f"{permit['jenis_kode']}_{permit['nik']}_{permit_id}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        logger.error(f"Error generating PDF for permit {permit_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat generate PDF. Silakan coba lagi.')
        return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))


# ── Permohonan Surat Management ───────────────────────────────────────

@dinas_bp.route("/permohonan")
@dinas_required
def permohonan_list():
    """Halaman daftar permohonan surat"""
    try:
        permits = get_all_permohonan_surat()
        return render_template("dinas/permohonan_list.html", permits=permits)
    except Exception as e:
        logger.error(f"Error loading permohonan list: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat daftar permohonan')
        return redirect(url_for('dinas.dashboard'))


@dinas_bp.route("/permohonan/detail/<int:permit_id>")
@dinas_required
def permohonan_detail(permit_id):
    """Halaman detail permohonan surat"""
    try:
        permit = get_permohonan_detail(permit_id)

        if not permit:
            flash_error('Permohonan tidak ditemukan!')
            return redirect(url_for('dinas.permohonan_list'))

        # Parse JSON data
        try:
            permit['data_json_parsed'] = json.loads(permit['data_json']) if permit['data_json'] else {}
        except json.JSONDecodeError:
            permit['data_json_parsed'] = {}

        return render_template("dinas/permohonan_detail.html", permit=permit)
    except Exception as e:
        logger.error(f"Error loading permohonan detail {permit_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat detail permohonan')
        return redirect(url_for('dinas.permohonan_list'))


@dinas_bp.route("/permohonan/approve/<int:permit_id>", methods=['POST'])
@dinas_required
def approve_permit_route(permit_id):
    """Setujui permohonan surat"""
    try:
        nomor_surat = request.form.get('nomor_surat', '').strip()
        catatan = request.form.get('catatan', '')

        if not nomor_surat:
            flash_error('Nomor surat harus diisi!')
            return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))

        result = approve_permohonan_surat(permit_id, session.get('user_id'), nomor_surat, catatan)

        if result:
            flash('Permohonan surat disetujui!', 'success')
        else:
            flash_error('Gagal menyetujui permohonan. Silakan coba lagi.')

        return redirect(url_for('dinas.permohonan_list'))
    except Exception as e:
        logger.error(f"Error approving permit {permit_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menyetujui permohonan')
        return redirect(url_for('dinas.permohonan_detail', permit_id=permit_id))


@dinas_bp.route("/permohonan/reject/<int:permit_id>", methods=['POST'])
@dinas_required
def reject_permit_route(permit_id):
    """Tolak permohonan surat"""
    try:
        catatan = request.form.get('catatan', '')
        result = reject_permohonan_surat(permit_id, session.get('user_id'), catatan)

        if result:
            flash('Permohonan surat ditolak.', 'info')
        else:
            flash_error('Gagal menolak permohonan. Silakan coba lagi.')

        return redirect(url_for('dinas.permohonan_list'))
    except Exception as e:
        logger.error(f"Error rejecting permit {permit_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menolak permohonan')
        return redirect(url_for('dinas.permohonan_list'))
