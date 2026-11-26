"""
CookFit - Smart Shopping List Generator Service (US-4)
Modul logika bisnis untuk:
1. Menghasilkan daftar belanjaan otomatis dari bahan masakan yang kurang (missing ingredients).
2. Mengagregasi / menggabungkan bahan yang sama saat pengguna memilih lebih dari 1 resep.
3. Menyediakan sistem checklist (toggle status terbeli/pending).
4. Mengelompokkan item belanjaan berdasarkan kategori dapur (Protein, Sayuran, Bumbu, dll).
5. Menyediakan fitur penghapusan item selesai dan kalkulasi progres belanja.
"""

from typing import List, Dict, Any, Optional


class ShoppingService:
    def __init__(self, persistent_store=None):
        self._shopping_items: List[Dict[str, Any]] = []
        self._next_id: int = 1
        self.persistent_store = persistent_store

    def add_item(self, name: str, category: str = "Lain-lain",
                 amount: str = "secukupnya", recipe_source: Optional[str] = None,
                 user_id: int = None) -> Dict[str, Any]:
        """Menambahkan bahan baru ke daftar belanja manual atau terprogram."""
        clean_name = str(name).strip() if name else ""
        if not clean_name:
            raise ValueError("Nama bahan belanjaan tidak boleh kosong.")

        clean_cat = str(category).strip() if category else "Lain-lain"
        clean_amount = str(amount).strip() if amount else "secukupnya"

        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk menyimpan daftar belanja.")
            return self.persistent_store.add_shopping_item(
                user_id, clean_name, clean_cat, clean_amount, recipe_source
            )

        # Cek apakah item dengan nama serupa sudah ada (case-insensitive deduplication)
        for item in self._shopping_items:
            if item["name"].lower() == clean_name.lower():
                item["count"] += 1
                if recipe_source and recipe_source not in item["recipes"]:
                    item["recipes"].append(recipe_source)
                return item

        item_id = self._next_id
        self._next_id += 1

        new_item = {
            "id": item_id,
            "name": clean_name,
            "category": clean_cat,
            "amount": clean_amount,
            "bought": False,
            "count": 1,
            "recipes": [recipe_source] if recipe_source else []
        }
        self._shopping_items.append(new_item)
        return new_item

    def generate_from_missing(self, missing_items: List[Dict[str, Any]],
                              recipe_title: Optional[str] = None,
                              user_id: int = None) -> List[Dict[str, Any]]:
        """
        Menghasilkan item belanjaan dari daftar missing ingredients hasil pencocokan resep.
        Menghindari duplikasi dengan menambah count jika item sudah ada di daftar belanja.
        """
        if not missing_items or not isinstance(missing_items, list):
            return []

        added_items = []
        for raw in missing_items:
            if not isinstance(raw, dict):
                continue
            name = raw.get("name")
            if not name:
                continue

            category = raw.get("category", "Bahan Dapur")
            amount = raw.get("amount", "1 porsi")

            item = self.add_item(
                name=name,
                category=category,
                amount=amount,
                recipe_source=recipe_title,
                user_id=user_id,
            )
            added_items.append(item)

        return added_items

    def toggle_item(self, item_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Mengubah status item antara sudah dibeli (True) atau belum (False)."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk memperbarui daftar belanja.")
            return self.persistent_store.toggle_shopping_item(user_id, item_id)
        for item in self._shopping_items:
            if item["id"] == item_id:
                item["bought"] = not item["bought"]
                return dict(item)
        return None

    def delete_item(self, item_id: int, user_id: int = None) -> bool:
        """Menghapus item belanjaan berdasarkan ID."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk menghapus daftar belanja.")
            return self.persistent_store.delete_shopping_item(user_id, item_id)
        for idx, item in enumerate(self._shopping_items):
            if item["id"] == item_id:
                del self._shopping_items[idx]
                return True
        return False

    def clear_completed(self, user_id: int = None) -> int:
        """Menghapus seluruh item yang sudah berstatus 'bought' (selesai dibeli)."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk menghapus daftar belanja.")
            return self.persistent_store.clear_completed_shopping_items(user_id)
        before_count = len(self._shopping_items)
        self._shopping_items = [i for i in self._shopping_items if not i["bought"]]
        return before_count - len(self._shopping_items)

    def clear_all(self, user_id: int = None) -> None:
        """Mengosongkan seluruh daftar belanjaan."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk menghapus daftar belanja.")
            self.persistent_store.clear_shopping_items(user_id)
            return
        self._shopping_items.clear()
        self._next_id = 1

    def get_items(self, category: Optional[str] = None,
                  user_id: int = None) -> List[Dict[str, Any]]:
        """Mengambil seluruh item belanjaan, dapat difilter per kategori."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk mengambil daftar belanja.")
            return self.persistent_store.get_shopping_items(user_id, category)
        if category:
            cat_lower = category.strip().lower()
            return [i for i in self._shopping_items if i["category"].lower() == cat_lower]
        return list(self._shopping_items)

    def get_summary(self, user_id: int = None) -> Dict[str, Any]:
        """Menghitung ringkasan statistik daftar belanja."""
        if self.persistent_store:
            if user_id is None:
                raise ValueError("User ID dibutuhkan untuk mengambil ringkasan belanja.")
            return self.persistent_store.get_shopping_summary(user_id)
        total = len(self._shopping_items)
        bought = sum(1 for i in self._shopping_items if i["bought"])
        pending = total - bought
        completion_pct = round((bought / total) * 100, 1) if total > 0 else 0.0

        # Kategori breakdown
        cat_counts: Dict[str, int] = {}
        for i in self._shopping_items:
            cat = i["category"]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            "total_items": total,
            "bought_count": bought,
            "pending_count": pending,
            "completion_percentage": completion_pct,
            "categories": cat_counts
        }
