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

    def test_goal_adjusts_daily_calorie_target(self):
        """Cutting mengurangi 300 kcal dan bulking menambah 300 kcal dari TDEE."""
        cutting = self.service.calculate_profile_metrics(
            "male", 65, 170, 22, 1.375, goal="cutting"
        )
        bulking = self.service.calculate_profile_metrics(
            "male", 65, 170, 22, 1.375, goal="bulking"
        )

        self.assertEqual(cutting["calorie_adjustment"], -300)
        self.assertEqual(cutting["daily_calorie_target"], 1910)
        self.assertEqual(bulking["calorie_adjustment"], 300)
        self.assertEqual(bulking["daily_calorie_target"], 2510)

        low_tdee_cutting = self.service.calculate_profile_metrics(
            "female", 55, 160, 24, 1.2, goal="cutting"
        )
        self.assertEqual(
            low_tdee_cutting["daily_calorie_target"],
            low_tdee_cutting["bmr"]
        )
        self.assertEqual(
            low_tdee_cutting["calorie_adjustment"],
            low_tdee_cutting["bmr"] - low_tdee_cutting["tdee"]
        )

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

    def test_ac5_portion_calculator_grams_and_units(self):
        """Uji takaran bahan dalam gram, siung, butir, dan satuan masak lainnya."""
        # 200 gram daging ayam (daging ayam = 190 kcal / 100g, 27g protein / 100g)
        ayam = self.service.calculate_ingredient_portion("Daging Ayam", 200, "gram")
        self.assertEqual(ayam["total_grams"], 200.0)
        self.assertEqual(ayam["calories"], 380.0)
        self.assertEqual(ayam["protein"], 54.0)

        # 3 siung bawang putih (1 siung = 5g -> total 15g)
        bawang = self.service.calculate_ingredient_portion("Bawang Putih", 3, "siung")
        self.assertEqual(bawang["total_grams"], 15.0)
        self.assertAlmostEqual(bawang["calories"], 22.3, places=1) # 15g / 100g * 149 = 22.35 (banker's rounding -> 22.3)
        self.assertAlmostEqual(bawang["protein"], 1.0, places=1)

        # 2 butir telur (1 butir = 50g -> total 100g, telur = 155 kcal, 13g protein)
        telur = self.service.calculate_ingredient_portion("Telur", 2, "butir")
        self.assertEqual(telur["total_grams"], 100.0)
        self.assertEqual(telur["calories"], 155.0)
        self.assertEqual(telur["protein"], 13.0)

        # 100 gram tahu (tahu = 76 kcal, 8g protein)
        tahu = self.service.calculate_ingredient_portion("Tahu", 100, "gram")
        self.assertEqual(tahu["total_grams"], 100.0)
        self.assertEqual(tahu["calories"], 76.0)
        self.assertEqual(tahu["protein"], 8.0)

    def test_ac6_portion_calculator_custom_macros_and_validation(self):
        """Uji takaran bahan kustom per 100g dan penanganan error."""
        # Bahan custom: 150g bahan X dengan 200 kcal/100g dan 20g protein/100g
        custom = self.service.calculate_ingredient_portion(
            name="Bahan Rahasia",
            amount=150,
            unit="gram",
            cal_per_100g=200,
            protein_per_100g=20
        )
        self.assertEqual(custom["total_grams"], 150.0)
        self.assertEqual(custom["calories"], 300.0)
        self.assertEqual(custom["protein"], 30.0)

        # Error validation
        with self.assertRaises(ValueError):
            self.service.calculate_ingredient_portion("", 100, "gram")

        with self.assertRaises(ValueError):
            self.service.calculate_ingredient_portion("Ayam", -10, "gram")

    def test_ac7_calculate_cooking_recipe_multi_ingredients(self):
        """Uji perhitungan resep masakan lengkap (kombinasi beberapa bahan)."""
        recipe_items = [
            {"name": "Daging Ayam", "amount": 200, "unit": "gram"},
            {"name": "Tahu", "amount": 100, "unit": "gram"},
            {"name": "Bawang Putih", "amount": 2, "unit": "siung"} # 10g
        ]
        result = self.service.calculate_cooking_recipe(recipe_items)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["total_grams"], 310.0) # 200 + 100 + 10
        # 380 kcal (ayam) + 76 kcal (tahu) + 14.9 kcal (bawang 10g) = 470.9 kcal
        self.assertAlmostEqual(result["total_calories"], 470.9, places=1)
        # 54g (ayam) + 8g (tahu) + 0.6g (bawang) = 62.6g
        self.assertAlmostEqual(result["total_protein"], 62.6, places=1)



if __name__ == "__main__":
    unittest.main()
