"""
Aduan & Program Kerja Routes (Public)
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from datetime import datetime
from models import get_desa_info, get_all_pages, add_aduan, get_aduan_by_nomor, get_all_aduan, get_all_program_kerja
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


# ════════════════════════════════════════════════════════════════════════
# ── ADUAN PUBLIK ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/aduan", methods=['GET', 'POST'])
def aduan():
    """Halaman form aduan publik"""
    from models import add_aduan
    
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        email = request.form.get('email', '').strip()
        telepon = request.form.get('telepon', '').strip()
        nik = request.form.get('nik', '').strip()
        alamat = request.form.get('alamat', '').strip()
        dusun = request.form.get('dusun', '').strip()
        judul = request.form.get('judul', '').strip()
        kategori = request.form.get('kategori', 'infrastruktur')
        lokasi = request.form.get('lokasi', '').strip()
        isi = request.form.get('deskripsi', '').strip()

        if not nama or not judul or not isi:
            flash('Nama, judul, dan deskripsi aduan wajib diisi!', 'error')
            return redirect(url_for('public.aduan'))

        logger.info(f"[PUBLIC-ADUAN] Form submitted: nama={nama}, judul={judul}, kategori={kategori}")
        success, nomor = add_aduan(
            nama=nama, judul=judul, deskripsi=isi, kategori=kategori,
            email=email or None, telepon=telepon or None, nik=nik or None,
            alamat=alamat or None, dusun=dusun or None, lokasi=lokasi or None
        )
        
        if success:
            logger.info(f"[PUBLIC-ADUAN] Success: nomor={nomor}")
            flash(f'Aduan berhasil dikirim! Nomor pengaduan: {nomor}', 'success')
        else:
            logger.error(f"[PUBLIC-ADUAN] Failed to submit: nama={nama}, judul={judul}")
            flash('Gagal mengirim aduan. Silakan coba lagi.', 'error')
        
        return redirect(url_for('public.aduan'))

    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        return render_template(
            "aduan.html",
            page={"title": "Aduan"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading aduan page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/aduan/cek", methods=['GET', 'POST'])
def cek_aduan():
    """Halaman cek status aduan"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        
        aduan_data = None
        nomor_cari = ''
        
        if request.method == 'POST':
            nomor_cari = request.form.get('nomor_aduan', '').strip()
            if nomor_cari:
                aduan_data = get_aduan_by_nomor(nomor_cari)
                if not aduan_data:
                    flash('Aduan tidak ditemukan. Pastikan nomor aduan benar.', 'warning')

        return render_template(
            "cek_aduan.html",
            page={"title": "Cek Aduan"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            aduan_data=aduan_data,
            nomor_cari=nomor_cari,
        )
    except Exception as e:
        logger.error(f"Error loading cek_aduan page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))


# ════════════════════════════════════════════════════════════════════════
# ── PROGRAM KERJA ─────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/program-kerja")
def program_kerja():
    """Halaman daftar program kerja desa"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        
        # Get filter
        tahun_filter = request.args.get('tahun', type=int)
        kategori_filter = request.args.get('kategori', '')
        
        program_list = get_all_program_kerja(aktif=1, tahun=tahun_filter)
        
        # Filter by kategori if specified
        if kategori_filter:
            program_list = [p for p in program_list if p.get('kategori') == kategori_filter]
        
        # Group by status
        by_status = {
            'rencana': [],
            'berlangsung': [],
            'selesai': [],
        }
        for p in program_list:
            status = p.get('status', 'berlangsung')
            if status in by_status:
                by_status[status].append(p)
            else:
                by_status['berlangsung'].append(p)
        
        # Get available years
        all_program = get_all_program_kerja(aktif=1)
        tahun_list = sorted(set(p.get('tahun') for p in all_program if p.get('tahun')), reverse=True)
        if not tahun_list:
            tahun_list = [datetime.now().year]
        
        # Kategori labels
        kategori_labels = {
            'pembangunan': 'Pembangunan',
            'pemberdayaan': 'Pemberdayaan',
            'pembinaan': 'Pembinaan',
            'pelayanan': 'Pelayanan',
            'kesehatan': 'Kesehatan',
            'pendidikan': 'Pendidikan',
            'umum': 'Umum',
        }
        
        status_labels = {
            'rencana': '🗓️ Rencana',
            'berlangsung': '🔄 Berlangsung',
            'selesai': '✅ Selesai',
        }

        return render_template(
            "program_kerja.html",
            page={"title": "Program Kerja"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            program_list=program_list,
            by_status=by_status,
            tahun_list=tahun_list,
            tahun_filter=tahun_filter,
            kategori_filter=kategori_filter,
            kategori_labels=kategori_labels,
            status_labels=status_labels,
        )
    except Exception as e:
        logger.error(f"Error loading program_kerja page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))


# ════════════════════════════════════════════════════════════════════════
# ── AGENDA DESA (TIMELINE) ───────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/agenda")
def agenda():
    """Halaman agenda desa (timeline)"""
    try:
        from models import get_all_agenda
        from datetime import date
        
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        
        # Get filter
        tahun_filter = request.args.get('tahun', type=int)
        status_filter = request.args.get('status', '')
        
        agenda_list = get_all_agenda(aktif=1, tahun=tahun_filter, status=status_filter)
        
        # Separate upcoming and past
        today = date.today()
        upcoming = []
        past = []
        
        for a in agenda_list:
            try:
                tgl = datetime.strptime(str(a.get('tanggal_mulai', '')), '%Y-%m-%d').date()
                if tgl >= today:
                    upcoming.append(a)
                else:
                    past.append(a)
            except:
                upcoming.append(a)
        
        # Get available years
        all_agenda = get_all_agenda(aktif=1)
        tahun_list = []
        for ag in all_agenda:
            try:
                tgl = datetime.strptime(str(ag.get('tanggal_mulai', '')), '%Y-%m-%d').date()
                if tgl.year not in tahun_list:
                    tahun_list.append(tgl.year)
            except:
                pass
        tahun_list = sorted(set(tahun_list), reverse=True)
        if not tahun_list:
            tahun_list = [datetime.now().year]
        
        # Kategori labels
        kategori_labels = {
            'kegiatan': '📌 Kegiatan',
            'rapat': '🏛️ Rapat',
            'musyawarah': '🤝 Musyawarah',
            'pembangunan': '🏗️ Pembangunan',
            'kesehatan': '🏥 Kesehatan',
            'pendidikan': '📚 Pendidikan',
            'umum': '📋 Umum',
        }
        
        status_labels = {
            'akan_datang': '🟢 Akan Datang',
            'sedang_berlangsung': '🟡 Sedang Berlangsung',
            'selesai': '🔵 Selesai',
            'dibatalkan': '🔴 Dibatalkan',
        }

        return render_template(
            "agenda.html",
            page={"title": "Agenda"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            agenda_list=agenda_list,
            upcoming=upcoming,
            past=past,
            tahun_list=tahun_list,
            tahun_filter=tahun_filter,
            status_filter=status_filter,
            kategori_labels=kategori_labels,
            status_labels=status_labels,
        )
    except Exception as e:
        logger.error(f"Error loading agenda page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.index'))
