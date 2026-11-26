from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, insert, select, update

from services.database import Database


CUSTOM_INGREDIENT_ID_OFFSET = 1_000_000
APP_TIMEZONE = ZoneInfo("Asia/Jakarta")


def current_app_date():
    return datetime.now(APP_TIMEZONE).date()


class PersistentStore:
    def __init__(self, database: Database):
        self.database = database
        self.daily_logs = database.daily_logs
        self.shopping_items = database.shopping_items
        self.user_ingredients = database.user_ingredients
        self.hidden_ingredients = database.user_hidden_ingredients

    def add_daily_log(self, user_id, entry):
        values = {
            "user_id": user_id,
            "log_date": current_app_date(),
            "recipe_title": entry["recipe_title"],
            "meal_type": entry["meal_type"],
            "calories": entry["calories"],
            "protein": entry["protein"],
            "carbs": entry["carbs"],
            "fat": entry["fat"],
        }
        with self.database.engine.begin() as connection:
            result = connection.execute(insert(self.daily_logs).values(**values))
            log_id = result.inserted_primary_key[0]
        return {"id": log_id, **{key: value for key, value in entry.items() if key != "id"}}

    def get_daily_logs(self, user_id, meal_type=None):
        statement = (
            select(self.daily_logs)
            .where(
                self.daily_logs.c.user_id == user_id,
                self.daily_logs.c.log_date == current_app_date(),
            )
            .order_by(self.daily_logs.c.id.desc())
        )
        if meal_type:
            statement = statement.where(
                func.lower(self.daily_logs.c.meal_type) == meal_type.strip().lower()
            )
        with self.database.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()
        return [
            {
                key: row[key]
                for key in ("id", "recipe_title", "meal_type", "calories", "protein", "carbs", "fat")
            }
            for row in rows
        ]

    def delete_daily_log(self, user_id, log_id):
        with self.database.engine.begin() as connection:
            result = connection.execute(
                delete(self.daily_logs).where(
                    self.daily_logs.c.id == log_id,
                    self.daily_logs.c.user_id == user_id,
                )
            )
        return result.rowcount > 0

    def clear_daily_logs(self, user_id):
        if user_id is None:
            raise ValueError("User ID dibutuhkan untuk menghapus catatan makan.")
        statement = delete(self.daily_logs).where(self.daily_logs.c.user_id == user_id)
        with self.database.engine.begin() as connection:
            connection.execute(statement)

    def add_shopping_item(self, user_id, name, category, amount, recipe_source=None):
        normalized_name = name.strip().casefold()
        with self.database.engine.begin() as connection:
            existing = connection.execute(
                select(self.shopping_items).where(
                    self.shopping_items.c.user_id == user_id,
                    func.lower(self.shopping_items.c.name) == normalized_name,
                )
            ).mappings().first()
            if existing:
                recipes = list(existing["recipes"] or [])
                if recipe_source and recipe_source not in recipes:
                    recipes.append(recipe_source)
                connection.execute(
                    update(self.shopping_items)
                    .where(self.shopping_items.c.id == existing["id"])
                    .values(count=existing["count"] + 1, recipes=recipes)
                )
                return {
                    **dict(existing),
                    "count": existing["count"] + 1,
                    "recipes": recipes,
                }

            recipes = [recipe_source] if recipe_source else []
            result = connection.execute(
                insert(self.shopping_items).values(
                    user_id=user_id,
                    name=name,
                    category=category,
                    amount=amount,
                    bought=False,
                    count=1,
                    recipes=recipes,
                )
            )
            item_id = result.inserted_primary_key[0]
        return {
            "id": item_id,
            "name": name,
            "category": category,
            "amount": amount,
            "bought": False,
            "count": 1,
            "recipes": recipes,
        }

    def get_shopping_items(self, user_id, category=None):
        statement = select(self.shopping_items).where(self.shopping_items.c.user_id == user_id)
        if category:
            statement = statement.where(
                func.lower(self.shopping_items.c.category) == category.strip().lower()
            )
        statement = statement.order_by(self.shopping_items.c.id)
        with self.database.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()
        return [dict(row) for row in rows]

    def get_shopping_summary(self, user_id):
        items = self.get_shopping_items(user_id)
        total = len(items)
        bought = sum(1 for item in items if item["bought"])
        categories = {}
        for item in items:
            categories[item["category"]] = categories.get(item["category"], 0) + 1
        return {
            "total_items": total,
            "bought_count": bought,
            "pending_count": total - bought,
            "completion_percentage": round((bought / total) * 100, 1) if total else 0.0,
            "categories": categories,
        }

    def toggle_shopping_item(self, user_id, item_id):
        with self.database.engine.begin() as connection:
            item = connection.execute(
                select(self.shopping_items).where(
                    self.shopping_items.c.user_id == user_id,
                    self.shopping_items.c.id == item_id,
                )
            ).mappings().first()
            if not item:
                return None
            bought = not item["bought"]
            connection.execute(
                update(self.shopping_items)
                .where(self.shopping_items.c.user_id == user_id, self.shopping_items.c.id == item_id)
                .values(bought=bought)
            )
        return {**dict(item), "bought": bought}

    def delete_shopping_item(self, user_id, item_id):
        with self.database.engine.begin() as connection:
            result = connection.execute(
                delete(self.shopping_items).where(
                    self.shopping_items.c.user_id == user_id,
                    self.shopping_items.c.id == item_id,
                )
            )
        return result.rowcount > 0

    def clear_completed_shopping_items(self, user_id):
        with self.database.engine.begin() as connection:
            result = connection.execute(
                delete(self.shopping_items).where(
                    self.shopping_items.c.user_id == user_id,
                    self.shopping_items.c.bought.is_(True),
                )
            )
        return result.rowcount

    def clear_shopping_items(self, user_id):
        if user_id is None:
            raise ValueError("User ID dibutuhkan untuk menghapus daftar belanja.")
        statement = delete(self.shopping_items).where(self.shopping_items.c.user_id == user_id)
        with self.database.engine.begin() as connection:
            connection.execute(statement)

    def get_custom_ingredients(self, user_id):
        with self.database.engine.connect() as connection:
            custom = connection.execute(
                select(self.user_ingredients)
                .where(self.user_ingredients.c.user_id == user_id)
                .order_by(self.user_ingredients.c.id)
            ).mappings().all()
            hidden = connection.execute(
                select(self.hidden_ingredients.c.ingredient_id).where(
                    self.hidden_ingredients.c.user_id == user_id
                )
            ).scalars().all()
        return (
            [
                {
                    "id": row["recipe_ingredient_id"]
                    if row["recipe_ingredient_id"] is not None
                    else row["id"] + CUSTOM_INGREDIENT_ID_OFFSET,
                    "name": row["name"],
                    "category": row["category"],
                    "calories_per_100g": row["calories_per_100g"],
                }
                for row in custom
            ],
            set(hidden),
        )

    def add_custom_ingredient(self, user_id, ingredient, recipe_ingredient_id=None):
        normalized_name = ingredient["name"].strip().casefold()
        with self.database.engine.begin() as connection:
            existing = connection.execute(
                select(self.user_ingredients).where(
                    self.user_ingredients.c.user_id == user_id,
                    self.user_ingredients.c.normalized_name == normalized_name,
                )
            ).mappings().first()
            if existing:
                return {
                    "id": existing["recipe_ingredient_id"]
                    if existing["recipe_ingredient_id"] is not None
                    else existing["id"] + CUSTOM_INGREDIENT_ID_OFFSET,
                    "name": existing["name"],
                    "category": existing["category"],
                    "calories_per_100g": existing["calories_per_100g"],
                }
            result = connection.execute(
                insert(self.user_ingredients).values(
                    user_id=user_id,
                    name=ingredient["name"],
                    normalized_name=normalized_name,
                    category=ingredient["category"],
                    calories_per_100g=ingredient["calories_per_100g"],
                    recipe_ingredient_id=recipe_ingredient_id,
                )
            )
            custom_id = result.inserted_primary_key[0]
        return {
            "id": recipe_ingredient_id
            if recipe_ingredient_id is not None
            else custom_id + CUSTOM_INGREDIENT_ID_OFFSET,
            "name": ingredient["name"],
            "category": ingredient["category"],
            "calories_per_100g": ingredient["calories_per_100g"],
        }

    def unhide_default_ingredient(self, user_id, ingredient_id):
        with self.database.engine.begin() as connection:
            connection.execute(
                delete(self.hidden_ingredients).where(
                    self.hidden_ingredients.c.user_id == user_id,
                    self.hidden_ingredients.c.ingredient_id == ingredient_id,
                )
            )

    def delete_ingredient(self, user_id, ingredient_id):
        if ingredient_id < CUSTOM_INGREDIENT_ID_OFFSET:
            with self.database.engine.begin() as connection:
                optional = connection.execute(
                    select(self.user_ingredients.c.id).where(
                        self.user_ingredients.c.user_id == user_id,
                        self.user_ingredients.c.recipe_ingredient_id == ingredient_id,
                    )
                ).scalar_one_or_none()
                if optional is not None:
                    connection.execute(
                        delete(self.user_ingredients).where(
                            self.user_ingredients.c.user_id == user_id,
                            self.user_ingredients.c.id == optional,
                        )
                    )
                    return True

        if ingredient_id >= CUSTOM_INGREDIENT_ID_OFFSET:
            custom_id = ingredient_id - CUSTOM_INGREDIENT_ID_OFFSET
            with self.database.engine.begin() as connection:
                result = connection.execute(
                    delete(self.user_ingredients).where(
                        self.user_ingredients.c.user_id == user_id,
                        self.user_ingredients.c.id == custom_id,
                    )
                )
            return result.rowcount > 0

        with self.database.engine.begin() as connection:
            exists = connection.execute(
                select(self.hidden_ingredients.c.ingredient_id).where(
                    self.hidden_ingredients.c.user_id == user_id,
                    self.hidden_ingredients.c.ingredient_id == ingredient_id,
                )
            ).first()
            if not exists:
                connection.execute(
                    insert(self.hidden_ingredients).values(
                        user_id=user_id,
                        ingredient_id=ingredient_id,
                    )
                )
        return True
