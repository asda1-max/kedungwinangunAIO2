"""
Pages Routes - Galeri, Kontak, Kritik Saran, Custom Pages
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime
from models import get_desa_info, get_config, get_all_galeri, get_all_pages, get_page_by_slug, add_kritik_saran
from config import NAV_LINKS, MAPS_EMBED_URL, DUSUN_DATA, LAINNYA_PAGES
import logging

logger = logging.getLogger(__name__)
public_bp = Blueprint('public', __name__)


def get_desa_info_with_maps():
    info = get_desa_info()
    info['maps_embed_url'] = MAPS_EMBED_URL
    info['dusun'] = DUSUN_DATA
    return info


def set_nav_active(page_key, request_path=None):
    """
    Set active nav link based on page key.
    If page_key is 'Lainnya', checks if request_path is in LAINNYA_PAGES.
    Uses prefix matching so /struktur/123 matches /struktur.
    """
    from config import LAINNYA_PAGES
    
    def matches_lainnya(path):
        """Check if path matches any LAINNYA_PAGES entry (prefix matching)"""
        if not path:
            return False
        for lp in LAINNYA_PAGES:
            # Skip Flask route syntax patterns
            if '<' in lp:
                continue
            if path == lp or path.startswith(lp + '/'):
                return True
        return False
    
    result = []
    for n in NAV_LINKS:
        if n["label"] == "Lainnya":
            result.append({
                "label": n["label"],
                "href": n["href"],
                "active": page_key == "Lainnya" and matches_lainnya(request_path),
                "is_dropdown": True
            })
        else:
            result.append({
                "label": n["label"],
                "href": n["href"],
                "active": n["label"] == page_key,
                "is_dropdown": False
            })
    return result


# ── Galeri ────────────────────────────────────────────────────────────────

@public_bp.route("/galeri")
def galeri():
    """Halaman galeri foto desa"""
    try:
        desa_info = get_desa_info_with_maps()
        foto_list = get_all_galeri(aktif=1)
        custom_pages = get_all_pages()

        return render_template(
            "galeri.html",
            desa=desa_info,
            nav_links=set_nav_active("Galeri"),
            foto_list=foto_list,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading galeri page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman galeri', 'error')
        return redirect(url_for('public.index'))


# ── Kontak ──────────────────────────────────────────────────────────────

@public_bp.route("/kontak")
def kontak():
    """Halaman informasi kontak desa"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        kontak_data = {
            'whatsapp': get_config("kontak_whatsapp", ""),
            'telepon': get_config("kontak_telepon", ""),
            'email': get_config("kontak_email", ""),
            'alamat': get_config("alamat_desa", ""),
            'facebook': get_config("sosial_facebook", ""),
            'instagram': get_config("sosial_instagram", ""),
            'twitter': get_config("sosial_twitter", ""),
        }

        return render_template(
            "kontak.html",
            desa=desa_info,
            nav_links=set_nav_active("Kontak"),
            kontak=kontak_data,
            tahun=datetime.now().year,
            config=kontak_data,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading kontak page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman kontak', 'error')
        return redirect(url_for('public.index'))


# ── Kritik Saran ────────────────────────────────────────────────────────

@public_bp.route("/kritik-saran", methods=['GET', 'POST'])
def kritik_saran():
    """Halaman dan form kritik/saran"""
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        email = request.form.get('email', '').strip()
        telepon = request.form.get('telepon', '').strip()
        subjek = request.form.get('subjek', '').strip()
        kategori = request.form.get('kategori', 'kritik')
        isi = request.form.get('isi', '').strip()

        if not nama or not subjek or not isi:
            flash('Nama, subjek, dan isi kritik/saran wajib diisi!', 'error')
            return redirect(url_for('public.kritik_saran'))

        if add_kritik_saran(nama, subjek, isi, email, telepon, kategori):
            flash('Terima kasih! Kritik dan saran Anda telah dikirim.', 'success')
        else:
            flash('Gagal mengirim kritik/saran. Silakan coba lagi.', 'error')

        return redirect(url_for('public.kritik_saran'))

    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        return render_template(
            "kritik_saran.html",
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading kritik_saran page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/api/kritik-saran", methods=['POST'])
def api_kritik_saran():
    """API endpoint untuk submit kritik/saran (JSON)"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Data tidak valid'}), 400

    nama = data.get('nama', '').strip()
    subjek = data.get('subjek', '').strip()
    isi = data.get('isi', '').strip()

    if not nama or not subjek or not isi:
        return jsonify({'success': False, 'error': 'Nama, subjek, dan isi wajib diisi'}), 400

    success = add_kritik_saran(
        nama=nama,
        subjek=subjek,
        isi=isi,
        email=data.get('email', '').strip() or None,
        telepon=data.get('telepon', '').strip() or None,
        kategori=data.get('kategori', 'kritik')
    )

    if success:
        return jsonify({'success': True, 'message': 'Kritik dan saran telah dikirim'})
    return jsonify({'success': False, 'error': 'Gagal mengirim'}), 500


# ── Custom Page ─────────────────────────────────────────────────────────

@public_bp.route("/page/<slug>")
def view_page(slug):
    """Halaman custom page"""
    try:
        from datetime import datetime
        desa_info = get_desa_info_with_maps()
        page = get_page_by_slug(slug)

        if not page:
            flash('Halaman tidak ditemukan', 'error')
            return redirect(url_for('public.index'))

        # Update nav_links with custom pages
        custom_pages = get_all_pages()
        nav_links_with_pages = NAV_LINKS.copy()
        if custom_pages:
            nav_links_with_pages.append({
                "label": "Lainnya",
                "href": "#",
                "active": False,
                "is_dropdown": True,
                "children": [{"label": p['title'], "href": f"/page/{p['slug']}", "icon": p['icon']} for p in custom_pages]
            })

        return render_template(
            "page.html",
            desa=desa_info,
            page=page,
            nav_links=nav_links_with_pages,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading page '{slug}': {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))
