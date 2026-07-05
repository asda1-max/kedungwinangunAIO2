"""
Database Error Handling Module
Berisi semua helper untuk error handling database operations

Penggunaan:
    from database import (
        db_execute,           # Execute query dengan error handling
        db_fetch_one,         # Fetch single row
        db_fetch_all,         # Fetch all rows
        with_db_connection,   # Context manager untuk connection
        handle_db_error,      # Handle database error
        DatabaseError,        # Custom exception
    )

Contoh:
    # Simple fetch
    user = db_fetch_one('SELECT * FROM users WHERE id = ?', (user_id,))

    # With context manager
    with with_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()
"""

import sqlite3
import functools
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple, Callable

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# ── Custom Exception ───────────────────────────────────────────────────────

class DatabaseError(Exception):
    """
    Custom exception untuk database errors.
    Menyediakan pesan yang user-friendly dan logging otomatis.
    """
    def __init__(self, message: str = "Terjadi kesalahan database", original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error
        self.db_error = True

    def __str__(self):
        return self.message


class DatabaseConnectionError(DatabaseError):
    """Error saat koneksi database gagal"""
    def __init__(self, message: str = "Gagal terhubung ke database"):
        super().__init__(message)


class DatabaseQueryError(DatabaseError):
    """Error saat eksekusi query gagal"""
    def __init__(self, message: str = "Gagal mengeksekusi query", original_error: Exception = None):
        super().__init__(message, original_error)


class DatabaseValidationError(DatabaseError):
    """Error validasi data (unique constraint, foreign key, etc.)"""
    def __init__(self, message: str, error_type: str = None):
        super().__init__(message)
        self.error_type = error_type


# ── Database Connection ────────────────────────────────────────────────────

def get_db_connection():
    """Ambil database connection"""
    from config import Config
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ── Error Handling ─────────────────────────────────────────────────────────

def handle_db_error(
    error: Exception,
    operation: str = "database operation",
    conn: sqlite3.Connection = None,
    rollback: bool = True
) -> Tuple[bool, str]:
    """
    Handle database error dengan logging dan cleanup.

    Args:
        error: Exception yang terjadi
        operation: Deskripsi operasi yang gagal (untuk log)
        conn: Database connection untuk cleanup
        rollback: Apakah perlu rollback

    Returns:
        Tuple (success: bool, message: str)
    """
    # Log error
    error_msg = str(error).lower()
    logger.error(f"Database Error ({operation}): {str(error)}")

    # Cleanup connection
    if conn:
        if rollback:
            try:
                conn.rollback()
            except:
                pass
        try:
            conn.close()
        except:
            pass

    # Determine error type dan pesan yang sesuai
    if "unique constraint" in error_msg or "duplicate" in error_msg:
        return False, "Data sudah ada! Tidak boleh duplikat."
    elif "foreign key constraint" in error_msg:
        return False, "Data tidak dapat dihapus karena masih digunakan."
    elif "not null constraint" in error_msg:
        return False, "Field wajib diisi tidak boleh kosong."
    elif "check constraint" in error_msg:
        return False, "Data tidak memenuhi syarat validasi."
    elif "no such table" in error_msg:
        return False, "Tabel database belum tersedia. Silakan hubungi administrator."
    elif "locked" in error_msg:
        return False, "Database sedang digunakan. Silakan coba lagi."
    else:
        return False, f"Terjadi kesalahan database. Silakan coba lagi."


def get_db_error_message(error: Exception) -> str:
    """
    Get user-friendly error message dari exception.

    Args:
        error: Exception yang terjadi

    Returns:
        str: User-friendly error message
    """
    error_msg = str(error).lower()

    if "unique constraint" in error_msg or "duplicate" in error_msg:
        return "Data sudah ada! Tidak boleh duplikat."
    elif "foreign key constraint" in error_msg:
        return "Data tidak dapat dihapus karena masih digunakan."
    elif "not null constraint" in error_msg:
        return "Field wajib diisi tidak boleh kosong."
    elif "check constraint" in error_msg:
        return "Data tidak memenuhi syarat validasi."
    elif "no such table" in error_msg:
        return "Tabel database belum tersedia."
    elif "locked" in error_msg:
        return "Database sedang digunakan. Silakan coba lagi."
    elif "syntax error" in error_msg:
        return "Format data tidak valid."
    else:
        return "Terjadi kesalahan database. Silakan coba lagi."


# ── Context Manager ─────────────────────────────────────────────────────────

@contextmanager
def with_db_connection():
    """
    Context manager untuk database connection.
    Menangani cleanup otomatis.

    Usage:
        with with_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
        # Connection otomatis di-close

    Raises:
        DatabaseConnectionError: Jika koneksi gagal
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    except sqlite3.OperationalError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise DatabaseConnectionError()
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        raise DatabaseError(str(e), e)
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


# ── Database Operation Wrappers ─────────────────────────────────────────────

def db_execute(
    query: str,
    params: Tuple = (),
    conn: sqlite3.Connection = None,
    commit: bool = True,
    return_lastrowid: bool = False,
    return_rowcount: bool = False
) -> Any:
    """
    Execute query dengan error handling.

    Args:
        query: SQL query
        params: Parameters untuk query
        conn: Connection (jika None, buat baru)
        commit: Apakah perlu commit
        return_lastrowid: Return last inserted ID
        return_rowcount: Return affected rows count

    Returns:
        varies based on parameters

    Raises:
        DatabaseQueryError: Jika query gagal
    """
    should_close = False
    if conn is None:
        try:
            conn = get_db_connection()
            should_close = True
        except Exception as e:
            logger.error(f"Failed to get connection: {str(e)}")
            raise DatabaseConnectionError()

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if commit:
            conn.commit()

        if return_lastrowid:
            result = cursor.lastrowid
        elif return_rowcount:
            result = cursor.rowcount
        else:
            result = None

        return result

    except sqlite3.IntegrityError as e:
        if should_close:
            conn.rollback()
        msg = get_db_error_message(e)
        logger.error(f"Integrity error: {str(e)}")
        raise DatabaseValidationError(msg, "integrity")

    except sqlite3.OperationalError as e:
        if should_close:
            conn.rollback()
        msg = get_db_error_message(e)
        logger.error(f"Operational error: {str(e)}")
        raise DatabaseQueryError(msg, e)

    except sqlite3.Error as e:
        if should_close:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise DatabaseError(str(e), e)

    finally:
        if should_close:
            conn.close()


def db_fetch_one(query: str, params: Tuple = (), conn: sqlite3.Connection = None) -> Optional[Dict]:
    """
    Fetch single row.

    Args:
        query: SQL query
        params: Parameters
        conn: Connection (jika None, buat baru)

    Returns:
        Dict atau None

    Raises:
        DatabaseQueryError: Jika query gagal
    """
    should_close = conn is None

    if conn is None:
        try:
            conn = get_db_connection()
        except Exception as e:
            logger.error(f"Failed to get connection: {str(e)}")
            raise DatabaseConnectionError()

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    except sqlite3.Error as e:
        logger.error(f"Fetch one error: {str(e)}")
        raise DatabaseQueryError(str(e), e)

    finally:
        if should_close and conn:
            conn.close()


def db_fetch_all(query: str, params: Tuple = (), conn: sqlite3.Connection = None) -> List[Dict]:
    """
    Fetch all rows.

    Args:
        query: SQL query
        params: Parameters
        conn: Connection (jika None, buat baru)

    Returns:
        List of Dict

    Raises:
        DatabaseQueryError: Jika query gagal
    """
    should_close = conn is None

    if conn is None:
        try:
            conn = get_db_connection()
        except Exception as e:
            logger.error(f"Failed to get connection: {str(e)}")
            raise DatabaseConnectionError()

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        logger.error(f"Fetch all error: {str(e)}")
        raise DatabaseQueryError(str(e), e)

    finally:
        if should_close and conn:
            conn.close()


# ── Decorators ─────────────────────────────────────────────────────────────

def db_operation(operation_name: str = None):
    """
    Decorator untuk handle database errors pada fungsi.

    Usage:
        @db_operation('get_user')
        def get_user(user_id):
            conn = get_db_connection()
            return conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    Args:
        operation_name: Nama operasi untuk logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            try:
                return func(*args, **kwargs)
            except sqlite3.IntegrityError as e:
                msg = get_db_error_message(e)
                logger.error(f"IntegrityError in {op_name}: {str(e)}")
                raise DatabaseValidationError(msg, "integrity")
            except sqlite3.OperationalError as e:
                logger.error(f"OperationalError in {op_name}: {str(e)}")
                raise DatabaseQueryError(str(e), e)
            except sqlite3.DatabaseError as e:
                logger.error(f"DatabaseError in {op_name}: {str(e)}")
                raise DatabaseConnectionError()
            except DatabaseError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {op_name}: {str(e)}")
                raise DatabaseError(f"Terjadi kesalahan: {str(e)}", e)
        return wrapper
    return decorator


def safe_db_operation(default_return: Any = None, log_error: bool = True):
    """
    Decorator yang mengembalikan default value jika terjadi error.

    Usage:
        @safe_db_operation(default_return=[])
        def get_users():
            return db_fetch_all('SELECT * FROM users')

    Args:
        default_return: Nilai default jika terjadi error
        log_error: Apakah perlu log error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DatabaseError as e:
                if log_error:
                    logger.error(f"DatabaseError in {func.__name__}: {str(e)}")
                return default_return
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


# ── Transaction Helper ─────────────────────────────────────────────────────

def db_transaction(func: Callable) -> Callable:
    """
    Decorator untuk transaction-based operations.
    Automatically handles commit/rollback.

    Usage:
        @db_transaction
        def update_user(user_id, data):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET ... WHERE id = ?', (...))
            return True

    Note:
        Connection akan di-close otomatis setelah selesai
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            error_msg = get_db_error_message(e)
            logger.error(f"Transaction error in {func.__name__}: {str(e)}")
            raise DatabaseError(error_msg, e)
        finally:
            if conn:
                conn.close()
    return wrapper


# ── Validation Helpers ─────────────────────────────────────────────────────

def check_unique(conn: sqlite3.Connection, table: str, field: str, value: Any, exclude_id: int = None) -> bool:
    """
    Check apakah value sudah ada di tabel (untuk validasi unique).

    Args:
        conn: Database connection
        table: Nama tabel
        field: Nama field
        value: Nilai yang dicek
        exclude_id: ID yang di-exclude (untuk update)

    Returns:
        bool: True jika unique (belum ada)
    """
    query = f"SELECT COUNT(*) as cnt FROM {table} WHERE {field} = ?"
    params = [value]

    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)

    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    return row['cnt'] == 0


