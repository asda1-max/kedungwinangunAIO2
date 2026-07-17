"""
Desa Kedungwinangun - Sistem Informasi Desa Digital
=================================================

Aplikasi web Flask untuk pengelolaan website desa dan layanan surat online.

Struktur Project:
    app.py           - Entry point utama
    config.py        - Konfigurasi dan konstanta
    models.py        - Database models dan helpers
    errors.py        - Error handling modules
    routes/          - Route handlers
        __init__.py
        public.py    - Route publik (beranda, berita)
        admin.py    - Route admin (kelola berita, config)
        user.py     - Route warga (register, login)
    templates/       - Template HTML
    static/          - Asset statis

Run:
    python app.py
"""

from flask import Flask, jsonify, request, render_template, send_from_directory, abort
from os import environ, makedirs
from os.path import exists, join
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()



from config import Config
from models import init_database

# ── Create Flask App ──────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# Session cookie hardening
app.config.update(
    SESSION_COOKIE_HTTPONLY=Config.SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE=Config.SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE=Config.SESSION_COOKIE_SECURE,
)

# Create upload folder if not exists
makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# ── Template Context: expose OpenRouter API key to templates ──────────
@app.context_processor
def inject_openrouter_key():
    """Expose OpenRouter API key to all templates (server-side call)"""
    return {
        'openrouter_api_key': environ.get('OPENROUTER_API_KEY', '')
    }

@app.context_processor
def inject_custom_pages():
    """Inject custom pages to all templates for mobile nav"""
    from models import get_all_pages
    return {'custom_pages_nav': get_all_pages()}

# ── Register Blueprints ───────────────────────────────────────────────
from routes import public_bp, admin_bp, admin_rtrw_bp, ebook_bp

app.register_blueprint(public_bp)    # Public routes: /, /berita, /berita/<id>
app.register_blueprint(admin_bp)      # Admin routes: /admin/*
app.register_blueprint(admin_rtrw_bp) # Admin RT/RW routes: /admin/rtrw/*
app.register_blueprint(ebook_bp)      # Admin E-Library routes: /admin/ebook/*


# ── Error Handlers ────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    """Handle 404 - Page not found"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Halaman tidak ditemukan",
            "status_code": 404
        }), 404

    # Try to render with error template
    try:
        return render_template(
            "error.html",
            error_code=404,
            title="404 - Halaman Tidak Ditemukan",
            message="Maaf, halaman yang Anda cari tidak ditemukan.",
            subtitle="Halaman mungkin telah dipindahkan atau dihapus.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 404
    except:
        return {"error": "Halaman tidak ditemukan"}, 404


@app.errorhandler(403)
def forbidden(e):
    """Handle 403 - Forbidden access"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Akses ditolak",
            "status_code": 403
        }), 403

    try:
        return render_template(
            "error.html",
            error_code=403,
            title="403 - Akses Ditolak",
            message="Anda tidak memiliki akses ke halaman ini.",
            subtitle="Silakan login terlebih dahulu atau hubungi administrator.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 403
    except:
        return {"error": "Akses ditolak"}, 403


@app.errorhandler(401)
def unauthorized(e):
    """Handle 401 - Unauthorized"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Silakan login terlebih dahulu",
            "status_code": 401
        }), 401

    try:
        return render_template(
            "error.html",
            error_code=401,
            title="401 - Unauthorized",
            message="Anda harus login untuk mengakses halaman ini.",
            subtitle="Silakan login terlebih dahulu.",
            back_url="/login",
            back_text="Login",
        ), 401
    except:
        return {"error": "Silakan login terlebih dahulu"}, 401


@app.errorhandler(500)
def server_error(e):
    """Handle 500 - Internal Server Error"""
    import logging
    logging.error(f"Server Error: {str(e)}")

    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Terjadi kesalahan server",
            "status_code": 500
        }), 500

    try:
        return render_template(
            "error.html",
            error_code=500,
            title="500 - Kesalahan Server",
            message="Maaf, terjadi kesalahan pada server.",
            subtitle="Silakan coba lagi beberapa saat lagi atau hubungi administrator.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 500
    except:
        return {"error": "Terjadi kesalahan server"}, 500


@app.errorhandler(400)
def bad_request(e):
    """Handle 400 - Bad Request"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Permintaan tidak valid",
            "status_code": 400
        }), 400

    try:
        return render_template(
            "error.html",
            error_code=400,
            title="400 - Permintaan Tidak Valid",
            message="Maaf, permintaan Anda tidak dapat diproses.",
            subtitle="Silakan periksa data yang Anda masukkan.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 400
    except:
        return {"error": "Permintaan tidak valid"}, 400


@app.errorhandler(413)
def request_entity_too_large(e):
    """Handle 413 - File too large"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Ukuran file terlalu besar. Maksimal 16MB.",
            "status_code": 413
        }), 413
    try:
        flash("Ukuran file terlalu besar. Maksimal 16MB.", "error")
        return redirect(request.referrer or "/admin/dashboard")
    except:
        return {"error": "Ukuran file terlalu besar"}, 413


