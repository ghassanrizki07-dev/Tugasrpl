## 📌 Daftar Isi
1. [Penjabaran Judul](#1-penjabaran-judul)
2. [Big Picture Permasalahan](#2-big-picture-permasalahan)
3. [Kenapa Mengambil Judul Ini](#3-kenapa-mengambil-judul-ini)
4. [Manfaat Proyek](#4-manfaat-proyek)
   - [Bagi Pengembang (Saya)](#bagi-pengembang-saya)
   - [Bagi Orang Lain (Pengguna & Konsumen)](#bagi-orang-lain-pengguna--konsumen)
5. [Fitur-Fitur Utama Platform](#5-fitur-fitur-utama-platform)
6. [Arsitektur Sistem & Engine Perhitungan](#6-arsitektur-sistem--engine-perhitungan)
7. [Teknologi yang Digunakan](#7-teknologi-yang-digunakan)
8. [Struktur Direktori Proyek](#8-struktur-direktori-proyek)
9. [Panduan Instalasi & Menjalankan](#9-panduan-instalasi--menjalankan)
10. [Rencana Pengembangan](#10-rencana-pengembangan)
11. [Kontributor](#11-kontributor)

---

## 1. Penjabaran Judul

**CookFit: Aplikasi Rekomendasi Resep Berdasarkan Bahan Dapur & Penghitung Kalori Harian Rumahan Berbasis Web Mobile**

* **CookFit:** Nama platform gabungan dari kata *Cook* (Memasak) dan *Fit* (Kebugaran/Kesehatan).
* **Rekomendasi Resep Berdasarkan Bahan Dapur:** Fitur yang menyarankan ide masakan secara otomatis sesuai daftar bahan makanan yang sedang tersedia di dapur/kulkas saat itu.
* **Penghitung Kalori Harian:** Modul kalkulator nutrisi sederhana untuk menghitung estimasi asupan kalori (serta makronutrisi: karbohidrat, protein, lemak) dari porsi makanan yang dimasak dan dikonsumsi.
* **Web Mobile:** Aplikasi web ringan yang dioptimalkan untuk layar *smartphone* agar mudah diakses langsung dari meja dapur.

---

## 2. Big Picture Permasalahan

Masalah sehari-hari di rumah atau tempat kos sering kali berkisar pada dua hal: bingung menentukan menu masakan dan sulit menjaga asupan nutrisi:

```text
[ Bahan Dapur Tersisa Sedikit ] ──► [ Bingung Mau Masak Apa ] ──► [ Akhirnya Beli Makanan Luar ]
                                                                             │
                                                                             ▼
[ Asupan Kalori Berlebih & Boros ] ◄── [ Tidak Tahu Kandungan Gizi Masakan ]
```

1. **Kebingungan Menu (*Decision Fatigue*):** Setiap hari orang menghabiskan waktu memikirkan "hari ini mau masak apa?" padahal di kulkas masih ada beberapa bahan tersisa.
2. **Asupan Kalori Tak Terukur:** Masakan rumah sering dianggap selalu sehat, padahal tanpa pengukuran porsi dan bahan, jumlah kalori bisa berlebihan tanpa disadari.
3. **Menu Makanan Luar Kurang Sehat:** Karena malas memikirkan ide resep dari bahan yang ada, orang cenderung memesan makanan cepat saji yang lebih mahal dan kurang sehat.

---

## 3. Kenapa Mengambil Judul Ini

1. **Sangat Ringkas Namun Fungsional:** Menggabungkan masalah praktis dapur (*pantry matching*) dengan pencatatan kesehatan (*calorie tracking*) dalam satu aplikasi terpadu.
2. **Implementasi Algoritma Dasar yang Menarik:** Menggunakan logika pencocokan himpunan (*set intersection*) untuk resep dan perhitungan aritmatika dasar untuk gizi, sangat pas untuk portofolio RPL.
3. **Tidak Membutuhkan API Mahal / AI Rumit:** Semua data resep dan data kalori bahan baku dapat disimpan dalam basis data lokal (MySQL) sehingga dapat berjalan cepat dan hemat biaya hosting.

---

## 4. Manfaat Proyek

### Bagi Pengembang (Saya)
* **Penguasaan Algoritma Filtering & Matching:** Melatih logika pemrosesan data untuk mencocokkan input bahan pengguna dengan pustaka resep secara efisien.
* **Pengolahan Data Nutrisi:** Memahami struktur data makronutrisi dan kalkulasi porsi makan (gram ke kalori).
* **Pembangunan Aplikasi Mobile-First:** Mengasah kemampuan membuat antarmuka UI/UX yang responsif dan nyaman digunakan dengan satu tangan di HP.

### Bagi Orang Lain (Pengguna & Konsumen)
* **Menghemat Waktu & Biaya:** Mengoptimalkan bahan makanan yang ada tanpa perlu sering membeli bahan baru atau memesan makanan luar.
* **Memudahkan Menjaga Berat Badan:** Membantu mengontrol target kalori harian (untuk diet menurunkan atau menaikkan berat badan).
* **Edukasi Gizi Masakan Rumah:** Pengguna menjadi tahu estimasi kalori dan makronutrisi dari masakan yang mereka buat sendiri.

---

## 5. Fitur-Fitur Utama Platform

| Modul | Fitur | Deskripsi |
| :--- | :--- | :--- |
| **Bahan Dapur (My Pantry)** | *Pilih Bahan Saat Ini* | Memilih bahan yang ada di kulkas/dapur melalui daftar centang (*checklist*) cepat. |
| **Pencari Resep (Recipe Matcher)** | *Smart Recipe Recommendation* | Menampilkan resep masakan yang diurutkan berdasarkan persentase kecocokan bahan terbanyak. |
| | *Resep Tinggi Protein* | Menyediakan pilihan resep ayam, tahu, telur, tuna, dan edamame dengan estimasi protein per porsi. Bahan resep yang belum tersedia tidak otomatis masuk Pantry; tambahkan melalui menu **+ Bahan** agar dapat dicocokkan. |
| | *Missing Ingredient Alert* | Penanda bahan apa saja yang kurang jika ingin memasak resep tertentu. |
| **Nutrisi & Kalori (NutriTracker)** | *Recipe Calorie Calculator* | Menampilkan estimasi Total Kalori, Protein, Karbohidrat, dan Lemak per porsi resep. |
| | *Daily Calorie Log* | Resep hanya dapat dicatat jika semua bahannya tersedia dan telah dipilih. |
| **Bahan Dapur (My Pantry)** | *Tambah Bahan* | Mengelola bahan pantry melalui menu khusus, terpisah dari kartu rekomendasi resep. |

---

## 6. Arsitektur Sistem & Engine Perhitungan

### Arsitektur Sistem High-Level

```text
[ Antarmuka Web Smartphone (Pilih Bahan / Catat Makan) ]
                          │
                          ▼
             [ Backend Service (PHP / Python) ]
                          │
     ┌────────────────────┴────────────────────┐
     ▼                                         ▼
[ Recipe Matching Engine ]           [ Calorie Calculator Engine ]
(Hitung % Kesesuaian Bahan)         (Kalkulasi Gram ke Kalori & BMR)
     │                                         │
     └────────────────────┬────────────────────┘
                          ▼
                   [ Database MySQL ]
        (Tabel: ingredients, recipes, daily_logs)
```

### Logika Engine & Rumus Perhitungan

#### 1. Algoritma Pencocokan Resep (*Recipe Matching Score*)
Sistem menghitung persentase kecocokan $S_{match}$ suatu resep berdasarkan himpunan bahan yang dimiliki pengguna ($A$) terhadap total bahan yang dibutuhkan resep ($B$):

$$S_{match} = \left( \frac{\vert{}A \cap B\vert{}}{\vert{}B\vert{}} \right) \times 100\%$$

* **Contoh:** Resep "Nasi Goreng Telur" butuh 5 bahan ($\vert{}B\vert{}=5$). Pengguna punya 4 bahan di kulkas ($\vert{}A \cap B\vert{}=4$).  
  $S_{match} = (4 / 5) \times 100\% = 80\%$ (Resep ditampilkan di urutan atas).

#### 2. Logika Hitung Total Kalori Porsi Makanan
Estimasi total kalori ($C_{total}$) dari suatu masakan dihitung dari penjumlahan kalori per bahan baku berdasarkan beratnya dalam gram ($g$):

$$C_{total} = \sum_{i=1}^{n} \left( \frac{g_i}{100} \times C_{100g, i} \right)$$

Di mana:
* $g_i$ = Berat bahan ke-$i$ yang digunakan (gram)
* $C_{100g, i}$ = Kandungan kalori bahan ke-$i$ per 100 gram

#### 3. Perhitungan Target Kalori Harian Pengguna (Rumus BMR Mifflin-St Jeor)
Untuk pengguna pria:
$$BMR = (10 \times \text{BB}) + (6.25 \times \text{TB}) - (5 \times \text{Usia}) + 5$$

Untuk pengguna wanita:
$$BMR = (10 \times \text{BB}) + (6.25 \times \text{TB}) - (5 \times \text{Usia}) - 161$$

*(Keterangan: BB dalam kg, TB dalam cm, dan Usia dalam tahun)*

Setelah TDEE dihitung, target kalori harian menyesuaikan tujuan pengguna:

* **Maintain:** target = TDEE.
* **Cutting:** target = TDEE - 300 kcal, dengan batas minimum sebesar BMR.
* **Bulking:** target = TDEE + 300 kcal.

Pilihan tujuan disimpan di profil akun dan dipakai sebagai batas target pada NutriTracker.

---

## 7. Teknologi yang Digunakan

* **Frontend:** HTML5, CSS3, & JavaScript (Vanilla JS) — Dibuat responsif agar nyaman dibuka di layar HP tanpa perlu *framework* JavaScript yang rumit.
* **Backend:** Python dengan Flask untuk halaman web dan REST API.
* **Database:** SQLite untuk data akun, dengan katalog resep dan bahan awal yang disediakan aplikasi.
* **Pengujian:** `unittest` bawaan Python untuk unit dan API tests.

---

## 8. Struktur Direktori Proyek

```text
Tugasrpl/
├── app.py                   # Flask application dan REST API
├── services/                # Layanan auth, resep, kalori, pantry, dan tracker
├── templates/               # Halaman HTML
├── static/                  # CSS dan JavaScript
├── tests/                   # Unit dan API tests
├── requirements.txt         # Dependensi Python
└── cookfit.db               # Database SQLite lokal (dibuat saat aplikasi dijalankan)
```

---

## 9. Panduan Instalasi & Menjalankan

### Prasyarat
* Python 3.9 atau yang lebih baru

### Instalasi
```bash
git clone https://github.com/ghassanrizki07-dev/Tugasrpl.git
cd Tugasrpl
python -m venv .venv
```

Aktifkan virtual environment, lalu pasang dependensi:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Menjalankan aplikasi
```bash
python app.py
```

Buka `http://127.0.0.1:5000` di browser. Database SQLite lokal dibuat otomatis saat aplikasi berjalan dan tidak perlu di-commit.

Untuk lingkungan yang membutuhkan sesi login tetap valid setelah server dimulai ulang, atur variabel lingkungan `SECRET_KEY` dengan nilai acak yang dirahasiakan sebelum menjalankan aplikasi.

### Menjalankan tes
```bash
python -m unittest discover -s tests -v
```

---

## 10. Rencana Pengembangan

```text
[ Minggu 1: Database & UI ] ──► [ Minggu 2: Recipe Matcher ] ──► [ Minggu 3: Calorie Tracker ]
- Master Data Resep & Kalori   - Fitur Filter Bahan Kulkas      - Log Makan Harian pengguna
- Layout UI Web Mobile CSS     - Algorithm Recipe Matching      - Grafik Progress Target Kalori
```

* **Minggu 1:** Menyiapkan skema database MySQL, mengisi master data 30+ resep rumahan dasar beserta kalori bahannya, serta mendesain antarmuka *mobile* berbasis CSS.
* **Minggu 2:** Membangun *Recipe Matching Engine* di backend PHP/Python (filter bahan terpakai & hitung persentase kecocokan resep).
* **Minggu 3:** Membangun *Calorie Tracker* (jurnal makan harian, kalkulator BMR/TDEE, dan ringkasan konsumsi kalori harian).

---

## 11. Kontributor

* **Full-Stack Developer:** https://github.com/ghassanrizki07-dev — *Bertanggung jawab atas perancangan database nutrisi, pembuatan algoritma pencocokan resep, perhitungan kalori, dan antarmuka web.*
