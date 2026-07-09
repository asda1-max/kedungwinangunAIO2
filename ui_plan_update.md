# UI PLAN UPDATE - Desa Kedungwinangun
## Redenominasi Visual: Minimalis, Elegan, Centric, Emoji-Based

**Versi**: 1.0  
**Tanggal**: 9 Juli 2026  
**Target**: Seluruh halaman public + admin  
**Prinsip**: Centric CSS | Minimalis | Elegan | Emoji-Only | Modern-Desa UX

---

## 1. DESIGN FOUNDATION

### 1.1 Color Palette (CSS Variables Centric)

```css
/* ── CSS Custom Properties - Single Source of Truth ── */
:root {
    /* Primary - Forest Green */
    --c-green-900: #0f3d14;   /* Darkest */
    --c-green-800: #155c1b;   /* Primary Dark */
    --c-green-700: #1a6b22;   /* Primary Mid */
    --c-green-600: #2a6726;   /* Primary Light */
    --c-green-500: #3d8c40;   /* Hover */
    --c-green-400: #5b8a4e;   /* Muted */
    --c-green-300: #73aa0f;   /* Accent */
    --c-green-200: #a3e635;   /* Accent Light */
    --c-green-100: #d9f5c1;   /* Tint */
    --c-green-50:  #f0fde6;   /* Lightest */

    /* Neutral */
    --c-neutral-900: #111827;
    --c-neutral-800: #1f2937;
    --c-neutral-700: #374151;
    --c-neutral-600: #4b5563;
    --c-neutral-500: #6b7280;
    --c-neutral-400: #9ca3af;
    --c-neutral-300: #d1d5db;
    --c-neutral-200: #e5e7eb;
    --c-neutral-100: #f3f4f6;
    --c-neutral-50:  #f9fafb;

    /* Semantic */
    --c-success: #16a34a;
    --c-warning: #ca8a04;
    --c-error:   #dc2626;
    --c-info:    #2563eb;

    /* Background */
    --bg-primary:   #ffffff;
    --bg-secondary: #f8faf7;
    --bg-tertiary:  #f0fde6;

    /* Text */
    --text-primary:   #111827;
    --text-secondary: #4b5563;
    --text-muted:     #9ca3af;
    --text-inverse:   #ffffff;

    /* Border */
    --border-light: #e5e7eb;
    --border-focus: #155c1b;

    /* Shadow */
    --shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
    --shadow-md:  0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
    --shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.05);
    --shadow-xl:  0 20px 25px -5px rgba(0,0,0,0.1),  0 8px 10px -6px rgba(0,0,0,0.06);

    /* Border Radius */
    --radius-sm:   6px;
    --radius-md:   10px;
    --radius-lg:   16px;
    --radius-xl:   24px;
    --radius-full: 9999px;

    /* Spacing (8px base) */
    --space-1:  4px;
    --space-2:  8px;
    --space-3:  12px;
    --space-4:  16px;
    --space-5:  20px;
    --space-6:  24px;
    --space-8:  32px;
    --space-10: 40px;
    --space-12: 48px;
    --space-16: 64px;
    --space-20: 80px;
    --space-24: 96px;

    /* Typography */
    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    /* Font Sizes */
    --text-xs:   0.75rem;   /* 12px */
    --text-sm:   0.875rem;  /* 14px */
    --text-base: 1rem;      /* 16px */
    --text-lg:   1.125rem;  /* 18px */
    --text-xl:   1.25rem;   /* 20px */
    --text-2xl:  1.5rem;    /* 24px */
    --text-3xl:  1.875rem;  /* 30px */
    --text-4xl:  2.25rem;   /* 36px */
    --text-5xl:  3rem;      /* 48px */

    /* Line Heights */
    --leading-tight:  1.25;
    --leading-snug:   1.375;
    --leading-normal: 1.5;
    --leading-relaxed: 1.625;

    /* Transitions */
    --transition-fast:   150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base:   250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow:  400ms cubic-bezier(0.4, 0, 0.2, 1);

    /* Z-Index */
    --z-dropdown: 100;
    --z-sticky:   200;
    --z-modal:    300;
    --z-toast:    400;
}
```

### 1.2 Typography Scale

```
┌─────────────────────────────────────────────────────────┐
│  HEADING SCALE (Font-weight: 700-800)                   │
├─────────────────────────────────────────────────────────┤
│  H1  |  3rem    (48px)   | line-height: 1.1           │
│  H2  |  2.25rem (36px)   | line-height: 1.2           │
│  H3  |  1.875rem (30px)  | line-height: 1.25          │
│  H4  |  1.5rem   (24px)  | line-height: 1.3           │
│  H5  |  1.25rem  (20px)  | line-height: 1.4           │
│  H6  |  1rem      (16px)  | line-height: 1.5           │
├─────────────────────────────────────────────────────────┤
│  BODY SCALE (Font-weight: 400-500)                      │
├─────────────────────────────────────────────────────────┤
│  Large   |  1.125rem (18px) | line-height: 1.625      │
│  Base    |  1rem      (16px) | line-height: 1.625      │
│  Small   |  0.875rem  (14px) | line-height: 1.5        │
│  XSmall  |  0.75rem   (12px) | line-height: 1.5        │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Spacing System (8px Base)

```
Centric spacing for ALL components:
──────────────────────────────────
4px   (0.25rem)  - Tight internal spacing
8px   (0.5rem)   - Icon gaps, tight padding
12px  (0.75rem)  - Form field padding
16px  (1rem)     - Standard padding
20px  (1.25rem)  - Card padding (mobile)
24px  (1.5rem)   - Card padding (desktop)
32px  (2rem)     - Section internal gaps
48px  (3rem)     - Section vertical spacing
64px  (4rem)     - Large section gap
80px  (5rem)     - Hero/Section separators
96px  (6rem)     - Major section break
```

---

## 2. LAYOUT SYSTEM (Centric Grid)

### 2.1 Container Max-Widths

```css
/* ── Container System - Single Max-Width Variants ── */
.container {
    width: 100%;
    margin-left: auto;
    margin-right: auto;
    padding-left:  var(--space-4);
    padding-right: var(--space-4);
}

.container-sm  { max-width: 640px; }   /* 640px  - Narrow content */
.container-md  { max-width: 768px; }   /* 768px  - Form pages */
.container-lg  { max-width: 1024px; }  /* 1024px - Standard page */
.container-xl  { max-width: 1280px; }  /* 1280px - Dashboard/Wide */
.container-2xl { max-width: 1440px; } /* 1440px - Full layout */
.container-full { max-width: none; }   /* Full width */

