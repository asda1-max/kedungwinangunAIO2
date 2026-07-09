"""
Admin Auth & Dashboard Routes
Part of admin.py refactoring
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, session, flash

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Auth Routes ─────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Redirect to unified login"""
    return redirect(url_for('public.login'))


@admin_bp.route("/logout")
def logout():
    """Logout admin"""
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('public.index'))


# ── Dashboard ──────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
def dashboard():
    """Dashboard admin"""
    from models import get_all_berita
    from errors import admin_required, flash_error

    # Check if user is logged in
    if not session.get('user_logged_in'):
        flash('Silakan login terlebih dahulu', 'warning')
        return redirect(url_for('public.login'))

    try:
        berita_list = get_all_berita()
        return render_template(
            "admin/dashboard.html",
            berita_list=berita_list,
            total_berita=len(berita_list),
            berita_unggulan=len([b for b in berita_list if b.get('unggulan') == 1])
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Terjadi kesalahan saat memuat dashboard', 'error')
        return redirect(url_for('public.index'))
