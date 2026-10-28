"""
CookFit - Main Flask Application Controller
Mengintegrasikan 6 Fitur Utama (User Stories):
1. US-0: User Authentication & Account Management (/api/auth/*, /login)
2. US-1: Smart Recipe Recommendation Engine (/api/match-recipes, /api/ingredients, /api/recipes)
3. US-2: BMR & TDEE Health Calculator Engine (/api/calculate-bmr)
4. US-3: Daily NutriTracker & Calorie Budgeting Engine (/api/daily-logs, /api/daily-summary)
5. US-4: Smart Shopping List Generator Engine (/api/shopping-list/*)
6. US-5: Web Application Interface & REST API Gateway (/)
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from services.recipe_service import RecipeService
from services.calorie_service import CalorieService
from services.tracker_service import TrackerService
from services.shopping_service import ShoppingService
from services.auth_service import AuthService
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Inisialisasi Service untuk seluruh fitur MVP
recipe_service = RecipeService()
calorie_service = CalorieService()
tracker_service = TrackerService()
shopping_service = ShoppingService()
auth_service = AuthService()


# ==========================================
# AUTH MIDDLEWARE - Login Required Decorator
# ==========================================
def login_required(f):
    """Decorator untuk melindungi route yang membutuhkan autentikasi."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Jika request API (JSON), kembalikan error JSON
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'message': 'Silakan login terlebih dahulu.'}), 401
            # Jika request halaman, redirect ke login
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# US-0: AUTHENTICATION ROUTES
# ==========================================
@app.route('/login')
def login_page():
    """Halaman login & registrasi CookFit."""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/api/auth/register', methods=['POST'])
def register_endpoint():
    """Mendaftarkan akun pengguna baru."""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    display_name = data.get('display_name', '')

    try:
        result = auth_service.register(username, password, display_name)
        # Auto-login setelah registrasi
        session['user_id'] = result['id']
        session['username'] = result['username']
        session['display_name'] = result['display_name']
        return jsonify({'status': 'success', 'data': result}), 201
    except ValueError as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login_endpoint():
    """Memverifikasi kredensial login."""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')

    try:
        user = auth_service.login(username, password)
        # Simpan session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['display_name'] = user['display_name']
        return jsonify({'status': 'success', 'data': user})
    except ValueError as err:
        return jsonify({'status': 'error', 'message': str(err)}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout_endpoint():
    """Menghapus session pengguna (logout)."""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Berhasil logout.'})


@app.route('/api/auth/me', methods=['GET'])
def current_user_endpoint():
    """Mengambil data profil pengguna yang sedang login."""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Belum login.'}), 401

    user = auth_service.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'status': 'error', 'message': 'User tidak ditemukan.'}), 404

    return jsonify({'status': 'success', 'data': user})


# ==========================================
# MAIN PAGE (Protected)
# ==========================================
@app.route('/')
@login_required
def index():
    """Halaman antarmuka web mobile CookFit."""
    return render_template('index.html')


# ==========================================
# US-1: RECIPE MATCHING ENDPOINTS
# ==========================================
@app.route('/api/ingredients', methods=['GET'])
@login_required
def get_ingredients():
    """Mengambil katalog bahan dapur yang dikelompokkan per kategori."""
    ingredients = recipe_service.get_all_ingredients()
    return jsonify({'status': 'success', 'data': ingredients})


@app.route('/api/ingredients', methods=['POST'])
@login_required
def add_ingredient():
    """Menambahkan bahan makanan baru ke kategori tertentu di pantry."""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    category = data.get('category', 'Sayuran & Bumbu')
    calories = data.get('calories_per_100g', 50)

    if not name:
        return jsonify({'status': 'error', 'message': 'Nama bahan makanan tidak boleh kosong.'}), 400

    try:
        new_item = recipe_service.add_ingredient(name, category, calories)
        actual_category = next(
            ingredient_category
            for ingredient_category, items in recipe_service.get_all_ingredients().items()
            if new_item in items
        )
        return jsonify({
            'status': 'success',
            'message': f'Bahan "{name}" berhasil ditambahkan ke kategori {actual_category}!',
            'data': new_item,
            'category': actual_category
        }), 201
    except ValueError as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