/* Breakpoints */
@media (min-width: 640px)  { .container { padding-left:  var(--space-6); padding-right: var(--space-6); } }
@media (min-width: 768px)  { .container { padding-left:  var(--space-8); padding-right: var(--space-8); } }
@media (min-width: 1024px) { .container { padding-left: var(--space-10); padding-right: var(--space-10); } }
```

### 2.2 Page Structure Pattern

```
┌─────────────────────────────────────────────────────────┐
│  NAVBAR (sticky, backdrop-blur, h-16/18)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [ HERO / PAGE HEADER ]                                │
│  - Centered title                                       │
│  - Subtitle                                            │
│  - Breadcrumb (if nested)                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  MAIN CONTENT                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  .container-lg / .container-md (centered)        │   │
│  │                                                  │   │
│  │  Section 1                                       │   │
│  │  ├── Section Header (centered)                   │   │
│  │  └── Content Grid (centered children)           │   │
│  │                                                  │   │
│  │  Section 2                                       │   │
│  │  └── ...                                         │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  FOOTER                                                 │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Section Patterns

```html
<!-- PATTERN A: Full-width with centered content -->
<section class="bg-white py-20">
    <div class="container-lg">
        <!-- Section Header - Always Centered -->
        <div class="text-center mb-12">
            <h2 class="text-3xl font-bold text-neutral-900">Judul Section</h2>
            <p class="mt-3 text-neutral-500 max-w-xl mx-auto">Deskripsi section</p>
        </div>
        <!-- Content - Grid centered -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Cards -->
        </div>
    </div>
</section>

<!-- PATTERN B: Soft background, centered -->
<section class="bg-neutral-50 py-16">
    <div class="container-md text-center">
        <!-- Content -->
    </div>
</section>

<!-- PATTERN C: Two-column split, centered individually -->
<section class="py-16">
    <div class="container-lg">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <!-- Each column self-contained -->
            <div class="text-center lg:text-left">
                <h3>...</h3>
                <p>...</p>
            </div>
            <div class="text-center lg:text-left">
                <h3>...</h3>
                <p>...</p>
            </div>
        </div>
    </div>
</section>
```

---

## 3. COMPONENT LIBRARY (Minimalist & Emoji-Based)

### 3.1 Buttons

```html
<!-- PRIMARY BUTTON -->
<button class="
    inline-flex items-center justify-center gap-2
    px-5 py-2.5
    bg-green-800 text-white
    text-sm font-semibold
    rounded-lg
    shadow-sm
    hover:bg-green-700 hover:shadow-md
    active:bg-green-900 active:shadow-sm
    disabled:opacity-50 disabled:cursor-not-allowed
    transition-all duration-150
">
    Button Text
</button>

<!-- SECONDARY BUTTON -->
<button class="
    inline-flex items-center justify-center gap-2
    px-5 py-2.5
    bg-white text-green-800
    text-sm font-semibold
    rounded-lg
    border-2 border-green-800
    hover:bg-green-50
    active:bg-green-100
    transition-all duration-150
">
    Button Text
</button>

<!-- GHOST BUTTON (text only) -->
<button class="
    inline-flex items-center justify-center gap-2
    px-3 py-2
    text-green-800 text-sm font-medium
    rounded-lg
    hover:bg-green-50
    active:bg-green-100
    transition-all duration-150
">
    Button Text
</button>

<!-- DANGER BUTTON -->
<button class="
    inline-flex items-center justify-center gap-2
    px-5 py-2.5
    bg-red-600 text-white
    text-sm font-semibold
    rounded-lg
    hover:bg-red-700
    active:bg-red-800
    transition-all duration-150
">
    Button Text
</button>

<!-- SIZES -->
<!-- sm:  px-3 py-1.5  text-xs -->
<!-- md:  px-5 py-2.5  text-sm (default) -->
<!-- lg:  px-6 py-3    text-base -->
<!-- xl:  px-8 py-4    text-lg -->
```

### 3.2 Cards (Minimalist)

```html
<!-- BASIC CARD -->
<div class="
    bg-white rounded-xl
    border border-neutral-200
    shadow-sm
    hover:shadow-md hover:border-neutral-300
    transition-all duration-200
    overflow-hidden
">
    <!-- Optional Image -->
    <div class="aspect-video bg-neutral-100">
        <img src="..." class="w-full h-full object-cover" />
    </div>
    
    <!-- Content -->
    <div class="p-5">
        <!-- Badge (emoji only, no Kaomoji) -->
        <span class="
            inline-flex items-center gap-1
            px-2 py-1
            bg-green-100 text-green-800
            text-xs font-semibold rounded-full
        ">
            Kategori
        </span>
        
        <!-- Title -->
        <h3 class="mt-3 text-lg font-bold text-neutral-900 line-clamp-2">
            Judul Card
        </h3>
        
        <!-- Excerpt -->
        <p class="mt-2 text-sm text-neutral-500 line-clamp-3">
            Deskripsi singkat card...
        </p>
        
        <!-- Meta -->
        <div class="mt-4 pt-4 border-t border-neutral-100 flex items-center justify-between">
            <span class="text-xs text-neutral-400">12 Jan 2026</span>
            <a href="#" class="text-sm font-medium text-green-800 hover:text-green-600">
                Baca Selengkapnya
            </a>
        </div>
    </div>
</div>

<!-- PROFILE CARD (for struktur) -->
<div class="
    bg-white rounded-xl p-6 text-center
    border border-neutral-200
    shadow-sm hover:shadow-md
    transition-all duration-200
">
    <!-- Avatar -->
    <div class="w-20 h-20 rounded-full bg-gradient-to-br from-green-800 to-green-300 mx-auto overflow-hidden">
        <img src="..." class="w-full h-full object-cover" />
    </div>
    
    <!-- Name & Title -->
    <h4 class="mt-4 font-bold text-neutral-900">Nama Lengkap</h4>
    <p class="mt-1 text-sm text-green-600">Jabatan</p>
    <p class="mt-0.5 text-xs text-neutral-400">Dusun / RW / RT</p>
</div>
```

### 3.3 Form Inputs

