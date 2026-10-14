"""
CookFit - Main Flask Application Controller
Mengintegrasikan 5 Fitur Utama (User Stories):
1. US-1: Smart Recipe Recommendation Engine (/api/match-recipes, /api/ingredients, /api/recipes)
2. US-2: BMR & TDEE Health Calculator Engine (/api/calculate-bmr)
3. US-3: Daily NutriTracker & Calorie Budgeting Engine (/api/daily-logs, /api/daily-summary)
4. US-4: Smart Shopping List Generator Engine (/api/shopping-list/*)
5. US-5: Web Application Interface & REST API Gateway (/)
"""

from flask import Flask, render_template, jsonify, request
from services.recipe_service import RecipeService
from services.calorie_service import CalorieService
from services.tracker_service import TrackerService
from services.shopping_service import ShoppingService

app = Flask(__name__)

# Inisialisasi Service untuk seluruh fitur MVP
recipe_service = RecipeService()
calorie_service = CalorieService()
tracker_service = TrackerService()
shopping_service = ShoppingService()


@app.route('/')
def index():
    """Halaman antarmuka web mobile CookFit."""
    return render_template('index.html')


# ==========================================
# US-1: RECIPE MATCHING ENDPOINTS
# ==========================================
@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Mengambil katalog bahan dapur yang dikelompokkan per kategori."""
    ingredients = recipe_service.get_all_ingredients()
    return jsonify({'status': 'success', 'data': ingredients})


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Mengambil seluruh data resep dalam katalog CookFit."""
    recipes = recipe_service.get_all_recipes()
    return jsonify({'status': 'success', 'data': recipes})


@app.route('/api/match-recipes', methods=['POST'])
def match_recipes():
    """
    Menghitung persentase kecocokan resep berdasarkan
    daftar ID bahan makanan yang dipilih pengguna di kulkas.
    """
    data = request.get_json(silent=True) or {}
    selected_ids = data.get('ingredient_ids', [])
    results = recipe_service.match_recipes(selected_ids)
    return jsonify({'status': 'success', 'data': results})


# ==========================================
# US-2: BMR & TDEE CALCULATOR ENDPOINT
# ==========================================
@app.route('/api/calculate-bmr', methods=['POST'])
def calculate_bmr_endpoint():
    """
    Menghitung BMR, TDEE, dan target makronutrisi harian berdasarkan profil fisik.
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


# ==========================================
# US-3: DAILY NUTRITRACKER & BUDGET ENDPOINTS
# ==========================================
@app.route('/api/daily-logs', methods=['GET', 'POST'])
def daily_logs_endpoint():
    """
    GET: Mengambil riwayat log makan harian (opsional filter ?meal_type=...).
    POST: Mencatat konsumsi menu masakan ke log harian.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            new_entry = tracker_service.add_log(
                recipe_title=data.get('recipe_title'),
                calories=data.get('calories', 0),
                protein=data.get('protein', 0),
                carbs=data.get('carbs', 0),
                fat=data.get('fat', 0),
                meal_type=data.get('meal_type', 'Makan Siang')
            )
            # Sync dengan calorie_service untuk backward compatibility
            calorie_service.add_daily_log(
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
    meal_filter = request.args.get('meal_type')
    logs = tracker_service.get_logs(meal_type=meal_filter)
    return jsonify({'status': 'success', 'data': logs})


@app.route('/api/daily-logs/<int:log_id>', methods=['DELETE'])
def delete_daily_log_endpoint(log_id):
    """Menghapus catatan makan dari log harian berdasarkan ID."""
    deleted = tracker_service.delete_log(log_id)
    calorie_service.delete_daily_log(log_id)
    if deleted:
        return jsonify({'status': 'success', 'message': f'Log #{log_id} berhasil dihapus.'})
    return jsonify({'status': 'error', 'message': 'Log tidak ditemukan.'}), 404


@app.route('/api/daily-summary', methods=['GET'])
def daily_summary_endpoint():
    """Mengambil akumulasi total kalori & makronutrisi harian serta analisis budget."""
    tdee = request.args.get('target_tdee', type=int)
    summary = tracker_service.get_summary(target_tdee=tdee)
    return jsonify({'status': 'success', 'data': summary})


# ==========================================
# US-4: SMART SHOPPING LIST ENDPOINTS
# ==========================================
@app.route('/api/shopping-list', methods=['GET'])
def get_shopping_list_endpoint():
    """Mengambil seluruh daftar belanjaan dan ringkasan progres."""
    category = request.args.get('category')
    items = shopping_service.get_items(category=category)
    summary = shopping_service.get_summary()
    return jsonify({'status': 'success', 'data': {'items': items, 'summary': summary}})


@app.route('/api/shopping-list/generate', methods=['POST'])
def generate_shopping_list_endpoint():
    """
    Menghasilkan item belanja otomatis dari missing ingredients resep.
    Payload: { missing_ingredients: [...], recipe_title: "..." }
    """
    data = request.get_json(silent=True) or {}
    missing = data.get('missing_ingredients', [])
    recipe_title = data.get('recipe_title')
    
    if not isinstance(missing, list):
        return jsonify({'status': 'error', 'message': 'missing_ingredients harus berupa array list.'}), 400

    generated = shopping_service.generate_from_missing(missing, recipe_title=recipe_title)
    return jsonify({
        'status': 'success',
        'message': f'{len(generated)} bahan berhasil ditambahkan ke daftar belanja.',
        'data': generated
    }), 201


@app.route('/api/shopping-list/items', methods=['POST'])
def add_custom_shopping_item():
    """Menambahkan bahan belanjaan kustom secara manual."""
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    category = data.get('category', 'Lain-lain')
    amount = data.get('amount', 'secukupnya')

    try:
        new_item = shopping_service.add_item(name=name, category=category, amount=amount)
        return jsonify({'status': 'success', 'data': new_item}), 201
    except ValueError as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


@app.route('/api/shopping-list/<int:item_id>/toggle', methods=['PATCH', 'POST'])
def toggle_shopping_item(item_id):
    """Mengubah status barang (sudah dibeli / belum)."""
    updated = shopping_service.toggle_item(item_id)
    if updated is not None:
        return jsonify({'status': 'success', 'data': updated})
    return jsonify({'status': 'error', 'message': 'Item belanja tidak ditemukan.'}), 404


@app.route('/api/shopping-list/<int:item_id>', methods=['DELETE'])
def delete_shopping_item(item_id):
    """Menghapus satu item belanjaan berdasarkan ID."""
    deleted = shopping_service.delete_item(item_id)
    if deleted:
        return jsonify({'status': 'success', 'message': f'Item #{item_id} berhasil dihapus.'})
    return jsonify({'status': 'error', 'message': 'Item belanja tidak ditemukan.'}), 404


@app.route('/api/shopping-list/clear', methods=['DELETE', 'POST'])
def clear_shopping_list():
    """Mengosongkan daftar belanjaan (seluruhnya atau hanya item selesai dibeli)."""
    completed_only = request.args.get('completed_only', 'false').lower() == 'true'
    if completed_only:
        removed_count = shopping_service.clear_completed()
        return jsonify({'status': 'success', 'message': f'{removed_count} barang terbeli berhasil dibersihkan.'})
    
    shopping_service.clear_all()
    return jsonify({'status': 'success', 'message': 'Daftar belanja berhasil dikosongkan.'})


if __name__ == '__main__':
    print("[COOKFIT] Server running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
