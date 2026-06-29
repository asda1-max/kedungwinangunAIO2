"""
Public Routes
Berisi route-route yang dapat diakses publik (tanpa login)
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, json
from models import (
    get_desa_info,
    get_all_berita,
    get_berita_by_id,
    get_config,
    get_all_galeri,
)
from config import NAV_LINKS, MAPS_EMBED_URL, DUSUN_DATA

public_bp = Blueprint('public', __name__)


def get_desa_info_with_maps():
    """Get desa info with maps URL"""
    info = get_desa_info()
    info['maps_embed_url'] = MAPS_EMBED_URL
    info['dusun'] = DUSUN_DATA
    return info


@public_bp.route("/")
def index():
    """Halaman utama / Beranda"""
    from datetime import datetime
    desa_info = get_desa_info_with_maps()
    berita_list = get_all_berita()

    # Get config values
    max_unggulan = int(get_config("berita_unggulan_tampil", 3))
    max_berita = int(get_config("berita_tampil_di_beranda", 6))
    carousel_stacks = int(get_config("berita_carousel_stacks", 2))

    # Featured carousel - berita UNGGULAN saja
    featured_list = [b for b in berita_list if b.get('unggulan') == 1][:max_unggulan]

    # Grid berita - berita terbaru (tidak termasuk featured)
    featured_ids = [b['id'] for b in featured_list]
    grid_berita = [b for b in berita_list if b['id'] not in featured_ids][:max_berita]

    # Galeri aktif
    galeri_list = get_all_galeri(aktif=1)[:8]

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
    }

    return render_template(
        "index.html",
        desa=desa_info,
        nav_links=NAV_LINKS,
        featured_list=featured_list,
        berita_list=grid_berita,
        galeri_list=galeri_list,
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
        carousel_stacks=carousel_stacks,
    )


@public_bp.route("/berita")
def berita():
    """Halaman daftar berita"""
    desa_info = get_desa_info_with_maps()
    berita_list = get_all_berita()
    max_berita = int(get_config("berita_tampil_di_halaman", 12))
    berita_list = berita_list[:max_berita]
    show_views = get_config("berita_tampilkan_views", "1") == "1"
    show_tanggal = get_config("berita_tampilkan_tanggal", "1") == "1"

    return render_template(
        "berita.html",
        desa=desa_info,
        nav_links=[{**n, "active": n["label"] == "Berita"} for n in NAV_LINKS],
        berita_list=berita_list,
        show_views=show_views,
        show_tanggal=show_tanggal,
    )


@public_bp.route("/berita/<int:berita_id>")
def detail_berita(berita_id):
    """Halaman detail berita"""
    desa_info = get_desa_info_with_maps()
    artikel = get_berita_by_id(berita_id)
    if not artikel:
        return "Berita tidak ditemukan", 404
    show_views = get_config("berita_tampilkan_views", "1") == "1"
    show_tanggal = get_config("berita_tampilkan_tanggal", "1") == "1"

    return render_template(
        "detail_berita.html",
        desa=desa_info,
        nav_links=[{**n, "active": n["label"] == "Berita"} for n in NAV_LINKS],
        artikel=artikel,
        show_views=show_views,
        show_tanggal=show_tanggal,
    )


@public_bp.route("/surat")
def surat_info():
    """Redirect /surat ke /layanan"""
    return redirect(url_for('public.layanan'))


@public_bp.route("/layanan")
def layanan():
    """Halaman daftar layanan - redirect guest ke register"""
    # Cek apakah user sudah login
    if 'user_logged_in' not in session:
        return redirect(url_for('user.register', next=url_for('public.layanan')))

    # User sudah login, tampilkan form permohonan surat
    from models import get_all_jenis_surat, create_permohonan_surat

    jenis_surat = get_all_jenis_surat()
    desa_info = get_desa_info_with_maps()

    # Handle form submission
    if request.method == 'POST':
        jenis_id = request.form.get('jenis_surat_id', '')
        data = {}
        for key, value in request.form.items():
            if key not in ['jenis_surat_id']:
                data[key] = value

        create_permohonan_surat(session.get('user_id'), jenis_id, json.dumps(data))
        flash('Permohonan surat berhasil diajukan! Mohon tunggu persetujuan.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template(
        "/user/surat_permohonan.html",
        desa=desa_info,
        nav_links=[{**n, "active": n["label"] == "Layanan"} for n in NAV_LINKS],
        jenis_surat=jenis_surat,
    )


@public_bp.route("/kontak")
def kontak():
    """Halaman informasi kontak desa"""
    from datetime import datetime
    desa_info = get_desa_info_with_maps()

    # Ambil data kontak dari config
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
        nav_links=[{**n, "active": n["label"] == "Kontak"} for n in NAV_LINKS],
        kontak=kontak_data,
        tahun=datetime.now().year,
        config=kontak_data,
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
    )


@public_bp.route("/galeri")
def galeri():
    """Halaman galeri foto desa"""
    from datetime import datetime
    desa_info = get_desa_info_with_maps()
    foto_list = get_all_galeri(aktif=1)

    return render_template(
        "galeri.html",
        desa=desa_info,
        nav_links=[{**n, "active": n["label"] == "Galeri"} for n in NAV_LINKS],
        foto_list=foto_list,
        tahun=datetime.now().year,
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
    )
