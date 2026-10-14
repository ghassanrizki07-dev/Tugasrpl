"""
Unit & Integration Tests untuk Flask Endpoints CookFit
Menguji rute HTTP dan respons JSON untuk memastikan aplikasi runnable dan endpoint berfungsi.
"""

import unittest
import json
from app import app


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_index_route(self):
        """Memverifikasi bahwa halaman web utama (/) dapat dimuat dengan HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CookFit", response.data)

    def test_api_ingredients_endpoint(self):
        """Memverifikasi bahwa /api/ingredients mengembalikan JSON daftar bahan berstatus success."""
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
        # Resep pertama dengan bahan [1, 4, 5] adalah Tumis Kangkung Telur dengan 100%
        first_recipe = data["data"][0]
        self.assertEqual(first_recipe["id"], 1)
        self.assertEqual(first_recipe["match_score"], 100)


if __name__ == '__main__':
    unittest.main()
