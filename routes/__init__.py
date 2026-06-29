"""
Routes Package
Berisi semua route handlers yang dipisahkan berdasarkan modul
"""

from routes.public import public_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.dinas import dinas_bp

__all__ = ['public_bp', 'admin_bp', 'user_bp', 'dinas_bp']
