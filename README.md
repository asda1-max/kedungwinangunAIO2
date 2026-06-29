# DESA CERDAS KEDUNGWINANGUN
## Sistem Informasi Desa dan Layanan Surat Online Berbasis Web

---

## 📋 ABSTRAK

Proyek ini merupakan implementasi **Teknologi Tepat Guna (TTG)** dalam bentuk sistem informasi desa digital yang dirancang untuk meningkatkan efisiensi pelayanan publik di Desa Kedungwinangun, Kecamatan Klirong, Kabupaten Kebumen. Sistem mencakup layanan administrasi berita desa, manajemen konten, serta **Layanan Surat Online** yang memungkinkan warga mengajukan permohonan surat keterangan secara mandiri melalui platform digital.

---

## 🎯 LATAR BELAKANG

Desa Kedungwinangun merupakan desa yang terletak di Kecamatan Klirong, Kabupaten Kebumen, Jawa Tengah. Selama ini, pelayanan administrasi desa seperti pengajuan surat keterangan (SKU, SKTM, SKCK, dll.) masih dilakukan secara konvensional dengan warga harus datang langsung ke balai desa. Hal ini menimbulkan beberapa permasalahan:

1. **Antrian panjang** di balai desa terutama pada hari-hari tertentu
2. **Waktu tempuh** yang cukup lama bagi warga yang tinggal di dusun terpencil
3. **Proses yang tidak transparan** dalam tracking status permohonan
4. **Keterbatasan jam layanan** karena tergantung kehadiran perangkat desa

Berdasarkan permasalahan tersebut, diperlukan sebuah solusi teknologi yang dapat menyederhanakan proses pelayanan publik sekaligus tetap mudah digunakan oleh seluruh lapisan masyarakat, termasuk warga lanjut usia.

---

## 🔧 TUJUAN DAN MANFAAT

### Tujuan
1. Mempermudah akses warga terhadap layanan administrasi desa
2. Menerapkan konsep Government to Citizen (G2C) dalam skala mikro
3. Menerapkan prinsip Tata Kelola Desa yang baik (Good Village Governance)
4. Meningkatkan transparansi dalam proses pelayanan surat

### Manfaat
- **Bagi Warga**: Mempercepat dan mempermudah pengajuan surat tanpa harus datang langsung
- **Bagi Pemerintah Desa**: Mempercepat proses verifikasi dan validasi dokumen
- **Bagi Desa**: Membangun citra desa modern yang peduli terhadap kemajuan teknologi

---

## 🛠️ JENIS TEKNOLOGI TEPAT GUNA (TTG)

### 1. Sistem Informasi Desa Terintegrasi

**Deskripsi:**
Aplikasi web berbasis Flask (Python) yang mengintegrasikan berbagai fungsi pelayanan desa dalam satu platform.

**Spesifikasi Teknis:**
- **Framework Backend:** Flask 3.0+
- **Bahasa Pemrograman:** Python 3.12
- **Database:** SQLite3
- **Frontend:** HTML5 + Tailwind CSS + Vanilla JavaScript
- **Security:** Werkzeug Security (Password Hashing)

**Fitur Utama:**
- Manajemen konten berita desa
- Dashboard administrasi
- Sistem multi-role (Admin, Dinas, Penduduk)

### 2. Layanan Surat Online (Desa E-Government)

**Deskripsi:**
Sistem penanganan permohonan surat keterangan secara digital yang menghubungkan warga dengan perangkat desa.

**Komponen:**
| Komponen | Fungsi |
|----------|--------|
| Modul Registrasi | Pendaftaran warga dengan validasi NIK dan upload dokumen |
| Modul Permohonan | Pengajuan surat dengan formulir dinamis |
| Modul Verifikasi | Proses persetujuan oleh petugas dinas |
| Modul Pelacakan | Monitoring status permohonan oleh warga |

**Jenis Surat yang Dilayani:**
1. SKU - Surat Keterangan Usaha
2. SKTM - Surat Keterangan Tidak Mampu
3. SKCK - Surat Pengantar SKCK
4. Domisili - Surat Keterangan Domisili
5. Kelahiran - Surat Keterangan Kelahiran
6. Kematian - Surat Keterangan Kematian
7. Belum Menikah - Surat Keterangan Belum Menikah

### 3. Arsitektur Multi-Role

**Deskripsi:**
Sistem manajemen akses berbasis peran (Role-Based Access Control) yang membedakan hak akses setiap pengguna.

| Peran | Deskripsi | Akses |
|-------|-----------|-------|
| **Administrator** | Pengelola sistem | Manajemen berita, konfigurasi website |
| **Petugas Dinas** | Perangkat desa | Verifikasi warga, persetujuan surat |
| **Penduduk** | Warga desa | Registrasi, pengajuan surat, tracking |

