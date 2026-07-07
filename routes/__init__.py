"""
Routes Package
Berisi semua route handlers yang dipisahkan berdasarkan modul
"""

from routes.public import public_bp
from routes.admin import admin_bp

__all__ = ['public_bp', 'admin_bp']
