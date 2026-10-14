from flask import Flask, render_template, jsonify, request
from services.recipe_service import RecipeService
from services.calorie_service import CalorieService

app = Flask(__name__)

# Inisialisasi Service Fitur 1 & 2
recipe_service = RecipeService()
calorie_service = CalorieService()

@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# FITUR 1: RECIPE MATCHING ENDPOINTS
# ==========================================
@app.route('/api/ingredients')
def get_ingredients():
    """Mengambil katalog bahan dapur yang dikelompokkan per kategori."""
    ingredients = recipe_service.get_all_ingredients()
    return jsonify({'status': 'success', 'data': ingredients})

@app.route('/api/recipes')
def get_recipes():
    """Mengambil seluruh data resep dalam katalog."""
    recipes = recipe_service.get_all_recipes()
    return jsonify({'status': 'success', 'data': recipes})

@app.route('/api/match-recipes', methods=['POST'])
def match_recipes():
    """
    Endpoint untuk menghitung persentase kecocokan resep berdasarkan
    daftar ID bahan makanan yang dipilih pengguna di kulkas.
    """
    data = request.get_json(silent=True) or {}
    selected_ids = data.get('ingredient_ids', [])
    
    results = recipe_service.match_recipes(selected_ids)
    return jsonify({'status': 'success', 'data': results})

# ==========================================
# FITUR 2: BMR & DAILY CALORIE TRACKER ENDPOINTS
# ==========================================
@app.route('/api/calculate-bmr', methods=['POST'])
def calculate_bmr_endpoint():
    """
    Endpoint untuk menghitung BMR dan TDEE berdasarkan parameter fisik pengguna.
    Payload: { gender, weight, height, age, activity_level }
    """
    data = request.get_json(silent=True) or {}
    gender = data.get('gender', 'male')
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    activity = data.get('activity_level', 1.375)

    try:
        metrics = calorie_service.calculate_profile_metrics(
            gender=str(gender),
            weight_kg=float(weight),
            height_cm=float(height),
            age_years=int(age),
            activity_level=float(activity)
        )
        return jsonify({'status': 'success', 'data': metrics})
    except (ValueError, TypeError) as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400

@app.route('/api/daily-logs', methods=['GET', 'POST'])
def daily_logs_endpoint():
    """
    GET: Mengambil riwayat log makan harian.
    POST: Mencatat konsumsi menu masakan ke log harian.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            new_entry = calorie_service.add_daily_log(
                recipe_title=data.get('recipe_title'),
                calories=data.get('calories', 0),
                protein=data.get('protein', 0),
                carbs=data.get('carbs', 0),
                fat=data.get('fat', 0),
                meal_type=data.get('meal_type', 'Makan Siang')
            )
            return jsonify({'status': 'success', 'data': new_entry}), 201
        except (ValueError, TypeError) as err:
            return jsonify({'status': 'error', 'message': str(err)}), 400

    # GET request
    logs = calorie_service.get_daily_logs()
    return jsonify({'status': 'success', 'data': logs})

@app.route('/api/daily-logs/<int:log_id>', methods=['DELETE'])
def delete_daily_log_endpoint(log_id):
    """Menghapus catatan makan dari log harian berdasarkan ID."""
    deleted = calorie_service.delete_daily_log(log_id)
    if deleted:
        return jsonify({'status': 'success', 'message': f'Log #{log_id} berhasil dihapus.'})
    return jsonify({'status': 'error', 'message': 'Log tidak ditemukan.'}), 404

@app.route('/api/daily-summary', methods=['GET'])
def daily_summary_endpoint():
    """Mengambil akumulasi total kalori & makronutrisi harian."""
    tdee = request.args.get('target_tdee', type=int)
    summary = calorie_service.get_daily_summary(target_tdee=tdee)
    return jsonify({'status': 'success', 'data': summary})

if __name__ == '__main__':
    print("[COOKFIT] Server running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
