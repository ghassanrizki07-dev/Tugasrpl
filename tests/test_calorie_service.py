"""
Unit Tests untuk Fitur Inti 2: Calorie & NutriTracker Engine (CookFit)
Memverifikasi Acceptance Criteria (AC):
- AC-2.1: Akurasi Perhitungan BMR & TDEE Pria (rumus Mifflin-St Jeor +5)
- AC-2.2: Akurasi Perhitungan BMR & TDEE Wanita (rumus Mifflin-St Jeor -161)
- AC-2.3: Validasi Batas & Error Handling Input Fisik (BB, TB, Usia, Gender)
- AC-2.4: Pengelolaan Log Nutrisi Harian (Add, Accumulate Macro/Calorie, Delete)
"""

import unittest
from services.calorie_service import CalorieService


class TestCalorieAndNutriTrackerEngine(unittest.TestCase):
    def setUp(self):
        """Inisialisasi service untuk pengujian kalkulator kalori dan tracker."""
        self.service = CalorieService()
        self.service.clear_logs()

    def test_ac1_male_bmr_and_tdee(self):
        """
        AC-2.1: BMR Pria = (10*BB) + (6.25*TB) - (5*Usia) + 5
        Contoh: Pria BB=65kg, TB=170cm, Usia=22thn, Aktivitas=1.375
        BMR = (10*65) + (6.25*170) - (5*22) + 5 = 650 + 1062.5 - 110 + 5 = 1607.5 kcal
        TDEE = 1607.5 * 1.375 = 2210.31 -> 2210 kcal
        """
        bmr = self.service.calculate_bmr(gender="male", weight_kg=65, height_cm=170, age_years=22)
        self.assertAlmostEqual(bmr, 1607.5, places=1)

        tdee = self.service.calculate_tdee(bmr, 1.375)
        self.assertEqual(tdee, 2210)

        # Uji metrik profil terpadu
        profile = self.service.calculate_profile_metrics("male", 65, 170, 22, 1.375)
        self.assertEqual(profile["tdee"], 2210)
        self.assertTrue(profile["target_macros"]["protein_grams"] > 0)
        self.assertTrue(profile["target_macros"]["carbs_grams"] > 0)

    def test_ac2_female_bmr_and_tdee(self):
        """
        AC-2.2: BMR Wanita = (10*BB) + (6.25*TB) - (5*Usia) - 161
        Contoh: Wanita BB=55kg, TB=160cm, Usia=24thn, Aktivitas=1.2 (Sedentary)
        BMR = (10*55) + (6.25*160) - (5*24) - 161 = 550 + 1000 - 120 - 161 = 1269.0 kcal
        TDEE = 1269.0 * 1.2 = 1522.8 -> 1523 kcal
        """
        bmr = self.service.calculate_bmr(gender="female", weight_kg=55, height_cm=160, age_years=24)
        self.assertAlmostEqual(bmr, 1269.0, places=1)

        tdee = self.service.calculate_tdee(bmr, 1.2)
        self.assertEqual(tdee, 1523)

    def test_ac3_validation_and_invalid_inputs(self):
        """AC-2.3: Input invalid harus memicu ValueError yang jelas."""
        # Gender tidak valid
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(gender="robot", weight_kg=60, height_cm=160, age_years=25)

        # Berat badan di luar rentang realistis
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(gender="male", weight_kg=-5, height_cm=170, age_years=20)
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(gender="male", weight_kg=999, height_cm=170, age_years=20)

        # Tinggi badan di luar rentang realistis
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(gender="female", weight_kg=50, height_cm=0, age_years=20)

        # Usia tidak masuk akal
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(gender="male", weight_kg=60, height_cm=170, age_years=-1)

        # BMR negatif atau tingkat aktivitas di luar batas
        with self.assertRaises(ValueError):
            self.service.calculate_tdee(bmr=-100, activity_level=1.375)
        with self.assertRaises(ValueError):
            self.service.calculate_tdee(bmr=1500, activity_level=0.5)

    def test_ac4_daily_logs_and_accumulation(self):
        """AC-2.4: Pencatatan jurnal makan harian, akumulasi makronutrisi, dan penghapusan entri."""
        # 1. Tambah makan siang
        entry1 = self.service.add_daily_log(
            recipe_title="Tumis Kangkung Telur",
            calories=210,
            protein=14,
            carbs=8,
            fat=12,
            meal_type="Makan Siang"
        )
        self.assertEqual(entry1["recipe_title"], "Tumis Kangkung Telur")
        self.assertEqual(entry1["calories"], 210)

        # 2. Tambah camilan sore
        entry2 = self.service.add_daily_log(
            recipe_title="Omelet Tahu Sehat",
            calories=250,
            protein=18,
            carbs=6,
            fat=15,
            meal_type="Makan Malam"
        )

        logs = self.service.get_daily_logs()
        self.assertEqual(len(logs), 2)

        # 3. Akumulasi ringkasan harian
        summary = self.service.get_daily_summary(target_tdee=2000)
        self.assertEqual(summary["total_calories"], 460)  # 210 + 250
        self.assertEqual(summary["total_protein"], 32)    # 14 + 18
        self.assertEqual(summary["total_carbs"], 14)      # 8 + 6
        self.assertEqual(summary["total_fat"], 27)        # 12 + 15
        self.assertAlmostEqual(summary["calorie_percentage"], 23.0, places=1) # (460/2000)*100 = 23%

        # 4. Hapus satu entri
        deleted = self.service.delete_daily_log(entry1["id"])
        self.assertTrue(deleted)
        self.assertEqual(len(self.service.get_daily_logs()), 1)

        # Summary setelah dihapus
        summary_after = self.service.get_daily_summary(target_tdee=2000)
        self.assertEqual(summary_after["total_calories"], 250)


if __name__ == "__main__":
    unittest.main()