@app.route('/api/ingredients/<int:ingredient_id>', methods=['DELETE'])
@login_required
def delete_ingredient(ingredient_id):
    """Menghapus bahan makanan dari katalog pantry."""
    deleted = recipe_service.delete_ingredient(ingredient_id)
    if deleted:
        return jsonify({'status': 'success', 'message': 'Bahan berhasil dihapus dari Pantry.'})
    return jsonify({'status': 'error', 'message': 'Bahan tidak ditemukan.'}), 404


@app.route('/api/recipes', methods=['GET'])
@login_required
def get_recipes():
    """Mengambil seluruh data resep dalam katalog CookFit."""
    recipes = recipe_service.get_all_recipes()
    return jsonify({'status': 'success', 'data': recipes})


@app.route('/api/match-recipes', methods=['POST'])
@login_required
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
@login_required
def calculate_bmr_endpoint():
    """
    Menghitung BMR, TDEE, dan target makronutrisi harian berdasarkan profil fisik.
    Payload: { gender, weight, height, age, activity_level, goal }
    """
    data = request.get_json(silent=True) or {}
    gender = data.get('gender', 'male')
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    activity = data.get('activity_level', 1.375)
    goal = data.get('goal', 'maintain')
    name = data.get('name')

    try:
        metrics = calorie_service.calculate_profile_metrics(
            gender=str(gender),
            weight_kg=float(weight),
            height_cm=float(height),
            age_years=int(age),
            activity_level=float(activity),
            goal=str(goal)
        )

        # Simpan BMR & TDEE ke profil user di database secara terisolasi per akun
        if 'user_id' in session:
            auth_service.update_profile(
                user_id=session['user_id'],
                display_name=name if name else None,
                gender=str(gender),
                weight=float(weight),
                height=float(height),
                age=int(age),
                activity_level=float(activity),
                bmr=metrics['bmr'],
                tdee=metrics['tdee'],
                goal=metrics['goal']
            )
            if name:
                session['display_name'] = name

        return jsonify({'status': 'success', 'data': metrics})
    except (ValueError, TypeError) as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


# ==========================================
# US-2B: COOKING PORTIONS & INGREDIENT NUTRITION CALCULATOR
# ==========================================
@app.route('/api/calculate-cooking', methods=['POST'])
@login_required
def calculate_cooking_endpoint():
    """
    Menghitung total kalori dan protein masakan berdasarkan takaran bahan (gram/siung/butir).
    Payload: { items: [ { name, amount, unit, cal_per_100g, protein_per_100g } ] }
    """
    data = request.get_json(silent=True) or {}
    items = data.get('items', [])

    try:
        results = calorie_service.calculate_cooking_recipe(items)
        return jsonify({'status': 'success', 'data': results})
    except (ValueError, TypeError) as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


@app.route('/api/calculate-cooking/portion', methods=['POST'])
@login_required
def calculate_portion_endpoint():
    """Menghitung kalori dan protein satu bahan masakan tertentu berdasarkan gram/unit."""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    amount = data.get('amount', 0)
    unit = data.get('unit', 'gram')
    cal_100 = data.get('cal_per_100g')
    p_100 = data.get('protein_per_100g')

    if not name:
        return jsonify({'status': 'error', 'message': 'Nama bahan makanan tidak boleh kosong.'}), 400

    try:
        res = calorie_service.calculate_ingredient_portion(
            name=name,
            amount=amount,
            unit=unit,
            cal_per_100g=cal_100,
            protein_per_100g=p_100
        )
        return jsonify({'status': 'success', 'data': res})
    except (ValueError, TypeError) as err:
        return jsonify({'status': 'error', 'message': str(err)}), 400


