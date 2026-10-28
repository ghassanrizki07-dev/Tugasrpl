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
                                  age_years: int, activity_level: float = 1.375,
                                  goal: str = "maintain") -> Dict[str, Any]:
        """
        Menghitung metrik lengkap BMR, TDEE, target kalori harian sesuai tujuan program (cutting/bulking/maintain),
        serta saran distribusi makronutrisi optimal.
        - Cutting: defisit kalori (-300 kcal) dengan protein lebih tinggi (35%) untuk menjaga massa otot.
        - Bulking: surplus kalori (+300 kcal) dengan karbohidrat lebih tinggi (55%) untuk energi & sintesis otot.
        - Maintain: kalori seimbang = TDEE (25% Protein, 50% Karbo, 25% Lemak).
        """
        bmr = self.calculate_bmr(gender, weight_kg, height_cm, age_years)
        tdee = self.calculate_tdee(bmr, activity_level)

        clean_goal = str(goal).strip().lower() if goal else "maintain"
        if clean_goal not in ("maintain", "cutting", "bulking"):
            clean_goal = "maintain"

        # Penyesuaian kalori & rasio makronutrisi berdasarkan goal
        if clean_goal == "cutting":
            # Target kalori minimal dibatasi tidak boleh lebih rendah dari batas aman BMR
            target_calories = max(int(round(bmr)), tdee - 300)
            # Rasio cutting: Protein 35%, Karbo 40%, Lemak 25%
            p_ratio, c_ratio, f_ratio = 0.35, 0.40, 0.25
        elif clean_goal == "bulking":
            target_calories = tdee + 300
            # Rasio bulking: Protein 25%, Karbo 55%, Lemak 20%
            p_ratio, c_ratio, f_ratio = 0.25, 0.55, 0.20
        else: # maintain
            target_calories = tdee
            # Rasio seimbang: Protein 25%, Karbo 50%, Lemak 25%
            p_ratio, c_ratio, f_ratio = 0.25, 0.50, 0.25

        calorie_adjustment = target_calories - tdee

        # 1g Protein = 4 kcal, 1g Karbo = 4 kcal, 1g Lemak = 9 kcal
        macro_targets = {
            "carbs_grams": int(round((target_calories * c_ratio) / 4)),
            "protein_grams": int(round((target_calories * p_ratio) / 4)),
            "fat_grams": int(round((target_calories * f_ratio) / 9))
        }

        return {
            "gender": gender,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age_years": age_years,
            "activity_level": activity_level,
            "goal": clean_goal,
            "bmr": round(bmr),
            "tdee": tdee,
            "calorie_adjustment": calorie_adjustment,
            "daily_calorie_target": target_calories,
            "target_calories": target_calories,
            "target_macros": macro_targets
        }

    # ==========================================
    # KALKULATOR TAKARAN BAHAN MASAKAN (PORTION CALCULATOR)
    # ==========================================
    def calculate_ingredient_portion(self, name: str, amount: float, unit: str = "gram",
                                     cal_per_100g: Optional[float] = None,
                                     protein_per_100g: Optional[float] = None,
                                     carbs_per_100g: Optional[float] = None,
                                     fat_per_100g: Optional[float] = None) -> Dict[str, Any]:
        """
        Menghitung kalori dan protein masakan berdasarkan takaran gram atau satuan (siung, butir, sdm, dll).
        """
        if not name or not str(name).strip():
            raise ValueError("Nama bahan tidak boleh kosong.")

        clean_name = str(name).strip()
        name_lower = clean_name.lower()

        try:
            qty = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Jumlah takaran harus berupa angka numerik.")

        if qty <= 0:
            raise ValueError("Jumlah takaran harus lebih dari 0.")

        clean_unit = str(unit).strip().lower() if unit else "gram"
        unit_mult = {
            "gram": 1.0,
            "g": 1.0,
            "kg": 1000.0,
            "siung": 5.0,      # 1 siung bawang ≈ 5 gram
            "butir": 50.0,     # 1 butir telur sedang ≈ 50 gram
            "sdm": 15.0,       # 1 sendok makan ≈ 15 gram
            "sdt": 5.0,        # 1 sendok teh ≈ 5 gram
            "ikat": 150.0,     # 1 ikat sayur ≈ 150 gram
            "potong": 50.0,    # 1 potong ≈ 50 gram
            "buah": 50.0       # 1 buah ≈ 50 gram
        }
        mult = unit_mult.get(clean_unit, 1.0)
        total_grams = round(qty * mult, 1)

        nutrition_lookup = {
            "dada ayam": {"cal": 165.0, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
            "daging ayam": {"cal": 190.0, "protein": 27.0, "carbs": 0.0, "fat": 8.0},
            "daging sapi": {"cal": 250.0, "protein": 26.0, "carbs": 0.0, "fat": 15.0},
            "telur ayam": {"cal": 155.0, "protein": 13.0, "carbs": 1.1, "fat": 11.0},
            "telur": {"cal": 155.0, "protein": 13.0, "carbs": 1.1, "fat": 11.0},
            "tahu putih": {"cal": 76.0, "protein": 8.0, "carbs": 1.9, "fat": 4.8},
            "tahu": {"cal": 76.0, "protein": 8.0, "carbs": 1.9, "fat": 4.8},
            "tempe": {"cal": 190.0, "protein": 19.0, "carbs": 9.4, "fat": 11.0},
            "ikan": {"cal": 110.0, "protein": 22.0, "carbs": 0.0, "fat": 2.5},
            "kangkung": {"cal": 19.0, "protein": 2.6, "carbs": 3.1, "fat": 0.2},
            "bayam": {"cal": 23.0, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
            "bawang merah & putih": {"cal": 40.0, "protein": 1.5, "carbs": 9.0, "fat": 0.1},
            "bawang merah": {"cal": 40.0, "protein": 1.4, "carbs": 9.0, "fat": 0.1},
            "bawang putih": {"cal": 149.0, "protein": 6.4, "carbs": 33.0, "fat": 0.5},
            "bawang": {"cal": 40.0, "protein": 1.5, "carbs": 9.0, "fat": 0.1},
            "cabai merah": {"cal": 40.0, "protein": 1.9, "carbs": 8.8, "fat": 0.4},
            "cabai": {"cal": 40.0, "protein": 1.9, "carbs": 8.8, "fat": 0.4},
            "wortel": {"cal": 41.0, "protein": 0.9, "carbs": 9.6, "fat": 0.2},
            "tomat": {"cal": 18.0, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
            "kecap manis": {"cal": 150.0, "protein": 2.0, "carbs": 35.0, "fat": 0.0},
            "minyak": {"cal": 884.0, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
            "nasi": {"cal": 130.0, "protein": 2.7, "carbs": 28.0, "fat": 0.3}
        }

        ref = nutrition_lookup.get(name_lower)
        if not ref:
            for k, v in nutrition_lookup.items():
                if k in name_lower or name_lower in k:
                    ref = v
                    break

        default_cal = ref["cal"] if ref else 50.0
        default_p = ref["protein"] if ref else 2.0
        default_c = ref["carbs"] if ref else 5.0
        default_f = ref["fat"] if ref else 1.0

        c_100 = float(cal_per_100g) if cal_per_100g is not None and cal_per_100g >= 0 else default_cal
        p_100 = float(protein_per_100g) if protein_per_100g is not None and protein_per_100g >= 0 else default_p
        carb_100 = float(carbs_per_100g) if carbs_per_100g is not None and carbs_per_100g >= 0 else default_c
        fat_100 = float(fat_per_100g) if fat_per_100g is not None and fat_per_100g >= 0 else default_f

        factor = total_grams / 100.0
        calories = round(factor * c_100, 1)
        protein = round(factor * p_100, 1)
        carbs = round(factor * carb_100, 1)
        fat = round(factor * fat_100, 1)

        return {
            "name": clean_name,
            "amount": qty,
            "unit": clean_unit,
            "total_grams": total_grams,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "cal_per_100g": c_100,
            "protein_per_100g": p_100
        }

    def calculate_cooking_recipe(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Menghitung total kalori, protein, karbohidrat, dan lemak dari seluruh bahan masakan.
        """
        if not items or not isinstance(items, list):
            return {
                "total_calories": 0.0,
                "total_protein": 0.0,
                "total_carbs": 0.0,
                "total_fat": 0.0,
                "total_grams": 0.0,
                "items": []
            }

        calculated_items = []
        tot_cal = 0.0
        tot_p = 0.0
        tot_c = 0.0
        tot_f = 0.0
        tot_grams = 0.0

        for item in items:
            name = item.get("name", "")
            amount = item.get("amount", 0)
            unit = item.get("unit", "gram")
            cal_100 = item.get("cal_per_100g")
            p_100 = item.get("protein_per_100g")
            c_100 = item.get("carbs_per_100g")
            f_100 = item.get("fat_per_100g")

            calc = self.calculate_ingredient_portion(
                name=name,
                amount=amount,
                unit=unit,
                cal_per_100g=cal_100,
                protein_per_100g=p_100,
                carbs_per_100g=c_100,
                fat_per_100g=f_100
            )
            calculated_items.append(calc)
            tot_cal += calc["calories"]
            tot_p += calc["protein"]
            tot_c += calc["carbs"]
            tot_f += calc["fat"]
            tot_grams += calc["total_grams"]

        return {
            "total_calories": round(tot_cal, 1),
            "total_protein": round(tot_p, 1),
            "total_carbs": round(tot_c, 1),
            "total_fat": round(tot_f, 1),
            "total_grams": round(tot_grams, 1),
            "items": calculated_items
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
