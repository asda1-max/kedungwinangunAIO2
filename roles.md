# Roles & Permissions - Desa Kedungwinangun AIO

Dokumentasi ini menjelaskan semua role yang ada di sistem, beserta kemampuan dan akses masing-masing role.

---

## 📋 Daftar Role

| Role | Label | Deskripsi |
|------|-------|-----------|
| `guest` | Tamu / Non-user | Pengunjung website tanpa login |
| `penduduk` | Penduduk / Warga | Warga desa yang sudah terdaftar dan terverifikasi |
| `dinas` | Petugas Dinas | Petugas yang mengelola pendaftaran & permohonan surat |
| `admin` | Administrator | Admin website yang mengelola konten website |

---

## 👤 GUEST (Tamu / Non-User)

Guest adalah pengguna yang **tidak login** ke sistem. Mereka hanya bisa mengakses halaman publik.

### ✅ Yang Bisa Dilakukan Guest

| Fitur | Akses | Keterangan |
|-------|-------|------------|
| **Beranda** | ✅ Read | Melihat halaman utama website |
| **Berita** | ✅ Read | Melihat daftar berita dan artikel |
| **Detail Berita** | ✅ Read | Membaca berita/artikel lengkap |
| **Galeri** | ✅ Read | Melihat foto-foto kegiatan desa |
| **Kontak** | ✅ Read | Melihat informasi kontak desa |
| **Layanan Surat** | ⚠️ Redirect | Diarahkan ke halaman registrasi/login |
| **API Berita** | ✅ Read | Mengakses data berita dalam format JSON |

### ❌ Yang Tidak Bisa Dilakukan Guest

- Mengajukan permohonan surat
- Melihat status permohonan surat
- Login ke sistem
- Mengakses dashboard apapun

### 🔐 Cara Login sebagai Guest

Guest harus **registrasi dan diverifikasi** oleh petugas dinas untuk bisa:
1. Login ke sistem
2. Mengajukan permohonan surat

---

## 🏠 PENGGUNA TERDAFTAR (Penduduk / Warga)

Role default untuk semua user yang mendaftar. Status awal adalah `pending` dan harus diverifikasi oleh petugas dinas.

### ✅ Yang Bisa Dilakukan Penduduk

| Fitur | Akses | Keterangan |
|-------|-------|------------|
| **Registrasi** | ✅ Create | Mendaftar dengan NIK 16 digit + upload KTP & KK |
| **Login** | ✅ Auth | Login jika status sudah `approved` |
| **Dashboard Warga** | ✅ Read | Melihat profil dan riwayat permohonan |
| **Profil** | ✅ Read | Melihat data diri (nama, NIK, email, alamat) |
| **Ajukan Surat** | ✅ Create | Mengajukan permohonan surat (SKU, SKTM, dll) |
| **Riwayat Surat** | ✅ Read | Melihat status permohonan surat (pending/approved/rejected) |

### ❌ Yang Tidak Bisa Dilakukan Penduduk

- Mengelola berita website
- Mengelola galeri
- Mengelola konfigurasi website
- Menyetujui/menolak pendaftaran user lain
- Menyetujui/menolak permohonan surat orang lain
- Mengakses panel admin atau panel dinas

### ⚠️ Status Akun Penduduk

| Status | Keterangan | Aksi yang Tersedia |
|--------|------------|-------------------|
| `pending` | Menunggu verifikasi | ⚠️ Tidak bisa login, hanya bisa menunggu |
| `approved` | Terverifikasi | ✅ Bisa login dan mengajukan surat |
| `rejected` | Ditolak | ❌ Ditolak, harus daftar ulang |

---

## 🏢 PETUGAS DINAS

Petugas yang bertugas memverifikasi pendaftaran warga dan memproses permohonan surat.

### Login Credentials
```
Username/NIK : DINAS001
Password     : dinas123
```

### ✅ Yang Bisa Dilakukan Petugas Dinas

| Fitur | Akses | Keterangan |
|-------|-------|------------|
| **Dashboard Dinas** | ✅ Read | Melihat statistik & data pending |
| **Pendaftaran Pending** | ✅ Read/Approve/Reject | Melihat & memproses pendaftaran warga baru |
| **Semua Data Warga** | ✅ Read | Melihat daftar semua warga |
| **Permohonan Surat** | ✅ Read/Approve/Reject | Melihat & memproses semua permohonan surat |
| **Detail Permohonan** | ✅ Read | Melihat detail lengkap permohonan |
| **Setujui Pendaftaran** | ✅ Write | Menyetujui pendaftaran warga baru |
| **Tolak Pendaftaran** | ✅ Write | Menolak pendaftaran + catatan |
| **Setujui Surat** | ✅ Write | Menyetujui permohonan surat + generate nomor surat |
| **Tolak Surat** | ✅ Write | Menolak permohonan surat + catatan |
| **Logout** | ✅ Auth | Keluar dari sistem |

### 📊 Dashboard Dinas Menampilkan

| Statistik | Keterangan |
|-----------|------------|
| Pendaftaran Pending | Jumlah warga yang belum diverifikasi |
| Surat Pending | Jumlah permohonan surat yang belum diproses |
| Disetujui | Total permohonan yang disetujui |
| Total Warga | Total semua warga terdaftar |

### ❌ Yang Tidak Bisa Dilakukan Petugas Dinas

- Mengelola berita website
- Mengelola galeri
- Mengelola konfigurasi website
- Mengubah pengaturan akun admin

---

## ⚙️ ADMINISTRATOR

Admin website yang bertanggung jawab mengelola konten dan konfigurasi website.

