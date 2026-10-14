"""
CookFit - Calorie & NutriTracker Service
Modul logika bisnis untuk:
1. Menghitung Basal Metabolic Rate (BMR) menggunakan rumus Mifflin-St Jeor
2. Menghitung Total Daily Energy Expenditure (TDEE) berdasarkan tingkat aktivitas fisik
3. Mengelola pencatatan jurnal makanan harian (NutriTracker) & akumulasi makronutrisi
"""

from typing import Dict, Any, List, Optional
import time

VALID_ACTIVITY_LEVELS = {
    1.2: "Sedentary (Sangat sedikit aktivitas / duduk saja)",
    1.375: "Light (Olahraga ringan 1-3 hari/minggu)",
    1.55: "Moderate (Olahraga sedang 3-5 hari/minggu)",
    1.725: "Active (Olahraga berat 6-7 hari/minggu)",
    1.9: "Very Active (Aktivitas fisik sangat berat / atlet)"
}


class CalorieService:
    def __init__(self):
        # In-memory storage untuk log harian (bisa diperluas ke DB)
        self._daily_logs: List[Dict[str, Any]] = []
        self._next_id: int = 1

    def calculate_bmr(self, gender: str, weight_kg: float, height_cm: float, age_years: int) -> float:
        """
        Menghitung BMR menggunakan rumus Mifflin-St Jeor.
        Pria  : BMR = (10 * weight) + (6.25 * height) - (5 * age) + 5
        Wanita: BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161
        """
        if not isinstance(gender, str) or gender.lower() not in ("male", "female", "pria", "wanita"):
            raise ValueError("Gender harus bernilai 'male' atau 'female'.")

        try:
            w = float(weight_kg)
            h = float(height_cm)
            a = int(age_years)
        except (ValueError, TypeError):
            raise ValueError("Berat, tinggi, dan usia harus berupa angka.")

        if w <= 0 or w > 350:
            raise ValueError("Berat badan harus bernilai antara 1 kg dan 350 kg.")
        if h <= 0 or h > 260:
            raise ValueError("Tinggi badan harus bernilai antara 1 cm dan 260 cm.")
        if a <= 0 or a > 130:
            raise ValueError("Usia harus bernilai antara 1 tahun dan 130 tahun.")

        is_male = gender.lower() in ("male", "pria")
        base = (10.0 * w) + (6.25 * h) - (5.0 * a)
        bmr = base + 5.0 if is_male else base - 161.0

        return round(bmr, 2)

    def calculate_tdee(self, bmr: float, activity_level: float) -> int:
        """
        Menghitung Total Daily Energy Expenditure (TDEE).
        TDEE = BMR * activity_level (dibulatkan ke integer terdekat).
        """
        if bmr <= 0:
            raise ValueError("BMR harus bernilai positif.")

        try:
            act = float(activity_level)
        except (ValueError, TypeError):
            raise ValueError("Tingkat aktivitas harus berupa angka numerik.")

        if act < 1.0 or act > 2.5:
            raise ValueError("Tingkat aktivitas di luar batas valid (1.0 - 2.5).")

        return int(round(bmr * act))

    def calculate_profile_metrics(self, gender: str, weight_kg: float, height_cm: float,
                                  age_years: int, activity_level: float = 1.375) -> Dict[str, Any]:
        """Menghitung metrik lengkap BMR, TDEE, dan saran distribusi makronutrisi."""
        bmr = self.calculate_bmr(gender, weight_kg, height_cm, age_years)
        tdee = self.calculate_tdee(bmr, activity_level)

        # Standar distribusi makro seimbang: Karbo 50%, Protein 25%, Lemak 25%
        # 1g Protein = 4 kcal, 1g Karbo = 4 kcal, 1g Lemak = 9 kcal
        macro_targets = {
            "carbs_grams": int(round((tdee * 0.50) / 4)),
            "protein_grams": int(round((tdee * 0.25) / 4)),
            "fat_grams": int(round((tdee * 0.25) / 9))
        }

        return {
            "gender": gender,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age_years": age_years,
            "activity_level": activity_level,
            "bmr": round(bmr),
            "tdee": tdee,
            "target_macros": macro_targets
        }

    # ==========================================
    # LOG NUTRISI HARIAN (NutriTracker)
    # ==========================================
    def add_daily_log(self, recipe_title: str, calories: float, protein: float = 0.0,
                      carbs: float = 0.0, fat: float = 0.0,
                      meal_type: str = "Makan Siang") -> Dict[str, Any]:
        """Menambahkan entri konsumsi makanan ke jurnal harian."""
        if not recipe_title or not str(recipe_title).strip():
            raise ValueError("Nama makanan tidak boleh kosong.")

        try:
            cal = max(0.0, float(calories))
            p = max(0.0, float(protein))
            c = max(0.0, float(carbs))
            f = max(0.0, float(fat))
        except (ValueError, TypeError):
            raise ValueError("Nilai nutrisi harus berupa angka numerik.")

        log_id = self._next_id
        self._next_id += 1
        entry = {
            "id": log_id,
            "recipe_title": str(recipe_title).strip(),
            "meal_type": meal_type,
            "calories": round(cal, 1),
            "protein": round(p, 1),
            "carbs": round(c, 1),
            "fat": round(f, 1)
        }
        self._daily_logs.insert(0, entry)
        return entry

    def get_daily_logs(self) -> List[Dict[str, Any]]:
        """Mengambil seluruh riwayat log makan harian."""
        return list(self._daily_logs)

    def get_daily_summary(self, target_tdee: Optional[int] = None) -> Dict[str, Any]:
        """Menghitung total akumulasi kalori dan makronutrisi harian."""
        total_cal = sum(item["calories"] for item in self._daily_logs)
        total_p = sum(item["protein"] for item in self._daily_logs)
        total_c = sum(item["carbs"] for item in self._daily_logs)
        total_f = sum(item["fat"] for item in self._daily_logs)

        progress_pct = 0.0
        if target_tdee and target_tdee > 0:
            progress_pct = round((total_cal / target_tdee) * 100, 1)

        return {
            "total_calories": round(total_cal, 1),
            "total_protein": round(total_p, 1),
            "total_carbs": round(total_c, 1),
            "total_fat": round(total_f, 1),
            "total_entries": len(self._daily_logs),
            "target_tdee": target_tdee,
            "calorie_percentage": progress_pct
        }

    def delete_daily_log(self, log_id: int) -> bool:
        """Menghapus entri log makan berdasarkan ID."""
        for idx, item in enumerate(self._daily_logs):
            if item["id"] == log_id:
                del self._daily_logs[idx]
                return True
        return False

    def clear_logs(self) -> None:
        """Membersihkan semua entri log harian (utilitas testing/reset)."""
        self._daily_logs.clear()
        self._next_id = 1