@app.errorhandler(503)
def service_unavailable(e):
    """Handle 503 - Service Unavailable"""
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Layanan tidak tersedia",
            "status_code": 503
        }), 503

    try:
        return render_template(
            "error.html",
            error_code=503,
            title="503 - Layanan Tidak Tersedia",
            message="Maaf, layanan sedang tidak tersedia.",
            subtitle="Silakan coba lagi beberapa saat lagi.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 503
    except:
        return {"error": "Layanan tidak tersedia"}, 503


# ── Security Headers Middleware ──────────────────────────────────────────

@app.after_request
def add_security_headers(response):
    """Add security headers to every response"""
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Enable XSS filter in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Cache control for sensitive pages
    if request.path.startswith('/admin') or request.path.startswith('/login'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    # Permissions policy (limit feature access)
    response.headers['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=(self "https://maps.google.com"), '
        'payment=(), usb=(), fullscreen=(self)'
    )
    # Content Security Policy (relaxed for Google Maps, Fonts, etc.)
    if request.path.startswith('/admin') or request.path.startswith('/login'):
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://maps.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "frame-src https://maps.google.com; "
            "connect-src 'self' https://openrouter.ai; "
            "form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
    return response


# ── CSRF Token Injection ─────────────────────────────────────────────────

import secrets

@app.context_processor
def inject_csrf_token():
    """Inject CSRF token into all templates for optional use"""
    from flask import session
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return {'csrf_token': session['_csrf_token']}


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    import logging
    import traceback

    # Log the error
    logging.error(f"Unhandled Exception: {str(e)}")
    logging.error(traceback.format_exc())

    # Return appropriate response based on request type
    if request.is_json:
        return jsonify({
            "success": False,
            "error": "Terjadi kesalahan tidak terduga",
            "status_code": 500
        }), 500

    try:
        return render_template(
            "error.html",
            error_code=500,
            title="Terjadi Kesalahan",
            message="Maaf, terjadi kesalahan yang tidak terduga.",
            subtitle="Silakan hubungi administrator jika masalah berlanjut.",
            back_url="/",
            back_text="Kembali ke Beranda",
        ), 500
    except:
        return {"error": "Terjadi kesalahan tidak terduga"}, 500


# ── API Routes ────────────────────────────────────────────────────────

@app.route("/api/berita")
def api_berita():
    """API untuk mengambil semua berita (JSON)"""
    from models import get_all_berita
    return jsonify(get_all_berita())


# ── Health Check ────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "app": "Desa Kedungwinangun"}


# ── Upload Files ────────────────────────────────────────────────────────

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files (KTP, KK, etc.)"""
    from flask import abort
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(upload_folder, filename)


@app.route("/foto/<path:filename>")
def serve_foto(filename):
    """Serve foto RT/RW and other location photos"""
    foto_dir = join(app.root_path, 'foto')
    if not exists(join(foto_dir, filename)):
        abort(404)
    return send_from_directory(foto_dir, filename)


# ── GeoJSON Files ──────────────────────────────────────────────────────

@app.route("/geojson/<path:filename>")
def serve_geojson(filename):
    """Serve GeoJSON files for map layers"""
    from flask import abort, Response
    import os
    import json
    
    geojson_folder = 'geojson'
    file_path = os.path.join(geojson_folder, filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Response(
            json.dumps(data),
            mimetype='application/geo+json',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as e:
        abort(500)


# ── Chatbot API (Server-side OpenRouter) ──────────────────────────────

# Fallback models in priority order
_CHATBOT_MODELS = [
    'deepseek/deepseek-v4-flash:free',
    'nvidia/nemotron-3-ultra-550b-a55b:free',
    'google/gemma-4-26b-a4b-it:free',
    'openrouter/free',
]

def _build_chatbot_prompt():
    """Build system prompt with dynamic RT/RW and Perangkat Desa data"""
    from models import get_all_lokasi_rtrw, get_all_struktur

    rtrw_list = get_all_lokasi_rtrw(aktif=1)
    struktur_list = get_all_struktur(aktif=1)

    rt_lines = []
    rw_lines = []
    for loc in rtrw_list:
        j = loc.get('jenis', '')
        if j == 'RT':
            rt_lines.append(f"  - RT {loc.get('rt', '')} RW {loc.get('rw', '')}: {loc.get('nama_ketua', '-')} ({loc.get('jabatan', 'Ketua RT')})")
        elif j == 'RW':
            rw_lines.append(f"  - RW {loc.get('rw', '')}: {loc.get('nama_ketua', '-')} ({loc.get('jabatan', 'Ketua RW')})")

    perangkat_lines = []
    for s in struktur_list:
        kat = s.get('kategori', '')
        if kat in ('perangkat', 'bpd', 'pkk', 'karang_taruna'):
            perangkat_lines.append(f"  - {s.get('jabatan', kat)}: {s.get('nama', '-')}")

    rtrw_text = "\n".join(rt_lines + rw_lines) or "  (belum ada data)"
    perangkat_text = "\n".join(perangkat_lines) or "  (belum ada data)"

    return f"""Kamu adalah asisten AI untuk Website Desa Kedungwinangun, Kecamatan Klirong, Kebumen, Jawa Tengah, Indonesia.

NAMA KADES : Moh Baequni

Konteks Website:
- Website resmi desa untuk informasi dan layanan publik
- Desa Kedungwinangun terletak di Kecamatan Klirong, Kabupaten Kebumen, Jawa Tengah
- Menyediakan berita terkini tentang kegiatan desa
- Layanan surat permohonan online
- Galeri foto kegiatan desa
- Kontak dan informasi pemerintahan desa

DATA RT/RW:
{rtrw_text}

PERANGKAT DESA:
{perangkat_text}

Pedoman:
- Jawab dengan ramah dalam Bahasa Indonesia informal (ngobrol)
- Jika pertanyaan di luar konteks website, jawab sebaik mungkin
- Cantumkan sumber jika merujuk ke data website
- Jika tidak tahu, jujur dan sarankan untuk menghubungi pihak terkait
- Batasi jawaban agar ringkas dan helpful (maksimal 3-4 paragraf)
- Gunakan emoji seperlunya untuk membuat jawaban lebih ramah"""


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Server-side chatbot endpoint using OpenRouter API.
    API key stays on server, not exposed to client.
    """
    api_key = environ.get('OPENROUTER_API_KEY', '')
    if not api_key:
        return jsonify({
            "error": "API_KEY_NOT_CONFIGURED",
            "message": "OPENROUTER_API_KEY belum disetting di environment"
        }), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "INVALID_REQUEST", "message": "Request body harus JSON"}), 400

    messages = data.get('messages', [])
    model = data.get('model', _CHATBOT_MODELS[0])

    # Build messages with dynamic system prompt
    system_prompt = _build_chatbot_prompt()
    all_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        if msg.get('role') in ('user', 'assistant'):
            all_messages.append({"role": msg['role'], "content": msg['content']})

    # Primary model attempt
    result = call_openrouter_api(api_key, model, all_messages)
    if result is not None:
        return jsonify({"text": result, "model": model})

    # Fallback chain — try each model in order
    for fallback_model in _CHATBOT_MODELS:
        if fallback_model == model:
            continue
        result = call_openrouter_api(api_key, fallback_model, all_messages)
        if result is not None:
            return jsonify({
                "text": result,
                "model": fallback_model,
                "fallback": True
            })

    return jsonify({
        "error": "ALL_MODELS_FAILED",
        "message": "Semua model AI gagal. Pastikan quota OpenRouter cukup."
    }), 503


def call_openrouter_api(api_key, model, messages, timeout=60):
    """
    Call OpenRouter API, return text on success, None on failure.
    Handles: rate limits (429), model unavailable (503), payment (402), network errors.
    """
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://kedungwinangun.desa.id',
            'X-Title': 'Desa Kedungwinangun AI Assistant'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['choices'][0]['message']['content']

    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode('utf-8')) if e.fp else {}
        err_msg = body.get('error', {}).get('message', str(e))

        if e.code == 429:
            # Rate limited — signal caller to try fallback
            return None
        if e.code == 402:
            return f"💳 **Saldo Habis**\n\nSaldo OpenRouter Anda telah habis. Silakan top-up di [openrouter.ai/credits](https://openrouter.ai/credits)"
        if e.code == 503:
            # Model unavailable — try fallback
            return None
        return f"❌ **Error API ({e.code})**\n\n{err_msg}"

    except urllib.error.URLError:
        # Network error — try fallback
        return None
    except Exception as e:
        return f"⚠️ **Error tidak dikenal**\n\n`{str(e)}`"


# ── Run Server ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize database on first run
    init_database()

    # Get port from environment or default to 5000
    port = int(environ.get('PORT', 5209))

    # Run development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )
