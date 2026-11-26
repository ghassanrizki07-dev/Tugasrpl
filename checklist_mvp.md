# Checklist Fitur MVP CookFit

## Status Pengujian

- **Hasil keseluruhan:** PASSED
- **Perintah:** `python -m unittest discover -s tests -v`
- **Ringkasan terakhir:** 222 tes berhasil, 0 gagal, 0 error (192 tes service/unit dan 30 tes API).
- **Target P11:** Belum terpenuhi: jumlah tes service/unit masih kurang 8 dari target 200.
- **Terakhir dijalankan:** 26 November 2026
- **Batasan deployment:** Pengujian lokal tidak membuktikan data persisten pada Vercel. Uji browser live menemukan API `/api/auth/me` dan `/api/daily-logs` merespons HTTP 401 setelah halaman dimuat ulang.
- **CI/deploy otomatis:** Belum dibuktikan; repositori GitHub saat ini tidak memiliki workflow GitHub Actions.
- **Efek test gagal:** Demonstrasi assertion gagal menghasilkan status `FAILED` dan exit code 1. Ini membuktikan runner memberi sinyal gagal, tetapi bukan bukti pipeline CI karena workflow belum tersedia.
- **Validasi storage lokal:** Tes SQLite sementara mengonfirmasi data log tetap tersedia lintas instance service dan data log, belanja, serta bahan custom terisolasi per pengguna.

## Temuan P10 dan Status Perbaikan

Temuan 1–4 diamati langsung pada deployment; temuan 5–11 ditelusuri pada implementasi layanan. Perbaikan kode telah dipush ke branch `v1.0` pada commit `e269fbc`, dan 11 GitHub Issues telah dibuat. Semua issue masih **OPEN** sampai database Neon disiapkan, `DATABASE_URL` dipasang di Vercel, lalu deployment baru diuji. Karena itu P10 belum boleh dinyatakan seluruhnya solved.

