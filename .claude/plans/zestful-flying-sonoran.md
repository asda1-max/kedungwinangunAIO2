# Plan: Modernisasi UI Dashboard (Admin, User, Dinas)

## Analisis Kondisi Saat Ini

### Template Files
- **Admin**: 22 template di `templates/admin/` (base.html + child templates)
- **Dinas**: 7 template di `templates/dinas/` (base.html + child templates)
- **User**: 4 template di `templates/user/` (standalone, tanpa base layout)

### Masalah UI yang Ditemukan
1. **Emoji di mana-mana**: 🏘️📊🖼️📄📢👥💰⚙️👤🌐🚪👋✓⏳✗📝
2. **Font tidak konsisten**: Admin pakai Inter, Dinas/User pakai Plus Jakarta Sans
3. **Desain terlalu ramai**: Gradien berlebihan, shadow berlebihan
4. **User templates tidak punya base layout**: Duplikasi kode

---

## Rencana Modernisasi

### 1. Sistem Icon (Semua Dashboard)
Ganti semua emoji dengan **inline SVG icons** menggunakan pola minimaliste:

```html
<!-- Contoh pengganti emoji -->
🏘️ → <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
       </svg>
📊 → <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
       </svg>
```

### 2. Color Palette Baru (Elegant Green)

| Element | Lama | Baru |
|---------|------|------|
| Primary | `#166534` (hijau tua) | `#059669` (emerald lebih modern) |
| Primary Light | `#22c55e` | `#10b981` |
| Background | `#f8fafc` | `#fafbfc` (lebih bersih) |
| Card BG | white | white dengan subtle border |
| Text | `#1e293b` | `#1e293b` (tetap) |
| Muted | `#64748b` | `#64748b` (tetap) |

### 3. Typography

Pakai **Plus Jakarta Sans** untuk SEMUA dashboard (lebih modern dari Inter):
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### 4. Card Components (Minimalist)

```css
/* Lama - terlalu berat */
.card {
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid #f1f5f9;
}

/* Baru - lebih clean */
.card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: white;
  transition: all 0.2s ease;
}
.card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
```

### 5. Stat Cards

```css
/* Lama - corner circle decoration */
.stat-card::before {
  content: '';
  border-radius: 50%;
  opacity: 0.5;
}

/* Baru - clean tanpa decoration */
.stat-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 20px 24px;
}
.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### 6. Sidebar Redesign

```css
/* Lama */
.sidebar {
  background: linear-gradient(180deg, #166534 0%, #14532d 100%);
  padding: 24px;
}

/* Baru - solid, lebih elegant */
.sidebar {
  background: #1e293b; /* dark slate */
  padding: 20px;
}
.nav-item {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}
.nav-item.active {
  background: rgba(255,255,255,0.1);
}
```

### 7. Badges - Clean Style

```css
/* Lama */
.badge {
  padding: 6px 14px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
}

/* Baru */
.badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.02em;
}
```

---

## Files yang Perlu Diubah

### Admin Templates (22 files)
1. `templates/admin/base.html` - Sidebar + global CSS
2. `templates/admin/dashboard.html`
3. `templates/admin/galeri.html`
4. `templates/admin/add_berita.html`
5. `templates/admin/edit_berita.html`
6. `templates/admin/add_galeri.html`
7. `templates/admin/edit_galeri.html`
8. `templates/admin/config.html`
9. `templates/admin/settings.html`
10. `templates/admin/pages.html`
11. `templates/admin/add_page.html`
12. `templates/admin/edit_page.html`
13. `templates/admin/struktur.html`
14. `templates/admin/add_struktur.html`
15. `templates/admin/edit_struktur.html`
16. `templates/admin/pengumuman.html`
17. `templates/admin/add_pengumuman.html`
18. `templates/admin/edit_pengumuman.html`
19. `templates/admin/apbdes.html`
20. `templates/admin/add_apbdes.html`
21. `templates/admin/edit_apbdes.html`
22. `templates/admin/login.html`

### Dinas Templates (7 files)
1. `templates/dinas/base.html` - Sidebar + global CSS
2. `templates/dinas/dashboard.html`
3. `templates/dinas/pending_users.html`
4. `templates/dinas/all_users.html`
5. `templates/dinas/permohonan_list.html`
6. `templates/dinas/permohonan_detail.html`
7. `templates/dinas/user_detail.html`

### User Templates (4 files)
1. `templates/user/base.html` - **BARU** (create shared layout)
2. `templates/user/dashboard.html` - Extend base
3. `templates/user/login.html`
4. `templates/user/register.html`
5. `templates/user/surat_permohonan.html`

---

## Langkah Implementasi

### Fase 1: Base Templates (Admin & Dinas)
1. Update CSS variables dan font di `admin/base.html`
2. Update CSS variables dan font di `dinas/base.html`
3. Ganti semua emoji dengan SVG icons di sidebar
4. Refine card, button, badge styles

### Fase 2: Child Templates (Admin)
1. Update dashboard.html dengan stat cards baru
2. Update semua tabel dengan style baru
3. Ganti emoji di badges, buttons, actions
4. Update forms dengan style baru

### Fase 3: Child Templates (Dinas)
1. Update dashboard.html
2. Update semua list/detail templates
3. Ganti emoji dengan SVG icons

### Fase 4: User Templates
1. Create `templates/user/base.html`
2. Update dashboard.html
3. Update login.html, register.html, surat_permohonan.html
4. Create shared SVG icon library

### Fase 5: Polish
1. Animasi halus (hover, transitions)
2. Responsive refinements
3. Empty states redesign
4. Alert styling consistency

---

## Target Hasil

- **Minimal emoji** - maksimal 1-2 untuk empty states
- **Elegant** - clean lines, good spacing, consistent hierarchy
- **Minimalist** - no unnecessary decorations, focus on content
- **Modern** - Plus Jakarta Sans, subtle shadows, refined colors
- **Consistent** - same styles across all 3 dashboards
