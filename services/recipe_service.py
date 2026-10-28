"""
CookFit - Recipe Matching Service
Modul logika bisnis untuk mencocokkan bahan dapur pengguna dengan katalog resep,
menghitung persentase kecocokan (set intersection), dan mengidentifikasi bahan yang kurang.
"""

from copy import deepcopy
from typing import List, Dict, Any, Optional, Set

DEFAULT_INGREDIENTS: Dict[str, List[Dict[str, Any]]] = {
    "Protein & Daging": [
        {"id": 1, "name": "Telur Ayam", "calories_per_100g": 155},
        {"id": 2, "name": "Dada Ayam", "calories_per_100g": 165},
        {"id": 3, "name": "Tahu Putih", "calories_per_100g": 76}
    ],
    "Sayuran & Bumbu": [
        {"id": 4, "name": "Kangkung", "calories_per_100g": 19},
        {"id": 5, "name": "Bawang Merah & Putih", "calories_per_100g": 40},
        {"id": 6, "name": "Cabai Merah", "calories_per_100g": 40}
    ]
}

OPTIONAL_RECIPE_INGREDIENTS: Dict[str, Dict[str, Any]] = {
    "tuna kaleng": {
        "id": 7,
        "name": "Tuna Kaleng",
        "category": "Protein & Daging",
        "calories_per_100g": 116
    },
    "edamame": {
        "id": 8,
        "name": "Edamame",
        "category": "Protein & Daging",
        "calories_per_100g": 121
    },
    "brokoli": {
        "id": 9,
        "name": "Brokoli",
        "category": "Sayuran & Bumbu",
        "calories_per_100g": 34
    },
    "timun": {
        "id": 10,
        "name": "Timun",
        "category": "Sayuran & Bumbu",
        "calories_per_100g": 15
    }
}

