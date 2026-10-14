"""
Unit Tests untuk Fitur Inti 1: Recipe Matching Engine (CookFit)
Memverifikasi Acceptance Criteria (AC):
- AC-1.1: Full Match (100% score jika semua bahan terpenuhi, missing=0)
- AC-1.2: Partial Match (persentase akurat proporsional dengan jumlah bahan yang ada)
- AC-1.3: Zero Match / Empty Input (0% score, semua bahan masuk list missing)
- AC-1.4: Sorting Order (resep terurut descending berdasarkan match_score)
- AC-1.5: Robust Input Handling (penanganan format input non-list, None, tipe string)
"""

import unittest
from services.recipe_service import RecipeService


class TestRecipeMatchingEngine(unittest.TestCase):
    def setUp(self):
        """Inisialisasi service dengan dataset mock terkontrol untuk pengujian."""
        self.mock_ingredients = {
            "Protein": [
                {"id": 1, "name": "Telur Ayam", "calories_per_100g": 155},
                {"id": 2, "name": "Dada Ayam", "calories_per_100g": 165},
                {"id": 3, "name": "Tahu Putih", "calories_per_100g": 76}
            ],
            "Sayuran": [
                {"id": 4, "name": "Kangkung", "calories_per_100g": 19},
                {"id": 5, "name": "Bawang Merah & Putih", "calories_per_100g": 40},
                {"id": 6, "name": "Cabai Red", "calories_per_100g": 40}
            ]
        }

        self.mock_recipes = [
            {
                "id": 1,
                "title": "Tumis Kangkung Telur",
                "required_ids": [1, 4, 5],
                "servings": 2
            },
            {
                "id": 2,
                "title": "Omelet Tahu Sehat",
                "required_ids": [1, 3, 5],
                "servings": 1
            },
            {
                "id": 3,
                "title": "Dada Ayam Tumis Bawang",
                "required_ids": [2, 5, 6],
                "servings": 2
            }
        ]

        self.service = RecipeService(
            ingredients_data=self.mock_ingredients,
            recipes_data=self.mock_recipes
        )

    def test_ac1_full_match(self):
        """AC-1.1: Jika semua bahan resep dimiliki pengguna, skor harus 100% dan missing kosong."""
        # Resep 1 (Tumis Kangkung Telur) butuh ID: [1, 4, 5]
        selected_ids = [1, 4, 5]
        results = self.service.match_recipes(selected_ids)

        # Cari resep 1 dalam hasil
        recipe_1 = next(r for r in results if r["id"] == 1)
        self.assertEqual(recipe_1["match_score"], 100)
        self.assertEqual(len(recipe_1["missing_ingredients"]), 0)
        self.assertEqual(recipe_1["matched_count"], 3)
        self.assertEqual(recipe_1["total_required"], 3)

    def test_ac2_partial_match(self):
        """AC-1.2: Jika hanya sebagian bahan yang dimiliki, skor harus proporsional."""
        # Resep 1 butuh [1, 4, 5]. Pengguna hanya punya [1, 4] -> 2 dari 3 bahan (67%)
        selected_ids = [1, 4]
        results = self.service.match_recipes(selected_ids)

        recipe_1 = next(r for r in results if r["id"] == 1)
        self.assertEqual(recipe_1["match_score"], 67)
        self.assertEqual(recipe_1["matched_count"], 2)
        self.assertEqual(len(recipe_1["missing_ingredients"]), 1)
        self.assertEqual(recipe_1["missing_ingredients"][0]["id"], 5)
        self.assertEqual(recipe_1["missing_ingredients"][0]["name"], "Bawang Merah & Putih")

    def test_ac3_zero_match_empty_selection(self):
        """AC-1.3: Jika pengguna tidak memilih bahan apa pun, skor harus 0%."""
        results = self.service.match_recipes([])
        for r in results:
            self.assertEqual(r["match_score"], 0)
            self.assertEqual(r["matched_count"], 0)
            self.assertEqual(len(r["missing_ingredients"]), r["total_required"])

    def test_ac4_sorting_order(self):
        """AC-1.4: Hasil harus terurut descending dari skor tertinggi ke terendah."""
        # Pengguna punya [2, 5, 6] (Resep 3 = 100%, Resep 1 = 33%, Resep 2 = 33%)
        selected_ids = [2, 5, 6]
        results = self.service.match_recipes(selected_ids)

        # Cek urutan
        scores = [r["match_score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(results[0]["id"], 3)
        self.assertEqual(results[0]["match_score"], 100)

    def test_ac5_robust_invalid_inputs(self):
        """AC-1.5: Input invalid (None, string IDs, tipe salah) tidak boleh memicu exception."""
        # Test input None
        res_none = self.service.match_recipes(None)
        self.assertEqual(len(res_none), 3)

        # Test string IDs yang bisa dikonversi ('1', '4')
        res_str = self.service.match_recipes(["1", "4", "invalid_item"])
        recipe_1 = next(r for r in res_str if r["id"] == 1)
        self.assertEqual(recipe_1["match_score"], 67)

        # Test non-iterable input
        res_int = self.service.match_recipes(12345)
        self.assertEqual(len(res_int), 3)


if __name__ == "__main__":
    unittest.main()