```html
<!-- TEXT INPUT -->
<div class="space-y-1.5">
    <label class="block text-sm font-medium text-neutral-700">
        Label <span class="text-red-500">*</span>
    </label>
    <input type="text" class="
        w-full px-4 py-2.5
        bg-white
        border-2 border-neutral-200
        rounded-lg
        text-sm text-neutral-900
        placeholder:text-neutral-400
        focus:outline-none focus:border-green-800 focus:ring-4 focus:ring-green-800/10
        disabled:bg-neutral-50 disabled:text-neutral-500
        transition-all duration-150
    " placeholder="Placeholder..." />
    <p class="text-xs text-neutral-400">Helper text</p>
</div>

<!-- TEXTAREA -->
<textarea class="
    w-full px-4 py-3
    bg-white
    border-2 border-neutral-200
    rounded-lg
    text-sm text-neutral-900
    placeholder:text-neutral-400
    focus:outline-none focus:border-green-800 focus:ring-4 focus:ring-green-800/10
    transition-all duration-150
    resize-y min-h-[120px]
" placeholder="Deskripsi..."></textarea>

<!-- SELECT -->
<select class="
    w-full px-4 py-2.5
    bg-white
    border-2 border-neutral-200
    rounded-lg
    text-sm text-neutral-900
    focus:outline-none focus:border-green-800 focus:ring-4 focus:ring-green-800/10
    transition-all duration-150
    cursor-pointer
">
    <option value="">Pilih...</option>
    <option value="1">Opsi 1</option>
</select>

<!-- CHECKBOX -->
<label class="flex items-start gap-3 cursor-pointer">
    <input type="checkbox" class="
        mt-0.5 w-5 h-5
        rounded border-2 border-neutral-300
        bg-white
        checked:bg-green-800 checked:border-green-800
        focus:ring-4 focus:ring-green-800/20
        cursor-pointer
        transition-all duration-150
    " />
    <span class="text-sm text-neutral-700">Accept terms and conditions</span>
</label>

<!-- FILE INPUT -->
<div class="
    border-2 border-dashed border-neutral-300
    rounded-xl p-8 text-center
    hover:border-green-400 hover:bg-green-50/30
    transition-all duration-150
    cursor-pointer
">
    <div class="text-3xl mb-2">Upload</div>
    <p class="text-sm text-neutral-500">Drag file or click to browse</p>
    <p class="mt-1 text-xs text-neutral-400">Max 5MB (PDF, JPG, PNG)</p>
</div>
```

### 3.4 Badges & Tags (Emoji-Only)

```html
<!-- STATUS BADGE (emoji) -->
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold">
    <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
    Label
</span>

<!-- STATUS VARIANTS -->
<!-- Pending: bg-yellow-100 text-yellow-700 -->
<!-- Aktif:  bg-green-100 text-green-700 -->
<!-- Nonaktif: bg-neutral-100 text-neutral-500 -->
<!-- Important: bg-red-100 text-red-700 -->

<!-- CATEGORY BADGE (emoji) -->
<span class="inline-flex items-center gap-1 px-2.5 py-1 bg-green-50 text-green-700 text-xs font-semibold rounded-full">
    Judul
</span>

<!-- PRIORITY BADGE -->
<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold uppercase">
    High
</span>
```

### 3.5 Navigation

```html
<!-- DESKTOP NAV LINK -->
<a href="#" class="
    px-4 py-2
    text-sm font-medium text-white/80
    rounded-lg
    hover:bg-white/10 hover:text-white
    active:bg-white/20
    transition-all duration-150
">
    Label
</a>

<!-- ACTIVE NAV LINK -->
<a href="#" class="
    px-4 py-2
    text-sm font-semibold text-white
    bg-white/20
    rounded-lg
    transition-all duration-150
">
    Label
</a>

<!-- DROPDOWN MENU -->
<div class="relative" x-data="{ open: false }">
    <button @click="open = !open" class="
        px-4 py-2
        text-sm font-medium text-white/80
        rounded-lg
        hover:bg-white/10 hover:text-white
        inline-flex items-center gap-1
    ">
        Label
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
    </button>
    
    <div x-show="open" x-transition
         @click.away="open = false"
         class="
            absolute left-0 mt-2
            w-56 bg-white rounded-xl shadow-xl border border-neutral-200
            py-2 z-50
         ">
        <a href="#" class="flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 hover:bg-green-50 hover:text-green-800">
            Judul Menu
        </a>
        <!-- divider -->
        <div class="my-2 border-t border-neutral-100"></div>
        <a href="#" class="flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-700 hover:bg-green-50 hover:text-green-800">
            Menu Lain
        </a>
    </div>
</div>
```

### 3.6 Alerts & Messages

```html
<!-- SUCCESS ALERT -->
<div class="
    flex items-start gap-3 p-4
    bg-green-50 border border-green-200
    rounded-xl
">
    <span class="text-xl text-green-600 flex-shrink-0">Success</span>
    <div>
        <h4 class="font-semibold text-green-800">Berhasil!</h4>
        <p class="mt-1 text-sm text-green-700">Pesan sukses...</p>
    </div>
</div>

<!-- ERROR ALERT -->
<div class="
    flex items-start gap-3 p-4
    bg-red-50 border border-red-200
    rounded-xl
">
    <span class="text-xl text-red-600 flex-shrink-0">Error</span>
    <div>
        <h4 class="font-semibold text-red-800">Gagal!</h4>
        <p class="mt-1 text-sm text-red-700">Pesan error...</p>
    </div>
</div>

<!-- INFO ALERT -->
<div class="
    flex items-start gap-3 p-4
    bg-blue-50 border border-blue-200
    rounded-xl
">
    <span class="text-xl text-blue-600 flex-shrink-0">Info</span>
    <div>
        <h4 class="font-semibold text-blue-800">Informasi</h4>
        <p class="mt-1 text-sm text-blue-700">Pesan info...</p>
    </div>
</div>

<!-- WARNING ALERT -->
<div class="
    flex items-start gap-3 p-4
    bg-yellow-50 border border-yellow-200
    rounded-xl
">
    <span class="text-xl text-yellow-600 flex-shrink-0">Warning</span>
    <div>
        <h4 class="font-semibold text-yellow-800">Peringatan</h4>
        <p class="mt-1 text-sm text-yellow-700">Pesan warning...</p>
    </div>
</div>
```

### 3.7 Tables

