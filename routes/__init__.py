"""
Routes Package
Berisi semua route handlers yang dipisahkan berdasarkan modul

Struktur:
    __init__.py         - Blueprint exports
    public_*.py         - Public routes (auth, home, berita, pages, struktur, info, aduan)
    admin_*.py          - Admin routes (dashboard, berita, galeri, pages, struktur, umkm, potensi, pengumuman, aduan, accounts)
"""

# Public blueprints
from routes.public_auth import public_bp as public_auth_bp
from routes.public_home import public_bp as public_home_bp
from routes.public_berita import public_bp as public_berita_bp
from routes.public_pages import public_bp as public_pages_bp
from routes.public_struktur import public_bp as public_struktur_bp
from routes.public_info import public_bp as public_info_bp
from routes.public_aduan import public_bp as public_aduan_bp

# Admin blueprints
from routes.admin_dashboard import admin_bp as admin_dashboard_bp
from routes.admin_berita import admin_bp as admin_berita_bp
from routes.admin_galeri import admin_bp as admin_galeri_bp
from routes.admin_pages import admin_bp as admin_pages_bp
from routes.admin_struktur import admin_bp as admin_struktur_bp
from routes.admin_umkm import admin_bp as admin_umkm_bp
from routes.admin_potensi import admin_bp as admin_potensi_bp
from routes.admin_pengumuman import admin_bp as admin_pengumuman_bp
from routes.admin_aduan import admin_bp as admin_aduan_bp
from routes.admin_accounts import admin_bp as admin_accounts_bp
from routes.admin_rtrw import admin_rtrw_bp

# Legacy imports (for backward compatibility)
from routes.public import public_bp
from routes.admin import admin_bp

__all__ = [
    # Legacy (original monolithic files - kept for compatibility)
    'public_bp',
    'admin_bp',
    # New modular public blueprints
    'public_auth_bp',
    'public_home_bp',
    'public_berita_bp',
    'public_pages_bp',
    'public_struktur_bp',
    'public_info_bp',
    'public_aduan_bp',
    # New modular admin blueprints
    'admin_dashboard_bp',
    'admin_berita_bp',
    'admin_galeri_bp',
    'admin_pages_bp',
    'admin_struktur_bp',
    'admin_umkm_bp',
    'admin_potensi_bp',
    'admin_pengumuman_bp',
    'admin_aduan_bp',
    'admin_accounts_bp',
]