| Issue | No. | Temuan | Perbaikan | Status |
|---|---|---|---|---|
| [#1](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/1) | 1 | Akun hilang setelah reload/perpindahan instance Vercel | Menggunakan SQLAlchemy dan PostgreSQL persisten; deployment Vercel menolak startup tanpa `DATABASE_URL`. | MENUNGGU KONFIGURASI NEON DAN UJI LIVE |
| [#2](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/2) | 2 | UI tetap menampilkan halaman utama setelah API autentikasi gagal | HTTP 401/404 mengarahkan pengguna ke login; aksi logout gagal menampilkan error, bukan berpura-pura berhasil. | MENUNGGU UJI LIVE |
| [#3](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/3) | 3 | Pantry memakai data fallback saat API gagal | Data Pantry hanya dirender setelah API berhasil; kegagalan menampilkan pesan error. | MENUNGGU UJI LIVE |
| [#4](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/4) | 4 | Rekomendasi memakai data fallback saat API gagal | Rekomendasi dihapus dari tampilan saat request gagal dan pesan error ditampilkan. | MENUNGGU UJI LIVE |
| [#5](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/5) | 5 | Catatan tracker hilang saat proses server berganti | Log disimpan di database dengan tanggal harian zona Asia/Jakarta. | MENUNGGU UJI LIVE |
| [#6](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/6) | 6 | Catatan tracker tidak diisolasi antar akun | Query tambah, baca, dan hapus log dibatasi dengan `user_id`. | MENUNGGU UJI LIVE |
| [#7](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/7) | 7 | Jurnal “harian” tidak memiliki batas tanggal | Log menyimpan tanggal dan GET hanya membaca tanggal saat ini zona Asia/Jakarta. | MENUNGGU UJI LIVE |
| [#8](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/8) | 8 | Daftar belanja hilang saat proses server berganti | Operasi daftar belanja memakai tabel PostgreSQL persisten. | MENUNGGU UJI LIVE |
| [#9](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/9) | 9 | Daftar belanja tidak diisolasi antar akun | Operasi daftar belanja dibatasi dengan `user_id`. | MENUNGGU UJI LIVE |
| [#10](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/10) | 10 | Bahan custom Pantry hilang saat proses server berganti | Bahan custom disimpan di database persisten. | MENUNGGU UJI LIVE |
| [#11](https://github.com/ghassanrizki07-dev/Tugasrpl/issues/11) | 11 | Bahan custom Pantry dibagikan antar akun | Bahan custom dan bahan bawaan yang disembunyikan disimpan per pengguna. | MENUNGGU UJI LIVE |

## Checklist Fitur

| Selesai | Fitur MVP | Status pengujian | Bukti pengujian |
|---|---|---|---|
| [x] | Registrasi akun dengan validasi dan penanganan username duplikat | **Unit test: PASSED** | `test_auth_service.py`: registrasi berhasil, validasi, dan username duplikat |
| [x] | Login, penolakan kredensial salah, logout, dan informasi sesi pengguna | **Unit/API test: PASSED** | `test_auth_service.py`, `test_api_endpoints.py`: siklus autentikasi dan akses tanpa login |
| [x] | Proteksi halaman dan API yang memerlukan login | **API test: PASSED** | `test_api_endpoints.py`: akses tanpa autentikasi ditolak |
| [x] | Profil pengguna dan aktivitas akun | **Unit/API test: PASSED** | `test_auth_service.py`, `test_api_endpoints.py`: pembaruan profil dan pencatatan hari aktif |
| [x] | Menampilkan katalog bahan dan resep | **API test: PASSED** | `test_api_endpoints.py`: endpoint bahan dan resep |
| [x] | Menambah dan menghapus bahan pantry | **Unit/API test: PASSED** | `test_recipe_service.py`, `test_api_endpoints.py`: pengelolaan bahan |
| [x] | Memilih dan mencari bahan pantry | **Unit test: PASSED** untuk logika bahan; pencarian antarmuka belum memiliki tes browser khusus | `test_recipe_service.py`; pencarian antarmuka tersedia pada halaman aplikasi |
| [x] | Rekomendasi resep berdasarkan bahan yang tersedia | **Unit/API test: PASSED** | `test_recipe_service.py`, `test_api_endpoints.py`: kecocokan penuh, parsial, tanpa kecocokan, dan urutan hasil |
| [x] | Menampilkan bahan resep yang belum tersedia dan menangani bahan opsional | **Unit/API test: PASSED** | `test_recipe_service.py`, `test_api_endpoints.py`: pencocokan bahan dan data bahan resep |
| [x] | Katalog pilihan resep tinggi protein | **Unit test: PASSED** | `test_recipe_service.py`: katalog resep tinggi protein |
| [x] | Kalkulasi BMR dan TDEE berdasarkan profil dan jenis kelamin | **Unit/API test: PASSED** | `test_calorie_service.py`, `test_api_endpoints.py`: kalkulasi BMR/TDEE |
| [x] | Penyesuaian target kalori sesuai tujuan pengguna | **Unit/API test: PASSED** | `test_calorie_service.py`, `test_api_endpoints.py`: target kalori dan siklus kalkulasi |
| [x] | Kalkulasi kalori serta makronutrisi resep dan porsi | **Unit/API test: PASSED** | `test_calorie_service.py`, `test_api_endpoints.py`: kalkulator resep, porsi, satuan, dan makro |
| [x] | Pencatatan konsumsi harian beserta validasi dan akumulasi nutrisi | **Unit/API test: PASSED** | `test_tracker_service.py`, `test_calorie_service.py`, `test_api_endpoints.py` |
| [x] | Analisis anggaran kalori harian dan filter berdasarkan waktu makan | **Unit test: PASSED** | `test_tracker_service.py`: budget, progres, sisa kalori, dan filter jenis makan |
| [x] | Penghapusan catatan konsumsi | **Unit/API test: PASSED** | `test_tracker_service.py`, `test_api_endpoints.py`: siklus pengelolaan log |
| [x] | Membuat daftar belanja dari bahan resep yang belum tersedia | **Unit/API test: PASSED** | `test_shopping_service.py`, `test_api_endpoints.py`: pembuatan daftar belanja |
| [x] | Menggabungkan bahan duplikat dan mengelompokkan daftar belanja | **Unit test: PASSED** | `test_shopping_service.py`: agregasi, kategori, dan filter |
| [x] | Menandai barang sudah dibeli dan menghitung progres | **Unit/API test: PASSED** | `test_shopping_service.py`, `test_api_endpoints.py`: toggle barang dan pengelolaan daftar |
| [x] | Menghapus satu barang, barang yang selesai, atau seluruh daftar belanja | **Unit/API test: PASSED** | `test_shopping_service.py`, `test_api_endpoints.py`: hapus dan bersihkan daftar |
| [x] | Halaman login dan halaman utama aplikasi | **API test: PASSED** untuk route dan autentikasi; tampilan visual belum diuji otomatis di browser | `test_api_endpoints.py`: route login dan halaman utama |
| [x] | Menolak pencatatan resep jika bahan yang diperlukan belum tersedia | **API test: PASSED** | `test_api_endpoints.py`: resep dengan bahan yang belum tersedia tidak dapat dicatat |

## Cakupan Tes

- Unit test menguji service autentikasi, resep/pantry, kalkulasi nutrisi, tracker, dan daftar belanja.
- API test menguji route Flask, autentikasi sesi, validasi request, serta siklus fitur utama.
- Penghitungan setelah penambahan tes storage: 192 tes service/unit dan 30 tes API. Tes API tidak dihitung sebagai unit test untuk target minimal 200.
- Status **PASSED** berarti rangkaian tes otomatis di atas lulus pada saat dijalankan. Interaksi visual browser, termasuk filter pencarian di antarmuka, belum memiliki tes browser otomatis khusus.
