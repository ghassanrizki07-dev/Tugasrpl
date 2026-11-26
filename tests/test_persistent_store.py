import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as app_module
from services.auth_service import AuthService
from services.database import Database, create_database_for_app
from services.persistent_store import PersistentStore
from services.recipe_service import RecipeService
from services.shopping_service import ShoppingService
from services.tracker_service import TrackerService


class TestPersistentStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "cookfit.db"
        self.database = Database(url=f"sqlite:///{database_path.as_posix()}")
        auth = AuthService(database=self.database)
        self.user_a = auth.register("persistent_a", "password")["id"]
        self.user_b = auth.register("persistent_b", "password")["id"]
        self.store = PersistentStore(self.database)
        self.tracker = TrackerService(persistent_store=self.store)
        self.shopping = ShoppingService(persistent_store=self.store)
        self.recipes = RecipeService(persistent_store=self.store)

    def tearDown(self):
        self.database.engine.dispose()
        self.temp_dir.cleanup()

    def test_daily_logs_persist_and_are_scoped_by_user(self):
        log_a = self.tracker.add_log(
            "Sup Ayam", 250, protein=20, user_id=self.user_a
        )
        log_b = self.tracker.add_log(
            "Salad", 120, protein=5, user_id=self.user_b
        )

        reopened_tracker = TrackerService(
            persistent_store=PersistentStore(self.database)
        )
        self.assertEqual(
            [entry["id"] for entry in reopened_tracker.get_logs(user_id=self.user_a)],
            [log_a["id"]],
        )
        self.assertEqual(
            [entry["id"] for entry in reopened_tracker.get_logs(user_id=self.user_b)],
            [log_b["id"]],
        )
        self.assertFalse(self.tracker.delete_log(log_b["id"], user_id=self.user_a))

        self.tracker.clear_logs(user_id=self.user_a)
        self.assertEqual(reopened_tracker.get_logs(user_id=self.user_a), [])
        self.assertEqual(len(reopened_tracker.get_logs(user_id=self.user_b)), 1)

    def test_shopping_items_and_clear_are_scoped_by_user(self):
        item_a = self.shopping.add_item("Tempe", user_id=self.user_a)
        item_b = self.shopping.add_item("Tempe", user_id=self.user_b)
        self.assertNotEqual(item_a["id"], item_b["id"])
        self.assertIsNone(self.shopping.toggle_item(item_a["id"], user_id=self.user_b))

        self.shopping.clear_all(user_id=self.user_a)
        self.assertEqual(self.shopping.get_items(user_id=self.user_a), [])
        self.assertEqual(len(self.shopping.get_items(user_id=self.user_b)), 1)

    def test_custom_ingredients_are_private_to_the_creating_user(self):
        ingredient = self.recipes.add_ingredient(
            "Jamur Tiram", "Sayuran & Bumbu", user_id=self.user_a
        )
        self.assertTrue(
            any(
                item["id"] == ingredient["id"]
                for items in self.recipes.get_all_ingredients(self.user_a).values()
                for item in items
            )
        )
        self.assertFalse(
            any(
                item["id"] == ingredient["id"]
                for items in self.recipes.get_all_ingredients(self.user_b).values()
                for item in items
            )
        )
        self.assertFalse(
            self.recipes.delete_ingredient(ingredient["id"], user_id=self.user_b)
        )

    def test_api_adds_persistent_custom_ingredient_and_returns_its_category(self):
        client = app_module.app.test_client()
        with patch.object(app_module, "recipe_service", self.recipes):
            with client.session_transaction() as session:
                session["user_id"] = self.user_a

            response = client.post(
                "/api/ingredients",
                json={
                    "name": "Jamur Uji API",
                    "category": "Sayuran & Bumbu",
                    "calories_per_100g": 35,
                },
            )

        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["category"], "Sayuran & Bumbu")
        self.assertEqual(body["data"]["name"], "Jamur Uji API")

    def test_vercel_requires_a_postgresql_database_url(self):
        with patch.dict(os.environ, {"VERCEL": "1", "DATABASE_URL": ""}):
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL must be configured"):
                create_database_for_app()

        with patch.dict(
            os.environ,
            {"VERCEL": "1", "DATABASE_URL": "sqlite:///temporary.db"},
        ):
            with self.assertRaisesRegex(RuntimeError, "must point to a PostgreSQL"):
                create_database_for_app()