### 4. Database Terpusat

**Deskripsi:**
Penggunaan database relasional SQLite untuk menyimpan seluruh data secara terpusat dan terstruktur.

**Tabel Database:**
- `users` - Data pengguna dan warga
- `berita` - Konten berita desa
- `jenis_surat` - Katalog jenis surat
- `permohonan_surat` - Riwayat permohonan
- `config` - Konfigurasi sistem

---

## 📊 DESKRIPSI TEKNIS

### Kebutuhan Sistem

#### Perangkat Keras (Hardware)
- Server dengan minimal 1GB RAM
- Prosesor setara Intel Celeron atau lebih tinggi
- Storage minimal 5GB
- Koneksi internet (untuk akses eksternal)

#### Perangkat Lunak (Software)
- Python 3.12 atau lebih tinggi
- Flask Framework
- Web Browser modern (Chrome, Firefox, Edge, Safari)

### Spesifikasi Teknis Detail

```
Bahasa Pemrograman    : Python 3.12+
Framework Backend      : Flask 3.0.0
Database              : SQLite3
Frontend              : HTML5, Tailwind CSS 3.x
JavaScript            : Vanilla JS (ES6+)
Server                : Werkzeug Development Server
Port Default          : 5000
```

### Struktur Direktori Proyek

```
kdgwinangun/
├── app.py                 # Aplikasi utama Flask
├── database.db           # Database SQLite
├── requirements.txt      # Daftar dependencies
├── uploads/              # Folder penyimpanan file upload
├── static/               # Aset statis (CSS, gambar)
│   ├── styles.css
│   └── images/
└── templates/            # Template HTML
    ├── index.html         # Halaman utama
    ├── berita.html       # Daftar berita
    ├── detail_berita.html
    ├── admin/            # Template panel admin
    ├── user/             # Template panel warga
    └── dinas/            # Template panel dinas
```

---

## 🔄 ALUR KERJA SISTEM

### A. Alur Pendaftaran Warga

```
┌─────────┐    ┌──────────────┐    ┌─────────┐    ┌─────────────┐
│  Warga  │───►│ Isi Form     │───►│ Upload  │───►│ Status:     │
│ Register │    │ Registrasi   │    │ KTP     │    │ PENDING     │
└─────────┘    └──────────────┘    └─────────┘    └──────┬──────┘
                                                            │
                                                            ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   Warga     │◄───│ Notifikasi   │◄───│  Dinas/Admin Review     │
│   Login     │    │ Approval     │    │  Setuju / Tolak          │
└─────────────┘    └──────────────┘    └─────────────────────────┘
```

### B. Alur Permohonan Surat

```
┌─────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│  Warga  │───►│ Pilih Jenis │───►│ Isi Formulir │───►│ Submit      │
│  Login   │    │ Surat       │    │ Permohonan   │    │ Permohonan  │
└─────────┘    └──────────────┘    └──────────────┘    └──────┬──────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────────┐
│   Warga     │◄───│ Notifikasi   │◄───│  Dinas Review & Verifikasi  │
│   Track     │    │ Status       │    │  Setuju + Generate No.Surat  │
└─────────────┘    └──────────────┘    └─────────────────────────────┘
```

---

## 📱 FITUR UTAMA

### 1. Website Publik
| Fitur | Deskripsi |
|-------|-----------|
| Beranda | Halaman utama dengan berita terbaru dan carousel |
| Berita | Daftar seluruh berita desa |
| Detail Berita | Halaman baca berita lengkap |
| Navigasi | Menu responsif untuk mobile |

### 2. Panel Admin
| Fitur | Deskripsi |
|-------|-----------|
| Dashboard | Statistik dan ringkasan data |
| Manajemen Berita | Tambah, edit, hapus berita |
| Konfigurasi | Pengaturan tampilan website |
| Pengaturan Akun | Ganti username/password admin |

### 3. Panel Dinas
| Fitur | Deskripsi |
|-------|-----------|
| Dashboard | Statistik permohonan masuk |
| Verifikasi Warga | Approval pendaftaran baru |
| Kelola Surat | Review dan approve permohonan |
| Data Warga | Daftar warga terdaftar |

### 4. Panel Warga
| Fitur | Deskripsi |
|-------|-----------|
| Dashboard | Riwayat permohonan surat |
| Ajukan Surat | Formulir permohonan surat |
| Profil | Data diri warga |

---

## 👥 SDM YANG TERLIBAT

| No | Peran | Deskripsi Tugas |
|----|-------|-----------------|
| 1 | Administrator Website | Pengelola konten berita dan konfigurasi sistem |
| 2 | Petugas Dinas | Verifikasi data warga dan persetujuan surat |
| 3 | Kepala Desa | Supervisi dan validasi final |

