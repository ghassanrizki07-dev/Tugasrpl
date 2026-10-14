from flask import Flask, render_template, jsonify, request
from services.recipe_service import RecipeService

app = Flask(__name__)

# Inisialisasi Service Fitur 1
recipe_service = RecipeService()

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    print("[COOKFIT] Server running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
