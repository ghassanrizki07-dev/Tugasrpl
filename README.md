# 🍳 CookFit: Web Mobile Rekomendasi Resep & Penghitung Kalori Rumahan

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/Node.js-v18%2B-green.svg)](https://nodejs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

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
