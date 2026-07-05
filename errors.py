"""
Error Handlers Module
Berisi semua error handling terpusat untuk aplikasi Flask

Penggunaan:
    from errors import (
        # Custom Exceptions
        AppError, DatabaseError, ValidationError, NotFoundError, UnauthorizedError, ForbiddenError,

        # Error Response Helpers
        flash_error, json_error_response, json_success_response,

        # Route Decorators
        admin_required, dinas_required, warga_required, login_required, require_role,

        # Validation Helpers
        validate_required, validate_nik, validate_email, validate_password,

        # Error Page Rendering
        render_error_page,

        # Safe Route Handler
        safe_handler,
    )

Contoh:
    # Use decorators for role protection
    @admin_required
    def admin_only_route():
        pass

    # Wrap route dengan safe_handler
    @safe_handler(fallback_url='/admin/dashboard')
    def my_route():
        # route code here
        pass
"""

import sqlite3
import functools
import logging
from flask import flash, redirect, url_for, request, jsonify, render_template

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# ── CUSTOM EXCEPTIONS ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

class AppError(Exception):
    """Base exception untuk semua error aplikasi"""
    def __init__(self, message: str, status_code: int = 400, category: str = "error"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.category = category

    def __str__(self):
        return self.message


class DatabaseError(AppError):
    """Error terkait database"""
    def __init__(self, message: str = "Terjadi kesalahan database", status_code: int = 500, original_error: Exception = None):
        super().__init__(message, status_code, "error")
        self.db_error = True
        self.original_error = original_error


class ValidationError(AppError):
    """Error validasi input"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code, "error")


class NotFoundError(AppError):
    """Error resource tidak ditemukan"""
    def __init__(self, message: str = "Resource tidak ditemukan", status_code: int = 404):
        super().__init__(message, status_code, "error")


class UnauthorizedError(AppError):
    """Error unauthorized access"""
    def __init__(self, message: str = "Anda tidak memiliki akses", status_code: int = 401):
        super().__init__(message, status_code, "error")


class ForbiddenError(AppError):
    """Error forbidden access"""
    def __init__(self, message: str = "Akses ditolak", status_code: int = 403):
        super().__init__(message, status_code, "error")


class FileError(AppError):
    """Error terkait file operations"""
    def __init__(self, message: str = "Terjadi kesalahan file", status_code: int = 500):
        super().__init__(message, status_code, "error")


class APIError(AppError):
    """Error untuk API endpoints"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        super().__init__(message, status_code, "error")
        self.error_code = error_code


# ════════════════════════════════════════════════════════════════════════════
# ── ERROR RESPONSE HELPERS ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def flash_error(message: str, category: str = "error") -> None:
    """
    Helper untuk flash error message.

    Args:
        message: Pesan error
        category: Kategori flash ('error', 'success', 'info', 'warning')
    """
    valid_categories = ["error", "success", "info", "warning"]
    if category not in valid_categories:
        category = "error"
    flash(message, category)


def json_error_response(
    message: str,
    status_code: int = 400,
    error_code: str = None,
    extra: dict = None
) -> tuple:
    """
    Generate JSON error response.

    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code untuk programmatic handling
        extra: Extra data untuk include dalam response

    Returns:
        tuple: (json_response, status_code)
    """
    response = {
        "success": False,
        "error": message,
        "status_code": status_code
    }
    if error_code:
        response["error_code"] = error_code
    if extra:
        response.update(extra)
    return jsonify(response), status_code


def json_success_response(
    message: str = None,
    data: any = None,
    status_code: int = 200
) -> tuple:
    """
    Generate JSON success response.

    Args:
        message: Success message
        data: Data untuk include dalam response
        status_code: HTTP status code

    Returns:
        tuple: (json_response, status_code)
    """
    response = {
        "success": True
    }
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def xml_http_request_error_response(
    message: str,
    status_code: int = 400
) -> tuple:
    """
    Generate XMLHTTPRequest/AJAX error response.

    Args:
        message: Error message
        status_code: HTTP status code

    Returns:
        tuple: (json_response, status_code)
    """
    return json_error_response(message, status_code)


# ════════════════════════════════════════════════════════════════════════════
# ── DATABASE ERROR HANDLERS ────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def handle_db_error(
    error: Exception,
    operation: str = "database operation",
    rollback_conn: sqlite3.Connection = None
) -> tuple:
    """
    Handle database error dengan logging dan response yang sesuai.

    Args:
        error: Exception yang terjadi
        operation: Deskripsi operasi yang gagal (untuk log message)
        rollback_conn: Connection untuk di-rollback jika perlu

    Returns:
        Tuple (success: bool, message: str)
    """
    # Log error
    logger.error(f"Database Error ({operation}): {str(error)}")

    # Rollback jika ada connection
    if rollback_conn:
        try:
            rollback_conn.rollback()
        except:
            pass

    # Determine error type
    error_str = str(error).lower()

    if "unique constraint" in error_str or "duplicate" in error_str:
        return False, "Data sudah ada! Tidak boleh duplikat."
    elif "foreign key constraint" in error_str:
        return False, "Data tidak dapat dihapus karena masih digunakan."
    elif "not null constraint" in error_str:
        return False, "Field wajib diisi tidak boleh kosong."
    elif "check constraint" in error_str:
        return False, "Data tidak memenuhi syarat validasi."
    elif "no such table" in error_str:
        return False, "Tabel database belum tersedia. Silakan hubungi administrator."
    elif "locked" in error_str:
        return False, "Database sedang digunakan. Silakan coba lagi."
    else:
        return False, "Terjadi kesalahan database. Silakan coba lagi."