```html
<div class="overflow-x-auto rounded-xl border border-neutral-200 shadow-sm">
    <table class="w-full text-sm">
        <thead class="bg-neutral-50 border-b border-neutral-200">
            <tr>
                <th class="px-4 py-3 text-left font-semibold text-neutral-600">Kolom 1</th>
                <th class="px-4 py-3 text-left font-semibold text-neutral-600">Kolom 2</th>
                <th class="px-4 py-3 text-left font-semibold text-neutral-600">Aksi</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100 bg-white">
            <tr class="hover:bg-green-50/50 transition-colors">
                <td class="px-4 py-3 text-neutral-900">Data 1</td>
                <td class="px-4 py-3 text-neutral-600">Data 2</td>
                <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                        <a href="#" class="px-3 py-1 text-xs font-medium text-green-800 bg-green-100 rounded-lg hover:bg-green-200">Edit</a>
                        <button class="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200">Hapus</button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### 3.8 Pagination

```html
<nav class="flex items-center justify-center gap-1">
    <a href="#" class="
        w-10 h-10 flex items-center justify-center
        rounded-lg text-sm font-medium
        text-neutral-500 hover:bg-neutral-100
        disabled:opacity-50 disabled:cursor-not-allowed
    ">
        Prev
    </a>
    
    <a href="#" class="
        w-10 h-10 flex items-center justify-center
        rounded-lg text-sm font-semibold
        bg-green-800 text-white
    ">1</a>
    
    <a href="#" class="
        w-10 h-10 flex items-center justify-center
        rounded-lg text-sm font-medium
        text-neutral-600 hover:bg-neutral-100
    ">2</a>
    
    <span class="w-10 h-10 flex items-center justify-center text-neutral-400">...</span>
    
    <a href="#" class="
        w-10 h-10 flex items-center justify-center
        rounded-lg text-sm font-medium
        text-neutral-600 hover:bg-neutral-100
    ">10</a>
    
    <a href="#" class="
        w-10 h-10 flex items-center justify-center
        rounded-lg text-sm font-medium
        text-neutral-500 hover:bg-neutral-100
    ">Next</a>
</nav>
```

---

## 4. PAGE-BY-PAGE UI SPECIFICATIONS

### 4.1 Homepage (index.html)

```
┌──────────────────────────────────────────────────────────┐
│  HERO SECTION                                            │
│  ────────────────────────────────────────────────────    │
│  [Centered layout, max-w-3xl mx-auto]                    │
│                                                          │
│  Badge: Welcome badge (no emoji, plain text + icon)     │
│  H1:     Desa Kedungwinangun (text-5xl/6xl, white)       │
│  Tagline: Subtitle (text-2xl, text-green-100)           │
│  Desc:    Description (text-lg, text-green-200/80)      │
│                                                          │
│  [Date/Time Card - glass effect, centered flex]          │
│  [Action Buttons - centered flex, gap-3]                │
│                                                          │
│  Bottom: SVG wave divider                               │
├──────────────────────────────────────────────────────────┤
│  PERANGKAT DESA                                          │
│  ────────────────────────────────────────────────────    │
│  [Full width bg, centered content]                      │
│  Section title + subtitle (text-center)                  │
│                                                          │
│  Grid: 2/3/6 cols, centered                              │
│  Card: Minimalist profile card                           │
│  - Avatar circle (gradient)                             │
│  - Name + Jabatan + dusun (truncate)                    │
│                                                          │
│  CTA link: "Lihat Semua" (centered below)              │
├──────────────────────────────────────────────────────────┤
│  TENTANG KAMI                                            │
│  ────────────────────────────────────────────────────    │
│  Two-column grid (lg)                                   │
│  Left: Info content + stats grid                        │
│  Right: Image/map embed (rounded-2xl)                   │
├──────────────────────────────────────────────────────────┤
│  PENGUMUMAN                                              │
│  ────────────────────────────────────────────────────    │
│  Section title + "Lihat Semua" link                     │
│                                                          │
│  List style (not cards):                                │
│  - Horizontal card with left accent border               │
│  - Icon + Title + Date + badge                          │
│  - "Selengkapnya" link on right                          │
├──────────────────────────────────────────────────────────┤
│  POTENSI DESA                                            │
│  ────────────────────────────────────────────────────    │
│  Category tabs (horizontal scroll on mobile)             │
│  Grid: 2/3/4 cols                                       │
│  Card: Icon + Title + Short desc (minimal)               │
├──────────────────────────────────────────────────────────┤
│  GALERI                                                  │
│  ────────────────────────────────────────────────────    │
│  Masonry/Grid: 2/3/4/5 cols                            │
│  Image card: Rounded-xl, hover scale                    │
│  Overlay on hover: Title + icon                         │
├──────────────────────────────────────────────────────────┤
│  BERITA                                                  │
│  ────────────────────────────────────────────────────    │
│  Two layouts: Featured (large) + Grid (small)           │
│  Card: Minimalist news card                             │
│  - Thumbnail (16:9)                                     │
│  - Category badge (emoji prefix)                        │
│  - Title (bold, 2 lines max)                          │
│  - Meta: date + views (small, muted)                   │
│  - "Baca Selengkapnya" link                            │
├──────────────────────────────────────────────────────────┤
│  LOKASI / PETA                                          │
│  ────────────────────────────────────────────────────    │
│  Full-width map embed (rounded-2xl, shadow)             │
│  Optional: Contact info below (centered)                │
├──────────────────────────────────────────────────────────┤
│  FOOTER                                                  │
│  ────────────────────────────────────────────────────    │
│  4-column grid: Logo+desc | Links | Links | Contact     │
│  Bottom bar: Copyright + Social icons (minimal)         │
└──────────────────────────────────────────────────────────┘
```

**Minimalism Checklist:**
- [ ] Hapus semua Kaomoji emoticons
- [ ] Badge hanya pakai text label + emoji di awal
- [ ] Hero: max 3 baris text
- [ ] Section padding: py-16 (desktop), py-12 (mobile)
- [ ] Card shadow: shadow-sm, hover:shadow-md
- [ ] Text truncation everywhere
- [ ] Remove decorative "dots" dan animated shapes yang tidak perlu

### 4.2 Berita List (berita.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER (minimal)                                   │
│  ────────────────────────────────────────────────────    │
│  H1: "Berita" (centered, text-4xl)                       │
│  Subtitle: "Berita dan informasi terkini" (text-lg)     │
│  Breadcrumb: Home / Berita                              │
├──────────────────────────────────────────────────────────┤
│  FILTER BAR (centered, sticky on scroll)                │
│  ────────────────────────────────────────────────────    │
│  Category pills (horizontal scroll)                     │
│  [All] [Category1] [Category2] ...                     │
│                                                          │
│  Right side: Sort dropdown                              │
├──────────────────────────────────────────────────────────┤
│  BERITA GRID                                             │
│  ────────────────────────────────────────────────────    │
│  Container: container-lg centered                       │
│  Grid: 1/2/3 cols                                      │
│                                                          │
│  Card:                                                  │
│  ┌─────────────────────────────────┐                   │
│  │ [IMAGE 16:9]                     │                   │
│  ├─────────────────────────────────┤                   │
│  │ [Badge]                         │                   │
│  │ Judul Berita (bold, 2 lines)    │                   │
│  │ Deskripsi singkat (3 lines)     │                   │
│  │ ─────────────────────────────── │                   │
│  │ 12 Jan 2026  •  150 views  →   │                   │
│  └─────────────────────────────────┘                   │
├──────────────────────────────────────────────────────────┤
│  PAGINATION                                              │
│  ────────────────────────────────────────────────────    │
│  Centered, minimal style                                │
└──────────────────────────────────────────────────────────┘
```

