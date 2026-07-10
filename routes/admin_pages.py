"""
Admin Pages Routes - Pages, Sejarah, Config
Part of admin.py refactoring
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated_function


def flash_error(msg):
    flash(msg, 'error')


# ════════════════════════════════════════════════════════════════════════
# ── CONFIG MANAGEMENT ──────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/config", methods=['GET', 'POST'])
@admin_required
def config():
    """Halaman konfigurasi website"""
    from models import get_all_config, update_config

    try:
        config_data = get_all_config()

        if request.method == 'POST':
            # Website Info
            update_config("website_nama", request.form.get('website_nama', ''))
            update_config("website_tagline", request.form.get('website_tagline', ''))
            update_config("website_deskripsi", request.form.get('website_deskripsi', ''))
            update_config("website_meta_description", request.form.get('website_meta_description', ''))

            # Berita Settings
            update_config("berita_tampil_di_beranda", request.form.get('berita_tampil_di_beranda', '6'))
            update_config("berita_unggulan_tampil", request.form.get('berita_unggulan_tampil', '3'))
            update_config("berita_carousel_stacks", request.form.get('berita_carousel_stacks', '2'))
            update_config("berita_tampil_di_halaman", request.form.get('berita_tampil_di_halaman', '12'))
            update_config("berita_tampilkan_views", '1' if request.form.get('berita_tampilkan_views') else '0')
            update_config("berita_tampilkan_tanggal", '1' if request.form.get('berita_tampilkan_tanggal') else '0')

            # Homepage Sections
            update_config("tampilkan_maps", '1' if request.form.get('tampilkan_maps') else '0')
            update_config("tampilkan_statistik", '1' if request.form.get('tampilkan_statistik') else '0')
            update_config("tampilkan_daftar_dusun", '1' if request.form.get('tampilkan_daftar_dusun') else '0')
            update_config("tampilkan_hero", '1' if request.form.get('tampilkan_hero') else '0')

            # Kontak
            update_config("kontak_whatsapp", request.form.get('kontak_whatsapp', ''))
            update_config("kontak_telepon", request.form.get('kontak_telepon', ''))
            update_config("kontak_email", request.form.get('kontak_email', ''))
            update_config("alamat_desa", request.form.get('alamat_desa', ''))

            # Sosial Media
            update_config("sosial_facebook", request.form.get('sosial_facebook', ''))
            update_config("sosial_instagram", request.form.get('sosial_instagram', ''))
            update_config("sosial_twitter", request.form.get('sosial_twitter', ''))
            update_config("sosial_tiktok", request.form.get('sosial_tiktok', ''))

            # Footer
            update_config("footer_copyright", request.form.get('footer_copyright', ''))

            flash('Pengaturan berhasil disimpan!', 'success')
            return redirect(url_for('admin.config'))

        return render_template("admin/config.html", config=config_data)
    except Exception as e:
        logger.error(f"Error in config page: {str(e)}")
        flash_error('Terjadi kesalahan saat menyimpan pengaturan')
        return redirect(url_for('admin.dashboard'))


# ════════════════════════════════════════════════════════════════════════
# ── PAGES MANAGEMENT ───────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/pages")
@admin_required
def pages():
    """Halaman list pages"""
    from models import get_all_pages

    try:
        all_pages = get_all_pages()
        return render_template("admin/pages.html", pages_list=all_pages)
    except Exception as e:
        logger.error(f"Error loading pages page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman pages')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/pages/add", methods=['GET', 'POST'])
@admin_required
def add_page_route():
    """Form tambah page"""
    from models import add_page, get_all_pages

    try:
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
            content = request.form.get('content', '').strip()
            icon = request.form.get('icon', '📄').strip()

            if not title or not slug:
                flash_error('Judul dan slug harus diisi!')
                return redirect(request.url)

            # Check if slug exists
            existing = get_all_pages()
            slugs = [p['slug'] for p in existing]
            if slug in slugs:
                flash_error('Slug sudah digunakan! Gunakan slug lain.')
                return redirect(request.url)

            result = add_page(title, slug, content, icon)
            if result:
                flash('Page berhasil dibuat!', 'success')
                return redirect(url_for('admin.pages'))
            else:
                flash_error('Gagal membuat page. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/add_page.html")
    except Exception as e:
        logger.error(f"Error in add_page_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form page')
        return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/edit/<int:page_id>", methods=['GET', 'POST'])
@admin_required
def edit_page_route(page_id):
    """Form edit page"""
    from models import get_page_by_id, update_page, get_all_pages

    try:
        page = get_page_by_id(page_id)
        if not page:
            flash_error('Page tidak ditemukan!')
            return redirect(url_for('admin.pages'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
            content = request.form.get('content', '').strip()
            icon = request.form.get('icon', '📄').strip()
            order_num = int(request.form.get('order_num', 0) or 0)
            active = 1 if request.form.get('active') else 0

            if not title or not slug:
                flash_error('Judul dan slug harus diisi!')
                return redirect(request.url)

            # Check if slug exists for other pages
            existing = get_all_pages()
            slugs = [p['slug'] for p in existing if p['id'] != page_id]
            if slug in slugs:
                flash_error('Slug sudah digunakan! Gunakan slug lain.')
                return redirect(request.url)

            result = update_page(page_id, title, slug, content, icon, order_num, active)
            if result:
                flash('Page berhasil diperbarui!', 'success')
                return redirect(url_for('admin.pages'))
            else:
                flash_error('Gagal memperbarui page. Silakan coba lagi.')
                return redirect(request.url)

        return render_template("admin/edit_page.html", page=page)
    except Exception as e:
        logger.error(f"Error in edit_page_route {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form page')
        return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/delete/<int:page_id>", methods=['POST'])
@admin_required
def delete_page_route(page_id):
    """Hapus page"""
    from models import delete_page

    try:
        result = delete_page(page_id)
        if result:
            flash('Page berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus page. Silakan coba lagi.')
    except Exception as e:
        logger.error(f"Error deleting page {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus page')
    return redirect(url_for('admin.pages'))


@admin_bp.route("/pages/toggle/<int:page_id>", methods=['POST'])
@admin_required
def toggle_page_route(page_id):
    """Toggle status aktif/nonaktif page"""
    from models import toggle_page_active

    try:
        result = toggle_page_active(page_id)
        if result:
            flash('Status page berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status page.')
    except Exception as e:
        logger.error(f"Error toggling page {page_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status page')
    return redirect(url_for('admin.pages'))


# ════════════════════════════════════════════════════════════════════════
# ── SEJARAH DESA MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/sejarah")
@admin_required
def sejarah():
    """Halaman list sejarah desa"""
    from models import get_all_sejarah

    try:
        all_sejarah = get_all_sejarah()
        return render_template("admin/sejarah.html", sejarah_list=all_sejarah)
    except Exception as e:
        logger.error(f"Error loading sejarah page: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman sejarah')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/sejarah/add", methods=['GET', 'POST'])
@admin_required
def add_sejarah_route():
    """Form tambah sejarah"""
    from models import add_sejarah

    if request.method == 'POST':
        try:
            judul = request.form.get('judul', '').strip()
            sub_judul = request.form.get('sub_judul', '').strip()
            konten = request.form.get('konten', '').strip()
            kategori = request.form.get('kategori', 'sejarah').strip()
            tahun_dari = request.form.get('tahun_dari', '')
            tahun_sampai = request.form.get('tahun_sampai', '')
            gambar_url = request.form.get('gambar_url', '').strip()
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            urutan = int(request.form.get('urutan', 0))

            if not judul:
                flash_error('Judul wajib diisi!')
                return redirect(request.url)

            # Parse tahun
            tahun_dari_int = int(tahun_dari) if tahun_dari else None
            tahun_sampai_int = int(tahun_sampai) if tahun_sampai else None

            result = add_sejarah(
                judul=judul,
                sub_judul=sub_judul,
                konten=konten,
                kategori=kategori,
                tahun_dari=tahun_dari_int,
                tahun_sampai=tahun_sampai_int,
                gambar_url=gambar_url,
                gambar_alt=gambar_alt,
                video_url=video_url,
                urutan=urutan
            )

            if result:
                flash('Entry sejarah berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.sejarah'))
            else:
                flash_error('Gagal menambahkan sejarah!')
        except Exception as e:
            logger.error(f"Error adding sejarah: {str(e)}")
            flash_error('Terjadi kesalahan saat menambahkan sejarah')

    return render_template("admin/add_sejarah.html")


@admin_bp.route("/sejarah/edit/<int:sejarah_id>", methods=['GET', 'POST'])
@admin_required
def edit_sejarah_route(sejarah_id):
    """Form edit sejarah"""
    from models import get_sejarah_by_id, update_sejarah

    sejarah = get_sejarah_by_id(sejarah_id)
    if not sejarah:
        flash_error('Sejarah tidak ditemukan!')
        return redirect(url_for('admin.sejarah'))

    if request.method == 'POST':
        try:
            judul = request.form.get('judul', '').strip()
            sub_judul = request.form.get('sub_judul', '').strip()
            konten = request.form.get('konten', '').strip()
            kategori = request.form.get('kategori', 'sejarah').strip()
            tahun_dari = request.form.get('tahun_dari', '')
            tahun_sampai = request.form.get('tahun_sampai', '')
            gambar_url = request.form.get('gambar_url', '').strip()
            gambar_alt = request.form.get('gambar_alt', '').strip()
            video_url = request.form.get('video_url', '').strip()
            aktif = 1 if request.form.get('aktif') else 0
            urutan = int(request.form.get('urutan', 0))

            if not judul:
                flash_error('Judul wajib diisi!')
                return redirect(request.url)

            tahun_dari_int = int(tahun_dari) if tahun_dari else None
            tahun_sampai_int = int(tahun_sampai) if tahun_sampai else None

            result = update_sejarah(
                sejarah_id=sejarah_id,
                judul=judul,
                sub_judul=sub_judul,
                konten=konten,
                kategori=kategori,
                tahun_dari=tahun_dari_int,
                tahun_sampai=tahun_sampai_int,
                gambar_url=gambar_url,
                gambar_alt=gambar_alt,
                video_url=video_url,
                aktif=aktif,
                urutan=urutan
            )

            if result:
                flash('Sejarah berhasil diupdate!', 'success')
                return redirect(url_for('admin.sejarah'))
            else:
                flash_error('Gagal update sejarah!')
        except Exception as e:
            logger.error(f"Error updating sejarah {sejarah_id}: {str(e)}")
            flash_error('Terjadi kesalahan saat update sejarah')

    return render_template("admin/edit_sejarah.html", sejarah=sejarah)


@admin_bp.route("/sejarah/delete/<int:sejarah_id>", methods=['POST'])
@admin_required
def delete_sejarah_route(sejarah_id):
    """Hapus sejarah"""
    from models import delete_sejarah

    try:
        result = delete_sejarah(sejarah_id)
        if result:
            flash('Sejarah berhasil dihapus!', 'success')
        else:
            flash_error('Gagal menghapus sejarah!')
    except Exception as e:
        logger.error(f"Error deleting sejarah {sejarah_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus sejarah')
    return redirect(url_for('admin.sejarah'))


@admin_bp.route("/sejarah/toggle/<int:sejarah_id>", methods=['POST'])
@admin_required
def toggle_sejarah_route(sejarah_id):
    """Toggle status aktif/nonaktif sejarah"""
    from models import toggle_sejarah_aktif

    try:
        result = toggle_sejarah_aktif(sejarah_id)
        if result:
            flash('Status sejarah berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status sejarah!')
    except Exception as e:
        logger.error(f"Error toggling sejarah {sejarah_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status sejarah')
    return redirect(url_for('admin.sejarah'))