def get_db_error_message(error: Exception) -> str:
    """
    Get user-friendly error message dari exception.

    Args:
        error: Exception yang terjadi

    Returns:
        str: User-friendly error message
    """
    error_str = str(error).lower()

    if "unique constraint" in error_str or "duplicate" in error_str:
        return "Data sudah ada! Tidak boleh duplikat."
    elif "foreign key constraint" in error_str:
        return "Data tidak dapat dihapus karena masih digunakan."
    elif "not null constraint" in error_str:
        return "Field wajib diisi tidak boleh kosong."
    elif "check constraint" in error_str:
        return "Data tidak memenuhi syarat validasi."
    elif "no such table" in error_str:
        return "Tabel database belum tersedia."
    elif "locked" in error_str:
        return "Database sedang digunakan. Silakan coba lagi."
    elif "syntax error" in error_str:
        return "Format data tidak valid."
    else:
        return "Terjadi kesalahan database. Silakan coba lagi."


def db_error_handler(func):
    """
    Decorator untuk handle database errors pada fungsi.

    Usage:
        @db_error_handler
        def get_user(user_id):
            conn = get_db_connection()
            return conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    Note:
        Untuk use case yang lebih advanced, gunakan decorators dari database.py
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError as e:
            success, message = handle_db_error(e, func.__name__)
            raise DatabaseError(message)
        except sqlite3.OperationalError as e:
            logger.error(f"SQL Operational Error in {func.__name__}: {str(e)}")
            raise DatabaseError("Terjadi kesalahan pada operasi database.")
        except sqlite3.DatabaseError as e:
            logger.error(f"Database Error in {func.__name__}: {str(e)}")
            raise DatabaseError("Terjadi kesalahan koneksi database.")
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Unexpected Error in {func.__name__}: {str(e)}")
            raise DatabaseError(f"Terjadi kesalahan tidak terduga: {str(e)}", original_error=e)
    return wrapper


# ════════════════════════════════════════════════════════════════════════════
# ── ROUTE PROTECTION DECORATORS ───────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def require_role(*allowed_roles):
    """
    Decorator untuk proteksi route berdasarkan role.

    Usage:
        @require_role('admin', 'dinas')
        def admin_dinas_route():
            pass

    Args:
        *allowed_roles: Role yang diizinkan ('admin', 'dinas', 'penduduk')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from flask import session

            if not session.get('user_logged_in'):
                flash_error('Silakan login terlebih dahulu.', 'error')
                return redirect(url_for('public.login'))

            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                flash_error('Anda tidak memiliki akses ke halaman ini.', 'error')
                # Redirect berdasarkan role
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'dinas':
                    return redirect(url_for('dinas.dashboard'))
                elif user_role == 'penduduk':
                    return redirect(url_for('user.dashboard'))
                else:
                    return redirect(url_for('public.index'))

            return func(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(func):
    """
    Decorator untuk proteksi route admin only.

    Usage:
        @admin_required
        def admin_dashboard():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import session

        if not session.get('user_logged_in'):
            flash_error('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('public.login'))

        if session.get('user_role') != 'admin':
            flash_error('Halaman ini hanya untuk Administrator.', 'error')
            return redirect(url_for('public.index'))

        return func(*args, **kwargs)
    return wrapper


def dinas_required(func):
    """
    Decorator untuk proteksi route dinas/admin.

    Usage:
        @dinas_required
        def verify_user_route():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import session

        if not session.get('user_logged_in'):
            flash_error('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('public.login'))

        if session.get('user_role') not in ['admin', 'dinas']:
            flash_error('Halaman ini hanya untuk petugas dinas.', 'error')
            return redirect(url_for('public.index'))

        return func(*args, **kwargs)
    return wrapper


def warga_required(func):
    """
    Decorator untuk proteksi route warga/penduduk.

    Usage:
        @warga_required
        def submit_permohonan():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import session

        if not session.get('user_logged_in'):
            flash_error('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('public.login') + '#warga')

        if session.get('user_role') != 'penduduk':
            flash_error('Halaman ini hanya untuk warga.', 'error')
            return redirect(url_for('public.index'))

        return func(*args, **kwargs)
    return wrapper


def login_required(func):
    """
    Decorator untuk proteksi route - user harus login (semua role).

    Usage:
        @login_required
        def any_logged_in_route():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import session

        if not session.get('user_logged_in'):
            flash_error('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('public.login'))

        return func(*args, **kwargs)
    return wrapper


# ════════════════════════════════════════════════════════════════════════════
# ── VALIDATION HELPERS ────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def validate_required(data: dict, required_fields: list, prefix: str = "") -> tuple:
    """
    Validasi field yang wajib ada.

    Args:
        data: Dictionary data
        required_fields: List nama field yang wajib ada
        prefix: Prefix untuk error message

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    if missing:
        field_names = ", ".join(missing)
        if prefix:
            return False, f"{prefix}: {field_names} wajib diisi."
        return False, f"Field berikut wajib diisi: {field_names}"

    return True, ""


def validate_nik(nik: str) -> tuple:
    """
    Validasi NIK (16 digit angka).

    Args:
        nik: NIK string

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not nik:
        return False, "NIK tidak boleh kosong."

    if not nik.isdigit():
        return False, "NIK harus berisi angka saja."

    if len(nik) != 16:
        return False, "NIK harus 16 digit."

    return True, ""


def validate_email(email: str) -> tuple:
    """
    Validasi format email.

    Args:
        email: Email string

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not email:
        return True, ""  # Email optional

    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format email tidak valid."

    return True, ""


def validate_password(password: str, min_length: int = 6) -> tuple:
    """
    Validasi password.

    Args:
        password: Password string
        min_length: Minimum panjang password

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Password tidak boleh kosong."

    if len(password) < min_length:
        return False, f"Password minimal {min_length} karakter."

    return True, ""


def validate_phone(phone: str) -> tuple:
    """
    Validasi format nomor telepon Indonesia.

    Args:
        phone: Nomor telepon string

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not phone:
        return True, ""  # Phone optional

    import re
    # Accept formats: 08xx, +628xx, 628xx, with or without dashes/spaces
    pattern = r'^(\+?62|0)[2-9][0-9]{7,11}$'
    cleaned = re.sub(r'[\s\-]', '', phone)
    if not re.match(pattern, cleaned):
        return False, "Format nomor telepon tidak valid."

    return True, ""


def validate_url(url: str, required: bool = False) -> tuple:
    """
    Validasi format URL.

    Args:
        url: URL string
        required: Apakah URL wajib ada

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    if not url:
        if required:
            return False, "URL wajib diisi."
        return True, ""

    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        return False, "Format URL tidak valid."

    return True, ""


def validate_integer(value: any, field_name: str = "nilai", min_val: int = None, max_val: int = None) -> tuple:
    """
    Validasi integer dengan range opsional.

    Args:
        value: Nilai untuk divalidasi
        field_name: Nama field untuk error message
        min_val: Nilai minimum
        max_val: Nilai maksimum

    Returns:
        Tuple (is_valid: bool, error_message: str)
    """
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} harus berupa angka."

    if min_val is not None and int_val < min_val:
        return False, f"{field_name} minimal adalah {min_val}."

    if max_val is not None and int_val > max_val:
        return False, f"{field_name} maksimal adalah {max_val}."

    return True, ""


# ════════════════════════════════════════════════════════════════════════════
# ── ERROR PAGE TEMPLATES ──────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def render_error_page(
    error_code: int,
    title: str = None,
    message: str = None,
    back_url: str = None,
    back_text: str = "Kembali"
) -> tuple:
    """
    Render error page dengan template统一.

    Args:
        error_code: HTTP status code
        title: Judul error
        message: Pesan error
        back_url: URL untuk tombol kembali (default: homepage)
        back_text: Text untuk tombol kembali

    Returns:
        Response tuple (rendered_html, status_code)
    """
    error_pages = {
        400: ("400 Bad Request", "Permintaan tidak valid"),
        401: ("401 Unauthorized", "Anda harus login terlebih dahulu"),
        403: ("403 Forbidden", "Anda tidak memiliki akses ke halaman ini"),
        404: ("404 Not Found", "Halaman yang Anda cari tidak ditemukan"),
        405: ("405 Method Not Allowed", "Metode request tidak diizinkan"),
        500: ("500 Internal Server Error", "Terjadi kesalahan pada server"),
        503: ("503 Service Unavailable", "Layanan sedang tidak tersedia"),
    }

    default_title, default_subtitle = error_pages.get(error_code, (str(error_code), "Terjadi kesalahan"))

    return render_template(
        "error.html",
        error_code=error_code,
        title=title or default_title,
        message=message or default_subtitle,
        subtitle=default_subtitle,
        back_url=back_url or "/",
        back_text=back_text,
    ), error_code


# ════════════════════════════════════════════════════════════════════════════
# ── SAFE ROUTE HANDLER ────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def safe_handler(func=None, fallback_url: str = None, error_message: str = "Terjadi kesalahan"):
    """
    Decorator untuk handle semua error dalam route.
    Mendukung both callable dan keyword-only arguments.

    Usage:
        # Basic usage
        @safe_handler
        def my_route():
            pass

        # With fallback URL
        @safe_handler(fallback_url='/admin/dashboard')
        def my_route():
            pass

        # With custom error message
        @safe_handler(error_message='Custom error message')
        def my_route():
            pass

    Args:
        func: Function being decorated (when used without parentheses)
        fallback_url: URL untuk redirect saat error
        error_message: Default error message
    """
    # Handle case where decorator is used without parentheses
    if func is not None:
        # @safe_handler without arguments
        return _safe_handler_wrapper(func, fallback_url=None, error_message="Terjadi kesalahan")

    # Handle case where decorator is used with arguments
    def decorator(f):
        return _safe_handler_wrapper(f, fallback_url, error_message)

    return decorator


def _safe_handler_wrapper(func, fallback_url, error_message):
    """Internal wrapper function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except NotFoundError as e:
            logger.warning(f"NotFoundError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 404)
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(404, "Tidak Ditemukan", str(e))

        except UnauthorizedError as e:
            logger.warning(f"UnauthorizedError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 401)
            return redirect(url_for('public.login'))

        except ForbiddenError as e:
            logger.warning(f"ForbiddenError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 403)
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(403, "Akses Ditolak", str(e))

        except ValidationError as e:
            logger.warning(f"ValidationError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 400)
            return redirect(request.url or fallback_url or '/')

        except DatabaseError as e:
            logger.error(f"DatabaseError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 500, error_code="DATABASE_ERROR")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(500, "Kesalahan Database", str(e))

        except FileError as e:
            logger.error(f"FileError in {func.__name__}: {str(e)}")
            flash_error(str(e), "error")
            if request.is_json:
                return json_error_response(str(e), 500, error_code="FILE_ERROR")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(500, "Kesalahan File", str(e))

        except APIError as e:
            logger.warning(f"APIError in {func.__name__}: {str(e)}")
            if request.is_json:
                return json_error_response(str(e), e.status_code, error_code=e.error_code)
            flash_error(str(e), "error")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(e.status_code, "API Error", str(e))

        except AppError as e:
            logger.warning(f"AppError in {func.__name__}: {str(e)}")
            flash_error(str(e), e.category)
            if request.is_json:
                return json_error_response(str(e), e.status_code)
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(e.status_code, "Error", str(e))

        except sqlite3.IntegrityError as e:
            msg = get_db_error_message(e)
            logger.error(f"IntegrityError in {func.__name__}: {str(e)}")
            flash_error(msg, "error")
            if request.is_json:
                return json_error_response(msg, 400, error_code="INTEGRITY_ERROR")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(400, "Validasi Gagal", msg)

        except sqlite3.OperationalError as e:
            logger.error(f"OperationalError in {func.__name__}: {str(e)}")
            flash_error("Terjadi kesalahan database. Silakan coba lagi.", "error")
            if request.is_json:
                return json_error_response("Terjadi kesalahan database", 500, error_code="OPERATIONAL_ERROR")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(500, "Kesalahan Database", "Terjadi kesalahan pada operasi database.")

        except Exception as e:
            logger.error(f"Unexpected Error in {func.__name__}: {str(e)}", exc_info=True)
            flash_error("Terjadi kesalahan tidak terduga. Silakan hubungi administrator.", "error")
            if request.is_json:
                return json_error_response("Internal server error", 500, error_code="INTERNAL_ERROR")
            if fallback_url:
                return redirect(fallback_url)
            return render_error_page(500, "Kesalahan Server", "Terjadi kesalahan tidak terduga.")

    return wrapper


# ════════════════════════════════════════════════════════════════════════════
# ── API HELPER DECORATORS ────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def api_handler(func):
    """
    Decorator untuk API routes dengan error handling yang konsisten.

    Usage:
        @api_handler
        def my_api_route():
            return jsonify({"data": ...})

    Note:
        Automatically handles JSON responses dan error formatting
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            return json_error_response(str(e), 404)
        except UnauthorizedError as e:
            return json_error_response(str(e), 401)
        except ForbiddenError as e:
            return json_error_response(str(e), 403)
        except ValidationError as e:
            return json_error_response(str(e), 400)
        except DatabaseError as e:
            logger.error(f"DatabaseError in API {func.__name__}: {str(e)}")
            return json_error_response(str(e), 500, error_code="DATABASE_ERROR")
        except APIError as e:
            return json_error_response(str(e), e.status_code, error_code=e.error_code)
        except Exception as e:
            logger.error(f"Unexpected Error in API {func.__name__}: {str(e)}")
            return json_error_response("Internal server error", 500, error_code="INTERNAL_ERROR")
    return wrapper


def require_json(func):
    """
    Decorator untuk require JSON request body.

    Usage:
        @require_json
        @api_handler
        def my_api_route():
            data = request.get_json()
            return jsonify(data)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return json_error_response("Request body harus JSON", 400, error_code="INVALID_CONTENT_TYPE")
        return func(*args, **kwargs)
    return wrapper


# ════════════════════════════════════════════════════════════════════════════
# ── LOGGING HELPERS ──────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

def log_route_access(func):
    """
    Decorator untuk logging akses route.

    Usage:
        @log_route_access
        def my_route():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import session
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        logger.info(f"Route access: {request.path} by user:{user_id} role:{user_role} from {request.remote_addr}")
        return func(*args, **kwargs)
    return wrapper


def log_error_and_return(error_message: str, fallback_url: str = None, log_level: str = "error"):
    """
    Helper untuk log error dan return redirect atau error page.

    Args:
        error_message: Message untuk di-log dan di-flash
        fallback_url: URL untuk redirect
        log_level: Level log ('error', 'warning', 'info')

    Returns:
        Response
    """
    log_func = getattr(logger, log_level, logger.error)
    log_func(error_message)

    flash_error(error_message)

    if request.is_json:
        return json_error_response(error_message)

    if fallback_url:
        return redirect(fallback_url)

    return render_error_page(500, "Terjadi Kesalahan", error_message)