### 4.3 Detail Berita (detail_berita.html)

```
┌──────────────────────────────────────────────────────────┐
│  BREADCRUMB                                             │
│  Home / Berita / Judul Berita                           │
├──────────────────────────────────────────────────────────┤
│  ARTICLE HEADER (max-w-3xl mx-auto)                     │
│  ────────────────────────────────────────────────────    │
│  [Badge: Kategori]                                     │
│  H1: Judul Berita (text-3xl/4xl)                       │
│  Meta: Penulis • Tanggal • Views                        │
│                                                          │
│  Featured Image (full-width, rounded-2xl)              │
├──────────────────────────────────────────────────────────┤
│  ARTICLE CONTENT                                        │
│  ────────────────────────────────────────────────────    │
│  Container: container-md (max-w-3xl)                   │
│  Prose styling: p, h2, h3, img, ul, ol, blockquote    │
│  Font: text-base, leading-relaxed, text-neutral-700    │
│  Image captions: text-sm text-neutral-500 italic       │
├──────────────────────────────────────────────────────────┤
│  SHARE / TAGS                                           │
│  ────────────────────────────────────────────────────    │
│  Tags: pill badges (centered)                          │
│  Share: icon buttons (centered)                        │
├──────────────────────────────────────────────────────────┤
│  KOMENTAR SECTION                                       │
│  ────────────────────────────────────────────────────    │
│  H2: "Komentar" (with count)                            │
│                                                          │
│  Comment Form: (if logged in or show guest form)       │
│  ┌─────────────────────────────────────────┐            │
│  │ [Avatar] [Textarea] [Submit Button]    │            │
│  └─────────────────────────────────────────┘            │
│                                                          │
│  Comment List:                                          │
│  - Avatar circle (initials)                             │
│  - Name + Date                                          │
│  - Comment text                                         │
│  - Reply button (if nested allowed)                     │
├──────────────────────────────────────────────────────────┤
│  RELATED BERITA                                         │
│  ────────────────────────────────────────────────────    │
│  H2: "Berita Terkait"                                   │
│  Grid: 1/2/3 cols (smaller cards)                      │
└──────────────────────────────────────────────────────────┘
```

### 4.4 Galeri (galeri.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER                                             │
│  H1: "Galeri" (text-4xl, centered)                       │
│  Subtitle: "Dokumentasi kegiatan desa"                  │
├──────────────────────────────────────────────────────────┤
│  FILTER BAR                                             │
│  ────────────────────────────────────────────────────    │
│  Category pills: [All] [Kegiatan] [Pembangunan] ...    │
│  + Search input (optional)                             │
├──────────────────────────────────────────────────────────┤
│  PHOTO GRID                                             │
│  ────────────────────────────────────────────────────    │
│  Container: container-xl centered                       │
│  Grid: 2 cols (mobile) / 3 cols (md) / 4 cols (lg)    │
│                                                          │
│  Photo Card:                                           │
│  ┌─────────────────────────────────┐                   │
│  │                                 │                    │
│  │      [IMAGE - square/4:3]       │                    │
│  │                                 │                    │
│  │  [Hover overlay: Title + icon] │                    │
│  │                                 │                    │
│  └─────────────────────────────────┘                   │
│                                                          │
│  Hover: scale(1.02) + overlay fade in                 │
├──────────────────────────────────────────────────────────┤
│  LIGHTBOX (when clicked)                               │
│  ────────────────────────────────────────────────────    │
│  Modal: Full-screen dark overlay                       │
│  - Large image centered                                 │
│  - Title + description below                          │
│  - Prev/Next arrows (minimal)                          │
│  - Close button (X icon, top right)                   │
│  - Keyboard: ESC to close, arrows to navigate          │
└──────────────────────────────────────────────────────────┘
```

### 4.5 Struktur Organisasi (struktur.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER                                             │
│  H1: "Struktur Organisasi"                              │
│  Subtitle: "Susunan Pemerintahan Desa"                   │
├──────────────────────────────────────────────────────────┤
│  CATEGORY TABS                                           │
│  ────────────────────────────────────────────────────    │
│  [Perangkat] [BPD] [PKK] [Karang Taruna] [RT] [RW]    │
│  (Horizontal scroll on mobile)                          │
├──────────────────────────────────────────────────────────┤
│  STRUKTUR GRID                                          │
│  ────────────────────────────────────────────────────    │
│  Container: container-lg centered                       │
│  Grid: 2/3/4 cols (depending on category)             │
│                                                          │
│  Profile Card:                                         │
│  ┌─────────────────────────────────┐                   │
│  │      [PHOTO - circle, 80px]     │                   │
│  │                                 │                   │
│  │  Nama Lengkap                   │                   │
│  │  Jabatan                        │                   │
│  │  Wilayah (Dusun/RW/RT)         │                   │
│  │  [View Detail] →               │                   │
│  └─────────────────────────────────┘                   │
├──────────────────────────────────────────────────────────┤
│  DETAIL MODAL (when card clicked)                      │
│  ────────────────────────────────────────────────────    │
│  Large profile:                                         │
│  - Photo (left, large)                                 │
│  - Full info (right):                                 │
│    - Nama, Jabatan                                     │
│    - NIK, Alamat, RT/RW                               │
│    - Kontak (wa/telp)                                 │
│    - Masa Jabatan                                     │
│  Close: X button                                       │
└──────────────────────────────────────────────────────────┘
```

