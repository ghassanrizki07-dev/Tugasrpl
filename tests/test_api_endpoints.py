"""
Unit & Integration Tests untuk Flask Endpoints CookFit
Menguji rute HTTP dan respons JSON untuk kedua fitur inti:
1. Feature 1: Recipe Matching & Ingredients Endpoints
2. Feature 2: BMR Calculation & Daily NutriTracker Endpoints
"""

import unittest
import json
from app import app, calorie_service


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        calorie_service.clear_logs()

    def test_index_route(self):
        """Memverifikasi bahwa halaman web utama (/) dapat dimuat dengan HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CookFit", response.data)

    def test_api_ingredients_endpoint(self):
        """Memverifikasi bahwa /api/ingredients mengembalikan JSON daftar bahan."""
        response = self.client.get('/api/ingredients')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("Protein & Daging", data["data"])

    def test_api_match_recipes_endpoint(self):
        """Memverifikasi bahwa /api/match-recipes menghitung rekomendasi resep via POST."""
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

    def test_api_calculate_bmr_endpoint(self):
        """Memverifikasi endpoint /api/calculate-bmr menghitung BMR & TDEE dengan benar."""
        payload = {
            "gender": "male",
            "weight": 65,
            "height": 170,
            "age": 22,
            "activity_level": 1.375
        }
        response = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["tdee"], 2210)

    def test_api_calculate_bmr_invalid_data(self):
        """Memverifikasi respons HTTP 400 jika input kalkulator BMR tidak valid."""
        payload = {"gender": "unknown", "weight": -10}
        response = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_api_daily_logs_lifecycle(self):
        """Memverifikasi lifecycle lengkap Daily Log: POST -> GET -> SUMMARY -> DELETE."""
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
        self.assertEqual(logs[0]["recipe_title"], "Tumis Kangkung Telur")

        # 3. GET summary
        res_sum = self.client.get('/api/daily-summary?target_tdee=2100')
        self.assertEqual(res_sum.status_code, 200)
        summary = json.loads(res_sum.data)["data"]
        self.assertEqual(summary["total_calories"], 210.0)
        self.assertEqual(summary["calorie_percentage"], 10.0)

        # 4. DELETE log
        res_del = self.client.delete(f'/api/daily-logs/{log_id}')
        self.assertEqual(res_del.status_code, 200)

        # 5. Verify empty
        res_get2 = self.client.get('/api/daily-logs')
        self.assertEqual(len(json.loads(res_get2.data)["data"]), 0)


if __name__ == '__main__':
    unittest.main()
