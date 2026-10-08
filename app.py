from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Data mock sederhana (beberapa bahan saja)
MOCK_INGREDIENTS = {
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

# Data mock 3 resep sederhana
MOCK_RECIPES = [
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ingredients')
def get_ingredients():
    return jsonify({'status': 'success', 'data': MOCK_INGREDIENTS})

@app.route('/api/match-recipes', methods=['POST'])
def match_recipes():
    data = request.get_json() or {}
    selected_ids = data.get('ingredient_ids', [])
    
    results = []
    for r in MOCK_RECIPES:
        req_set = set(r['required_ids'])
        sel_set = set(selected_ids)
        matched = req_set.intersection(sel_set)
        score = int((len(matched) / len(req_set)) * 100) if req_set else 100
        
        missing_ids = [i for i in req_set if i not in sel_set]
        missing_names = []
        # Cari nama bahan yang hilang
        for cat in MOCK_INGREDIENTS.values():
            for item in cat:
                if item['id'] in missing_ids:
                    missing_names.append({"name": item['name']})
        
        recipe_copy = dict(r)
        recipe_copy['match_score'] = score
        recipe_copy['missing_ingredients'] = missing_names
        results.append(recipe_copy)
    
    # Sort berdasarkan match score tertinggi
    results.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify({'status': 'success', 'data': results})

if __name__ == '__main__':
    print("[COOKFIT] Server running at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