### 4.6 Aduan (aduan.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER                                             │
│  H1: "Pengaduan Masyarakat"                             │
│  Subtitle: "Sampaikan keluhan dan saran Anda"           │
├──────────────────────────────────────────────────────────┤
│  TWO COLUMNS (lg)                                       │
│  ────────────────────────────────────────────────────    │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │                  │  │                  │            │
│  │  FORM ADUAN      │  │  INFO PANEL      │            │
│  │                  │  │                  │            │
│  │  [Nama]          │  │  +628123...      │            │
│  │  [NIK]           │  │  Alamat Kantor   │            │
│  │  [Telepon]       │  │                  │            │
│  │  [Email]         │  │  Atau hubungi    │            │
│  │  [Dusun]         │  │  langsung ke     │            │
│  │  [Judul]         │  │  Kantor Desa     │            │
│  │  [Kategori ▼]    │  │                  │            │
│  │  [Lokasi]        │  │                  │            │
│  │  [Deskripsi]     │  │                  │            │
│  │  [File opsional] │  │                  │            │
│  │                  │  │                  │            │
│  │  [Kirim Aduan]   │  │                  │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                          │
│  NOTE: Form max-width container-md, centered            │
├──────────────────────────────────────────────────────────┤
│  CATEGORY GUIDE                                          │
│  ────────────────────────────────────────────────────    │
│  Grid: 3/4 cols                                        │
│  Icon (emoji) + Title + Short desc                     │
├──────────────────────────────────────────────────────────┤
│  RECENT TRACKING                                        │
│  ────────────────────────────────────────────────────    │
│  Track input + Check button                            │
│  Result card if found                                  │
└──────────────────────────────────────────────────────────┘
```

### 4.7 Program Kerja (program_kerja.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER                                             │
│  H1: "Program Kerja"                                     │
│  Subtitle: "Program kerja Pemerintah Desa"              │
├──────────────────────────────────────────────────────────┤
│  FILTER BAR                                             │
│  ────────────────────────────────────────────────────    │
│  Tahun: [Dropdown] [Filter]                            │
│  Status: [All] [Rencana] [Berlangsung] [Selesai]      │
├──────────────────────────────────────────────────────────┤
│  PROGRAM LIST BY STATUS                                │
│  ────────────────────────────────────────────────────    │
│  Container: container-lg centered                       │
│                                                          │
│  Section per status:                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🔄 BERLANGSUNG (with count badge)               │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Program Card:                                   │   │
│  │ [Icon] [Title] - [Tahun]                      │   │
│  │ Progress bar [XX%]                              │   │
│  │ Target: ... | Realisasi: ...                   │   │
│  │ [Detail] →                                     │   │
│  └─────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────┤
│  STATISTICS (optional)                                  │
│  ────────────────────────────────────────────────────    │
│  Summary cards: Total program, ongoing, completed       │
└──────────────────────────────────────────────────────────┘
```

### 4.8 Transparansi (transparansi.html)

```
┌──────────────────────────────────────────────────────────┐
│  PAGE HEADER                                             │
│  H1: "Transparansi APBDes"                             │
│  Subtitle: "Laporan Penggunaan Anggaran Desa"           │
├──────────────────────────────────────────────────────────┤
│  YEAR SELECTOR                                          │
│  ────────────────────────────────────────────────────    │
│  [2024 ▼] [2023] [2022] [2021]                        │
│  (Pills style, centered)                               │
├──────────────────────────────────────────────────────────┤
│  SUMMARY CARDS                                         │
│  ────────────────────────────────────────────────────    │
│  Container: container-lg centered                       │
│  Grid: 3 cols                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ Total    │ │ Total    │ │ Net      │              │
│  │ Pendapatan│ │ Belanja  │ │ Pembiayaan│              │
│  │ Rp XXX   │ │ Rp XXX   │ │ Rp XXX   │              │
│  └──────────┘ └──────────┘ └──────────┘              │
├──────────────────────────────────────────────────────────┤
│  BREAKDOWN TABS                                        │
│  ────────────────────────────────────────────────────    │
│  [Pendapatan] [Belanja] [Pembiayaan]                   │
│                                                          │
│  Table/List per tab:                                   │
│  ┌─────────────────────────────────────────┐            │
│  │ Keterangan     │ Jumlah      │ Action   │            │
│  ├─────────────────────────────────────────┤            │
│  │ Item 1         │ Rp XXX       │ Detail → │            │
│  │ Item 2         │ Rp XXX       │ Detail → │            │
│  └─────────────────────────────────────────┘            │
├──────────────────────────────────────────────────────────┤
│  VISUALIZATION (optional)                               │
│  ────────────────────────────────────────────────────    │
│  Simple pie chart / bar chart (CSS or Chart.js)         │
└──────────────────────────────────────────────────────────┘
```

---

## 5. ADMIN PANEL UI SPECIFICATIONS

### 5.1 Admin Layout Pattern

```
┌─────────────────────────────────────────────────────────┐
│  ADMIN SIDEBAR (if applicable) OR                      │
│  ADMIN TOPBAR                                          │
├─────────────────────────────────────────────────────────┤
│  ADMIN HEADER                                          │
│  ──────────────────────────────────────────────────    │
│  Page title + Breadcrumb                                │
│  Action buttons (Tambah, Export, etc)                   │
├─────────────────────────────────────────────────────────┤
│  ADMIN CONTENT                                         │
│  ──────────────────────────────────────────────────    │
│  Container: container-xl centered                      │
│                                                          │
│  STATISTICS ROW (if dashboard)                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │
│  │ Stat │ │ Stat │ │ Stat │ │ Stat │                 │
│  └──────┘ └──────┘ └──────┘ └──────┘                 │
│                                                          │
│  CONTENT AREA                                          │
│  Tables, Forms, Cards                                  │
│                                                          │
│  PAGINATION (if table)                                │
├─────────────────────────────────────────────────────────┤
│  ADMIN FOOTER                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Admin Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  DASHBOARD                                              │
│  ──────────────────────────────────────────────────    │
│                                                          │
│  STATS GRID (4 cols)                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ Total   │ │ Aktif   │ │ Pending │ │ Views   │     │
│  │ Berita  │ │ Berita  │ │ Aduan   │ │ Total   │     │
│  │ 150     │ │ 45      │ │ 12      │ │ 10.5K  │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│                                                          │
│  TWO COLUMNS                                           │
│  ┌─────────────────────┐ ┌─────────────────────┐       │
│  │ RECENT ACTIVITY     │ │ QUICK ACTIONS       │       │
│  │ - User registered   │ │ + Tambah Berita     │       │
│  │ - Aduan submitted   │ │ + Tambah Galeri     │       │
│  │ - Berita updated    │ │ + Lihat Aduan       │       │
│  └─────────────────────┘ └─────────────────────┘       │
│                                                          │
│  RECENT ITEMS TABLE                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Judul        │ Kategori │ Status │ Aksi         │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ...          │ ...      │ ...    │ [E] [D]     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Admin Form Pages

```
┌─────────────────────────────────────────────────────────┐
│  ADD/EDIT PAGE                                         │
│  ──────────────────────────────────────────────────    │
│                                                          │
│  Breadcrumb: Admin / Module / Add                       │
│                                                          │
│  FORM CARD (container-md, centered)                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │  [Field Label]                                  │   │
│  │  [Input Field]                                  │   │
│  │                                                 │   │
│  │  [Field Label]                                  │   │
│  │  [Textarea / Rich Text Editor]                  │   │
│  │                                                 │   │
│  │  [Field Label - with preview]                   │   │
│  │  [Dropzone / Image Preview]                     │   │
│  │                                                 │   │
│  │  ─────────────────────────────────────────     │   │
│  │  [Batal]              [Simpan]                 │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  SIDEBAR HELP (optional)                               │
│  Tips & guidelines                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 6. DARK MODE SPECIFICATIONS

