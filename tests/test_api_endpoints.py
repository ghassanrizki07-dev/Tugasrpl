"""
Unit & Integration Tests untuk REST API Endpoints CookFit (US-5)
Menguji kontrak HTTP, status code, dan validasi data untuk seluruh 5 User Stories:
1. US-1: Recipe Matching & Ingredients API (/api/ingredients, /api/recipes, /api/match-recipes)
2. US-2: BMR & TDEE Health Calculator API (/api/calculate-bmr)
3. US-3: Daily NutriTracker & Calorie Budget API (/api/daily-logs, /api/daily-summary)
4. US-4: Smart Shopping List API (/api/shopping-list, /api/shopping-list/generate, toggle, clear)
5. US-5: Web Mobile App View (/)
"""

import unittest
import json
from app import app, calorie_service, tracker_service, shopping_service


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        """Menyiapkan test client dan mereset state in-memory sebelum setiap pengujian."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        calorie_service.clear_logs()
        tracker_service.clear_logs()
        shopping_service.clear_all()

    def test_index_route(self):
        """AC-5.1: Memverifikasi bahwa halaman web utama (/) dapat dimuat dengan HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CookFit", response.data)
        self.assertIn(b"Daftar Belanja Dapur", response.data)

    def test_api_ingredients_and_recipes(self):
        """AC-5.2: Memverifikasi endpoint katalog /api/ingredients dan /api/recipes."""
        # 1. Ingredients
        res_ing = self.client.get('/api/ingredients')
        self.assertEqual(res_ing.status_code, 200)
        data_ing = json.loads(res_ing.data)
        self.assertEqual(data_ing["status"], "success")
        self.assertIn("Protein & Daging", data_ing["data"])

        # 2. Recipes
        res_rec = self.client.get('/api/recipes')
        self.assertEqual(res_rec.status_code, 200)
        data_rec = json.loads(res_rec.data)
        self.assertEqual(data_rec["status"], "success")
        self.assertTrue(len(data_rec["data"]) >= 3)

    def test_api_match_recipes_endpoint(self):
        """AC-5.3: Memverifikasi /api/match-recipes menghitung rekomendasi resep via POST."""
        payload = {"ingredient_ids": [1, 4, 5]}
        response = self.client.post(
            '/api/match-recipes',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertTrue(len(data["data"]) > 0)
        self.assertEqual(data["data"][0]["match_score"], 100)

    def test_api_calculate_bmr_lifecycle(self):
        """AC-5.4: Memverifikasi /api/calculate-bmr untuk input valid (200) dan invalid (400)."""
        # Valid input
        valid_payload = {
            "gender": "male",
            "weight": 65,
            "height": 170,
            "age": 22,
            "activity_level": 1.375
        }
        res_ok = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(res_ok.status_code, 200)
        data_ok = json.loads(res_ok.data)
        self.assertEqual(data_ok["status"], "success")
        self.assertEqual(data_ok["data"]["tdee"], 2210)

        # Invalid input (berat negatif) -> Harus 400
        invalid_payload = {"gender": "female", "weight": -10, "height": 160, "age": 20}
        res_err = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(res_err.status_code, 400)
        data_err = json.loads(res_err.data)
        self.assertEqual(data_err["status"], "error")

    def test_api_daily_logs_lifecycle(self):
        """AC-5.5: Memverifikasi lifecycle lengkap Daily Log: POST -> GET -> SUMMARY -> DELETE."""
        # 1. POST add log
        log_payload = {
            "recipe_title": "Tumis Kangkung Telur",
            "calories": 210,
            "protein": 14,
            "carbs": 8,
            "fat": 12,
            "meal_type": "Makan Siang"
        }
        res_post = self.client.post(
            '/api/daily-logs',
            data=json.dumps(log_payload),
            content_type='application/json'
        )
        self.assertEqual(res_post.status_code, 201)
        created_entry = json.loads(res_post.data)["data"]
        log_id = created_entry["id"]

        # 2. GET daily logs
        res_get = self.client.get('/api/daily-logs')
        self.assertEqual(res_get.status_code, 200)
        logs = json.loads(res_get.data)["data"]
        self.assertEqual(len(logs), 1)

        # 3. GET summary
        res_sum = self.client.get('/api/daily-summary?target_tdee=2100')
        self.assertEqual(res_sum.status_code, 200)
        summary = json.loads(res_sum.data)["data"]
        self.assertEqual(summary["total_calories"], 210.0)
        self.assertEqual(summary["budget_status"], "under_budget")

        # 4. DELETE log
        res_del = self.client.delete(f'/api/daily-logs/{log_id}')
        self.assertEqual(res_del.status_code, 200)

        # 5. Verify deleted
        res_del_not_found = self.client.delete(f'/api/daily-logs/{log_id}')
        self.assertEqual(res_del_not_found.status_code, 404)

    def test_api_shopping_list_lifecycle(self):
        """AC-5.6: Memverifikasi lifecycle lengkap Shopping List: GENERATE -> GET -> TOGGLE -> CLEAR."""
        # 1. POST generate dari missing ingredients
        gen_payload = {
            "recipe_title": "Dada Ayam Tumis Bawang",
            "missing_ingredients": [
                {"id": 2, "name": "Dada Ayam", "category": "Protein", "amount": "200 gram"},
                {"id": 6, "name": "Cabai Red", "category": "Sayuran & Bumbu", "amount": "secukupnya"}
            ]
        }
        res_gen = self.client.post(
            '/api/shopping-list/generate',
            data=json.dumps(gen_payload),
            content_type='application/json'
        )
        self.assertEqual(res_gen.status_code, 201)
        data_gen = json.loads(res_gen.data)["data"]
        self.assertEqual(len(data_gen), 2)
        item_id = data_gen[0]["id"]

        # 2. GET shopping list
        res_get = self.client.get('/api/shopping-list')
        self.assertEqual(res_get.status_code, 200)
        items = json.loads(res_get.data)["data"]["items"]
        self.assertEqual(len(items), 2)

        # 3. PATCH toggle status
        res_toggle = self.client.patch(f'/api/shopping-list/{item_id}/toggle')
        self.assertEqual(res_toggle.status_code, 200)
        toggled = json.loads(res_toggle.data)["data"]
        self.assertTrue(toggled["bought"])

        # 4. DELETE clear completed only
        res_clear_comp = self.client.delete('/api/shopping-list/clear?completed_only=true')
        self.assertEqual(res_clear_comp.status_code, 200)

        # Cek sisa item
        res_rem = self.client.get('/api/shopping-list')
        items_rem = json.loads(res_rem.data)["data"]["items"]
        self.assertEqual(len(items_rem), 1)

        # 5. DELETE clear all
        res_clear_all = self.client.delete('/api/shopping-list/clear')
        self.assertEqual(res_clear_all.status_code, 200)
        res_final = self.client.get('/api/shopping-list')
        self.assertEqual(len(json.loads(res_final.data)["data"]["items"]), 0)


if __name__ == '__main__':
    unittest.main()