DEFAULT_RECIPES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Tumis Kangkung Telur",
        "image_icon": "Sayur",
        "prep_time": 15,
        "servings": 2,
        "total_calories": 210,
        "total_protein": 14,
        "total_carbs": 8,
        "total_fat": 12,
        "required_ids": [1, 4, 5],
        "ingredients": [
            {"name": "Kangkung", "amount": "1 ikat", "calories": 40},
            {"name": "Telur Ayam", "amount": "2 butir", "calories": 140},
            {"name": "Bawang & Cabai", "amount": "secukupnya", "calories": 30}
        ],
        "instructions": "1. Tumis bawang dan cabai hingga harum.\n2. Masukkan telur, orak-arik hingga matang.\n3. Masukkan kangkung, bumbui garam & penyedap, aduk sebentar hingga layu."
    },
    {
        "id": 2,
        "title": "Omelet Tahu Sehat",
        "image_icon": "Telur",
        "prep_time": 10,
        "servings": 1,
        "total_calories": 250,
        "total_protein": 18,
        "total_carbs": 6,
        "total_fat": 15,
        "required_ids": [1, 3, 5],
        "ingredients": [
            {"name": "Telur Ayam", "amount": "2 butir", "calories": 140},
            {"name": "Tahu Putih", "amount": "100 gram", "calories": 80},
            {"name": "Bawang Merah", "amount": "2 siung", "calories": 30}
        ],
        "instructions": "1. Hancurkan tahu putih dan campurkan dengan kocokan telur.\n2. Tambahkan irisan bawang dan sedikit garam.\n3. Goreng di atas teflon dengan sedikit minyak hingga matang keemasan."
    },
    {
        "id": 3,
        "title": "Dada Ayam Tumis Bawang",
        "image_icon": "Ayam",
        "prep_time": 20,
        "servings": 2,
        "total_calories": 320,
        "total_protein": 35,
        "total_carbs": 5,
        "total_fat": 10,
        "required_ids": [2, 5, 6],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "200 gram", "calories": 260},
            {"name": "Bawang & Cabai", "amount": "secukupnya", "calories": 60}
        ],
        "instructions": "1. Potong dada ayam dadu kecil.\n2. Tumis bawang dan cabai hingga wangi.\n3. Masukkan potongan dada ayam, masak hingga matang dan bumbu meresap."
    },
    {
        "id": 4,
        "title": "Ayam Panggang Bawang Putih Tinggi Protein",
        "image_icon": "Ayam",
        "prep_time": 30,
        "servings": 1,
        "total_calories": 340,
        "total_protein": 62,
        "total_carbs": 4,
        "total_fat": 8,
        "required_ids": [2, 5, 6],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "200 gram", "calories": 330},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 10},
            {"name": "Cabai Merah", "amount": "secukupnya", "calories": 5}
        ],
        "instructions": "1. Lumuri dada ayam dengan bawang putih, cabai, garam, dan lada.\n2. Diamkan selama 10 menit agar bumbu meresap.\n3. Panggang di oven atau teflon anti lengket hingga matang merata."
    },
    {
        "id": 5,
        "title": "Tahu Ayam Kukus Tinggi Protein",
        "image_icon": "Kukus",
        "prep_time": 25,
        "servings": 1,
        "total_calories": 330,
        "total_protein": 55,
        "total_carbs": 8,
        "total_fat": 12,
        "required_ids": [2, 3, 5],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "150 gram", "calories": 248},
            {"name": "Tahu Putih", "amount": "100 gram", "calories": 76},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 6}
        ],
        "instructions": "1. Cincang dada ayam dan haluskan tahu, lalu campurkan dengan bawang putih dan bumbu secukupnya.\n2. Bentuk adonan menjadi beberapa bagian.\n3. Kukus selama 15–20 menit hingga ayam matang."
    },
    {
        "id": 6,
        "title": "Omelet Dada Ayam Tinggi Protein",
        "image_icon": "Telur",
        "prep_time": 20,
        "servings": 1,
        "total_calories": 310,
        "total_protein": 44,
        "total_carbs": 3,
        "total_fat": 14,
        "required_ids": [1, 2, 5],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "100 gram", "calories": 165},
            {"name": "Telur Ayam", "amount": "2 butir", "calories": 140},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 5}
        ],
        "instructions": "1. Potong dada ayam kecil-kecil dan masak hingga matang.\n2. Kocok telur bersama bawang cincang dan sedikit garam.\n3. Tuangkan telur ke ayam, lalu masak di teflon anti lengket hingga omelet matang."
    },
    {
        "id": 7,
        "title": "Tuna Brokoli Tumis Tinggi Protein",
        "image_icon": "Tuna",
        "prep_time": 15,
        "servings": 1,
        "total_calories": 225,
        "total_protein": 41,
        "total_carbs": 12,
        "total_fat": 3,
        "required_ids": [7, 9, 5],
        "ingredients": [
            {"name": "Tuna Kaleng", "amount": "150 gram", "calories": 174},
            {"name": "Brokoli", "amount": "100 gram", "calories": 34},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 17}
        ],
        "instructions": "1. Tiriskan tuna dan potong brokoli menjadi bagian kecil.\n2. Tumis bawang dengan sedikit air, lalu masukkan brokoli hingga empuk.\n3. Masukkan tuna, aduk hingga panas dan sajikan."
    },
    {
        "id": 8,
        "title": "Bowl Edamame Tahu dan Brokoli",
        "image_icon": "Sayur",
        "prep_time": 20,
        "servings": 1,
        "total_calories": 245,
        "total_protein": 24,
        "total_carbs": 20,
        "total_fat": 10,
        "required_ids": [8, 3, 9],
        "ingredients": [
            {"name": "Edamame", "amount": "100 gram", "calories": 121},
            {"name": "Tahu Putih", "amount": "100 gram", "calories": 76},
            {"name": "Brokoli", "amount": "100 gram", "calories": 34}
        ],
        "instructions": "1. Rebus edamame dan brokoli hingga matang.\n2. Potong tahu, lalu kukus atau panggang hingga hangat.\n3. Sajikan tahu bersama edamame dan brokoli."
    },
    {
        "id": 9,
        "title": "Salad Tuna Telur dan Timun",
        "image_icon": "Telur",
        "prep_time": 15,
        "servings": 1,
        "total_calories": 235,
        "total_protein": 33,
        "total_carbs": 5,
        "total_fat": 9,
        "required_ids": [7, 1, 10],
        "ingredients": [
            {"name": "Tuna Kaleng", "amount": "100 gram", "calories": 116},
            {"name": "Telur Ayam", "amount": "1 butir", "calories": 78},
            {"name": "Timun", "amount": "100 gram", "calories": 15}
        ],
        "instructions": "1. Rebus telur hingga matang dan tiriskan tuna.\n2. Iris telur dan timun.\n3. Campurkan dengan tuna, bumbui lada dan sedikit garam, lalu sajikan."
    }
]