### 6.1 Dark Mode Color Overrides

```css
/* Dark Mode - Single override set */
.dark {
    /* Backgrounds */
    --bg-primary:   #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary:  #1e293b;

    /* Text */
    --text-primary:   #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted:     #64748b;
    --text-inverse:   #0f172a;

    /* Borders */
    --border-light: #334155;
    --border-focus: #4ade80;

    /* Cards */
    --card-bg: #1e293b;
    --card-border: #334155;
    --card-shadow: 0 4px 6px rgba(0,0,0,0.3);

    /* Primary adjustments */
    --c-green-100: #166534;  /* darker for contrast */
    --c-green-50:  #14532d;
}

/* Component-level overrides */
.dark body {
    background-color: #0f172a;
    color: #f1f5f9;
}

.dark .bg-white { background-color: #1e293b !important; }
.dark .bg-neutral-50 { background-color: #1e293b !important; }
.dark .bg-neutral-100 { background-color: #0f172a !important; }

.dark .text-neutral-900 { color: #f1f5f9; }
.dark .text-neutral-700 { color: #e2e8f0; }
.dark .text-neutral-600 { color: #cbd5e1; }
.dark .text-neutral-500 { color: #94a3b8; }

.dark .border-neutral-200 { border-color: #334155; }
.dark .border-neutral-300 { border-color: #475569; }

.dark header { background-color: #052e16 !important; }
.dark footer { background-color: #052e16 !important; }

/* Form inputs */
.dark input[type="text"],
.dark input[type="email"],
.dark input[type="password"],
.dark textarea,
.dark select {
    background-color: #1e293b;
    border-color: #334155;
    color: #f1f5f9;
}

.dark input:focus,
.dark textarea:focus,
.dark select:focus {
    border-color: #4ade80;
    box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.1);
}

/* Card hover states */
.dark .bg-white:hover {
    background-color: #334155 !important;
}
```

---

## 7. RESPONSIVE BREAKPOINTS

```css
/* Mobile First breakpoints */
/* Use container classes to center content at each breakpoint */

/* sm:  640px  - Large phones */
@media (min-width: 640px) { }

/* md:  768px  - Tablets */
@media (min-width: 768px) { }

/* lg:  1024px - Small laptops */
@media (min-width: 1024px) { }

/* xl:  1280px - Desktops */
@media (min-width: 1280px) { }

/* 2xl: 1536px - Large screens */
@media (min-width: 1536px) { }
```

### 7.1 Grid Columns by Breakpoint

| Layout | Mobile | sm | md | lg | xl |
|--------|--------|----|----|----|-----|
| News Grid | 1 col | 2 col | 2 col | 3 col | 3 col |
| Gallery Grid | 2 col | 3 col | 4 col | 5 col | 6 col |
| Profile Cards | 2 col | 3 col | 4 col | 6 col | 6 col |
| Two Column | 1 col | 1 col | 1 col | 2 col | 2 col |
| Stats | 2 col | 2 col | 4 col | 4 col | 4 col |
| Footer | 1 col | 2 col | 2 col | 4 col | 4 col |

---

## 8. ANIMATIONS & TRANSITIONS

### 8.1 Allowed Animations (Minimal)

```css
/* ── APPROVED ANIMATIONS ── */

/* Fade in on scroll (subtle) */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Slide up (for modals/tooltips) */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Scale fade (for dropdowns) */
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

/* REMOVE THESE (clutter): */
/* ❌ bounce */
/* ❌ wiggle */
/* ❌ shake */
/* ❌ flash */
/* ❌ jello */
/* ❌ rotateIn */
/* ❌ any Kaomoji animations */
```

### 8.2 Transition Guidelines

```css
/* Use these consistently: */
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);   /* Fast: hovers */
transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);   /* Base: toggles */
transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);   /* Slow: reveals */

/* Don't animate: */
/* ❌ font-size */
/* ❌ height (except collapse) */
/* ❌ width (except expand) */
/* ❌ shadows excessively */
```

---

## 9. EMOJI REPLACEMENT GUIDE

### 9.1 Replace Kaomoji with Emoji

| Before (Kaomoji) | After (Emoji) | Usage |
|-----------------|---------------|-------|
| (^o^) | thumbsup | Celebration |
| (T_T) | sob | Sadness |
| (o_o) | eyes | Surprise |
| \m/ | - | Rock |
| (^_^)v | OK | Victory |
| (握拳) | flexed | Strength |
| (╯°□°)╯ | angry | Anger |

### 9.2 Standard Emoji Set for Each Category

```
KATEGORI           EMOJI SET YANG DIIZINKAN
──────────────────────────────────────────────
Kategori Berita     news | scroll | memo | newspaper | book
Kategori Aduan     construction | tools | warning | shield | megaphone
Kategori Galeri    camera | photo | image | frame
Kategori UMKM       food | drink | hammer | leaf | fish | shopping
Kategori Agenda     calendar | clock | pin | flag | star
Status              clock | check | x | hourglass | alert

NAV ICONS (minimal SVG, not emoji):
- Home: SVG house
- News: SVG newspaper
- Gallery: SVG image
- Contact: SVG phone/email
- User: SVG user
- Settings: SVG gear
```

### 9.3 Remove Emojis from These Places

```
REMOVE EMOJI FROM:
─────────────────────────────────────
❌ Section dividers decorative
❌ Empty states illustrations
❌ Loader/spinner placeholders
❌ Background decorative elements
❌ Footer separator lines
❌ Card border decorations
❌ "New" badges
❌ Feature bullets (use CSS dots)
```

---

## 10. ACCESSIBILITY REQUIREMENTS

### 10.1 Color Contrast

```
MINIMUM CONTRAST RATIOS:
─────────────────────────────────
Normal text: 4.5:1 (WCAG AA)
Large text:  3.0:1 (WCAG AA)
UI elements: 3.0:1 (WCAG AA)
Background:   Verify all text passes

TEST ALL COLOR COMBINATIONS:
- Green-800 text on white: PASS (8.9:1)
- Green-600 text on white: PASS (4.6:1)
- White text on Green-800: PASS (10.3:1)
- Gray-500 text on white: FAIL (2.9:1) → Use Gray-600+
```

### 10.2 Focus States

