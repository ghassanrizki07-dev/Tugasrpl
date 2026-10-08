// CookFit Frontend Engine - Interactive Prototype

let selectedIngredients = new Set();
let allIngredientsCategorized = {};
let currentRecipes = [];
let dailyLogs = [];
let userProfile = {
    name: 'Pengguna CookFit',
    gender: 'male',
    weight: 65,
    height: 170,
    age: 22,
    activity_level: 1.375,
    bmr: 1605,
    tdee: 2206
};

// Mock data fallback jika offline / standalone
const FALLBACK_INGREDIENTS = {
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
};

const FALLBACK_RECIPES = [
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
];

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadIngredients();
    updateTrackerUI();
    updateProfileUI();
});

// ==========================================
// NAVIGATION SYSTEM
// ==========================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.dataset.tab;
            
            navItems.forEach(n => n.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));

            item.classList.add('active');
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add('active');

            if (targetTab === 'recipes-tab') {
                triggerRecipeMatching();
            }
        });
    });
}

// ==========================================
// PANTRY & INGREDIENT CHECKLIST
// ==========================================
async function loadIngredients() {
    try {
        const res = await fetch('/api/ingredients');
        const json = await res.json();
        if (json.status === 'success') {
            allIngredientsCategorized = json.data;
        } else {
            allIngredientsCategorized = FALLBACK_INGREDIENTS;
        }
    } catch (err) {
        allIngredientsCategorized = FALLBACK_INGREDIENTS;
    }
    renderPantryGrid();
}

function renderPantryGrid(filterText = '') {
    const container = document.getElementById('pantry-categories-container');
    if (!container) return;
    container.innerHTML = '';

    for (const [category, items] of Object.entries(allIngredientsCategorized)) {
        const filteredItems = items.filter(item => 
            item.name.toLowerCase().includes(filterText.toLowerCase())
        );

        if (filteredItems.length === 0) continue;

        const catBox = document.createElement('div');
        catBox.className = 'category-group';
        
        const catTitle = document.createElement('div');
        catTitle.className = 'category-title';
        catTitle.innerHTML = `<span>${category}</span> <span>${filteredItems.length} bahan</span>`;
        catBox.appendChild(catTitle);

        const grid = document.createElement('div');
        grid.className = 'pantry-grid';

        filteredItems.forEach(item => {
            const isSelected = selectedIngredients.has(item.id);
            const itemEl = document.createElement('div');
            itemEl.className = `pantry-item ${isSelected ? 'selected' : ''}`;
            itemEl.innerHTML = `
                <div class="pantry-checkbox">${isSelected ? '✓' : ''}</div>
                <div class="pantry-name">${item.name}</div>
                <div class="pantry-cal">${item.calories_per_100g} kcal</div>
            `;

            itemEl.addEventListener('click', () => {
                toggleIngredientSelection(item.id);
                renderPantryGrid(document.getElementById('pantry-search')?.value || '');
            });

            grid.appendChild(itemEl);
        });

        catBox.appendChild(grid);
        container.appendChild(catBox);
    }

    updateSelectedCountBadge();
}

function toggleIngredientSelection(id) {
    if (selectedIngredients.has(id)) {
        selectedIngredients.delete(id);
    } else {
        selectedIngredients.add(id);
    }
    updateSelectedCountBadge();
}

function updateSelectedCountBadge() {
    const count = selectedIngredients.size;
    const b1 = document.getElementById('selected-count-badge');
    const b2 = document.getElementById('nav-pantry-badge');
    if (b1) b1.textContent = `${count} Bahan`;
    if (b2) b2.textContent = count;
}

function filterPantry() {
    const val = document.getElementById('pantry-search')?.value || '';
    renderPantryGrid(val);
}