---

## 📅 JADWAL PELAKSANAAN

| No | Tahapan | Durasi | Keterangan |
|----|---------|--------|------------|
| 1 | Analisis Kebutuhan | 1 minggu | Observasi lapangan, wawancara |
| 2 | Perancangan Sistem | 1 minggu | Desain database, flowchart |
| 3 | Pengembangan | 3 minggu | Coding, testing |
| 4 | Implementasi | 1 minggu | Deploy, training pengguna |
| 5 | Evaluasi | 1 minggu | Pengumpulan umpan balik |

---

## 💰 ANGGARAN

Proyek ini menggunakan prinsip **Open Source** dan **Free Software**, sehingga tidak memerlukan biaya lisensi. Berikut estimasi biaya operasional:

| Komponen | Estimasi Biaya |
|-----------|----------------|
| Domain (opsional) | Rp 50.000 - 150.000/tahun |
| Hosting/VPS (opsional) | Rp 100.000 - 500.000/bulan |
| Pengembangan | Sukarela (KKN) |
| **Total** | **Minimal Rp 0** |

---

## 📌 PENJELASAN TTG/IPTEK

### Apa itu TTG (Teknologi Tepat Guna)?

**TTG** adalah teknologi yang dirancang sesuai dengan kebutuhan, kemampuan sumber daya, serta kondisi sosial-budaya masyarakat setempat. Prinsip utamanya adalah:

1. **Tepat Guna** - Sesuai dengan kebutuhan masyarakat
2. **Tepat Biaya** - Ekonomis dan terjangkau
3. **Tepat Sasaran** - Mudah dipahami dan digunakan
4. **Tepat Teknologi** - Tidak terlalu kompleks namun efektif

### Mengapa Website Desa Termasuk TTG?

1. **Konteks Lokal**: Dibuat khusus untuk Desa Kedungwinangun dengan mempertimbangkan karakteristik warganya
2. **Kemudahan Akses**: Warga dapat mengakses layanan dari mana saja selama ada internet
3. **Efisiensi Biaya**: Menggunakan teknologi open source tanpa biaya lisensi
4. **Ramah Pengguna**: Dirancang dengan antarmuka sederhana yang mudah dipahami
5. **Berkelanjutan**: Mudah dikembangkan sesuai kebutuhan desa

### Inovasi yang Dihadirkan

| Aspek | Konvensional | Dengan Sistem Ini |
|-------|--------------|-------------------|
| Pendaftaran | Datang langsung | Online dengan upload dokumen |
| Pengajuan Surat | Isi formulir fisik | Formulir digital interaktif |
| Verifikasi | Tertunda karena antrian | Real-time dengan notifikasi |
| Tracking | Tidak jelas | Monitoring status online |

---

## 🔒 KEAMANAN SISTEM

1. **Password Hashing**: Menggunakan algoritma PBKDF2 untuk menyimpan password
2. **Session Management**: Pengelolaan sesi login yang aman
3. **Input Validation**: Validasi seluruh input pengguna
4. **File Upload Security**: Pembatasan tipe file dan ukuran upload
5. **Access Control**: Pemisahan hak akses berdasarkan role

---

## 🚀 CARA INSTALASI

### Prasyarat
- Python 3.12 atau lebih tinggi
- pip (Python Package Manager)

### Langkah Instalasi

```bash
# 1. Clone atau download proyek
cd kdgwinangun

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
python app.py

# 4. Buka browser
# - Panel Admin: http://localhost:5000/admin/login
# - Panel Dinas: http://localhost:5000/login
# - Website:     http://localhost:5000/
```

### Kredensial Default

| Akun | Username/NIK | Password |
|------|--------------|----------|
| Admin | adminkedungwinangung | adminkedungwinangun |
| Dinas | DINAS001 | dinas123 |

---

## 📝 CATATAN PENTING

1. **Untuk Produção**: Disarankan menggunakan web server seperti Nginx dengan Gunicorn
2. **Database**: Untuk skala besar, migrate ke PostgreSQL atau MySQL
3. **File Storage**: Untuk production, gunakan cloud storage seperti AWS S3
4. **SSL Certificate**: Wajib menggunakan HTTPS untuk keamanan data

---

## 📞 KONTAK

**Kelompok KKN Desa Kedungwinangun**
Kecamatan Klirong, Kabupaten Kebumen, Jawa Tengah

---

## 📜 LISENSI

Proyek ini dikembangkan sebagai bagian dari kegiatan **Kuliah Kerja Nyata (KKN)** dan bersifat open source untuk kepentingan pelayanan masyarakat desa.

---

*Document ini merupakan bagian dari laporan KKN yang dapat digunakan sebagai referensi teknologi tepat guna (TTG) dalam implementasi desa digital.*