```css
/* All interactive elements MUST have visible focus */
*:focus-visible {
    outline: 2px solid var(--c-green-300);
    outline-offset: 2px;
}

/* Remove default outline, add custom */
button:focus-visible,
a:focus-visible,
input:focus-visible {
    outline: 2px solid var(--c-green-400);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
}
```

### 10.3 Semantic HTML

```
REQUIRED:
──────────────────────────────────
- Use <header>, <nav>, <main>, <footer>
- Use <article> for news
- Use <section> with aria-label
- Use <button> for actions, <a> for links
- Use <h1> once per page, hierarchy maintained
- Use <img alt="..."> for all images
- Use <form> with proper labels
- Use aria-* for dynamic content
```

---

## 11. IMPLEMENTATION CHECKLIST

### 11.1 Phase 1: Foundation (CSS Variables & Base)
- [ ] Create `css/design-system.css` with all CSS variables
- [ ] Create `css/utilities.css` for utility classes
- [ ] Create `css/components.css` for component styles
- [ ] Update `base.html` to import design system
- [ ] Update `tailwind.config.js` to use CSS variables

### 11.2 Phase 2: Layout Standardization
- [ ] Add container classes to all page wrappers
- [ ] Standardize section padding (py-16 desktop, py-12 mobile)
- [ ] Center all section headers
- [ ] Apply max-width to all content areas

### 11.3 Phase 3: Component Refactoring
- [ ] Refactor all buttons (remove Kaomoji)
- [ ] Refactor all badges (emoji-only)
- [ ] Refactor all cards (minimal shadow)
- [ ] Refactor all forms (consistent input styles)
- [ ] Refactor all tables (minimal style)
- [ ] Refactor all alerts (minimal style)

### 11.4 Phase 4: Page-by-Page
- [ ] Homepage (index.html)
- [ ] Berita list & detail
- [ ] Galeri (with lightbox)
- [ ] Struktur organisasi
- [ ] Aduan form
- [ ] Program kerja
- [ ] Transparansi
- [ ] Info kependudukan
- [ ] Sejarah
- [ ] Kontak
- [ ] Pengumuman

### 11.5 Phase 5: Admin Panel
- [ ] Dashboard
- [ ] Berita CRUD
- [ ] Galeri CRUD
- [ ] Struktur CRUD
- [ ] UMKM CRUD
- [ ] Aduan management
- [ ] Form pages (add/edit)

### 11.6 Phase 6: Polish
- [ ] Dark mode testing
- [ ] Mobile responsiveness
- [ ] Accessibility audit
- [ ] Performance check
- [ ] Cross-browser testing

---

## 12. FILES TO CREATE/MODIFY

```
FILES TO CREATE:
─────────────────────────────────────────────────────────
css/
├── design-system.css      # CSS Variables & Base
├── components.css         # Component Styles
├── layouts.css            # Page Layouts
└── utilities.css          # Utility Classes

FILES TO MODIFY:
─────────────────────────────────────────────────────────
templates/
├── base.html               # Import design system
├── index.html              # Homepage
├── berita.html             # News list
├── detail_berita.html      # News detail
├── galeri.html             # Gallery
├── struktur.html           # Organization
├── aduan.html              # Complaint form
├── program_kerja.html      # Work programs
├── transparansi.html       # Budget
├── info_kependudukan.html  # Demographics
├── sejarah.html            # History
├── kontak.html             # Contact
├── pengumuman.html         # Announcements
├── page.html               # Custom page

admin/templates/
├── base.html               # Admin layout
├── dashboard.html          # Admin dashboard
├── berita.html             # Admin news
├── galeri.html             # Admin gallery
├── struktur.html           # Admin struktur
└── ... (all admin templates)

static/
└── styles.css              # Main CSS (update imports)
```

---

## 13. SUCCESS CRITERIA

### Visual
- [ ] All pages use centered max-width containers
- [ ] Consistent spacing (8px base grid)
- [ ] Consistent border-radius (use variables)
- [ ] Consistent shadows (use variables)
- [ ] No Kaomoji anywhere
- [ ] Emoji usage is minimal and purposeful

### UX
- [ ] Page load < 3s
- [ ] All interactions have feedback
- [ ] Forms are easy to complete
- [ ] Navigation is intuitive
- [ ] Mobile experience is smooth
- [ ] Residents can complete tasks without confusion

### Technical
- [ ] CSS variables used everywhere
- [ ] No inline styles
- [ ] Semantic HTML
- [ ] Accessible (WCAG AA)
- [ ] Dark mode functional
- [ ] Responsive at all breakpoints

---

## 14. APPENDIX: QUICK REFERENCE

### Emoji Quick Reference

```
DISPLAY EMOJI (allowed in UI):
─────────────────────────────────────────────────────────
Navigation Icons: SVG only (not emoji)
Status Indicators:  • (dot) or  (number badge)
Category Labels:    Short text + optional icon prefix
Empty States:      SVG illustration + text
Loading States:    SVG spinner + text
Error States:      text only
Success States:    text only

IF EMOJI NEEDED (use sparingly):
─────────────────────────────────────────────────────────
📰 News/Berita
📅 Agenda
📊 Stats/Charts
📷 Gallery
📢 Announcement
🏛️ Government
🏠 Village
👤 Person
✅ Complete/Success
⏳ Pending/Process
❌ Error/Reject
🔄 Refresh/Update
➕ Add/Create
✏️ Edit
🗑️ Delete
🔍 Search
⚙️ Settings
📁 Folder/Directory
📄 Document
📎 Attachment
🔗 Link
📞 Contact
📧 Email
📍 Location
⏰ Time/Schedule
🎯 Target/Goal
💰 Budget/Money
📈 Progress/Growth
🔒 Security/Private
👁️ View/Hide
```

### Color Quick Reference

```
TEXT COLORS:
─────────────────────────────────────────────────────────
Primary:      text-neutral-900 / dark:text-neutral-50
Secondary:    text-neutral-600 / dark:text-neutral-400
Muted:       text-neutral-400 / dark:text-neutral-500
Accent:      text-green-800 / dark:text-green-400

BACKGROUNDS:
─────────────────────────────────────────────────────────
Base:        bg-neutral-50 / dark:bg-slate-900
Card:        bg-white / dark:bg-slate-800
Highlight:   bg-green-50 / dark:bg-green-900/20

BORDERS:
─────────────────────────────────────────────────────────
Light:       border-neutral-200 / dark:border-neutral-700
Focus:       border-green-600 / dark:border-green-400
```

---

*Document created: 9 Juli 2026*
*Last updated: 9 Juli 2026*
*Version: 1.0*
o