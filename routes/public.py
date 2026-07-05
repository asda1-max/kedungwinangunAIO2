"""
Public Routes
Berisi route-route yang dapat diakses publik (tanpa login)

Error Handling:
    Menggunakan decorators dari errors.py:
    - safe_handler: Handle semua error dalam route
    - api_handler: Handle error untuk API endpoints
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, abort
from functools import wraps
from werkzeug.security import check_password_hash
from models import (
    get_desa_info,
    get_all_berita,
    get_berita_by_id,
    get_config,
    get_all_galeri,
    get_user_by_nik,
    get_user_by_username,
    get_user_by_nip,
    verify_user,
    get_all_pages,
    get_page_by_slug,
    get_komentar_by_berita,
    build_comment_tree,
    create_komentar,
    delete_komentar,
    get_komentar_by_id,
    count_komentar_by_berita,
)
from config import NAV_LINKS, MAPS_EMBED_URL, DUSUN_DATA
from errors import safe_handler, flash_error, ValidationError, NotFoundError, json_success_response
import logging

# Setup logging
logger = logging.getLogger(__name__)

public_bp = Blueprint('public', __name__)


def get_desa_info_with_maps():
    """Get desa info with maps URL"""
    info = get_desa_info()
    info['maps_embed_url'] = MAPS_EMBED_URL
    info['dusun'] = DUSUN_DATA
    return info


# ── Unified Login Route ──────────────────────────────────────────────────

@public_bp.route("/login", methods=['GET', 'POST'])
def login():
    """Unified login page for Admin, Dinas, and Warga"""
    from datetime import datetime

    # Redirect if already logged in
    if session.get('user_logged_in'):
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'dinas':
            return redirect(url_for('dinas.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'admin')

        if login_type == 'admin':
            # Admin Login (using username)
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Username dan password wajib diisi!', 'error')
                return redirect(request.url)

            user = get_user_by_username(username)
            if user and user['role'] == 'admin' and check_password_hash(user['password_hash'], password):
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user.get('nik', '')
                session['user_role'] = user['role']
                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Username atau password salah!', 'error')

        elif login_type == 'dinas':
            # Dinas Login (using NIP)
            nip = request.form.get('nip', '').strip()
            password = request.form.get('password', '')

            if not nip or not password:
                flash('NIP dan password wajib diisi!', 'error')
                return redirect(request.url)

            user = get_user_by_nip(nip)
            if user and user['role'] == 'dinas' and check_password_hash(user['password_hash'], password):
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user.get('nik', '')
                session['user_role'] = user['role']
                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')
                return redirect(url_for('dinas.dashboard'))
            else:
                flash('NIP atau password salah!', 'error')

        elif login_type == 'warga':
            # Warga Login
            nik = request.form.get('nik', '').strip()
            password = request.form.get('password', '')

            if not nik or not password:
                flash('NIK dan password wajib diisi!', 'error')
                return redirect(request.url)

            user = verify_user(nik, password)
            if user:
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user['nik']
                session['user_role'] = user['role']

                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')
                return redirect(url_for('user.dashboard'))
            else:
                flash('NIK atau password salah!', 'error')

    # Render login page
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        return render_template(
            "login.html",
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman. Silakan coba lagi.', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/")
def index():
    """Halaman utama / Beranda"""
    from datetime import datetime

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
            custom_pages=custom_pages,
            carousel_stacks=carousel_stacks,
        )
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman utama', 'error')
        return render_template("index.html", error=True)


@public_bp.route("/berita")
def berita():
    """Halaman daftar berita"""
    try:
        desa_info = get_desa_info_with_maps()
        berita_list = get_all_berita()
        custom_pages = get_all_pages()

        try:
            max_berita = int(get_config("berita_tampil_di_halaman", 12))
        except (ValueError, TypeError):
            max_berita = 12

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
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading berita page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman berita', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/berita/<int:berita_id>")
def detail_berita(berita_id):
    """Halaman detail berita"""
    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        artikel = get_berita_by_id(berita_id)

        if not artikel:
            flash('Berita tidak ditemukan', 'error')
            return redirect(url_for('public.berita'))

        show_views = get_config("berita_tampilkan_views", "1") == "1"
        show_tanggal = get_config("berita_tampilkan_tanggal", "1") == "1"

        return render_template(
            "detail_berita.html",
            desa=desa_info,
            nav_links=[{**n, "active": n["label"] == "Berita"} for n in NAV_LINKS],
            artikel=artikel,
            show_views=show_views,
            show_tanggal=show_tanggal,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading berita {berita_id}: {str(e)}")
        flash('Terjadi kesalahan saat memuat berita', 'error')
        return redirect(url_for('public.berita'))


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
    import json

    try:
        custom_pages = get_all_pages()
        jenis_surat = get_all_jenis_surat()
        desa_info = get_desa_info_with_maps()

        # Handle form submission
        if request.method == 'POST':
            jenis_id = request.form.get('jenis_surat_id', '')
            data = {}
            for key, value in request.form.items():
                if key not in ['jenis_surat_id']:
                    data[key] = value

            if not jenis_id:
                flash('Pilih jenis surat terlebih dahulu', 'error')
                return redirect(request.url)

            success = create_permohonan_surat(session.get('user_id'), jenis_id, json.dumps(data))
            if success:
                flash('Permohonan surat berhasil diajukan! Mohon tunggu persetujuan.', 'success')
            else:
                flash('Terjadi kesalahan saat mengajukan permohonan. Silakan coba lagi.', 'error')
            return redirect(url_for('user.dashboard'))

        return render_template(
            "/user/surat_permohonan.html",
            desa=desa_info,
            nav_links=[{**n, "active": n["label"] == "Layanan"} for n in NAV_LINKS],
            jenis_surat=jenis_surat,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error in layanan: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman layanan', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/kontak")
def kontak():
    """Halaman informasi kontak desa"""
    from datetime import datetime

    try:
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

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
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading kontak page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman kontak', 'error')
        return redirect(url_for('public.index'))


@public_bp.route("/galeri")
def galeri():
    """Halaman galeri foto desa"""
    from datetime import datetime

    try:
        desa_info = get_desa_info_with_maps()
        foto_list = get_all_galeri(aktif=1)
        custom_pages = get_all_pages()

        return render_template(
            "galeri.html",
            desa=desa_info,
            nav_links=[{**n, "active": n["label"] == "Galeri"} for n in NAV_LINKS],
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
            # Add Lainnya with custom pages
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


@public_bp.route("/peta-interaktif")
def peta_interaktif():
    """Halaman Peta Interaktif Desa Kedungwinangun"""
    from datetime import datetime

    try:
        from models import get_all_pages
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()

        return render_template(
            "peta_interaktif.html",
            page={"title": "Peta Interaktif"},
            desa=desa_info,
            nav_links=NAV_LINKS,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
        )
    except Exception as e:
        logger.error(f"Error loading peta interaktif page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman peta', 'error')
        return redirect(url_for('public.index'))


# ════════════════════════════════════════════════════════════════════════
# ── STRUKTUR ORGANISASI ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/struktur")
def struktur():
    """Halaman Struktur Organisasi Desa"""
    from datetime import datetime

    try:
        from models import get_all_pages, get_all_struktur
        desa_info = get_desa_info_with_maps()
        custom_pages = get_all_pages()
        struktur_list = get_all_struktur()

        # Group by kategori
        grouped = {'pemerintah': [], 'bpd': [], 'rtrw': [], 'kader': []}
        for item in struktur_list:
            kat = item.get('kategori', '')
            if kat in grouped:
                grouped[kat].append(item)

        return render_template(
            "struktur.html",
            page={"title": "Struktur Organisasi"},
            desa=desa_info,
            nav_links=NAV_LINKS,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            grouped_struktur=grouped,
        )
    except Exception as e:
        logger.error(f"Error loading struktur page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman struktur', 'error')
        return redirect(url_for('public.index'))


# ════════════════════════════════════════════════════════════════════════
# ── PENGUMUMAN ────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/pengumuman")
def pengumuman():
    """Halaman Pengumuman Desa"""
    from datetime import datetime

    try:
        from models import get_all_pages, get_all_pengumuman
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
            pengumuman.append({
                'id': p['id'],
                'judul': p['judul'],
                'isi': p['isi'],
                'kategori': p['kategori'],
                'kategori_label': kategori_labels.get(p['kategori'], '📢 Umum'),
                'is_penting': bool(p['is_penting']),
                'tanggal': datetime.strptime(p['created_at'][:10], '%Y-%m-%d').strftime('%d %B %Y') if p.get('created_at') else '-',
                'author': p.get('author', 'Pemerintahan Desa'),
                'lampiran': p.get('lampiran') or None,
            })

        return render_template(
            "pengumuman.html",
            page={"title": "Pengumuman"},
            desa=desa_info,
            nav_links=NAV_LINKS,
            tahun=datetime.now().year,
            site_name=desa_info['nama'],
            site_tagline=desa_info['tagline'],
            site_description=desa_info['deskripsi'],
            custom_pages=custom_pages,
            pengumuman=pengumuman,
        )
    except Exception as e:
        logger.error(f"Error loading pengumuman page: {str(e)}")
        flash('Terjadi kesalahan saat memuat halaman pengumuman', 'error')
        return redirect(url_for('public.index'))


# ════════════════════════════════════════════════════════════════════════
# ── TRANSPARANSI APBDes ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/transparansi")
def transparansi():
    """Halaman Transparansi APBDes"""
    from datetime import datetime

    try:
        from models import get_all_pages, get_apbdes_by_tahun, get_apbdes_summary, get_available_tahun
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
            nav_links=NAV_LINKS,
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


# ════════════════════════════════════════════════════════════════════════
# ── API: KOMENTAR BERITA ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["GET"])
def api_get_komentar(berita_id):
    """Ambil semua komentar untuk sebuah berita (JSON tree)"""
    try:
        flat = get_komentar_by_berita(berita_id)
        tree = build_comment_tree(flat)
        total = count_komentar_by_berita(berita_id)
        return jsonify({
            "success": True,
            "comments": tree,
            "total": total,
        })
    except Exception as e:
        logger.error(f"Error getting komentar for berita {berita_id}: {str(e)}")
        return jsonify({"success": False, "error": "Terjadi kesalahan saat mengambil komentar"}), 500


@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["POST"])
def api_post_komentar(berita_id):
    """Post komentar baru atau reply"""
    try:
        if request.is_json:
            data = request.get_json()
            konten = (data.get("konten") or "").strip()
            parent_id = data.get("parent_id")
            nama_pengirim = (data.get("nama_pengirim") or "").strip()
        else:
            konten = (request.form.get("konten") or "").strip()
            parent_id = request.form.get("parent_id")
            nama_pengirim = (request.form.get("nama_pengirim") or "").strip()

        if not konten:
            return jsonify({"success": False, "error": "Konten tidak boleh kosong"}), 400

        user_id = session.get("user_id")
        user_role = session.get("user_role")

        # Tentukan nama pengirim
        if user_id:
            sender = session.get("user_nama", "Anonim")
        elif nama_pengirim:
            sender = nama_pengirim
        else:
            return jsonify({"success": False, "error": "Nama wajib diisi untuk tamu"}), 400

        # Validate parent_id
        if parent_id:
            parent_id = int(parent_id)
            # Pastikan parent comment ada dan milik berita yang sama
            parent = get_komentar_by_id(parent_id)
            if not parent or parent['berita_id'] != berita_id:
                return jsonify({"success": False, "error": "Komentar induk tidak ditemukan"}), 400

        create_komentar(berita_id, konten, sender, parent_id, user_id)
        return jsonify({"success": True, "message": "Komentar terkirim!"})

    except Exception as e:
        logger.error(f"Error posting komentar for berita {berita_id}: {str(e)}")
        return jsonify({"success": False, "error": "Terjadi kesalahan saat mengirim komentar"}), 500


@public_bp.route("/api/berita/<int:berita_id>/komentar/<int:komentar_id>", methods=["DELETE"])
def api_delete_komentar(berita_id, komentar_id):
    """Hapus komentar (owner atau admin saja)"""
    try:
        user_id = session.get("user_id")
        user_role = session.get("user_role")

        if not user_id:
            return jsonify({"success": False, "error": "Login required"}), 401

        if user_role not in ['admin', 'dinas']:
            return jsonify({"success": False, "error": "Tidak memiliki hak hapus"}), 403

        komentar = get_komentar_by_id(komentar_id)
        if not komentar or komentar['berita_id'] != berita_id:
            return jsonify({"success": False, "error": "Komentar tidak ditemukan"}), 404

        # Admin/Dinas bisa hapus siapa saja; warga hanya hapus milik sendiri
        if user_role not in ['admin', 'dinas'] and komentar['user_id'] != user_id:
            return jsonify({"success": False, "error": "Tidak memiliki hak hapus"}), 403

        delete_komentar(komentar_id)
        return jsonify({"success": True, "message": "Komentar dihapus"})

    except Exception as e:
        logger.error(f"Error deleting komentar {komentar_id}: {str(e)}")
        return jsonify({"success": False, "error": "Terjadi kesalahan saat menghapus komentar"}), 500
