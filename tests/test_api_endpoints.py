"""
Unit & Integration Tests untuk REST API Endpoints CookFit (US-0 - US-5)
Menguji kontrak HTTP, status code, session authentication, dan validasi data untuk seluruh User Stories:
0. US-0: Authentication API (/api/auth/register, /api/auth/login, /api/auth/me, /api/auth/logout)
1. US-1: Recipe Matching & Ingredients API (/api/ingredients, /api/recipes, /api/match-recipes)
2. US-2: BMR & TDEE Health Calculator API (/api/calculate-bmr)
3. US-3: Daily NutriTracker & Calorie Budget API (/api/daily-logs, /api/daily-summary)
4. US-4: Smart Shopping List API (/api/shopping-list, /api/shopping-list/generate, toggle, clear)
5. US-5: Web Mobile App View (/) & Login View (/login)
"""

import unittest
import json
from app import app, calorie_service, tracker_service, shopping_service, auth_service


class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        """Menyiapkan test client, membersihkan data, dan menyiapkan session user."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        calorie_service.clear_logs()
        tracker_service.clear_logs()
        shopping_service.clear_all()

        # Buat user test jika belum ada
        self.test_username = "testuser_api"
        self.test_password = "password123"
        try:
            auth_service.register(self.test_username, self.test_password, "Test User API")
        except ValueError:
            pass  # User sudah terdaftar di DB sebelumnya

    def _login_session(self):
        """Helper untuk mengatur session login pada test client."""
        user = auth_service.login(self.test_username, self.test_password)
        with self.client.session_transaction() as sess:
            sess['user_id'] = user['id']
            sess['username'] = user['username']
            sess['display_name'] = user['display_name']
        return user

    # ==========================================
    # US-0: AUTHENTICATION TESTS
    # ==========================================
    def test_unauthenticated_access_protection(self):
        """AC-0.1: Memverifikasi route terlindungi menolak user yang belum login."""
        # Akses halaman / tanpa login -> Redirect (302) ke /login
        res_page = self.client.get('/')
        self.assertEqual(res_page.status_code, 302)
        self.assertIn('/login', res_page.headers['Location'])

        # Akses API tanpa login -> 401 Unauthorized
        res_api = self.client.get('/api/ingredients')
        self.assertEqual(res_api.status_code, 401)
        data = json.loads(res_api.data)
        self.assertEqual(data["status"], "error")

    def test_auth_register_and_login_lifecycle(self):
        """AC-0.2: Memverifikasi siklus registrasi, login, me, dan logout."""
        import time
        unique_user = f"user_{int(time.time() * 1000)}"

        # 1. Register baru
        reg_payload = {
            "username": unique_user,
            "password": "mypassword",
            "display_name": "New Explorer"
        }
        res_reg = self.client.post(
            '/api/auth/register',
            data=json.dumps(reg_payload),
            content_type='application/json'
        )
        self.assertEqual(res_reg.status_code, 201)
        data_reg = json.loads(res_reg.data)
        self.assertEqual(data_reg["status"], "success")

        # 2. Get current user (/api/auth/me) setelah register
        res_me = self.client.get('/api/auth/me')
        self.assertEqual(res_me.status_code, 200)
        data_me = json.loads(res_me.data)["data"]
        self.assertEqual(data_me["username"], unique_user)
        self.assertEqual(data_me["active_days"], 1)
        self.assertIn("created_at", data_me)

        # Repeated use on the same calendar day must not inflate active days.
        res_me_again = self.client.get('/api/auth/me')
        self.assertEqual(res_me_again.status_code, 200)
        self.assertEqual(json.loads(res_me_again.data)["data"]["active_days"], 1)

        # 3. Logout
        res_logout = self.client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)

        # 4. Verify logged out (/api/auth/me harus 401)
        res_me_after = self.client.get('/api/auth/me')
        self.assertEqual(res_me_after.status_code, 401)

        # 5. Login kembali dengan password yang benar
        res_login = self.client.post(
            '/api/auth/login',
            data=json.dumps({"username": unique_user, "password": "mypassword"}),
            content_type='application/json'
        )
        self.assertEqual(res_login.status_code, 200)

        # 6. Login dengan password salah -> 401
        res_bad_login = self.client.post(
            '/api/auth/login',
            data=json.dumps({"username": unique_user, "password": "wrongpassword"}),
            content_type='application/json'
        )
        self.assertEqual(res_bad_login.status_code, 401)

    def test_login_page_route(self):
        """AC-0.3: Memverifikasi halaman login dapat diakses dengan HTTP 200."""
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"CookFit", res.data)
        self.assertIn(b"Masuk ke akun CookFit", res.data)

    # ==========================================
    # US-1 - US-5: PROTECTED CORE FEATURES
    # ==========================================
    def test_index_route_authenticated(self):
        """AC-5.1: Memverifikasi bahwa halaman web utama (/) dapat dimuat dengan HTTP 200 jika sudah login."""
        self._login_session()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CookFit", response.data)
        self.assertIn(b"Tambah Bahan ke Pantry", response.data)

    def test_api_ingredients_and_recipes(self):
        """AC-5.2: Memverifikasi endpoint katalog /api/ingredients dan /api/recipes."""
        self._login_session()
        # 1. Ingredients GET
        res_ing = self.client.get('/api/ingredients')
        self.assertEqual(res_ing.status_code, 200)
        data_ing = json.loads(res_ing.data)
        self.assertEqual(data_ing["status"], "success")
        self.assertIn("Protein & Daging", data_ing["data"])
        pantry_ingredient_names = {
            ingredient["name"]
            for ingredients in data_ing["data"].values()
            for ingredient in ingredients
        }
        self.assertTrue({"Tuna Kaleng", "Edamame", "Brokoli", "Timun"}.isdisjoint(pantry_ingredient_names))

        # Bahan resep tambahan baru masuk Pantry setelah ditambahkan lewat fitur tambah bahan.
        res_optional = self.client.post(
            '/api/ingredients',
            data=json.dumps({
                "name": "Tuna Kaleng",
                "category": "Sayuran & Bumbu",
                "calories_per_100g": 50
            }),
            content_type='application/json'
        )
        self.assertEqual(res_optional.status_code, 201)
        optional_item = json.loads(res_optional.data)["data"]
        self.assertEqual(optional_item["id"], 7)
        self.assertEqual(json.loads(res_optional.data)["category"], "Protein & Daging")

        res_optional_match = self.client.post(
            '/api/match-recipes',
            data=json.dumps({"ingredient_ids": [7]}),
            content_type='application/json'
        )
        matched_tuna_recipe = next(
            recipe for recipe in json.loads(res_optional_match.data)["data"]
            if recipe["id"] == 7
        )
        self.assertEqual(matched_tuna_recipe["match_score"], 33)
        self.assertIn("Brokoli", [item["name"] for item in matched_tuna_recipe["missing_ingredients"]])
        self.client.delete(f'/api/ingredients/{optional_item["id"]}')

        # 2. Ingredients POST (tambah bahan baru ke kategori tertentu)
        post_payload = {
            "name": "Daging Sapi Segar",
            "category": "Protein & Daging",
            "calories_per_100g": 250
        }
        res_post = self.client.post(
            '/api/ingredients',
            data=json.dumps(post_payload),
            content_type='application/json'
        )
        self.assertEqual(res_post.status_code, 201)
        created_item = json.loads(res_post.data)["data"]
        self.assertEqual(created_item["name"], "Daging Sapi Segar")

        # 3. Ingredients DELETE
        res_del = self.client.delete(f'/api/ingredients/{created_item["id"]}')
        self.assertEqual(res_del.status_code, 200)

        # 4. Recipes GET
        res_rec = self.client.get('/api/recipes')
        self.assertEqual(res_rec.status_code, 200)
        data_rec = json.loads(res_rec.data)
        self.assertEqual(data_rec["status"], "success")
        self.assertTrue(len(data_rec["data"]) >= 3)

    def test_api_match_recipes_endpoint(self):
        """AC-5.3: Memverifikasi /api/match-recipes menghitung rekomendasi resep via POST."""
        self._login_session()
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
        self._login_session()
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
        self.assertEqual(data_ok["data"]["daily_calorie_target"], 2210)

        valid_payload["goal"] = "cutting"
        res_cutting = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        data_cutting = json.loads(res_cutting.data)
        self.assertEqual(res_cutting.status_code, 200)
        self.assertEqual(data_cutting["data"]["daily_calorie_target"], 1910)
        self.assertEqual(
            auth_service.get_user_by_id(self._login_session()["id"])["goal"],
            "cutting"
        )

        valid_payload["goal"] = "bulking"
        res_bulking = self.client.post(
            '/api/calculate-bmr',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        data_bulking = json.loads(res_bulking.data)
        self.assertEqual(res_bulking.status_code, 200)
        self.assertEqual(data_bulking["data"]["daily_calorie_target"], 2510)

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
        self._login_session()
        # 1. POST add log
        log_payload = {
            "recipe_id": 1,
            "ingredient_ids": [1, 4, 5],
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

    def test_recipe_with_missing_ingredients_cannot_be_logged(self):
        """Resep hanya bisa dicatat jika semua bahan yang dibutuhkan dipilih."""
        self._login_session()
        payload = {
            "recipe_id": 3,
            "ingredient_ids": [2, 5],
            "recipe_title": "Dada Ayam Tumis Bawang",
            "calories": 320,
            "protein": 35,
            "carbs": 5,
            "fat": 10
        }

        rejected = self.client.post(
            '/api/daily-logs',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(rejected.status_code, 400)
        self.assertIn("Cabai Merah", json.loads(rejected.data)["message"])
        self.assertEqual(json.loads(self.client.get('/api/daily-logs').data)["data"], [])

        payload.pop("recipe_id")
        omitted_id_rejected = self.client.post(
            '/api/daily-logs',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(omitted_id_rejected.status_code, 400)

        payload["ingredient_ids"] = [2, 5, 6]
        accepted = self.client.post(
            '/api/daily-logs',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(accepted.status_code, 201)
        self.assertEqual(len(json.loads(self.client.get('/api/daily-logs').data)["data"]), 1)

    def test_api_shopping_list_lifecycle(self):
        """AC-5.6: Memverifikasi lifecycle lengkap Shopping List: GENERATE -> GET -> TOGGLE -> CLEAR."""
        self._login_session()
        # 1. POST generate dari missing ingredients
        gen_payload = {
            "recipe_title": "Dada Ayam Tumis Bawang",
            "missing_ingredients": [
                {"id": 2, "name": "Dada Ayam", "category": "Protein", "amount": "200 gram"},
                {"id": 6, "name": "Cabai Merah", "category": "Sayuran & Bumbu", "amount": "secukupnya"}
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

    def test_api_cooking_portion_and_recipe_calculator(self):
        """Memverifikasi API kalkulator takaran masakan dan resep multi-bahan."""
        self._login_session()

        # 1. Preview takaran tunggal: 250 gram Daging Ayam
        portion_payload = {
            "name": "Daging Ayam",
            "amount": 250,
            "unit": "gram"
        }
        res_portion = self.client.post(
            '/api/calculate-cooking/portion',
            data=json.dumps(portion_payload),
            content_type='application/json'
        )
        self.assertEqual(res_portion.status_code, 200)
        data_portion = json.loads(res_portion.data)["data"]
        self.assertEqual(data_portion["total_grams"], 250.0)
        self.assertEqual(data_portion["calories"], 475.0) # 2.5 * 190
        self.assertEqual(data_portion["protein"], 67.5)   # 2.5 * 27

        # 2. Preview satuan siung: 4 siung Bawang Merah (4 * 5g = 20g)
        siung_payload = {
            "name": "Bawang Merah",
            "amount": 4,
            "unit": "siung"
        }
        res_siung = self.client.post(
            '/api/calculate-cooking/portion',
            data=json.dumps(siung_payload),
            content_type='application/json'
        )
        self.assertEqual(res_siung.status_code, 200)
        data_siung = json.loads(res_siung.data)["data"]
        self.assertEqual(data_siung["total_grams"], 20.0)

        # 3. Hitung total resep gabungan: Ayam 200g + Tahu 100g
        recipe_payload = {
            "items": [
                {"name": "Daging Ayam", "amount": 200, "unit": "gram"},
                {"name": "Tahu", "amount": 100, "unit": "gram"}
            ]
        }
        res_recipe = self.client.post(
            '/api/calculate-cooking',
            data=json.dumps(recipe_payload),
            content_type='application/json'
        )
        self.assertEqual(res_recipe.status_code, 200)
        data_recipe = json.loads(res_recipe.data)["data"]
        self.assertEqual(data_recipe["total_grams"], 300.0)
        self.assertEqual(data_recipe["total_calories"], 456.0) # 380 + 76
        self.assertEqual(data_recipe["total_protein"], 62.0)   # 54 + 8
        self.assertEqual(len(data_recipe["items"]), 2)

        # 4. Error validation: nama kosong
        bad_portion = {"name": "", "amount": 100, "unit": "gram"}
        res_bad = self.client.post(
            '/api/calculate-cooking/portion',
            data=json.dumps(bad_portion),
            content_type='application/json'
        )
        self.assertEqual(res_bad.status_code, 400)


if __name__ == '__main__':
    unittest.main()
