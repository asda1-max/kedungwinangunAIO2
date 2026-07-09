"""
Info & Transparansi Routes - Kependudukan, Pengumuman, Peta, APBDes
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime
from models import (
    get_desa_info, get_all_pages, get_all_kependudukan, get_all_pengumuman,
    get_all_umkm, get_umkm_for_geojson, get_apbdes_by_tahun, get_apbdes_summary,
    get_available_tahun, get_lokasi_rtrw_geojson
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


# ── Info Kependudukan ────────────────────────────────────────────────────

@public_bp.route("/info-kependudukan")
def info_kependudukan():
    """Halaman Info Kependudukan dengan Charts"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        all_data = get_all_kependudukan()

        stats = {}
        for item in all_data:
            stats[item['label'].lower().replace(' ', '_').replace('-', '_')] = item.get('jumlah', 0)

        return render_template(
            "info_kependudukan.html",
            page={"title": "Info Kependudukan"},
            stats=stats,
            site_name=desa_info['nama'],
            nav_links=set_nav_active("Kependudukan"),
            tahun=datetime.now().year,
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading kependudukan: {str(e)}")
        return redirect(url_for('public.index'))


# ── Pengumuman ──────────────────────────────────────────────────────────

@public_bp.route("/pengumuman")
def pengumuman():
    """Halaman Pengumuman Desa"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        pengumuman_list = get_all_pengumuman(aktif=1)

        # Format for display
        pengumuman = []
        for p in pengumuman_list:
            kategori_labels = {
                'penting': '🔴 Penting',
                'kegiatan': '📅 Kegiatan',
                'bantuan': '💰 Bantuan',
                'umum': '📢 Umum'
            }
            raw_created_at = p.get('created_at')
            tanggal = '-'
            if raw_created_at:
                try:
                    tanggal = datetime.strptime(str(raw_created_at)[:10], '%Y-%m-%d').strftime('%d %B %Y')
                except Exception:
                    tanggal = str(raw_created_at)

            pengumuman.append({
                'id': p.get('id'),
                'judul': p.get('judul', ''),
                'isi': p.get('isi', ''),
                'kategori': p.get('kategori', 'umum'),
                'kategori_label': kategori_labels.get(p.get('kategori', 'umum'), '📢 Umum'),
                'is_penting': 1 if p.get('is_penting') else 0,
                'tanggal': tanggal,
                'author': p.get('author', 'Pemerintahan Desa'),
                'lampiran': p.get('lampiran') or None,
            })

        return render_template(
            "pengumuman.html",
            page={"title": "Pengumuman"},
            desa=desa_info,
            nav_links=set_nav_active("Pengumuman"),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            pengumuman=pengumuman,
            pengumuman_list=pengumuman,
        )
    except Exception as e:
        logger.error(f"Error loading pengumuman page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman pengumuman', 'error')
        return redirect(url_for('public.index'))


# ── Peta Interaktif ─────────────────────────────────────────────────────

@public_bp.route("/peta-interaktif")
def peta_interaktif():
    """Halaman Peta Interaktif Desa Kedungwinangun"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        # Get UMKM data
        umkm_list = get_all_umkm(aktif=1)
        umkm_geojson = get_umkm_for_geojson(aktif=1)
        
        # Get RT/RW locations from database
        rtrw_geojson = get_lokasi_rtrw_geojson()

        # Kategori labels
        kategori_labels = {
            'makanan': '🍜 Makanan',
            'minuman': '🥤 Minuman',
            'kerajinan': '🎨 Kerajinan',
            'jasa': '🔧 Jasa',
            'pertanian': '🌾 Pertanian',
            'peternakan': '🐔 Peternakan',
            'perikanan': '🐟 Perkins',
            'umum': '🏪 Umum',
        }

        return render_template(
            "peta_interaktif.html",
            page={"title": "Peta Interaktif"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            umkm_list=umkm_list,
            umkm_geojson=umkm_geojson,
            rtrw_geojson=rtrw_geojson,
            kategori_labels=kategori_labels,
        )
    except Exception as e:
        logger.error(f"Error loading peta interaktif page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman peta', 'error')
        return redirect('/')


@public_bp.route("/api/umkm/geojson")
def api_umkm_geojson():
    """API endpoint for UMKM GeoJSON data"""
    geojson = get_umkm_for_geojson(aktif=1)
    return jsonify(geojson)


# ── Transparansi APBDes ────────────────────────────────────────────────

@public_bp.route("/transparansi")
def transparansi():
    """Halaman Transparansi APBDes"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        # Get tahun dari query param atau tahun terbaru
        tahun_list = get_available_tahun()
        if not tahun_list:
            tahun_list = [datetime.now().year]
        tahun = request.args.get('tahun', tahun_list[0], type=int)

        apbdes_list = get_apbdes_by_tahun(tahun)
        summary = get_apbdes_summary(tahun)

        # Group by jenis
        grouped = {'pendapatan': [], 'belanja': [], 'pembiayaan': []}
        for item in apbdes_list:
            if item['jenis'] in grouped:
                grouped[item['jenis']].append(item)

        # Calculate totals
        total_pendapatan = sum(item['jumlah'] for item in grouped['pendapatan'])
        total_belanja = sum(item['jumlah'] for item in grouped['belanja'])
        total_pembiayaan_in = sum(item['jumlah'] for item in grouped['pembiayaan']) if grouped['pembiayaan'] else 0
        pembiayaan_net = total_pembiayaan_in  # Simplified

        apbdes = {
            'tahun': tahun,
            'total_pendapatan': total_pendapatan,
            'total_belanja': total_belanja,
            'pembiayaan_net': pembiayaan_net,
            'pendapatan': grouped['pendapatan'],
            'belanja': grouped['belanja'],
            'pembiayaan': grouped['pembiayaan'],
            'realisasi': [
                {'icon': '🛠️', 'nama': 'Pembangunan', 'realisasi': 65, 'jumlah_rencana': 400_000_000, 'jumlah_realisasi': 260_000_000},
                {'icon': '👥', 'nama': 'Pemerintahan', 'realisasi': 80, 'jumlah_rencana': 200_000_000, 'jumlah_realisasi': 160_000_000},
                {'icon': '🤝', 'nama': 'Pemberdayaan', 'realisasi': 45, 'jumlah_rencana': 120_000_000, 'jumlah_realisasi': 54_000_000},
                {'icon': '🎭', 'nama': 'Kegiatan', 'realisasi': 90, 'jumlah_rencana': 100_000_000, 'jumlah_realisasi': 90_000_000},
            ],
        }

        return render_template(
            "transparansi.html",
            page={"title": "Transparansi"},
            desa=desa_info,
            nav_links=set_nav_active("Lainnya", request.path),
            tahun=tahun,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            apbdes=apbdes,
        )
    except Exception as e:
        logger.error(f"Error loading transparansi page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman transparansi', 'error')
        return redirect(url_for('public.index'))
