"""
Unit Tests untuk Fitur Inti 3: Daily NutriTracker & Calorie Budget Service (CookFit)
Memverifikasi Acceptance Criteria (AC-3):
- AC-3.1: Validasi Input & Penambahan Entri Jurnal Makanan
- AC-3.2: Akumulasi Presisi Total Kalori & Makronutrisi Harian
- AC-3.3: Analisis Anggaran Kalori (TDEE Progress %, Sisa Kuota, Status Budget)
- AC-3.4: Filtering Riwayat Konsumsi Berdasarkan Waktu Makan (Sarapan, Siang, Malam, Camilan)
- AC-3.5: Lifecycle Manajemen Jurnal (Get by ID, Delete Log, Clear Logs)
"""

import unittest
from services.tracker_service import TrackerService


class TestTrackerServiceEngine(unittest.TestCase):
    def setUp(self):
        """Inisialisasi instance TrackerService yang bersih sebelum setiap pengujian."""
        self.tracker = TrackerService()

    def test_ac1_add_log_validation(self):
        """AC-3.1: Menambahkan entri makanan dengan validasi nama dan nutrisi non-negatif."""
        # 1. Tambah data valid
        entry = self.tracker.add_log(
            recipe_title="Oatmeal Pisang",
            calories=310.5,
            protein=11.2,
            carbs=55.0,
            fat=5.5,
            meal_type="Sarapan"
        )
        self.assertEqual(entry["id"], 1)
        self.assertEqual(entry["recipe_title"], "Oatmeal Pisang")
        self.assertEqual(entry["meal_type"], "Sarapan")
        self.assertEqual(entry["calories"], 310.5)

        # 2. Uji nama kosong harus gagal
        with self.assertRaises(ValueError):
            self.tracker.add_log(recipe_title="", calories=200)

        with self.assertRaises(ValueError):
            self.tracker.add_log(recipe_title="   ", calories=200)

        # 3. Uji nilai nutrisi negatif harus gagal
        with self.assertRaises(ValueError):
            self.tracker.add_log(recipe_title="Ayam Bakar", calories=-100)

        with self.assertRaises(ValueError):
            self.tracker.add_log(recipe_title="Ayam Bakar", calories=200, protein=-5)

    def test_ac2_nutrient_accumulation(self):
        """AC-3.2: Akumulasi total kalori dan makronutrisi harian harus tepat."""
        self.tracker.add_log("Sarapan Telur Rebus", calories=140, protein=12, carbs=1, fat=10, meal_type="Sarapan")
        self.tracker.add_log("Nasi Dada Ayam", calories=450, protein=35, carbs=50, fat=8, meal_type="Makan Siang")
        self.tracker.add_log("Tumis Tahu Sayur", calories=210, protein=15, carbs=15, fat=10, meal_type="Makan Malam")

        summary = self.tracker.get_summary()
        self.assertEqual(summary["total_entries"], 3)
        self.assertEqual(summary["total_calories"], 800.0)
        self.assertEqual(summary["total_protein"], 62.0)
        self.assertEqual(summary["total_carbs"], 66.0)
        self.assertEqual(summary["total_fat"], 28.0)

    def test_ac3_calorie_budget_analysis(self):
        """AC-3.3: Perhitungan persentase progres, sisa kalori, dan status kuota budget."""
        target_tdee = 2000

        # Kasus A: Under budget (total 1000 dari 2000 = 50%)
        self.tracker.add_log("Menu 1", calories=1000)
        sum_under = self.tracker.get_summary(target_tdee=target_tdee)
        self.assertEqual(sum_under["calorie_percentage"], 50.0)
        self.assertEqual(sum_under["remaining_calories"], 1000.0)
        self.assertEqual(sum_under["budget_status"], "under_budget")

        # Kasus B: On target (tambah 950 cal -> total 1950 dari 2000 = 97.5%)
        self.tracker.add_log("Menu 2", calories=950)
        sum_target = self.tracker.get_summary(target_tdee=target_tdee)
        self.assertEqual(sum_target["calorie_percentage"], 97.5)
        self.assertEqual(sum_target["remaining_calories"], 50.0)
        self.assertEqual(sum_target["budget_status"], "on_target")

        # Kasus C: Over budget (tambah 250 cal -> total 2200 dari 2000 = 110%)
        self.tracker.add_log("Menu 3", calories=250)
        sum_over = self.tracker.get_summary(target_tdee=target_tdee)
        self.assertEqual(sum_over["calorie_percentage"], 110.0)
        self.assertEqual(sum_over["remaining_calories"], -200.0)
        self.assertEqual(sum_over["budget_status"], "over_budget")

    def test_ac4_filter_by_meal_type(self):
        """AC-3.4: Filter riwayat konsumsi berdasarkan waktu makan."""
        self.tracker.add_log("Roti Gandum", calories=150, meal_type="Sarapan")
        self.tracker.add_log("Soto Ayam", calories=380, meal_type="Makan Siang")
        self.tracker.add_log("Kacang Almond", calories=120, meal_type="Camilan")
        self.tracker.add_log("Buah Apel", calories=80, meal_type="Camilan")

        # Ambil semua
        all_logs = self.tracker.get_logs()
        self.assertEqual(len(all_logs), 4)

        # Filter Sarapan
        breakfast = self.tracker.get_logs(meal_type="Sarapan")
        self.assertEqual(len(breakfast), 1)
        self.assertEqual(breakfast[0]["recipe_title"], "Roti Gandum")

        # Filter Camilan
        snacks = self.tracker.get_logs(meal_type="Camilan")
        self.assertEqual(len(snacks), 2)

    def test_ac5_management_lifecycle(self):
        """AC-3.5: Penghapusan entri berdasarkan ID, pencarian ID, dan reset seluruh log."""
        e1 = self.tracker.add_log("Pancake Madu", calories=280)
        e2 = self.tracker.add_log("Sup Sayur", calories=120)

        # Get by ID
        found = self.tracker.get_log_by_id(e1["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["recipe_title"], "Pancake Madu")

        # Non-existent ID
        not_found = self.tracker.get_log_by_id(9999)
        self.assertIsNone(not_found)

        # Hapus e1
        deleted = self.tracker.delete_log(e1["id"])
        self.assertTrue(deleted)
        self.assertEqual(len(self.tracker.get_logs()), 1)

        # Hapus ID yang sudah tidak ada
        deleted_again = self.tracker.delete_log(e1["id"])
        self.assertFalse(deleted_again)

        # Reset all
        self.tracker.clear_logs()
        self.assertEqual(len(self.tracker.get_logs()), 0)


if __name__ == "__main__":
    unittest.main()
