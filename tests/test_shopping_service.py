"""
Unit Tests untuk Fitur Inti 4: Smart Shopping List Generator Engine (CookFit)
Memverifikasi Acceptance Criteria (AC-4):
- AC-4.1: Ekstraksi Bahan Kurang Menjadi Item Belanjaan Terstruktur
- AC-4.2: Deduplikasi & Agregasi Bahan Serupa dari Berbagai Resep
- AC-4.3: Mekanisme Checklist (Toggle Status Dibeli & Progres Persentase)
- AC-4.4: Pengelompokan & Filter Berdasarkan Kategori Bahan
- AC-4.5: Pembersihan Item Terbeli (Clear Completed) & Reset Daftar Belanja
"""

import unittest
from services.shopping_service import ShoppingService


class TestShoppingServiceEngine(unittest.TestCase):
    def setUp(self):
        """Inisialisasi ShoppingService sebelum setiap test."""
        self.shopping = ShoppingService()

    def test_ac1_generate_from_missing_ingredients(self):
        """AC-4.1: Mengonversi daftar bahan kurang menjadi item belanjaan terstruktur."""
        missing = [
            {"id": 4, "name": "Kangkung", "category": "Sayuran", "amount": "1 ikat"},
            {"id": 5, "name": "Bawang Merah", "category": "Bumbu", "amount": "3 siung"}
        ]

        items = self.shopping.generate_from_missing(missing, recipe_title="Tumis Kangkung")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["name"], "Kangkung")
        self.assertEqual(items[0]["category"], "Sayuran")
        self.assertEqual(items[0]["amount"], "1 ikat")
        self.assertFalse(items[0]["bought"])
        self.assertIn("Tumis Kangkung", items[0]["recipes"])

    def test_ac2_deduplication_and_aggregation(self):
        """AC-4.2: Menggabungkan bahan yang sama dari beberapa resep ke satu item belanja."""
        # Resep 1 butuh Bawang Merah
        self.shopping.add_item(name="Bawang Merah", category="Bumbu", amount="3 siung", recipe_source="Resep A")
        # Resep 2 juga butuh Bawang Merah
        updated = self.shopping.add_item(name="bawang merah", category="Bumbu", amount="2 siung", recipe_source="Resep B")

        items = self.shopping.get_items()
        self.assertEqual(len(items), 1)  # Tidak menduplikasi item
        self.assertEqual(updated["count"], 2)
        self.assertIn("Resep A", updated["recipes"])
        self.assertIn("Resep B", updated["recipes"])

    def test_ac3_toggle_bought_and_progress_percentage(self):
        """AC-4.3: Toggle status item belanja dan verifikasi persentase progres penyelesaian."""
        item1 = self.shopping.add_item("Telur Ayam", "Protein", "1/2 kg")
        item2 = self.shopping.add_item("Tahu Putih", "Protein", "2 kotak")
        item3 = self.shopping.add_item("Kecap Asin", "Bumbu", "1 botol")

        # Kondisi awal: 0 dari 3 dibeli (0%)
        initial_summary = self.shopping.get_summary()
        self.assertEqual(initial_summary["total_items"], 3)
        self.assertEqual(initial_summary["bought_count"], 0)
        self.assertEqual(initial_summary["completion_percentage"], 0.0)

        # Tandai item1 sebagai dibeli
        toggled = self.shopping.toggle_item(item1["id"])
        self.assertIsNotNone(toggled)
        self.assertTrue(toggled["bought"])

        # Summary setelah 1 item dibeli: 1 dari 3 = 33.3%
        mid_summary = self.shopping.get_summary()
        self.assertEqual(mid_summary["bought_count"], 1)
        self.assertEqual(mid_summary["pending_count"], 2)
        self.assertEqual(mid_summary["completion_percentage"], 33.3)

        # Tandai item2 sebagai dibeli: 2 dari 3 = 66.7%
        self.shopping.toggle_item(item2["id"])
        summary_2 = self.shopping.get_summary()
        self.assertEqual(summary_2["completion_percentage"], 66.7)

        # Uncheck item1 kembali
        uncheck = self.shopping.toggle_item(item1["id"])
        self.assertFalse(uncheck["bought"])

    def test_ac4_category_grouping_and_filtering(self):
        """AC-4.4: Pengelompokan dan pemfilteran item berdasarkan kategori dapur."""
        self.shopping.add_item("Dada Ayam", category="Protein")
        self.shopping.add_item("Telur", category="Protein")
        self.shopping.add_item("Bayam", category="Sayuran")
        self.shopping.add_item("Garam", category="Bumbu")

        summary = self.shopping.get_summary()
        self.assertEqual(summary["categories"]["Protein"], 2)
        self.assertEqual(summary["categories"]["Sayuran"], 1)
        self.assertEqual(summary["categories"]["Bumbu"], 1)

        # Filter Protein
        protein_items = self.shopping.get_items(category="Protein")
        self.assertEqual(len(protein_items), 2)

        # Filter Sayuran
        sayur_items = self.shopping.get_items(category="Sayuran")
        self.assertEqual(len(sayur_items), 1)
        self.assertEqual(sayur_items[0]["name"], "Bayam")

    def test_ac5_clear_completed_and_delete(self):
        """AC-4.5: Membersihkan item yang sudah selesai dibeli dan menghapus item individual."""
        i1 = self.shopping.add_item("Minyak Goreng")
        i2 = self.shopping.add_item("Cabai Rawit")
        i3 = self.shopping.add_item("Bawang Putih")

        # Beli i1 dan i3
        self.shopping.toggle_item(i1["id"])
        self.shopping.toggle_item(i3["id"])

        # Hapus yang sudah dibeli
        removed_count = self.shopping.clear_completed()
        self.assertEqual(removed_count, 2)

        remaining = self.shopping.get_items()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["name"], "Cabai Rawit")

        # Hapus item sisa secara manual
        del_success = self.shopping.delete_item(i2["id"])
        self.assertTrue(del_success)
        self.assertEqual(len(self.shopping.get_items()), 0)

        # Clear all
        self.shopping.add_item("Kopi Bubuk")
        self.shopping.clear_all()
        self.assertEqual(len(self.shopping.get_items()), 0)


