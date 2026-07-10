"""
Homepage Route - Beranda
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from datetime import datetime
from models import (
    get_desa_info, get_all_berita, get_config, get_all_galeri,
    get_all_potensi, get_all_pengumuman, get_all_struktur, get_all_pages
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
    """
    # Check if we should highlight "Lainnya"
    highlight_lainnya = page_key == "Lainnya" and request_path and request_path in LAINNYA_PAGES
    
    result = []
    for n in NAV_LINKS:
        if n["label"] == "Lainnya":
            result.append({
                "label": n["label"],
                "href": n["href"],
                "active": highlight_lainnya,
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


@public_bp.route("/")
def index():
    """Halaman utama / Beranda"""
    try:
        desa_info = get_desa_info_with_maps()
        berita_list = get_all_berita()
        custom_pages = get_all_pages()

        # Get config values
        try:
            max_unggulan = int(get_config("berita_unggulan_tampil", 3))
            max_berita = int(get_config("berita_tampil_di_beranda", 6))
            carousel_stacks = int(get_config("berita_carousel_stacks", 2))
        except (ValueError, TypeError):
            max_unggulan, max_berita, carousel_stacks = 3, 6, 2

        # Featured carousel - berita UNGGULAN saja
        featured_list = [b for b in berita_list if b.get('unggulan') == 1][:max_unggulan]

        # Grid berita - berita terbaru (tidak termasuk featured)
        featured_ids = [b['id'] for b in featured_list]
        grid_berita = [b for b in berita_list if b['id'] not in featured_ids][:max_berita]

        # Galeri aktif
        galeri_list = get_all_galeri(aktif=1)[:8]

        # Potensi desa aktif
        potensi_list = get_all_potensi()
        potensi_aktif = [p for p in potensi_list if p.get('aktif') == 1]

        # Group potensi by kategori
        potensi_grouped = {}
        for p in potensi_aktif:
            kat = p.get('kategori', 'Lainnya')
            if kat not in potensi_grouped:
                potensi_grouped[kat] = []
            potensi_grouped[kat].append(p)

        # Pengumuman aktif
        pengumuman_list = get_all_pengumuman()
        pengumuman_aktif = [p for p in pengumuman_list if p.get('aktif') == 1][:5]

        # Perangkat Desa aktif
        struktur_list = get_all_struktur(aktif=1)
        perangkat_desa = [s for s in struktur_list if s.get('kategori') == 'perangkat'][:6]

        # Config untuk template
        show_maps = get_config("tampilkan_maps", "1") == "1"
        show_stats = get_config("tampilkan_statistik", "1") == "1"
        show_dusun = get_config("tampilkan_daftar_dusun", "1") == "1"
        show_hero = get_config("tampilkan_hero", "1") == "1"
        show_views = get_config("berita_tampilkan_views", "1") == "1"
        show_tanggal = get_config("berita_tampilkan_tanggal", "1") == "1"

        # Footer config
        config_data = {
            'alamat_desa': get_config("alamat_desa", ""),
            'kontak_telepon': get_config("kontak_telepon", ""),
            'kontak_whatsapp': get_config("kontak_whatsapp", ""),
            'kontak_email': get_config("kontak_email", ""),
            'sosial_facebook': get_config("sosial_facebook", ""),
            'sosial_instagram': get_config("sosial_instagram", ""),
            'sosial_twitter': get_config("sosial_twitter", ""),
            'sosial_tiktok': get_config("sosial_tiktok", ""),
        }

        return render_template(
            "index.html",
            desa=desa_info,
            nav_links=set_nav_active("Beranda"),
            featured_list=featured_list,
            berita_list=grid_berita,
            galeri_list=galeri_list,
            potensi_grouped=potensi_grouped,
            pengumuman_list=pengumuman_aktif,
            perangkat_desa=perangkat_desa,
            config=config_data,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            show_maps=show_maps,
            show_stats=show_stats,
            show_dusun=show_dusun,
            show_hero=show_hero,
            show_views=show_views,
            show_tanggal=show_tanggal,
            custom_pages=custom_pages,
            carousel_stacks=carousel_stacks,
        )
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman utama', 'error')
        return render_template("index.html", error=True)
