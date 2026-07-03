# Plan: Fitur Komentar Reddit-Style untuk Berita

## Goal
Tambahkan threaded comments (stacking/Reddit-style) ke halaman detail berita (`/berita/<id>`), dengan support multi-level nesting dan moderation.

## Aturan
- **Siapa komentar**: User login (prioritas) atau tamu (wajib isi nama)
- **Nesting**: Multi-level tanpa batas (Reddit-style, `parent_id`)
- **Moderasi**: User bisa hapus komentar sendiri, Admin hapus semua

---

## Langkah 1 — Database: Tabel `komentar`

**File**: `models.py`

Tambah `komentar` table via `CREATE TABLE IF NOT EXISTS` di `init_database()`:

```sql
CREATE TABLE IF NOT EXISTS komentar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    berita_id INTEGER NOT NULL,
    parent_id INTEGER,
    user_id INTEGER,
    nama_pengirim TEXT NOT NULL,
    konten TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (berita_id) REFERENCES berita(id),
    FOREIGN KEY (parent_id) REFERENCES komentar(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Tambah field `user_id` nullable — kalau tamu, `user_id = NULL`, `nama_pengirim = nama yang diisi`.

---

## Langkah 2 — Models: Fungsi CRUD Komentar

**File**: `models.py`

Tambah 4 fungsi:

```python
def get_komentar_by_berita(berita_id):
    """Ambil semua komentar untuk sebuah berita, return flat list"""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT k.*, u.nama_lengkap, u.role
        FROM komentar k
        LEFT JOIN users u ON k.user_id = u.id
        WHERE k.berita_id = ?
        ORDER BY k.created_at ASC
    ''', (berita_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def build_comment_tree(flat_comments):
    """Konversi flat list -> nested tree untuk rendering"""
    # pakai dict lookup + parent_id linking
    # return list of root comments (each with nested 'children')

def create_komentar(berita_id, konten, nama_pengirim, parent_id=None, user_id=None):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO komentar (berita_id, parent_id, user_id, nama_pengirim, konten)
        VALUES (?, ?, ?, ?, ?)
    ''', (berita_id, parent_id, user_id, nama_pengirim, konten))
    conn.commit()
    conn.close()

def delete_komentar(komentar_id):
    """Soft delete: hapus komentar + semua child-nya (rekursif)."""
    # Ambil semua ID yang mau dihapus (komentar + semua descendants)
    # DELETE FROM komentar WHERE id IN (...)
    # Atau: DELETE FROM komentar WHERE id = ? OR parent_id = ?
    # Strategi aman: hapus leaf nodes dulu (yang tidak punya child)
```

---

## Langkah 3 — Routes: API Endpoint JSON

**File**: `routes/public.py`

Tambah route baru:

```
POST   /api/berita/<int:berita_id>/komentar      → buat komentar
GET    /api/berita/<int:berita_id>/komentar      → get semua komentar (JSON tree)
DELETE /api/berita/<int:berita_id>/komentar/<int:komentar_id>  → hapus
```

Implementasi:

```python
@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["GET"])
def api_get_komentar(berita_id):
    flat = get_komentar_by_berita(berita_id)
    tree = build_comment_tree(flat)
    return jsonify({"success": True, "comments": tree})

@public_bp.route("/api/berita/<int:berita_id>/komentar", methods=["POST"])
def api_post_komentar(berita_id):
    data = request.get_json()
    konten = data.get("konten", "").strip()
    parent_id = data.get("parent_id")
    nama_pengirim = data.get("nama_pengirim", "").strip()
    user_id = session.get("user_id")
    if not konten:
        return jsonify({"success": False, "error": "Konten tidak boleh kosong"})
    if not user_id and not nama_pengirim:
        return jsonify({"success": False, "error": "Nama wajib diisi untuk tamu"})
    sender = session.get("user_nama") or nama_pengirim
    create_komentar(berita_id, konten, sender, parent_id, user_id)
    return jsonify({"success": True})

@public_bp.route("/api/berita/<int:berita_id>/komentar/<int:komentar_id>", methods=["DELETE"])
def api_delete_komentar(berita_id, komentar_id):
    user_role = session.get("user_role")
    user_id = session.get("user_id")
    # Ambil komentar, cek ownership
    # Bisa hapus kalau user_role == 'admin' ATAU user_id match
    # return jsonify({"success": True/False, "error": "..."})