def check_foreign_key(conn: sqlite3.Connection, table: str, field: str, value: Any) -> bool:
    """
    Check apakah foreign key exists.

    Args:
        conn: Database connection
        table: Nama tabel referensi
        field: Nama field ID
        value: Nilai ID

    Returns:
        bool: True jika exists
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE id = ?", (value,))
    row = cursor.fetchone()
    return row['cnt'] > 0


# ── Batch Operations ────────────────────────────────────────────────────────

def db_batch_insert(
    table: str,
    fields: List[str],
    values: List[Tuple],
    conn: sqlite3.Connection = None
) -> int:
    """
    Batch insert multiple rows.

    Args:
        table: Nama tabel
        fields: List nama field
        values: List tuple values
        conn: Connection (jika None, buat baru)

    Returns:
        int: Jumlah row yang diinsert

    Raises:
        DatabaseQueryError: Jika insert gagal
    """
    should_close = conn is None

    if conn is None:
        conn = get_db_connection()

    try:
        cursor = conn.cursor()
        placeholders = ', '.join(['?' for _ in fields])
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"

        cursor.executemany(query, values)
        conn.commit()
        return cursor.rowcount

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Batch insert error: {str(e)}")
        raise DatabaseQueryError(str(e), e)

    finally:
        if should_close:
            conn.close()
