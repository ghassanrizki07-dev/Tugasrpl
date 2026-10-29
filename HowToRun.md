# Petunjuk Menjalankan CookFit

Dokumen ini menjelaskan cara menyiapkan, menjalankan, dan menguji aplikasi CookFit di Windows.

## Prasyarat

- Python 3.9 atau yang lebih baru
- Git
- Browser web

Pastikan Python dan Git sudah tersedia dengan membuka PowerShell dan menjalankan:

```powershell
python --version
git --version
```

## 1. Unduh kode aplikasi

```powershell
git clone https://github.com/ghassanrizki07-dev/Tugasrpl.git
cd Tugasrpl
```

## 2. Siapkan virtual environment

Buat virtual environment untuk memasang dependensi proyek tanpa mengubah instalasi Python global:

```powershell
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi skrip, jalankan perintah berikut di jendela PowerShell yang sama, lalu coba aktivasi kembali:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Pasang dependensi

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Jalankan aplikasi

```powershell
python app.py
```

Setelah pesan server muncul, buka alamat berikut di browser:

```text
http://127.0.0.1:5000
```

Biarkan jendela PowerShell tetap terbuka selama aplikasi digunakan. Untuk menghentikan server, tekan `Ctrl+C`.

Database SQLite akan dibuat atau disiapkan otomatis saat aplikasi dijalankan. File database lokal tidak perlu diunggah ke GitHub.

## Cara Menggunakan Aplikasi

### 1. Daftar atau masuk

- Saat pertama kali membuka aplikasi, pilih **Daftar Sekarang** jika belum memiliki akun.
- Isi nama tampilan, username, password, dan konfirmasi password, lalu pilih **Daftar & Mulai**.
- Jika sudah memiliki akun, masukkan username dan password lalu pilih **Masuk**.

### 2. Pilih bahan di Pantry

- Halaman **Pantry** menampilkan bahan makanan yang tersedia.
- Gunakan kolom **Cari bahan makanan** untuk menemukan bahan tertentu.
- Centang bahan yang saat ini tersedia di dapur. Jumlah bahan terpilih terlihat di bagian atas halaman.
- Pilih **Cari Resep** atau tab **Resep** untuk melihat rekomendasi berdasarkan bahan yang dipilih.

### 3. Lihat dan catat resep

- Di tab **Resep**, resep dengan persentase kecocokan bahan ditampilkan bersama informasi kalori, protein, karbohidrat, dan lemak.
- Bagian **Bahan kurang** menunjukkan bahan yang belum tersedia.
- Pilih **Lihat resep** untuk membaca daftar bahan dan langkah memasak.
- Pilih **+ Log Makan** untuk mencatat resep. Tombol ini hanya dapat digunakan jika semua bahan resep tersedia dan sudah dipilih di Pantry.

### 4. Atur profil dan target kalori

- Buka tab **Kalkulator**.
- Isi nama, jenis kelamin, berat, tinggi, usia, dan tingkat aktivitas.
- Pilih tujuan kalori: **Maintain**, **Cutting**, atau **Bulking**.
- Pilih **Simpan & Hitung Ulang** untuk melihat estimasi BMR, TDEE, dan target kalori harian.
- Lengkapi profil ini agar target di Tracker sesuai dengan kondisi dan tujuan Anda.

### 5. Pantau catatan nutrisi

- Buka tab **Tracker** untuk melihat kalori, protein, karbohidrat, dan lemak dari makanan yang sudah dicatat.
- Daftar **Jurnal Makan** menampilkan resep yang dicatat hari ini.
- Gunakan tombol **Hapus** pada entri jurnal jika ingin menghapus catatan tersebut.
- Untuk menambahkan makanan, kembali ke tab **Resep** dan pilih **+ Log Makan** pada resep yang bahannya lengkap.

### 6. Tambahkan bahan sendiri

- Buka tab **+ Bahan** untuk menambahkan bahan makanan yang belum ada di Pantry.
- Isi nama bahan, pilih kategori, dan sesuaikan estimasi kalori per 100 gram jika diperlukan.
- Pilih **Tambahkan ke Pantry**. Bahan yang baru ditambahkan dapat dicari dan dicentang di tab Pantry.
- Di halaman yang sama, daftar bahan tersedia. Pilih **Hapus** pada bahan yang ingin dikeluarkan dari Pantry.

### 7. Keluar dari akun

- Pilih ikon akun di kanan atas, lalu pilih **Logout**.
- Untuk menggunakan aplikasi kembali, masuk lagi menggunakan akun Anda.

## Menjalankan tes

Buka PowerShell di folder proyek, aktifkan virtual environment jika belum aktif, lalu jalankan:

```powershell
python -m unittest discover -s tests -v
```

## Memulai kembali di lain waktu

Buka PowerShell, pindah ke folder proyek, aktifkan virtual environment, lalu jalankan aplikasi:

```powershell
cd Tugasrpl
.\.venv\Scripts\Activate.ps1
python app.py
```

Jika virtual environment belum pernah dibuat, ikuti kembali langkah 2 dan 3 terlebih dahulu.