def _make_empty_name_test(raw_name):
    """Membangun test case parameterized untuk penolakan nama belanja kosong."""
    def test_fn(self):
        with self.assertRaises(ValueError):
            self.shopping.add_item(raw_name)
    return test_fn


def _make_invalid_missing_list_test(raw_missing):
    """Membangun test case parameterized untuk generate_from_missing dengan input tidak valid."""
    def test_fn(self):
        result = self.shopping.generate_from_missing(raw_missing, recipe_title="Resep Uji")
        self.assertEqual(result, [])
    return test_fn


class TestShoppingServiceExtended(unittest.TestCase):
    def setUp(self):
        self.shopping = ShoppingService()

    def test_whitespace_trimmed_deduplication(self):
        """Nama dengan spasi dan huruf berbeda tetap teragregasi sebagai satu item."""
        self.shopping.add_item(" Garam Dapur ", "Bumbu", "1 bungkus", "Resep 1")
        updated = self.shopping.add_item("garam dapur", "Bumbu", "1 sdt", "Resep 2")
        self.assertEqual(len(self.shopping.get_items()), 1)
        self.assertEqual(updated["count"], 2)

    def test_same_recipe_source_not_duplicated(self):
        """Nama resep sumber yang sama tidak tercatat dua kali di item['recipes']."""
        self.shopping.add_item("Gula", "Bumbu", "1 sdm", "Resep X")
        updated = self.shopping.add_item("Gula", "Bumbu", "2 sdm", "Resep X")
        self.assertEqual(updated["recipes"], ["Resep X"])
        self.assertEqual(updated["count"], 2)

    def test_default_category_and_amount_fallback(self):
        """Kategori dan takaran kosong fallback ke default 'Lain-lain' dan 'secukupnya'."""
        item = self.shopping.add_item("Tisu Dapur", category="", amount="")
        self.assertEqual(item["category"], "Lain-lain")
        self.assertEqual(item["amount"], "secukupnya")

    def test_empty_summary_completion_zero(self):
        """Summary daftar kosong mengembalikan 0% progres tanpa division by zero."""
        summary = self.shopping.get_summary()
        self.assertEqual(summary["total_items"], 0)
        self.assertEqual(summary["completion_percentage"], 0.0)
        self.assertEqual(summary["categories"], {})

    def test_single_item_bought_100_percent(self):
        """Satu item yang dibeli menghasilkan 100.0% progres penyelesaian."""
        item = self.shopping.add_item("Minyak")
        self.shopping.toggle_item(item["id"])
        summary = self.shopping.get_summary()
        self.assertEqual(summary["completion_percentage"], 100.0)
        self.assertEqual(summary["pending_count"], 0)

    def test_toggle_nonexistent_id_returns_none(self):
        """Toggle pada ID item yang tidak ditemukan mengembalikan None."""
        self.assertIsNone(self.shopping.toggle_item(9999))

    def test_delete_nonexistent_id_returns_false(self):
        """Delete pada ID item yang tidak ditemukan mengembalikan False."""
        self.assertFalse(self.shopping.delete_item(9999))

    def test_clear_completed_when_none_bought_returns_zero(self):
        """clear_completed mengembalikan 0 jika belum ada item yang dicentang."""
        self.shopping.add_item("Kecap")
        self.assertEqual(self.shopping.clear_completed(), 0)
        self.assertEqual(len(self.shopping.get_items()), 1)

    def test_category_filter_case_insensitive_and_whitespace(self):
        """Filter kategori daftar belanja bersifat case-insensitive."""
        self.shopping.add_item("Tahu", category="Protein")
        items = self.shopping.get_items("  protein  ")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Tahu")

    def test_generate_from_missing_filters_malformed_rows(self):
        """Entri non-dict atau tanpa nama diabaikan tanpa error oleh generator."""
        raw = [
            "bukan dict",
            None,
            {"id": 1},
            {"id": 2, "name": "Brokoli"},
        ]
        added = self.shopping.generate_from_missing(raw, recipe_title="Sup")
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["name"], "Brokoli")
        self.assertEqual(added[0]["category"], "Bahan Dapur")
        self.assertEqual(added[0]["amount"], "1 porsi")

    def test_toggle_returns_defensive_copy(self):
        """Mutasi hasil toggle_item tidak memengaruhi data tersimpan."""
        item = self.shopping.add_item("Jahe")
        toggled = self.shopping.toggle_item(item["id"])
        toggled["name"] = "Diubah"
        self.assertEqual(self.shopping.get_items()[0]["name"], "Jahe")

    def test_category_counts_after_deletion(self):
        """Statistik kategori berkurang akurat setelah satu item dihapus."""
        i1 = self.shopping.add_item("Ayam", category="Protein")
        self.shopping.add_item("Ikan", category="Protein")
        self.shopping.delete_item(i1["id"])
        summary = self.shopping.get_summary()
        self.assertEqual(summary["categories"]["Protein"], 1)

    def test_clear_all_resets_id_counter(self):
        """clear_all mengembalikan penomoran ID item berikutnya menjadi 1."""
        self.shopping.add_item("Garam")
        self.shopping.add_item("Gula")
        self.shopping.clear_all()
        fresh = self.shopping.add_item("Merica")
        self.assertEqual(fresh["id"], 1)


for _name, _raw in [
    ("reject_empty_string_name", ""),
    ("reject_whitespace_name", "   "),
    ("reject_none_name", None),
]:
    setattr(TestShoppingServiceExtended, f"test_{_name}", _make_empty_name_test(_raw))

for _name, _missing in [
    ("generate_none_input", None),
    ("generate_empty_list", []),
    ("generate_non_list_string", "invalid"),
]:
    setattr(TestShoppingServiceExtended, f"test_{_name}", _make_invalid_missing_list_test(_missing))


if __name__ == "__main__":
    unittest.main()