// ==========================================
// SMART RECIPE MATCHER ENGINE
// ==========================================
async function triggerRecipeMatching() {
    const listContainer = document.getElementById('recipe-list-container');
    if (!listContainer) return;

    listContainer.innerHTML = `<div style="text-align:center; padding: 40px; color: #94a3b8;">🔄 Menghitung persentase kecocokan resep...</div>`;

    try {
        const body = { ingredient_ids: Array.from(selectedIngredients) };
        const res = await fetch('/api/match-recipes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const json = await res.json();

        if (json.status === 'success') {
            currentRecipes = json.data;
            renderRecipeList(json.data);
            return;
        }
    } catch (err) {
        // Fallback matching client side
    }

    calculateClientSideMatching();
}

function calculateClientSideMatching() {
    const selSet = selectedIngredients;
    const results = FALLBACK_RECIPES.map(r => {
        const reqSet = new Set(r.required_ids);
        let matchCount = 0;
        let missing = [];

        r.required_ids.forEach(id => {
            if (selSet.has(id)) {
                matchCount++;
            } else {
                // cari nama
                for (const items of Object.values(FALLBACK_INGREDIENTS)) {
                    const found = items.find(i => i.id === id);
                    if (found) missing.push({ name: found.name });
                }
            }
        });

        const score = Math.round((matchCount / reqSet.size) * 100);
        return {
            ...r,
            match_score: score,
            missing_ingredients: missing
        };
    });

    results.sort((a, b) => b.match_score - a.match_score);
    currentRecipes = results;
    renderRecipeList(results);
}

function renderRecipeList(recipes) {
    const container = document.getElementById('recipe-list-container');
    if (!container) return;
    container.innerHTML = '';

    if (!recipes || recipes.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding:40px; color:#94a3b8;">Tidak ada resep ditemukan.</div>`;
        return;
    }

    recipes.forEach(r => {
        let badgeClass = 'high';
        if (r.match_score < 40) badgeClass = 'low';
        else if (r.match_score < 75) badgeClass = 'medium';

        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <div class="match-badge ${badgeClass}">${r.match_score}% Match</div>
            <div class="recipe-header">
                <div class="recipe-icon">${r.image_icon}</div>
                <div class="recipe-info">
                    <div class="recipe-title">${r.title}</div>
                    <div class="recipe-meta">
                        <span>⏱️ ${r.prep_time} mnt</span> • <span>🍽️ ${r.servings} Porsi</span>
                    </div>
                </div>
            </div>

            <div class="nutri-pills">
                <div class="nutri-pill">🔥 ${r.total_calories} <span>kcal</span></div>
                <div class="nutri-pill">🥩 P: ${r.total_protein}g</div>
                <div class="nutri-pill">🍚 K: ${r.total_carbs}g</div>
                <div class="nutri-pill">🥑 L: ${r.total_fat}g</div>
            </div>

            ${r.missing_ingredients && r.missing_ingredients.length > 0 ? `
                <div class="missing-box">
                    <div class="missing-title">⚠️ Bahan Kurang (${r.missing_ingredients.length}):</div>
                    <div class="missing-list">${r.missing_ingredients.map(m => m.name).join(', ')}</div>
                </div>
            ` : `
                <div class="missing-box" style="background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3);">
                    <div class="missing-title" style="color: #34d399;">✅ Semua Bahan Tersedia di Kulkas!</div>
                </div>
            `}

            <div class="recipe-actions">
                <button class="btn-secondary" onclick="viewRecipeDetail(${r.id})">📖 Panduan Resep</button>
                <button class="btn-outline-primary" onclick="logRecipeToTracker('${r.title.replace(/'/g, "\\'")}', ${r.total_calories}, ${r.total_protein}, ${r.total_carbs}, ${r.total_fat})">+ Log Makan</button>
            </div>
        `;

        container.appendChild(card);
    });
}

// ==========================================
// RECIPE DETAIL MODAL
// ==========================================
function viewRecipeDetail(recipeId) {
    const r = currentRecipes.find(item => item.id === recipeId) || FALLBACK_RECIPES.find(item => item.id === recipeId);
    if (!r) return;

    document.getElementById('modal-recipe-title').textContent = `${r.image_icon} ${r.title}`;
    
    let ingHtml = r.ingredients.map(i => `<li><b>${i.name}</b> (${i.amount}) - ${i.calories} kcal</li>`).join('');
    document.getElementById('modal-ingredients-list').innerHTML = ingHtml;
    document.getElementById('modal-instructions').innerHTML = r.instructions.replace(/\n/g, '<br>');
    
    document.getElementById('recipe-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('recipe-modal').classList.remove('active');
}

// ==========================================
// NUTRITRACKER & DAILY LOG (Interactive local log)
// ==========================================
function logRecipeToTracker(title, calories, protein, carbs, fat) {
    const newLog = {
        id: Date.now(),
        recipe_title: title,
        meal_type: 'Makan Siang',
        calories: calories,
        protein: protein,
        carbs: carbs,
        fat: fat
    };
    dailyLogs.unshift(newLog);
    alert(`✅ "${title}" berhasil ditambahkan ke NutriTracker!`);
    updateTrackerUI();
}

function deleteLogEntry(id) {
    dailyLogs = dailyLogs.filter(l => l.id !== id);
    updateTrackerUI();
}

function updateTrackerUI() {
    let totCal = 0, totP = 0, totC = 0, totF = 0;
    dailyLogs.forEach(l => {
        totCal += l.calories;
        totP += l.protein;
        totC += l.carbs;
        totF += l.fat;
    });

    const targetTdee = userProfile.tdee;
    const percentage = Math.min(Math.round((totCal / targetTdee) * 100), 100);

    const cVal = document.getElementById('current-calories-val');
    const tVal = document.getElementById('target-tdee-val');
    const bar = document.getElementById('progress-bar-fill');

    if (cVal) cVal.textContent = totCal;
    if (tVal) tVal.textContent = targetTdee;
    if (bar) bar.style.width = `${percentage}%`;

    const mP = document.getElementById('macro-protein');
    const mC = document.getElementById('macro-carbs');
    const mF = document.getElementById('macro-fat');

    if (mP) mP.textContent = `${totP}g`;
    if (mC) mC.textContent = `${totC}g`;
    if (mF) mF.textContent = `${totF}g`;

    renderLogList();
}

function renderLogList() {
    const container = document.getElementById('daily-logs-container');
    if (!container) return;
    container.innerHTML = '';

    if (dailyLogs.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 20px; color: #94a3b8; font-size:13px;">Belum ada makanan dicatat hari ini. Klik "+ Log Makan" pada resep.</div>`;
        return;
    }

    dailyLogs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'log-item';
        item.innerHTML = `
            <div>
                <div class="log-title">${log.recipe_title}</div>
                <div class="log-meta">${log.meal_type} • P:${log.protein}g K:${log.carbs}g L:${log.fat}g</div>
            </div>
            <div style="display:flex; align-items:center;">
                <div class="log-cal">+${log.calories} kcal</div>
                <button class="btn-del" onclick="deleteLogEntry(${log.id})">🗑️</button>
            </div>
        `;
        container.appendChild(item);
    });
}

// ==========================================
// PROFILE & BMR/TDEE CALCULATOR
// ==========================================
function updateProfileUI() {
    const bmrEl = document.getElementById('disp-bmr');
    const tdeeEl = document.getElementById('disp-tdee');
    if (bmrEl) bmrEl.textContent = `${userProfile.bmr} kcal`;
    if (tdeeEl) tdeeEl.textContent = `${userProfile.tdee} kcal`;
}

function saveProfile(e) {
    e.preventDefault();

    const name = document.getElementById('prof-name').value;
    const gender = document.getElementById('prof-gender').value;
    const weight = parseFloat(document.getElementById('prof-weight').value) || 60;
    const height = parseFloat(document.getElementById('prof-height').value) || 165;
    const age = parseInt(document.getElementById('prof-age').value) || 20;
    const activity = parseFloat(document.getElementById('prof-activity').value) || 1.375;

    let bmr = 0;
    if (gender === 'male') {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }

    const tdee = Math.round(bmr * activity);
    bmr = Math.round(bmr);

    userProfile = { name, gender, weight, height, age, activity_level: activity, bmr, tdee };

    updateProfileUI();
    updateTrackerUI();
    alert('✅ Profil & Target TDEE Harian Berhasil Diperbarui!');
}
