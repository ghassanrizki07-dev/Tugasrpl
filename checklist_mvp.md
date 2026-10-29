# Checklist Fitur MVP CookFit

## Status Pengujian

- **Hasil keseluruhan:** PASSED
- **Perintah:** `python -m unittest discover -s tests -v`
- **Ringkasan:** 48 tes berhasil, 0 gagal, 0 error.
- **Terakhir dijalankan:** 29 Oktober 2026

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
- Status **PASSED** berarti rangkaian tes otomatis di atas lulus pada saat dijalankan. Interaksi visual browser, termasuk filter pencarian di antarmuka, belum memiliki tes browser otomatis khusus.
