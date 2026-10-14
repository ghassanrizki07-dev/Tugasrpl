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


if __name__ == "__main__":
    unittest.main()
