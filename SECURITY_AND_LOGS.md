# Laporan Pengujian, Security, dan Penanganan Insiden (Log & Error)

Dokumen ini berisi dokumentasi resmi hasil uji keamanan (security), catatan perubahan arsitektur (changelog), analisis log sistem, serta panduan mitigasi error untuk aplikasi **CookFit**.

---

## 1. Hasil Uji Keamanan (Security Test Report)

Seluruh lapisan keamanan telah diuji secara otomatis melalui test suite (`tests/test_auth_service.py` & `tests/test_api_endpoints.py`):

| Area Proteksi | Mekanisme & Implementasi | Status Uji | Bukti Validasi |
| :--- | :--- | :--- | :--- |
| **Password Storage** | Menggunakan algoritma hash satu arah `generate_password_hash` dan `check_password_hash` (Werkzeug/PBKDF2/scrypt). Password mentah (plaintext) tidak pernah disimpan di database. | **PASSED** | `test_auth_service.py:test_register_success` |
| **Session & Route Guard** | Decorator `@login_required` memproteksi seluruh halaman utama dan API endpoint internal (`/`, `/api/ingredients`, `/api/daily-logs`, dll). Request tanpa sesi ditolak (HTTP 302 / 401). | **PASSED** | `test_api_endpoints.py:test_unauthenticated_access_protection` |
| **Isolasi Akun (Multi-User)** | Data profil, nilai BMR/TDEE, dan catatan harian NutriTracker diisolasi menggunakan `user_id`. Akun baru selalu dimulai dari nilai 0 tanpa membocorkan data akun lain. | **PASSED** | `test_auth_service.py:test_accounts_have_independent_bmr_calculations` |
| **Pencegahan SQL Injection** | Semua query SQL menggunakan *parameterized queries* (`?` placeholder) via library bawaan SQLite3. | **PASSED** | `services/auth_service.py` |
| **Validasi Input & Boundary** | Validasi input numerik non-negatif pada berat badan, tinggi badan, usia, gramasi bahan, dan nama bahan masakan. Menolak angka negatif, string kosong, dan format tidak valid dengan HTTP 400. | **PASSED** | `test_calorie_service.py:test_ac3_validation_and_invalid_inputs` |

---

## 2. Catatan Perubahan Relevan (Changelog)

1. **Autentikasi & Database Akun SQLite (`cookfit.db`):**
   - Menambahkan tabel `users` dengan penyimpanan hash password, nama tampilan, gender, usia, metrik fisik, dan target BMR/TDEE.
2. **Kalkulator Takaran Masakan & Porsi Bahan:**
   - Menambahkan konversi takaran fleksibel: gram, kg, siung (5g), butir (50g), sendok makan (15g), sendok teh (5g), ikat sayur (150g), dan potong/buah (50g).
   - Menghitung nilai kalori dan protein per gram secara proporsional.
   - Fitur pencatatan masakan langsung ke NutriTracker.
3. **Penyelarasan Target Program (Cutting & Bulking):**
   - **Cutting:** Mengurangi target harian sebesar 300-500 kcal dengan batas aman minimum sebesar BMR pengguna.
   - **Bulking:** Menambah target surplus 300-500 kcal dari TDEE untuk pertumbuhan massa otot.
   - **Maintain:** Target kalori seimbang sama dengan TDEE.
4. **Pantry Dinamis & Pengelompokan Kategori:**
   - Pengguna dapat menambahkan bahan makanan kustom ke kategori "Protein & Daging" atau "Sayuran & Bumbu".

---

## 3. Analisis Log Sistem, Akar Masalah, dan Tindakan Perbaikan

Berikut adalah standar pencatatan log yang aman (tidak membocorkan data sensitif pengguna), identifikasi penyebab, dan solusi perbaikannya:

### 1. Percobaan Login dengan Kredensial Tidak Valid
- **Contoh Log Aman:**
  ```text
  WARNING:auth: Failed login attempt for username 'budi'. Invalid credentials.
  ```
  *(Catatan Keamanan: Password yang diinput tidak boleh dicatat ke dalam log).*
- **Akar Penyebab:** Pengguna salah memasukkan username atau password.
- **Tindakan Perbaikan:** Menampilkan pesan error umum pada antarmuka pengguna tanpa membedakan apakah username atau password yang salah guna mencegah teknik *User Enumeration Attack*.

### 2. Percobaan Akses Endpoint Tanpa Login (Unauthorized Access)
- **Contoh Log Aman:**
  ```text
  INFO:werkzeug: 127.0.0.1 - - [05/Nov/2026 12:30:15] "GET /api/daily-logs HTTP/1.1" 401 Unauthorized
  ```
- **Akar Penyebab:** Request API dikirimkan oleh browser atau client tanpa cookie sesi login yang aktif/valid.
- **Tindakan Perbaikan:** Interceptor `@login_required` memotong alur eksekusi, menghentikan akses database, dan merespons dengan JSON `{ status: 'error', message: 'Sesi login tidak valid atau telah berakhir.' }`.

### 3. Validasi Input Payload Buruk (Bad Request)
- **Contoh Log Aman:**
  ```text
  WARNING:app: Validation failed on /api/calculate-bmr. Input: weight=-5, height=170. Error: Berat badan harus lebih dari 0.
  ```
- **Akar Penyebab:** Payload JSON yang dikirimkan client berisi angka di luar batas aman/realistis.
- **Tindakan Perbaikan:** Modul kalkulator melempar exception `ValueError` terstruktur yang ditangkap API handler untuk mengembalikan kode status HTTP 400 beserta keterangan bidang yang keliru.

### 4. Koneksi Server Terputus (Port Refused)
- **Contoh Log:**
  ```text
  ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
  ```
- **Akar Penyebab:** Script client/browser mencoba mengakses `http://127.0.0.1:5000` sebelum proses server Flask dijalankan.
- **Tindakan Perbaikan:** Pastikan proses daemon server telah aktif dengan menjalankan `python app.py` dan memverifikasi port 5000 dalam kondisi listening.

---

## 4. Status Eksekusi Unit Test Suite

```text
Ran 48 tests in 5.757s

OK (48/48 tests passed, 0 failures, 0 errors)
```
Semua modul (`auth_service`, `recipe_service`, `calorie_service`, `tracker_service`, `shopping_service`, dan `api_endpoints`) telah teruji dan siap untuk deployment.
