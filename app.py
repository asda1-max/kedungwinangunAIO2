"""
Desa Kedungwinangun - Sistem Informasi Desa Digital
=================================================

Aplikasi web Flask untuk pengelolaan website desa dan layanan surat online.

Struktur Project:
    app.py           - Entry point utama
    config.py        - Konfigurasi dan konstanta
    models.py        - Database models dan helpers
    routes/          - Route handlers
        __init__.py
        public.py    - Route publik (beranda, berita)
        admin.py    - Route admin (kelola berita, config)
        user.py     - Route warga (register, login, permohonan)
        dinas.py    - Route dinas (verifikasi, approve surat)
    templates/       - Template HTML
    static/          - Asset statis

Run:
    python app.py
"""

from flask import Flask, jsonify, request, render_template
from os import environ, makedirs
from os.path import exists
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()



from config import Config
from models import init_database

# ── Create Flask App ──────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# Create upload folder if not exists
makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# ── Template Context: expose OpenRouter API key to templates ──────────
@app.context_processor
def inject_openrouter_key():
    """Expose OpenRouter API key to all templates (server-side call)"""
    return {
        'openrouter_api_key': environ.get('OPENROUTER_API_KEY', '')
    }

# ── Register Blueprints ───────────────────────────────────────────────
from routes import public_bp, admin_bp, user_bp, dinas_bp

app.register_blueprint(public_bp)    # Public routes: /, /berita, /berita/<id>
app.register_blueprint(admin_bp)      # Admin routes: /admin/*
app.register_blueprint(user_bp)       # User routes: /register, /login, /dashboard, /surat/*
app.register_blueprint(dinas_bp)      # Dinas routes: /dinas/*


# ── Error Handlers ────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return {"error": "Halaman tidak ditemukan"}, 404


@app.errorhandler(500)
def server_error(e):
    return {"error": "Terjadi kesalahan server"}, 500


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


# ── Chatbot API (Server-side OpenRouter) ──────────────────────────────

# Fallback models in priority order
_CHATBOT_MODELS = [
    'nvidia/nemotron-3-ultra-550b-a55b:free',
    'google/gemma-4-26b-a4b-it:free',
    'openrouter/free',
]

_CHATBOT_SYSTEM_PROMPT = """Kamu adalah asisten AI untuk Website Desa Kedungwinangun, Kebumen, Jawa Tengah, Indonesia.

NAMA KADES : Moh Baequni

Konteks Website:
- Website resmi desa untuk informasi dan layanan publik
- Desa Kedungwinangun terletak di Kecamatan Kutowinangun, Kabupaten Kebumen, Jawa Tengah
- Menyediakan berita terkini tentang kegiatan desa
- Layanan surat permohonan online
- Galeri foto kegiatan desa
- Kontak dan informasi pemerintahan desa

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

    # Build messages with system prompt
    all_messages = [{"role": "system", "content": _CHATBOT_SYSTEM_PROMPT}]
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
