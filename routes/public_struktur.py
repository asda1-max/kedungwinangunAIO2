"""
Struktur & Sejarah Routes
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from datetime import datetime
from models import (
    get_desa_info, get_all_pages, get_all_struktur, get_struktur_by_id,
    get_all_sejarah
)
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
# ── STRUKTUR ORGANISASI ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/struktur")
def struktur():
    """Halaman Struktur Organisasi Desa"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        struktur_list = get_all_struktur(aktif=1)

        # Group by kategori (new categories)
        grouped = {'perangkat': [], 'bpd': [], 'pkk': [], 'karang_taruna': [], 'rt': [], 'rw': []}
        for item in struktur_list:
            kat = item.get('kategori', '')
            if kat in grouped:
                grouped[kat].append(item)

        # Kategori labels
        kategori_labels = {
            'perangkat': 'Perangkat Desa',
            'bpd': 'BPD',
            'pkk': 'PKK',
            'karang_taruna': 'Karang Taruna',
            'rt': 'RT',
            'rw': 'RW',
        }

        return render_template(
            "struktur.html",
            page={"title": "Struktur Organisasi"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            grouped_struktur=grouped,
            kategori_labels=kategori_labels,
        )
    except Exception as e:
        logger.error(f"Error loading struktur page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman struktur', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/struktur/<int:struktur_id>")
def struktur_detail(struktur_id):
    """Detail personil struktur organisasi"""
    try:
        item = get_struktur_by_id(struktur_id)
        if not item:
            flash('Data tidak ditemukan', 'error')
            return redirect(url_for('public.struktur'))

        # Get related items in same kategori
        related = get_all_struktur(aktif=1)
        related = [r for r in related if r['kategori'] == item['kategori'] and r['id'] != struktur_id][:4]

        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        return render_template(
            "struktur_detail.html",
            page={"title": item['nama']},
            item=item,
            related=related,
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading struktur detail {struktur_id}: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman', 'error')
        return redirect(url_for('public.struktur'))


# ════════════════════════════════════════════════════════════════════════
# ── SEJARAH DESA ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/sejarah")
def sejarah():
    """Halaman Sejarah Desa - immersive timeline"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        # Get sejarah entries from database (aktif only)
        sejarah_items = get_all_sejarah(aktif=1)

        # If no entries, show default placeholder
        if not sejarah_items:
            sejarah_items = [
                {
                    'tahun_dari': 1900,
                    'tahun_sampai': 1945,
                    'judul': 'Awal Mula Desa',
                    'sub_judul': 'Lahirnya Sebuah Komunitas',
                    'konten': 'Desa Kedungwinangun telah berdiri sejak awal abad ke-20, menjadi salah satu desa tertua di Kecamatan Klirong, Kabupaten Kebumen.',
                    'gambar_url': '',
                    'video_url': ''
                },
                {
                    'tahun_dari': 1945,
                    'tahun_sampai': 1970,
                    'judul': 'Masa Kemerdekaan',
                    'sub_judul': 'Periode Perjuangan',
                    'konten': 'Setelah kemerdekaan Indonesia, desa ini mulai berkembang dengan pendidikan dan pertanian. Masyarakat bersatu membangun desa dari keterpurukan.',
                    'gambar_url': '',
                    'video_url': ''
                },
                {
                    'tahun_dari': 1970,
                    'tahun_sampai': 2000,
                    'judul': 'Era Modernisasi',
                    'sub_judul': 'Transformasi Desa',
                    'konten': 'Pembangunan infrastruktur mulai merata, jalan desa diaspal, listrik masuk ke seluruh dusun, dan akses pendidikan semakin terbuka.',
                    'gambar_url': '',
                    'video_url': ''
                },
                {
                    'tahun_dari': 2000,
                    'tahun_sampai': 2020,
                    'judul': 'Era Digital',
                    'sub_judul': 'Desa Menyongsong Teknologi',
                    'konten': 'Mulai memasuki era digital dengan website resmi desa dan sistem informasi pemerintahan. Generasi muda mulai kembali ke desa membawa inovasi.',
                    'gambar_url': '',
                    'video_url': ''
                },
                {
                    'tahun_dari': 2020,
                    'tahun_sampai': None,
                    'judul': 'Kedungwinangun Sekarang',
                    'sub_judul': 'Melangkah ke Masa Depan',
                    'konten': 'Desa Kedungwinangun terus berkembang dengan potensi pertanian, UMKM, dan pelayanan digital untuk warga. Visi masa depan yang cerah telah dimulai.',
                    'gambar_url': '',
                    'video_url': ''
                }
            ]

        return render_template(
            "sejarah.html",
            page={"title": "Sejarah Desa"},
            desa=desa_info,
            nav_links=set_nav_active("Sejarah"),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            sejarah_items=sejarah_items,
        )
    except Exception as e:
        logger.error(f"Error loading sejarah page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman sejarah', 'error')
        return redirect(url_for('public.index'))
