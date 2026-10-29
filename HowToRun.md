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
