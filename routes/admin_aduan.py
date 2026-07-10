"""
Admin Aduan, Program Kerja & Agenda Routes
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
# ── KRITIK DAN SARAN MANAGEMENT ──────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/kritik-saran")
@admin_required
def kritik_saran():
    """Halaman daftar kritik dan saran"""
    from models import get_all_kritik_saran, get_kritik_saran_stats

    try:
        kritik_saran_list = get_all_kritik_saran(include_read=True)
        stats = get_kritik_saran_stats()
        
        return render_template(
            "admin/kritik_saran.html",
            kritik_saran_list=kritik_saran_list,
            stats=stats,
        )
    except Exception as e:
        logger.error(f"Error loading kritik_saran: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/kritik-saran/read/<int:ks_id>", methods=['POST'])
@admin_required
def read_kritik_saran(ks_id):
    """Tandai kritik/saran sudah dibaca"""
    from models import mark_kritik_saran_read

    try:
        result = mark_kritik_saran_read(ks_id)
        if result:
            flash('Kritik/saran ditandai sudah dibaca', 'success')
        else:
            flash_error('Gagal menandai kritik/saran')
    except Exception as e:
        logger.error(f"Error marking kritik_saran read {ks_id}: {str(e)}")
        flash_error('Terjadi kesalahan')
    return redirect(url_for('admin.kritik_saran'))


@admin_bp.route("/kritik-saran/delete/<int:ks_id>", methods=['POST'])
@admin_required
def delete_kritik_saran_route(ks_id):
    """Hapus kritik/saran"""
    from models import delete_kritik_saran

    try:
        result = delete_kritik_saran(ks_id)
        if result:
            flash('Kritik/saran berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus kritik/saran')
    except Exception as e:
        logger.error(f"Error deleting kritik_saran {ks_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.kritik_saran'))


# ════════════════════════════════════════════════════════════════════════
# ── ADUAN MANAGEMENT ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/aduan")
@admin_required
def aduan():
    """Halaman daftar aduan"""
    from models import get_all_aduan, get_aduan_stats

    try:
        aduan_list = get_all_aduan()
        stats = get_aduan_stats()
        
        # Filter
        status_filter = request.args.get('status', '')
        if status_filter:
            aduan_list = [a for a in aduan_list if a.get('status') == status_filter]
        
        return render_template(
            "admin/aduan.html",
            aduan_list=aduan_list,
            stats=stats,
            status_filter=status_filter,
        )
    except Exception as e:
        logger.error(f"Error loading aduan: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/aduan/<int:aduan_id>", methods=['GET', 'POST'])
@admin_required
def aduan_detail(aduan_id):
    """Detail aduan dan form respon"""
    from models import get_aduan_by_id, respond_aduan, update_aduan

    try:
        item = get_aduan_by_id(aduan_id)
        if not item:
            flash_error('Aduan tidak ditemukan!')
            return redirect(url_for('admin.aduan'))
        
        if request.method == 'POST':
            action = request.form.get('action', '')
            
            if action == 'respond':
                catatan = request.form.get('catatan', '').strip()
                logger.info(f"[ADUAN] respond action: aduan_id={aduan_id}, catatan length={len(catatan)}")
                if catatan:
                    result = respond_aduan(aduan_id, catatan, session.get('user_id'))
                    if result:
                        flash('Tanggapan berhasil dikirim!', 'success')
                    else:
                        logger.warning(f"[ADUAN] respond_aduan returned False for aduan_id={aduan_id}")
                        flash_error('Gagal mengirim tanggapan.')
                else:
                    flash_error('Catatan/tanggapan wajib diisi!')
            
            elif action == 'update_status':
                logger.info(f"[ADUAN] update_status action: aduan_id={aduan_id}")
                status = request.form.get('status', '')
                catatan = request.form.get('catatan', '').strip()
                judul = request.form.get('judul', item['judul'])
                isi = request.form.get('deskripsi', item.get('isi', ''))
                kategori = request.form.get('kategori', item['kategori'])
                lokasi = request.form.get('lokasi', item['lokasi'] or '')
                
                result = update_aduan(aduan_id, judul, isi, kategori, lokasi, status, None, catatan)
                if result:
                    flash('Status aduan berhasil diperbarui!', 'success')
                else:
                    logger.warning(f"[ADUAN] update_aduan returned False for aduan_id={aduan_id}")
                    flash_error('Gagal memperbarui status.')
            
            return redirect(url_for('admin.aduan_detail', aduan_id=aduan_id))
        
        return render_template("admin/aduan_detail.html", item=item)
    except Exception as e:
        logger.error(f"Error loading aduan detail {aduan_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.aduan'))


@admin_bp.route("/aduan/delete/<int:aduan_id>", methods=['POST'])
@admin_required
def delete_aduan_route(aduan_id):
    """Hapus aduan"""
    from models import delete_aduan

    try:
        result = delete_aduan(aduan_id)
        if result:
            flash('Aduan berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus aduan')
    except Exception as e:
        logger.error(f"Error deleting aduan {aduan_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.aduan'))


# ════════════════════════════════════════════════════════════════════════
# ── PROGRAM KERJA MANAGEMENT ─────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/program-kerja")
@admin_required
def program_kerja():
    """Halaman manajemen program kerja"""
    from models import get_all_program_kerja

    try:
        program_list = get_all_program_kerja()
        
        # Filter
        tahun_filter = request.args.get('tahun', type=int)
        if tahun_filter:
            program_list = [p for p in program_list if p.get('tahun') == tahun_filter]
        
        # Group by status
        grouped = {'rencana': [], 'berlangsung': [], 'selesai': []}
        for p in program_list:
            status = p.get('status', 'berlangsung')
            if status in grouped:
                grouped[status].append(p)
        
        return render_template(
            "admin/program_kerja.html",
            program_list=program_list,
            grouped=grouped,
            tahun_filter=tahun_filter,
        )
    except Exception as e:
        logger.error(f"Error loading program_kerja: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/program-kerja/add", methods=['GET', 'POST'])
@admin_required
def add_program_kerja_route():
    """Form tambah program kerja"""
    from models import add_program_kerja
    from datetime import datetime
    
    try:
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'pembangunan')
            tahun = request.form.get('tahun', datetime.now().year, type=int)
            target = request.form.get('target', '').strip()
            realiasi = request.form.get('realiasi', '').strip()
            anggaran = request.form.get('anggaran', '').strip()
            icon = request.form.get('icon', '📋').strip()
            status = request.form.get('status', 'berlangsung')
            
            if not judul:
                flash_error('Judul program kerja harus diisi!')
                return redirect(request.url)
            
            result = add_program_kerja(nama=judul, deskripsi=deskripsi, kategori=kategori, tahun=tahun, target=target, realiasi=realiasi, anggaran=anggaran, icon=icon, status=status)
            logger.info(f"[PROGRAM_KERJA] add_program_kerja called with: judul={judul}, kategori={kategori}, tahun={tahun}, status={status}")
            if result:
                flash('Program kerja berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.program_kerja'))
            else:
                logger.warning(f"[PROGRAM_KERJA] add_program_kerja returned False for judul={judul}")
                flash_error('Gagal menambahkan program kerja.')
                return redirect(request.url)
        
        return render_template("admin/add_program_kerja.html")
    except Exception as e:
        logger.error(f"Error in add_program_kerja_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/edit/<int:program_id>", methods=['GET', 'POST'])
@admin_required
def edit_program_kerja_route(program_id):
    """Form edit program kerja"""
    from models import get_program_kerja_by_id, update_program_kerja
    from datetime import datetime
    
    try:
        item = get_program_kerja_by_id(program_id)
        if not item:
            flash_error('Program kerja tidak ditemukan!')
            return redirect(url_for('admin.program_kerja'))
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'pembangunan')
            tahun = request.form.get('tahun', datetime.now().year, type=int)
            target = request.form.get('target', '').strip()
            realiasi = request.form.get('realiasi', '').strip()
            anggaran = request.form.get('anggaran', '').strip()
            icon = request.form.get('icon', '📋').strip()
            status = request.form.get('status', 'berlangsung')
            aktif = 1 if request.form.get('aktif') else 0
            urutan = request.form.get('urutan', 0, type=int)
            
            if not judul:
                flash_error('Judul program kerja harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[PROGRAM_KERJA] update_program_kerja called: id={program_id}, nama={judul}")
            result = update_program_kerja(program_id, nama=judul, deskripsi=deskripsi, kategori=kategori, tahun=tahun, target=target, realiasi=realiasi, anggaran=anggaran, icon=icon, status=status, aktif=aktif, urutan=urutan)
            if result:
                flash('Program kerja berhasil diperbarui!', 'success')
                return redirect(url_for('admin.program_kerja'))
            else:
                logger.warning(f"[PROGRAM_KERJA] update_program_kerja returned False for id={program_id}")
                flash_error('Gagal memperbarui program kerja.')
                return redirect(request.url)
        
        return render_template("admin/edit_program_kerja.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_program_kerja_route {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/delete/<int:program_id>", methods=['POST'])
@admin_required
def delete_program_kerja_route(program_id):
    """Hapus program kerja"""
    from models import delete_program_kerja

    try:
        result = delete_program_kerja(program_id)
        if result:
            flash('Program kerja berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus program kerja')
    except Exception as e:
        logger.error(f"Error deleting program_kerja {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.program_kerja'))


@admin_bp.route("/program-kerja/toggle/<int:program_id>", methods=['POST'])
@admin_required
def toggle_program_kerja_route(program_id):
    """Toggle status aktif program kerja"""
    from models import toggle_program_kerja_aktif

    try:
        result = toggle_program_kerja_aktif(program_id)
        if result:
            flash('Status program kerja berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status program kerja.')
    except Exception as e:
        logger.error(f"Error toggling program_kerja {program_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('admin.program_kerja'))


# ════════════════════════════════════════════════════════════════════════
# ── AGENDA MANAGEMENT ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════

@admin_bp.route("/agenda")
@admin_required
def agenda():
    """Halaman manajemen agenda"""
    from models import get_all_agenda

    try:
        agenda_list = get_all_agenda()
        
        # Filter
        tahun_filter = request.args.get('tahun', type=int)
        status_filter = request.args.get('status', '')
        
        if tahun_filter:
            agenda_list = [a for a in agenda_list if a.get('tanggal_mulai') and str(tahun_filter) in str(a['tanggal_mulai'])]
        if status_filter:
            agenda_list = [a for a in agenda_list if a.get('status') == status_filter]
        
        return render_template(
            "admin/agenda.html",
            agenda_list=agenda_list,
            tahun_filter=tahun_filter,
            status_filter=status_filter,
        )
    except Exception as e:
        logger.error(f"Error loading agenda: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat halaman')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route("/agenda/add", methods=['GET', 'POST'])
@admin_required
def add_agenda_route():
    """Form tambah agenda"""
    from models import add_agenda
    
    try:
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'kegiatan')
            tanggal_mulai = request.form.get('tanggal_mulai', '')
            tanggal_selesai = request.form.get('tanggal_selesai', '')
            waktu = request.form.get('waktu', '').strip()
            lokasi = request.form.get('lokasi', '').strip()
            icon = request.form.get('icon', '📅').strip()
            penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
            peserta = request.form.get('peserta', '').strip()
            status = request.form.get('status', 'akan_datang')
            
            if not judul or not tanggal_mulai:
                flash_error('Judul dan Tanggal Mulai harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[AGENDA] add_agenda called: judul={judul}, tanggal={tanggal_mulai}")
            result = add_agenda(judul=judul, deskripsi=deskripsi, kategori=kategori, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai or None, waktu=waktu, lokasi=lokasi, icon=icon, penanggung_jawab=penanggung_jawab, peserta=peserta, status=status)
            if result:
                flash('Agenda berhasil ditambahkan!', 'success')
                return redirect(url_for('admin.agenda'))
            else:
                logger.warning(f"[AGENDA] add_agenda returned False for judul={judul}")
                flash_error('Gagal menambahkan agenda.')
                return redirect(request.url)
        
        return render_template("admin/add_agenda.html")
    except Exception as e:
        logger.error(f"Error in add_agenda_route: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/edit/<int:agenda_id>", methods=['GET', 'POST'])
@admin_required
def edit_agenda_route(agenda_id):
    """Form edit agenda"""
    from models import get_agenda_by_id, update_agenda
    
    try:
        item = get_agenda_by_id(agenda_id)
        if not item:
            flash_error('Agenda tidak ditemukan!')
            return redirect(url_for('admin.agenda'))
        
        if request.method == 'POST':
            judul = request.form.get('judul', '').strip()
            deskripsi = request.form.get('deskripsi', '').strip()
            kategori = request.form.get('kategori', 'kegiatan')
            tanggal_mulai = request.form.get('tanggal_mulai', '')
            tanggal_selesai = request.form.get('tanggal_selesai', '')
            waktu = request.form.get('waktu', '').strip()
            lokasi = request.form.get('lokasi', '').strip()
            icon = request.form.get('icon', '📅').strip()
            penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
            peserta = request.form.get('peserta', '').strip()
            status = request.form.get('status', 'akan_datang')
            aktif = 1 if request.form.get('aktif') else 0
            urutan = request.form.get('urutan', 0, type=int)
            
            if not judul or not tanggal_mulai:
                flash_error('Judul dan Tanggal Mulai harus diisi!')
                return redirect(request.url)
            
            logger.info(f"[AGENDA] update_agenda called: id={agenda_id}, judul={judul}")
            result = update_agenda(agenda_id, judul=judul, deskripsi=deskripsi, kategori=kategori, tanggal_mulai=tanggal_mulai, tanggal_selesai=tanggal_selesai or None, waktu=waktu, lokasi=lokasi, icon=icon, penanggung_jawab=penanggung_jawab, peserta=peserta, status=status, aktif=aktif, urutan=urutan)
            if result:
                flash('Agenda berhasil diperbarui!', 'success')
                return redirect(url_for('admin.agenda'))
            else:
                logger.warning(f"[AGENDA] update_agenda returned False for id={agenda_id}")
                flash_error('Gagal memperbarui agenda.')
                return redirect(request.url)
        
        return render_template("admin/edit_agenda.html", item=item)
    except Exception as e:
        logger.error(f"Error in edit_agenda_route {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat memuat form')
        return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/delete/<int:agenda_id>", methods=['POST'])
@admin_required
def delete_agenda_route(agenda_id):
    """Hapus agenda"""
    from models import delete_agenda

    try:
        result = delete_agenda(agenda_id)
        if result:
            flash('Agenda berhasil dihapus', 'success')
        else:
            flash_error('Gagal menghapus agenda')
    except Exception as e:
        logger.error(f"Error deleting agenda {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat menghapus')
    return redirect(url_for('admin.agenda'))


@admin_bp.route("/agenda/toggle/<int:agenda_id>", methods=['POST'])
@admin_required
def toggle_agenda_route(agenda_id):
    """Toggle status aktif agenda"""
    from models import toggle_agenda_aktif

    try:
        result = toggle_agenda_aktif(agenda_id)
        if result:
            flash('Status agenda berhasil diubah!', 'success')
        else:
            flash_error('Gagal mengubah status agenda.')
    except Exception as e:
        logger.error(f"Error toggling agenda {agenda_id}: {str(e)}")
        flash_error('Terjadi kesalahan saat mengubah status')
    return redirect(url_for('admin.agenda'))