### Login Credentials
```
Username/NIK : ADMIN001
Password     : adminkedungwinangun
```

### ✅ Yang Bisa Dilakukan Administrator

#### 📰 Manajemen Berita
| Fitur | Akses | Keterangan |
|-------|-------|------------|
| Dashboard Admin | ✅ Read | Melihat statistik berita |
| Tambah Berita | ✅ Create | Membuat berita baru |
| Edit Berita | ✅ Update | Mengubah berita |
| Hapus Berita | ✅ Delete | Menghapus berita |
| Berita Unggulan | ✅ Toggle | Menandai berita sebagai unggulan |

#### 🖼️ Manajemen Galeri
| Fitur | Akses | Keterangan |
|-------|-------|------------|
| Daftar Galeri | ✅ Read | Melihat semua foto galeri |
| Tambah Foto | ✅ Create | Menambahkan foto ke galeri |
| Edit Foto | ✅ Update | Mengubah info foto |
| Hapus Foto | ✅ Delete | Menghapus foto dari galeri |
| Toggle Aktif | ✅ Toggle | Mengaktifkan/menonaktifkan foto |

#### ⚙️ Konfigurasi Website
| Fitur | Akses | Keterangan |
|-------|-------|------------|
| Website Info | ✅ Update | Nama, tagline, deskripsi website |
| Berita Settings | ✅ Update | Jumlah berita di homepage, carousel, dll |
| Homepage Sections | ✅ Toggle | Tampilkan/sembunyikan maps, statistik, dusun |
| Kontak | ✅ Update | WhatsApp, telepon, email, alamat |
| Sosial Media | ✅ Update | Facebook, Instagram, Twitter |
| Footer | ✅ Update | Copyright text |

#### 👤 Pengaturan Akun
| Fitur | Akses | Keterangan |
|-------|-------|------------|
| Ubah Username | ✅ Update | Mengubah NIK/login |
| Ubah Password | ✅ Update | Mengubah password |

#### 🌐 Lainnya
| Fitur | Akses | Keterangan |
|-------|-------|------------|
| Lihat Website | ✅ Link | Membuka website publik di tab baru |
| Logout | ✅ Auth | Keluar dari sistem |

### ❌ Yang Tidak Bisa Dilakukan Administrator

- Memproses pendaftaran warga
- Menyetujui/menolak permohonan surat
- Mengelola data warga

---

## 📊 Perbandingan Fitur per Role

| Fitur | Guest | Penduduk | Dinas | Admin |
|-------|:-----:|:---------:|:-----:|:-----:|
| Lihat Beranda | ✅ | ✅ | ✅ | ✅ |
| Lihat Berita | ✅ | ✅ | ✅ | ✅ |
| Lihat Galeri | ✅ | ✅ | ✅ | ✅ |
| Lihat Kontak | ✅ | ✅ | ✅ | ✅ |
| Registrasi | ❌ | ✅ | ❌ | ❌ |
| Ajukan Surat | ❌ | ✅ | ❌ | ❌ |
| Lihat Status Surat | ❌ | ✅ | ✅ | ❌ |
| Approve Pendaftaran | ❌ | ❌ | ✅ | ❌ |
| Reject Pendaftaran | ❌ | ❌ | ✅ | ❌ |
| Approve Surat | ❌ | ❌ | ✅ | ❌ |
| Reject Surat | ❌ | ❌ | ✅ | ❌ |
| Lihat Semua Warga | ❌ | ❌ | ✅ | ❌ |
| Tambah Berita | ❌ | ❌ | ❌ | ✅ |
| Edit Berita | ❌ | ❌ | ❌ | ✅ |
| Hapus Berita | ❌ | ❌ | ❌ | ✅ |
| Kelola Galeri | ❌ | ❌ | ❌ | ✅ |
| Konfigurasi Website | ❌ | ❌ | ❌ | ✅ |
| Ubah Password Admin | ❌ | ❌ | ❌ | ✅ |

---

## 🔄 Alur Verifikasi User

```
[GUESt] → [Registrasi] → [PENDING] → [Dinas Setuju] → [APPROVED] → [Login & Ajukan Surat]
                              ↓
                       [Dinas Tolak] → [REJECTED] → [Daftar Ulang]
```

## 📝 Jenis Surat yang Tersedia

| Kode | Nama Surat | Dokumen Required |
|------|------------|------------------|
| SKU | Surat Keterangan Usaha | KTP, KK |
| SKTM | Surat Keterangan Tidak Mampu | KTP, KK, Surat RT |
| SKCK | Surat Pengantar SKCK | KTP |
| DOMISILI | Surat Keterangan Domisili | KTP, KK |
| BELUM_NIKAH | Surat Keterangan Belum Menikah | KTP, KK, Surat RT |
| LAHIR | Surat Keterangan Kelahiran | KTP Ayah, KTP Ibu, KK, Surat Bidan |
| MATI | Surat Keterangan Kematian | KTP Almarhum, KK, Surat Kades |

---

## 🔗 Link Penting

| Halaman | URL |
|---------|-----|
| Beranda | `/` |
| Login Admin | `/admin/login` |
| Login Warga | `/login` |
| Registrasi | `/register` |
| Dashboard Admin | `/admin/dashboard` |
| Dashboard Dinas | `/dinas/dashboard` |
| Dashboard Warga | `/dashboard` |
| Berita | `/berita` |
| Galeri | `/galeri` |
| Kontak | `/kontak` |
| API Berita | `/api/berita` |

---

*Dokumen ini dibuat pada 23 Juni 2026*