class RecipeService:
    def __init__(self, ingredients_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                 recipes_data: Optional[List[Dict[str, Any]]] = None):
        self.ingredients_data = (
            ingredients_data if ingredients_data is not None else deepcopy(DEFAULT_INGREDIENTS)
        )
        self.recipes_data = recipes_data if recipes_data is not None else DEFAULT_RECIPES
        self._ingredient_name_map = self._build_ingredient_map()

    def _build_ingredient_map(self) -> Dict[int, str]:
        """Membuat pemetaan ID bahan ke Nama bahan untuk lookup cepat."""
        mapping = {}
        for category, items in self.ingredients_data.items():
            for item in items:
                mapping[item["id"]] = item["name"]
        for item in OPTIONAL_RECIPE_INGREDIENTS.values():
            mapping[item["id"]] = item["name"]
        return mapping

    def get_all_ingredients(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mengambil katalog seluruh bahan makanan yang dikelompokkan per kategori."""
        return self.ingredients_data

    def add_ingredient(self, name: str, category: str, calories_per_100g: int = 50) -> Dict[str, Any]:
        """
        Menambahkan bahan makanan baru ke dalam kategori yang dipilih.
        Kategori yang didukung: 'Protein & Daging' dan 'Sayuran & Bumbu'.
        """
        if not name or not str(name).strip():
            raise ValueError("Nama bahan makanan tidak boleh kosong.")

        clean_name = str(name).strip()
        optional_ingredient = OPTIONAL_RECIPE_INGREDIENTS.get(clean_name.casefold())

        for existing_category, items in self.ingredients_data.items():
            for item in items:
                if item["name"].strip().casefold() == clean_name.casefold():
                    return item

        # Normalisasi kategori
        target_category = "Sayuran & Bumbu"
        if "protein" in str(category).lower() or "daging" in str(category).lower():
            target_category = "Protein & Daging"
        if optional_ingredient:
            target_category = optional_ingredient["category"]

        if target_category not in self.ingredients_data:
            self.ingredients_data[target_category] = []

        if optional_ingredient:
            new_id = optional_ingredient["id"]
        else:
            reserved_ids = {
                item["id"] for item in OPTIONAL_RECIPE_INGREDIENTS.values()
            }
            all_ids = [
                item["id"]
                for items in self.ingredients_data.values()
                for item in items
            ]
            new_id = max(all_ids + list(reserved_ids), default=0) + 1

        if optional_ingredient:
            cal = optional_ingredient["calories_per_100g"]
        else:
            try:
                cal = int(calories_per_100g) if calories_per_100g is not None else 50
            except (ValueError, TypeError):
                cal = 50

        new_item = {
            "id": new_id,
            "name": clean_name,
            "calories_per_100g": max(cal, 0)
        }

        self.ingredients_data[target_category].append(new_item)
        self._ingredient_name_map[new_id] = clean_name
        return new_item

    def delete_ingredient(self, ingredient_id: int) -> bool:
        """Menghapus bahan makanan dari katalog."""
        for category, items in self.ingredients_data.items():
            for i, item in enumerate(items):
                if item["id"] == ingredient_id:
                    items.pop(i)
                    optional_item = next(
                        (
                            optional
                            for optional in OPTIONAL_RECIPE_INGREDIENTS.values()
                            if optional["id"] == ingredient_id
                        ),
                        None
                    )
                    if optional_item:
                        self._ingredient_name_map[ingredient_id] = optional_item["name"]
                    else:
                        self._ingredient_name_map.pop(ingredient_id, None)
                    return True
        return False

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Mengambil semua daftar resep dalam katalog."""
        return self.recipes_data

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Mencari resep berdasarkan ID."""
        for recipe in self.recipes_data:
            if recipe["id"] == recipe_id:
                return dict(recipe)
        return None

    def match_recipes(self, selected_ingredient_ids: Any) -> List[Dict[str, Any]]:
        """
        Menghitung persentase kecocokan resep berdasarkan ID bahan yang dimiliki pengguna.
        Formula:
            S_match = (|A ∩ B| / |B|) * 100%
        Hasil diurutkan secara descending berdasarkan match_score.
        """
        # Sanitasi dan validasi input
        if not selected_ingredient_ids or not isinstance(selected_ingredient_ids, (list, set, tuple)):
            clean_selected_set: Set[int] = set()
        else:
            clean_selected_set = set()
            for item in selected_ingredient_ids:
                try:
                    clean_selected_set.add(int(item))
                except (ValueError, TypeError):
                    continue

        results = []
        for recipe in self.recipes_data:
            required_set = set(recipe.get("required_ids", []))
            
            if not required_set:
                score = 100
                missing_ids = []
            else:
                matched_set = required_set.intersection(clean_selected_set)
                score = int(round((len(matched_set) / len(required_set)) * 100))
                missing_ids = [ing_id for ing_id in required_set if ing_id not in clean_selected_set]

            # Kumpulkan informasi bahan yang kurang
            missing_items = []
            for ing_id in missing_ids:
                name = self._ingredient_name_map.get(ing_id, f"Bahan #{ing_id}")
                missing_items.append({"id": ing_id, "name": name})

            recipe_result = dict(recipe)
            recipe_result["match_score"] = score
            recipe_result["matched_count"] = len(required_set) - len(missing_ids)
            recipe_result["total_required"] = len(required_set)
            recipe_result["missing_ingredients"] = missing_items

            results.append(recipe_result)

        # Urutkan berdasarkan match score tertinggi
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results
