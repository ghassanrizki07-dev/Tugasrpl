"""
CookFit - Daily NutriTracker & Calorie Budget Service (US-3)
Modul logika bisnis untuk:
1. Mencatat jurnal makan harian beserta rincian kalori & makronutrisi.
2. Menghitung akumulasi harian kalori, protein, karbohidrat, dan lemak.
3. Menganalisis anggaran kalori terhadap target TDEE (persentase, sisa kalori, status budget).
4. Memfilter riwayat konsumsi berdasarkan waktu makan (Sarapan, Makan Siang, Makan Malam, Camilan).
5. Mengelola penghapusan entri dan reset log nutrisi.
"""

from typing import List, Dict, Any, Optional

VALID_MEAL_TYPES = ["Sarapan", "Makan Siang", "Makan Malam", "Camilan"]


class TrackerService:
    def __init__(self):
        self._daily_logs: List[Dict[str, Any]] = []
        self._next_id: int = 1

    def add_log(self, recipe_title: str, calories: float, protein: float = 0.0,
                carbs: float = 0.0, fat: float = 0.0,
                meal_type: str = "Makan Siang") -> Dict[str, Any]:
        """
        Menambahkan entri konsumsi makanan baru ke log harian.
        Validasi: Nama makanan tidak boleh kosong, kalori & makro harus numerik >= 0.
        """
        if not recipe_title or not str(recipe_title).strip():
            raise ValueError("Nama makanan tidak boleh kosong.")

        try:
            cal = float(calories)
            p = float(protein)
            c = float(carbs)
            f = float(fat)
        except (ValueError, TypeError):
            raise ValueError("Nilai nutrisi (kalori, protein, karbo, lemak) harus berupa angka numerik.")

        if cal < 0 or p < 0 or c < 0 or f < 0:
            raise ValueError("Nilai nutrisi tidak boleh bernilai negatif.")

        clean_meal_type = str(meal_type).strip() if meal_type else "Makan Siang"

        entry_id = self._next_id
        self._next_id += 1

        entry = {
            "id": entry_id,
            "recipe_title": str(recipe_title).strip(),
            "meal_type": clean_meal_type,
            "calories": round(cal, 1),
            "protein": round(p, 1),
            "carbs": round(c, 1),
            "fat": round(f, 1)
        }
        self._daily_logs.insert(0, entry)
        return entry

    def get_logs(self, meal_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Mengambil riwayat log makanan.
        Dapat difilter berdasarkan jenis jam makan jika parameter meal_type diberikan.
        """
        if meal_type:
            target = meal_type.strip().lower()
            return [l for l in self._daily_logs if l["meal_type"].lower() == target]
        return list(self._daily_logs)

    def get_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """Mencari entri jurnal berdasarkan ID."""
        for item in self._daily_logs:
            if item["id"] == log_id:
                return dict(item)
        return None

    def delete_log(self, log_id: int) -> bool:
        """Menghapus entri log makan berdasarkan ID."""
        for idx, item in enumerate(self._daily_logs):
            if item["id"] == log_id:
                del self._daily_logs[idx]
                return True
        return False

    def get_summary(self, target_tdee: Optional[int] = None) -> Dict[str, Any]:
        """
        Menghitung total akumulasi harian dan perbandingan terhadap target TDEE.
        Mengembalikan status anggaran: under_budget, on_target, atau over_budget.
        """
        total_cal = round(sum(item["calories"] for item in self._daily_logs), 1)
        total_p = round(sum(item["protein"] for item in self._daily_logs), 1)
        total_c = round(sum(item["carbs"] for item in self._daily_logs), 1)
        total_f = round(sum(item["fat"] for item in self._daily_logs), 1)

        progress_pct = 0.0
        remaining_cal = None
        status = "untracked"

        if target_tdee and target_tdee > 0:
            progress_pct = round((total_cal / target_tdee) * 100, 1)
            remaining_cal = round(target_tdee - total_cal, 1)
            if progress_pct > 105.0:
                status = "over_budget"
            elif progress_pct >= 95.0:
                status = "on_target"
            else:
                status = "under_budget"

        return {
            "total_calories": total_cal,
            "total_protein": total_p,
            "total_carbs": total_c,
            "total_fat": total_f,
            "total_entries": len(self._daily_logs),
            "target_tdee": target_tdee,
            "remaining_calories": remaining_cal,
            "calorie_percentage": progress_pct,
            "budget_status": status
        }

    def clear_logs(self) -> None:
        """Mengosongkan seluruh entri jurnal (untuk testing atau reset harian)."""
        self._daily_logs.clear()
        self._next_id = 1
