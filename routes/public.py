"""
Public Routes
Berisi route-route yang dapat diakses publik (tanpa login)
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
from werkzeug.security import check_password_hash
from models import (
    get_desa_info,
    get_all_berita,
    get_berita_by_id,
    get_config,
    get_all_galeri,
    get_user_by_nik,
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
            # Admin/Dinas Login
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            user = get_user_by_nik(username)
            if user and user['role'] in ['admin', 'dinas'] and check_password_hash(user['password_hash'], password):
                session['user_logged_in'] = True
                session['user_id'] = user['id']
                session['user_nama'] = user['nama_lengkap']
                session['user_nik'] = user['nik']
                session['user_role'] = user['role']

                flash(f'Selamat datang, {user["nama_lengkap"]}!', 'success')

                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('dinas.dashboard'))
            else:
                flash('Username atau password salah!', 'error')

        elif login_type == 'warga':
            # Warga Login
            nik = request.form.get('nik', '').strip()
            password = request.form.get('password', '')

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
    desa_info = get_desa_info_with_maps()
    custom_pages = get_all_pages()
    return render_template(
        "login.html",
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
        custom_pages=custom_pages,
    )


@public_bp.route("/")
def index():
    """Halaman utama / Beranda"""
    from datetime import datetime
    desa_info = get_desa_info_with_maps()
    berita_list = get_all_berita()
    custom_pages = get_all_pages()

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
        custom_pages=custom_pages,
        carousel_stacks=carousel_stacks,
    )


@public_bp.route("/berita")
def berita():
    """Halaman daftar berita"""
    desa_info = get_desa_info_with_maps()
    berita_list = get_all_berita()
    custom_pages = get_all_pages()
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
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
        custom_pages=custom_pages,
    )


@public_bp.route("/berita/<int:berita_id>")
def detail_berita(berita_id):
    """Halaman detail berita"""
    desa_info = get_desa_info_with_maps()
    custom_pages = get_all_pages()
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
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
        custom_pages=custom_pages,
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

        create_permohonan_surat(session.get('user_id'), jenis_id, json.dumps(data))
        flash('Permohonan surat berhasil diajukan! Mohon tunggu persetujuan.', 'success')
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


@public_bp.route("/kontak")
def kontak():
    """Halaman informasi kontak desa"""
    from datetime import datetime
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


@public_bp.route("/galeri")
def galeri():
    """Halaman galeri foto desa"""
    from datetime import datetime
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


@public_bp.route("/page/<slug>")
def view_page(slug):
    """Halaman custom page"""
    from datetime import datetime
    desa_info = get_desa_info_with_maps()
    page = get_page_by_slug(slug)

    if not page:
        return "Page tidak ditemukan", 404

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


@public_bp.route("/peta-interaktif")
def peta_interaktif():
    """Halaman Peta Interaktif Desa Kedungwinangun"""
    from datetime import datetime
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


# ════════════════════════════════════════════════════════════════════════
# ── STRUKTUR ORGANISASI ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/struktur")
def struktur():
    """Halaman Struktur Organisasi Desa"""
    from datetime import datetime
    from models import get_all_pages

    desa_info = get_desa_info_with_maps()
    custom_pages = get_all_pages()

    # Data contoh struktur organisasi
    struktur_pemerintah = [
        {'nama': 'Drs. H. Ahmad Zainuri', 'jabatan': 'Kepala Desa', 'status': 'PNS Desa'},
        {'nama': 'Sri Hartati', 'jabatan': 'Sekretaris Desa', 'status': 'PNS Desa'},
        {'nama': 'Budi Santoso', 'jabatan': 'Kasi Pemerintahan', 'status': ' perangkat Desa'},
        {'nama': 'Siti Aminah', 'jabatan': 'Kasi Kesejahteraan', 'status': 'Perangkat Desa'},
        {'nama': 'Joko Priyanto', 'jabatan': 'Kasi Pembangunan', 'status': 'Perangkat Desa'},
        {'nama': 'Mariam', 'jabatan': 'Kaur Keuangan', 'status': 'Perangkat Desa'},
        {'nama': 'Ahmad Dahlan', 'jabatan': 'Kaur Umum', 'status': 'Perangkat Desa'},
    ]

    struktur_bpd = [
        {'nama': 'H. Suprianto', 'jabatan': 'Ketua BPD'},
        {'nama': 'Nurasiah', 'jabatan': 'Wakil Ketua'},
        {'nama': 'Mansur', 'jabatan': 'Sekretaris'},
        {'nama': 'Rohmah', 'jabatan': 'Anggota'},
        {'nama': 'Dedi Kurniawan', 'jabatan': 'Anggota'},
        {'nama': 'Kartika Sari', 'jabatan': 'Anggota'},
        {'nama': 'Hendra Wijaya', 'jabatan': 'Anggota'},
        {'nama': 'Lestari', 'jabatan': 'Anggota'},
    ]

    struktur_rtrw = [
        {'no_rw': '01', 'ketua_rw': 'Sugeng Riyanto', 'rt_list': [
            {'no_rt': '01', 'ketua_rt': 'Warto'},
            {'no_rt': '02', 'ketua_rt': 'Sukarman'},
            {'no_rt': '03', 'ketua_rt': 'Maryono'},
        ]},
        {'no_rw': '02', 'ketua_rw': 'Karsono', 'rt_list': [
            {'no_rt': '01', 'ketua_rt': 'Jiminem'},
            {'no_rt': '02', 'ketua_rt': 'Sarwono'},
        ]},
        {'no_rw': '03', 'ketua_rw': 'Markowi', 'rt_list': [
            {'no_rt': '01', 'ketua_rt': 'Tukinem'},
            {'no_rt': '02', 'ketua_rt': 'Paimin'},
            {'no_rt': '03', 'ketua_rt': 'Gatot'},
        ]},
    ]

    struktur_kader = [
        {'icon': '👩', 'nama': 'Kader PKK', 'jumlah': 15},
        {'icon': '👶', 'nama': 'Kader POSYANDU', 'jumlah': 12},
        {'icon': '🔥', 'nama': 'Kader Kebersihan', 'jumlah': 8},
        {'icon': '🌾', 'nama': 'Kader Pertanian', 'jumlah': 10},
        {'icon': '💪', 'nama': 'Relawan Desa', 'jumlah': 20},
        {'icon': '🛡️', 'nama': 'Satgas COVID-19', 'jumlah': 15},
    ]

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
        struktur_pemerintah=struktur_pemerintah,
        struktur_bpd=struktur_bpd,
        struktur_rtrw=struktur_rtrw,
        struktur_kader=struktur_kader,
    )


# ════════════════════════════════════════════════════════════════════════
# ── PENGUMUMAN ────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/pengumuman")
def pengumuman():
    """Halaman Pengumuman Desa"""
    from datetime import datetime
    from models import get_all_pages

    desa_info = get_desa_info_with_maps()
    custom_pages = get_all_pages()

    # Data contoh pengumuman
    pengumuman = [
        {
            'id': 1,
            'judul': 'Pendaftaran BLT-DD Tahun 2026',
            'isi': 'Bapak/Ibu warga Desa Kedungwinangun yang membutuhkan bantuan Langsung Tunai dari Dana Desa, silakan mendaftar di Kantor Desa mulai tanggal 1-15 Juli 2026. Syarat: fc KTP, fc KK, surat keterangan tidak mampu dari RT/RW.',
            'kategori': 'penting',
            'kategori_label': '🔴 Penting',
            'is_penting': True,
            'tanggal': '28 Juni 2026',
            'author': 'Pemerintahan Desa',
            'lampiran': 'Formulir Pendaftaran.pdf',
        },
        {
            'id': 2,
            'judul': 'Rapat Bulanan Pemerintah Desa',
            'isi': 'Akan dilaksanakan rapat bulanan pemerintah desa pada hari Sabtu, 5 Juli 2026 pukul 09.00 WIB di Aula Kantor Desa. Agenda: evaluasi program kerja semester I dan rencana kegiatan semester II.',
            'kategori': 'kegiatan',
            'kategori_label': '📅 Kegiatan',
            'is_penting': False,
            'tanggal': '1 Juli 2026',
            'author': 'Sekretaris Desa',
            'lampiran': None,
        },
        {
            'id': 3,
            'judul': 'Penerimaan Bantuan PKH & KIP',
            'isi': 'Bantuan PKH (Program Keluarga Harapan) dan KIP (Kartu Indonesia Pintar) akan didistribusikan pada minggu ketiga Juli 2026. Keluarga penerima akan diinformasikan melalui RT/RW masing-masing.',
            'kategori': 'bantuan',
            'kategori_label': '💰 Bantuan',
            'is_penting': True,
            'tanggal': '25 Juni 2026',
            'author': 'Kasi Kesejahteraan',
            'lampiran': 'Daftar Penerima.pdf',
        },
        {
            'id': 4,
            'judul': 'Posyandu Balita - Bulan Juli',
            'isi': 'Kegiatan Posyandu Balita akan dilaksanakan pada hari Minggu, 6 Juli 2026 pukul 08.00-12.00 di masing-masing balai dusun. Mari antar buah hati Anda untuk pemeriksaan kesehatan dan imunisasi.',
            'kategori': 'kegiatan',
            'kategori_label': '📅 Kegiatan',
            'is_penting': False,
            'tanggal': '28 Juni 2026',
            'author': 'Kader PKK',
            'lampiran': None,
        },
        {
            'id': 5,
            'judul': 'Pemberitahuan Pemadaman Listrik',
            'isi': 'Akan dilakukan pemadaman listrik terencana pada hari Kamis, 3 Juli 2026 pukul 09.00-15.00 untuk perawatan jaringan. Mohon warga menyiapkan kebutuhan air dan listrik cadangan.',
            'kategori': 'penting',
            'kategori_label': '🔴 Penting',
            'is_penting': True,
            'tanggal': '30 Juni 2026',
            'author': 'Pemerintahan Desa',
            'lampiran': None,
        },
    ]

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


# ════════════════════════════════════════════════════════════════════════
# ── TRANSPARANSI APBDes ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/transparansi")
def transparansi():
    """Halaman Transparansi APBDes"""
    from datetime import datetime
    from models import get_all_pages

    desa_info = get_desa_info_with_maps()
    custom_pages = get_all_pages()
    tahun = 2026

    # Data APBDes contoh
    apbdes = {
        'tahun': tahun,
        'total_pendapatan': 850_000_000,
        'total_belanja': 820_000_000,
        'pembiayaan_net': 30_000_000,
        'pendapatan': [
            {'icon': '💵', 'nama': 'Pendapatan Asli Desa (PAD)', 'deskripsi': 'Hasil usaha, swadaya, dan sumbangan', 'jumlah': 50_000_000},
            {'icon': '🏛️', 'nama': 'Dana Desa', 'deskripsi': 'Transfer dari APBN', 'jumlah': 500_000_000},
            {'icon': '📊', 'nama': 'Alokasi Dana Desa (ADD)', 'deskripsi': 'Bagian dari DAU Kabupaten', 'jumlah': 200_000_000},
            {'icon': '🎁', 'nama': 'Bantuan Kabupaten/Kota', 'deskripsi': 'Hibah dan bantuan lainnya', 'jumlah': 100_000_000},
        ],
        'belanja': [
            {'icon': '🛠️', 'nama': 'Belanja Pembangunan', 'deskripsi': 'Infrastruktur, gedung, jalan', 'jumlah': 400_000_000},
            {'icon': '👥', 'nama': 'Belanja Pemerintahan', 'deskripsi': 'Gaji Perangkat, ATK, operasional', 'jumlah': 200_000_000},
            {'icon': '🤝', 'nama': 'Belanja Pemberdayaan', 'deskripsi': 'Pelatihan, BUMDes, kegiatan warga', 'jumlah': 120_000_000},
            {'icon': '🎭', 'nama': 'Belanja Kegiatan', 'deskripsi': 'Event desa, perayaan hari besar', 'jumlah': 100_000_000},
        ],
        'pembiayaan': [
            {'icon': '📥', 'nama': 'Penerimaan Pembiayaan', 'deskripsi': 'Sisa lebih tahun anggaran sebelumnya', 'jumlah': 50_000_000},
            {'icon': '📤', 'nama': 'Pengeluaran Pembiayaan', 'deskripsi': 'Penyertaan modal BUMDes', 'jumlah': 20_000_000},
        ],
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
        tahun=datetime.now().year,
        site_name=desa_info['nama'],
        site_tagline=desa_info['tagline'],
        site_description=desa_info['deskripsi'],
        custom_pages=custom_pages,
        apbdes=apbdes,
    )


# ════════════════════════════════════════════════════════════════════════
# ── API: KOMENTAR BERITA ───────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["GET"])
def api_get_komentar(berita_id):
    """Ambil semua komentar untuk sebuah berita (JSON tree)"""
    flat = get_komentar_by_berita(berita_id)
    tree = build_comment_tree(flat)
    total = count_komentar_by_berita(berita_id)
    return jsonify({
        "success": True,
        "comments": tree,
        "total": total,
    })


@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["POST"])
def api_post_komentar(berita_id):
    """Post komentar baru atau reply"""
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


@public_bp.route("/api/berita/<int:berita_id>/komentar/<int:komentar_id>", methods=["DELETE"])
def api_delete_komentar(berita_id, komentar_id):
    """Hapus komentar (owner atau admin saja)"""
    user_id = session.get("user_id")
    user_role = session.get("user_role")

    if not user_id:
        return jsonify({"success": False, "error": "Login required"}), 401

    if user_role not in ['admin', 'dinas']:
        return jsonify({"success": False, "error": "Tidak memiliki hak hapus"}), 403

    komentar = get_komentar_by_id(komentar_id)
    if not komentar or komentar['berita_id'] != berita_id:
        return jsonify({"success": False, "error": "Komentar tidak ditemukan"}), 404

    # Admin/Dinas bisa hapus siapa saja; warga hanya hapusmilik sendiri
    if user_role not in ['admin', 'dinas'] and komentar['user_id'] != user_id:
        return jsonify({"success": False, "error": "Tidak memiliki hak hapus"}), 403

    delete_komentar(komentar_id)
    return jsonify({"success": True, "message": "Komentar dihapus"})
