"""
Berita Routes - List, Detail, Komentar API
Part of public.py refactoring
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from datetime import datetime
from models import (
    get_all_berita, get_berita_by_id, get_config, get_all_pages,
    get_komentar_by_berita, build_comment_tree, create_komentar,
    delete_komentar, get_komentar_by_id, count_komentar_by_berita
)
from config import NAV_LINKS, MAPS_EMBED_URL, DUSUN_DATA
import logging

logger = logging.getLogger(__name__)
public_bp = Blueprint('public', __name__)


def get_desa_info_with_maps():
    info = get_desa_info()
    info['maps_embed_url'] = MAPS_EMBED_URL
    info['dusun'] = DUSUN_DATA
    return info


# ── Berita List ──────────────────────────────────────────────────────────

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


# ── API: KOMENTAR BERITA ─────────────────────────────────────────────────

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