```

---

## Langkah 4 — Template: Komentar Section di `detail_berita.html`

**File**: `templates/detail_berita.html`

Tambah section komentar SEBELUM `<a href="/berita" class="btn-back">` (tombol kembali). Include:

### 4a. HTML Structure

```html
<section class="komentar-section">
  <h3>💬 Komentar <span id="comment-count">(0)</span></h3>

  <!-- Form komentar baru -->
  <form id="comment-form" class="comment-form">
    {% if session.user_logged_in %}
      <div class="comment-form-header">
        <span class="commenter-name">{{ session.user_nama }}</span>
      </div>
    {% else %}
      <input type="text" name="nama" placeholder="Nama kamu" required class="form-input">
    {% endif %}
    <textarea name="konten" placeholder="Tulis komentar..." rows="3" required></textarea>
    <button type="submit" class="btn btn-primary">Kirim Komentar</button>
  </form>

  <!-- Komentar list (stacked/Reddit style) -->
  <div id="comments-container" class="comments-container"></div>
</section>
```

### 4b. CSS Styling (tambah di `<style>` block)

```css
/* Reddit-style stacking */
.komentar-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}
.comment-thread {
  margin-left: 0;
  border-left: 2px solid var(--border);
  padding-left: 0.75rem;
  margin-top: 0.5rem;
}
.comment-thread .comment-thread {
  margin-left: 1rem;
  border-left-color: #2d5a27; /* deeper green */
}
.comment-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}
.comment-header {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.comment-author { font-weight: 600; color: var(--primary); }
.comment-author.admin { color: #e74c3c; }
.comment-time { font-size: 0.75rem; }
.comment-body { margin: 0.25rem 0; line-height: 1.5; }
.comment-actions { display: flex; gap: 0.75rem; font-size: 0.8rem; }
.comment-actions button {
  background: none; border: none; color: #888;
  cursor: pointer; padding: 0;
}
.comment-actions button:hover { color: var(--primary); }
.comment-form textarea {
  width: 100%; resize: vertical; min-height: 80px;
  padding: 0.5rem; border-radius: 8px;
  border: 1px solid var(--border); font-family: inherit;
}
.comment-form-header { margin-bottom: 0.25rem; font-weight: 600; }
```

### 4c. JavaScript (tambah di `<script>` block)

```javascript
const beritaId = {{ artikel.id }};
const isLoggedIn = {{ 'true' if session.user_logged_in else 'false' }};
const userRole = "{{ session.user_role }}";
const userId = {{ session.user_id or 'null' }};

async function loadComments() {
  const res = await fetch(`/api/berita/${beritaId}/komentar`);
  const data = await res.json();
  renderComments(data.comments);
  document.getElementById('comment-count').textContent = `(${countAll(data.comments)})`;
}

function countAll(comments) {
  return comments.reduce((n, c) => n + 1 + countAll(c.children || []), 0);
}

function renderComments(comments, level = 0) {
  // Render each comment with reply button
  // Recursively render children with increased margin-left
  // Reply button sets parent_id in the form
}

function setupForm() {
  // Submit via fetch POST
  // On success: reload comments
  // Reply flow: set hidden parent_id field
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadComments);
```

---

## Langkah 5 — Render Tree Helper

**File**: `models.py` — `build_comment_tree`

Konsep: Flat list → nested tree

```python
def build_comment_tree(flat):
    lookup = {c['id']: {**c, 'children': []} for c in flat}
    roots = []
    for comment in flat:
        if comment['parent_id'] is None:
            roots.append(lookup[comment['id']])
        else:
            parent = lookup.get(comment['parent_id'])
            if parent:
                parent['children'].append(lookup[comment['id']])
    return roots
```

---

## Ringkasan File yang Diedit

| File | Aksi |
|------|------|
| `models.py` | Tambah table `komentar` di schema + 4 fungsi model |
| `routes/public.py` | Tambah 3 route API (GET, POST, DELETE) |
| `templates/detail_berita.html` | Tambah section komentar + CSS + JS |

---

## Waktu Estimasi

5 step, linear. Step 2 & 3 bisa paralel (models + routes tidak overlap).