# ==========================================
# US-3: DAILY NUTRITRACKER & BUDGET ENDPOINTS
# ==========================================
@app.route('/api/daily-logs', methods=['GET', 'POST'])
@login_required
def daily_logs_endpoint():
    """
    GET: Mengambil riwayat log makan harian (opsional filter ?meal_type=...).
    POST: Mencatat konsumsi menu masakan ke log harian.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        try:
            recipe_id = data.get('recipe_id')
            recipe_title = data.get('recipe_title')
            if recipe_id is None and recipe_title:
                matching_recipe = next(
                    (
                        recipe for recipe in recipe_service.get_all_recipes()
                        if recipe["title"].strip().casefold() == str(recipe_title).strip().casefold()
                    ),
                    None
                )
                if matching_recipe:
                    recipe_id = matching_recipe["id"]

            if recipe_id is not None:
                try:
                    recipe_id = int(recipe_id)
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': 'ID resep tidak valid.'}), 400

                recipe = recipe_service.get_recipe_by_id(recipe_id)
                if not recipe:
                    return jsonify({'status': 'error', 'message': 'Resep tidak ditemukan.'}), 404

                ingredient_ids = data.get('ingredient_ids')
                if not isinstance(ingredient_ids, list):
                    return jsonify({
                        'status': 'error',
                        'message': 'Daftar bahan resep wajib dikirim.'
                    }), 400

                try:
                    selected_ids = {int(ingredient_id) for ingredient_id in ingredient_ids}
                except (ValueError, TypeError):
                    return jsonify({
                        'status': 'error',
                        'message': 'Daftar bahan resep tidak valid.'
                    }), 400

                missing_ids = set(recipe.get('required_ids', [])) - selected_ids
                if missing_ids:
                    missing_names = [
                        ingredient["name"]
                        for items in recipe_service.get_all_ingredients().values()
                        for ingredient in items
                        if ingredient["id"] in missing_ids
                    ]
                    missing_names.extend(
                        f"Bahan #{ingredient_id}"
                        for ingredient_id in missing_ids
                        if not any(
                            ingredient["id"] == ingredient_id
                            for items in recipe_service.get_all_ingredients().values()
                            for ingredient in items
                        )
                    )
                    missing_list = ', '.join(missing_names)
                    return jsonify({
                        'status': 'error',
                        'message': f'Lengkapi semua bahan resep sebelum mencatat ke Log Makan: {missing_list}.'
                    }), 400

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
@login_required
def delete_daily_log_endpoint(log_id):
    """Menghapus catatan makan dari log harian berdasarkan ID."""
    deleted = tracker_service.delete_log(log_id)
    calorie_service.delete_daily_log(log_id)
    if deleted:
        return jsonify({'status': 'success', 'message': f'Log #{log_id} berhasil dihapus.'})
    return jsonify({'status': 'error', 'message': 'Log tidak ditemukan.'}), 404


@app.route('/api/daily-summary', methods=['GET'])
@login_required
def daily_summary_endpoint():
    """Mengambil akumulasi total kalori & makronutrisi harian serta analisis budget."""
    tdee = request.args.get('target_tdee', type=int)
    summary = tracker_service.get_summary(target_tdee=tdee)
    return jsonify({'status': 'success', 'data': summary})


# ==========================================
# US-4: SMART SHOPPING LIST ENDPOINTS
# ==========================================
@app.route('/api/shopping-list', methods=['GET'])
@login_required
def get_shopping_list_endpoint():
    """Mengambil seluruh daftar belanjaan dan ringkasan progres."""
    category = request.args.get('category')
    items = shopping_service.get_items(category=category)
    summary = shopping_service.get_summary()
    return jsonify({'status': 'success', 'data': {'items': items, 'summary': summary}})


@app.route('/api/shopping-list/generate', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def toggle_shopping_item(item_id):
    """Mengubah status barang (sudah dibeli / belum)."""
    updated = shopping_service.toggle_item(item_id)
    if updated is not None:
        return jsonify({'status': 'success', 'data': updated})
    return jsonify({'status': 'error', 'message': 'Item belanja tidak ditemukan.'}), 404


@app.route('/api/shopping-list/<int:item_id>', methods=['DELETE'])
@login_required
def delete_shopping_item(item_id):
    """Menghapus satu item belanjaan berdasarkan ID."""
    deleted = shopping_service.delete_item(item_id)
    if deleted:
        return jsonify({'status': 'success', 'message': f'Item #{item_id} berhasil dihapus.'})
    return jsonify({'status': 'error', 'message': 'Item belanja tidak ditemukan.'}), 404


@app.route('/api/shopping-list/clear', methods=['DELETE', 'POST'])
@login_required
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
