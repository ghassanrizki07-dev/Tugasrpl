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


def _make_budget_threshold_test(calories, target_tdee, expected_pct, expected_status, expected_remaining):
    """Membangun test case parameterized untuk threshold budget kalori."""
    def test_fn(self):
        if calories > 0:
            self.tracker.add_log("Menu Uji", calories=calories)
        summary = self.tracker.get_summary(target_tdee=target_tdee)
        self.assertEqual(summary["calorie_percentage"], expected_pct)
        self.assertEqual(summary["budget_status"], expected_status)
        self.assertEqual(summary["remaining_calories"], expected_remaining)
    return test_fn


def _make_invalid_nutrition_test(kwargs):
    """Membangun test case parameterized untuk input nutrisi invalid pada TrackerService."""
    def test_fn(self):
        with self.assertRaises(ValueError):
            self.tracker.add_log("Menu Invalid", **kwargs)
    return test_fn


class TestTrackerServiceExtended(unittest.TestCase):
    def setUp(self):
        self.tracker = TrackerService()

    def test_decimal_macro_rounding(self):
        """Nilai kalori dan makro desimal dibulatkan ke 1 angka di belakang koma."""
        entry = self.tracker.add_log("Salad", calories=123.456, protein=10.24, carbs=15.67, fat=3.14)
        self.assertEqual(entry["calories"], 123.5)
        self.assertEqual(entry["protein"], 10.2)
        self.assertEqual(entry["carbs"], 15.7)
        self.assertEqual(entry["fat"], 3.1)

    def test_zero_calorie_log_allowed(self):
        """Entri makanan/minuman nol kalori tetap diperbolehkan dicatat."""
        entry = self.tracker.add_log("Air Mineral", calories=0, protein=0, carbs=0, fat=0)
        self.assertEqual(entry["calories"], 0.0)
        self.assertEqual(len(self.tracker.get_logs()), 1)

    def test_empty_meal_type_defaults_to_makan_siang(self):
        """Meal type kosong atau None default ke 'Makan Siang'."""
        entry = self.tracker.add_log("Nasi Uduk", calories=300, meal_type="")
        self.assertEqual(entry["meal_type"], "Makan Siang")

    def test_filter_meal_type_case_insensitive_and_whitespace(self):
        """Filter waktu makan bersifat case-insensitive dan mengabaikan spasi."""
        self.tracker.add_log("Bubur", calories=200, meal_type="Sarapan")
        self.tracker.add_log("Bakso", calories=400, meal_type="Makan Siang")
        self.assertEqual(len(self.tracker.get_logs("  sarapan  ")), 1)
        self.assertEqual(len(self.tracker.get_logs("SARAPAN")), 1)

    def test_filter_nonexistent_meal_type_returns_empty(self):
        """Filter waktu makan yang belum ada mengembalikan list kosong."""
        self.tracker.add_log("Bubur", calories=200, meal_type="Sarapan")
        self.assertEqual(self.tracker.get_logs("Tengah Malam"), [])

    def test_empty_summary_zero_totals(self):
        """Ringkasan saat log masih kosong bernilai nol tanpa error."""
        summary = self.tracker.get_summary(target_tdee=2000)
        self.assertEqual(summary["total_entries"], 0)
        self.assertEqual(summary["total_calories"], 0.0)
        self.assertEqual(summary["calorie_percentage"], 0.0)

    def test_id_sequence_monotonic_after_delete(self):
        """ID tetap bertambah secara berurutan meski entri sebelumnya dihapus."""
        e1 = self.tracker.add_log("A", calories=100)
        self.tracker.delete_log(e1["id"])
        e2 = self.tracker.add_log("B", calories=150)
        self.assertEqual(e2["id"], 2)

    def test_get_log_by_id_returns_copy(self):
        """Mutasi hasil get_log_by_id tidak merusak state internal tracker."""
        e1 = self.tracker.add_log("Roti", calories=150)
        fetched = self.tracker.get_log_by_id(e1["id"])
        fetched["calories"] = 9999
        self.assertEqual(self.tracker.get_log_by_id(e1["id"])["calories"], 150.0)

    def test_logs_ordered_newest_first(self):
        """Log terbaru muncul pada urutan pertama (index 0)."""
        self.tracker.add_log("Pertama", calories=100)
        self.tracker.add_log("Kedua", calories=200)
        logs = self.tracker.get_logs()
        self.assertEqual([l["recipe_title"] for l in logs], ["Kedua", "Pertama"])


for _name, _cal, _tdee, _pct, _status, _rem in [
    ("budget_under_threshold", 1899, 2000, 95.0, "on_target", 101.0),
    ("budget_strict_under", 1800, 2000, 90.0, "under_budget", 200.0),
    ("budget_exact_95_pct", 1900, 2000, 95.0, "on_target", 100.0),
    ("budget_exact_105_pct", 2100, 2000, 105.0, "on_target", -100.0),
    ("budget_over_105_pct", 2102, 2000, 105.1, "over_budget", -102.0),
    ("budget_zero_tdee_untracked", 500, 0, 0.0, "untracked", None),
]:
    setattr(
        TestTrackerServiceExtended,
        f"test_{_name}",
        _make_budget_threshold_test(_cal, _tdee, _pct, _status, _rem)
    )

for _name, _kwargs in [
    ("invalid_negative_carbs", {"calories": 100, "carbs": -1}),
    ("invalid_negative_fat", {"calories": 100, "fat": -0.5}),
    ("invalid_non_numeric_calories", {"calories": "banyak"}),
    ("invalid_non_numeric_protein", {"calories": 100, "protein": "x"}),
    ("invalid_none_calories", {"calories": None}),
    ("invalid_none_fat", {"calories": 100, "fat": None}),
]:
    setattr(TestTrackerServiceExtended, f"test_{_name}", _make_invalid_nutrition_test(_kwargs))


if __name__ == "__main__":
    unittest.main()
