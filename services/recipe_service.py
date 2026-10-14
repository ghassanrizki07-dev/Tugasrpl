"""
CookFit - Recipe Matching Service
Modul logika bisnis untuk mencocokkan bahan dapur pengguna dengan katalog resep,
menghitung persentase kecocokan (set intersection), dan mengidentifikasi bahan yang kurang.
"""

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
        {"id": 6, "name": "Cabai Red", "calories_per_100g": 40}
    ]
}

DEFAULT_RECIPES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Tumis Kangkung Telur",
        "image_icon": "🥗",
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
        "image_icon": "🍳",
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
        "image_icon": "🍗",
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
    }
]


class RecipeService:
    def __init__(self, ingredients_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                 recipes_data: Optional[List[Dict[str, Any]]] = None):
        self.ingredients_data = ingredients_data if ingredients_data is not None else DEFAULT_INGREDIENTS
        self.recipes_data = recipes_data if recipes_data is not None else DEFAULT_RECIPES
        self._ingredient_name_map = self._build_ingredient_map()

    def _build_ingredient_map(self) -> Dict[int, str]:
        """Membuat pemetaan ID bahan ke Nama bahan untuk lookup cepat."""
        mapping = {}
        for category, items in self.ingredients_data.items():
            for item in items:
                mapping[item["id"]] = item["name"]
        return mapping

    def get_all_ingredients(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mengambil katalog seluruh bahan makanan yang dikelompokkan per kategori."""
        return self.ingredients_data

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
