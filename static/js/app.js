// CookFit Frontend Engine - Interactive Prototype

let selectedIngredients = new Set();
let allIngredientsCategorized = {};
let currentRecipes = [];
let dailyLogs = [];
let userProfile = {
    name: '',
    gender: 'male',
    weight: 0,
    height: 0,
    age: 0,
    activity_level: 1.375,
    bmr: 0,
    tdee: 0,
    goal: 'maintain',
    daily_calorie_target: 0
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
        {"id": 6, "name": "Cabai Merah", "calories_per_100g": 40}
    ]
};

const OPTIONAL_RECIPE_INGREDIENTS = {
    'tuna kaleng': { id: 7, name: 'Tuna Kaleng', category: 'Protein & Daging', calories_per_100g: 116 },
    'edamame': { id: 8, name: 'Edamame', category: 'Protein & Daging', calories_per_100g: 121 },
    'brokoli': { id: 9, name: 'Brokoli', category: 'Sayuran & Bumbu', calories_per_100g: 34 },
    'timun': { id: 10, name: 'Timun', category: 'Sayuran & Bumbu', calories_per_100g: 15 }
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
    },
    {
        "id": 4,
        "title": "Ayam Panggang Bawang Putih Tinggi Protein",
        "image_icon": "🍗",
        "prep_time": 30,
        "servings": 1,
        "total_calories": 340,
        "total_protein": 62,
        "total_carbs": 4,
        "total_fat": 8,
        "required_ids": [2, 5, 6],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "200 gram", "calories": 330},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 10},
            {"name": "Cabai Merah", "amount": "secukupnya", "calories": 5}
        ],
        "instructions": "1. Lumuri dada ayam dengan bawang putih, cabai, garam, dan lada.\n2. Diamkan selama 10 menit agar bumbu meresap.\n3. Panggang di oven atau teflon anti lengket hingga matang merata."
    },
    {
        "id": 5,
        "title": "Tahu Ayam Kukus Tinggi Protein",
        "image_icon": "🍲",
        "prep_time": 25,
        "servings": 1,
        "total_calories": 330,
        "total_protein": 55,
        "total_carbs": 8,
        "total_fat": 12,
        "required_ids": [2, 3, 5],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "150 gram", "calories": 248},
            {"name": "Tahu Putih", "amount": "100 gram", "calories": 76},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 6}
        ],
        "instructions": "1. Cincang dada ayam dan haluskan tahu, lalu campurkan dengan bawang putih dan bumbu secukupnya.\n2. Bentuk adonan menjadi beberapa bagian.\n3. Kukus selama 15–20 menit hingga ayam matang."
    },
    {
        "id": 6,
        "title": "Omelet Dada Ayam Tinggi Protein",
        "image_icon": "🍳",
        "prep_time": 20,
        "servings": 1,
        "total_calories": 310,
        "total_protein": 44,
        "total_carbs": 3,
        "total_fat": 14,
        "required_ids": [1, 2, 5],
        "ingredients": [
            {"name": "Dada Ayam", "amount": "100 gram", "calories": 165},
            {"name": "Telur Ayam", "amount": "2 butir", "calories": 140},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 5}
        ],
        "instructions": "1. Potong dada ayam kecil-kecil dan masak hingga matang.\n2. Kocok telur bersama bawang cincang dan sedikit garam.\n3. Tuangkan telur ke ayam, lalu masak di teflon anti lengket hingga omelet matang."
    },
    {
        "id": 7,
        "title": "Tuna Brokoli Tumis Tinggi Protein",
        "image_icon": "🐟",
        "prep_time": 15,
        "servings": 1,
        "total_calories": 225,
        "total_protein": 41,
        "total_carbs": 12,
        "total_fat": 3,
        "required_ids": [7, 9, 5],
        "ingredients": [
            {"name": "Tuna Kaleng", "amount": "150 gram", "calories": 174},
            {"name": "Brokoli", "amount": "100 gram", "calories": 34},
            {"name": "Bawang Merah & Putih", "amount": "secukupnya", "calories": 17}
        ],
        "instructions": "1. Tiriskan tuna dan potong brokoli menjadi bagian kecil.\n2. Tumis bawang dengan sedikit air, lalu masukkan brokoli hingga empuk.\n3. Masukkan tuna, aduk hingga panas dan sajikan."
    },
    {
        "id": 8,
        "title": "Bowl Edamame Tahu dan Brokoli",
        "image_icon": "🥗",
        "prep_time": 20,
        "servings": 1,
        "total_calories": 245,
        "total_protein": 24,
        "total_carbs": 20,
        "total_fat": 10,
        "required_ids": [8, 3, 9],
        "ingredients": [
            {"name": "Edamame", "amount": "100 gram", "calories": 121},
            {"name": "Tahu Putih", "amount": "100 gram", "calories": 76},
            {"name": "Brokoli", "amount": "100 gram", "calories": 34}
        ],
        "instructions": "1. Rebus edamame dan brokoli hingga matang.\n2. Potong tahu, lalu kukus atau panggang hingga hangat.\n3. Sajikan tahu bersama edamame dan brokoli."
    },
    {
        "id": 9,
        "title": "Salad Tuna Telur dan Timun",
        "image_icon": "🥚",
        "prep_time": 15,
        "servings": 1,
        "total_calories": 235,
        "total_protein": 33,
        "total_carbs": 5,
        "total_fat": 9,
        "required_ids": [7, 1, 10],
        "ingredients": [
            {"name": "Tuna Kaleng", "amount": "100 gram", "calories": 116},
            {"name": "Telur Ayam", "amount": "1 butir", "calories": 78},
            {"name": "Timun", "amount": "100 gram", "calories": 15}
        ],
        "instructions": "1. Rebus telur hingga matang dan tiriskan tuna.\n2. Iris telur dan timun.\n3. Campurkan dengan tuna, bumbui lada dan sedikit garam, lalu sajikan."
    }
];

document.addEventListener('DOMContentLoaded', () => {
    loadCurrentUser();
    initNavigation();
    loadIngredients();
    loadDailyLogs();
    renderIngredientsSummaryList();
    updateTrackerUI();
    updateProfileUI();
});

// ==========================================
// AUTH - CURRENT USER & LOGOUT
// ==========================================
async function loadCurrentUser() {
    try {
        const res = await fetch('/api/auth/me');
        const json = await res.json();
        if (json.status === 'success' && json.data) {
            const user = json.data;
            const avatar = document.getElementById('user-avatar');
            const displayName = user.display_name || user.username || '';
            if (avatar) {
                avatar.textContent = (displayName || '?')[0].toUpperCase();
                avatar.title = displayName;
            }
            // Sinkronkan profil akun dari database secara terisolasi per user
            userProfile.name = displayName;
            userProfile.gender = user.gender || 'male';
            userProfile.weight = Number(user.weight) || 0;
            userProfile.height = Number(user.height) || 0;
            userProfile.age = Number(user.age) || 0;
            userProfile.activity_level = Number(user.activity_level) || 1.375;
            userProfile.bmr = Number(user.bmr) || 0;
            userProfile.tdee = Number(user.tdee) || 0;
            userProfile.goal = user.goal || 'maintain';
            userProfile.daily_calorie_target = calculateDailyCalorieTarget(
                userProfile.tdee, userProfile.bmr, userProfile.goal
            );

            // Update form fields profil
            const nameEl = document.getElementById('prof-name');
            const genderEl = document.getElementById('prof-gender');
            const weightEl = document.getElementById('prof-weight');
            const heightEl = document.getElementById('prof-height');
            const ageEl = document.getElementById('prof-age');
            const activityEl = document.getElementById('prof-activity');
            const goalEl = document.getElementById('prof-goal');

            if (nameEl) nameEl.value = userProfile.name;
            if (genderEl) genderEl.value = userProfile.gender;
            if (weightEl) weightEl.value = userProfile.weight > 0 ? userProfile.weight : '';
            if (heightEl) heightEl.value = userProfile.height > 0 ? userProfile.height : '';
            if (ageEl) ageEl.value = userProfile.age > 0 ? userProfile.age : '';
            if (activityEl) activityEl.value = userProfile.activity_level;
            if (goalEl) goalEl.value = userProfile.goal;

            updateProfileUI();
            updateTrackerUI();
        }
    } catch (err) {
        console.warn('Gagal memuat data user:', err);
    }
}

async function handleLogout() {
    if (!confirm('Yakin ingin keluar dari CookFit?')) return;
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (err) {}
    window.location.href = '/login';
}


// ==========================================
// NAVIGATION SYSTEM
// ==========================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.dataset.tab;
            switchToTab(targetTab);
        });
    });
}

function switchToTab(targetTab) {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(n => n.classList.remove('active'));
    tabContents.forEach(t => t.classList.remove('active'));

    const navBtn = document.querySelector(`.nav-item[data-tab="${targetTab}"]`);
    if (navBtn) navBtn.classList.add('active');

    const targetEl = document.getElementById(targetTab);
    if (targetEl) targetEl.classList.add('active');

    if (targetTab === 'recipes-tab') {
        triggerRecipeMatching();
    } else if (targetTab === 'shopping-tab') {
        renderIngredientsSummaryList();
    }
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
    renderIngredientsSummaryList();
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
                const optionalIngredient = Object.values(OPTIONAL_RECIPE_INGREDIENTS)
                    .find(ingredient => ingredient.id === id);
                if (optionalIngredient) {
                    missing.push({ name: optionalIngredient.name });
                }
                for (const items of Object.values(FALLBACK_INGREDIENTS)) {
                    const found = items.find(i => i.id === id);
                    if (found && !missing.some(item => item.name === found.name)) {
                        missing.push({ name: found.name });
                    }
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
            <div class="recipe-header">
                <div class="recipe-icon">${r.image_icon}</div>
                <div class="recipe-info">
                    <div class="recipe-title-row">
                        <div class="recipe-title">${r.title}</div>
                        <div class="match-badge ${badgeClass}">${r.match_score}% Match</div>
                    </div>
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
                <button class="btn-secondary" onclick="viewRecipeDetail(${r.id})">📖 Panduan</button>
                <button
                    class="btn-outline-primary"
                    onclick="logRecipeToTracker(${r.id})"
                    ${r.missing_ingredients && r.missing_ingredients.length > 0
                        ? 'disabled title="Lengkapi semua bahan di Pantry sebelum mencatat resep ini." style="opacity:0.5; cursor:not-allowed;"'
                        : ''}
                >+ Log Makan</button>
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
// ==========================================
// NUTRITRACKER & DAILY LOG (Connected to Backend API)
// ==========================================
async function loadDailyLogs() {
    try {
        const res = await fetch('/api/daily-logs');
        const json = await res.json();
        if (json.status === 'success') {
            dailyLogs = json.data;
        }
    } catch (err) {
        // Fallback local memory
    }
    updateTrackerUI();
}

async function logRecipeToTracker(recipeId) {
    const recipe = currentRecipes.find(item => item.id === recipeId)
        || FALLBACK_RECIPES.find(item => item.id === recipeId);
    if (!recipe) {
        alert('Resep tidak ditemukan. Silakan muat ulang daftar resep.');
        return;
    }

    if (recipe.missing_ingredients && recipe.missing_ingredients.length > 0) {
        alert('Lengkapi semua bahan resep di Pantry sebelum mencatatnya ke Log Makan.');
        return;
    }

    const payload = {
        recipe_id: recipe.id,
        ingredient_ids: Array.from(selectedIngredients),
        recipe_title: recipe.title,
        meal_type: 'Makan Siang',
        calories: recipe.total_calories,
        protein: recipe.total_protein,
        carbs: recipe.total_carbs,
        fat: recipe.total_fat
    };

    try {
        const res = await fetch('/api/daily-logs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.status === 'success') {
            await loadDailyLogs();
            alert(`✅ "${recipe.title}" berhasil ditambahkan ke NutriTracker!`);
            return;
        }
        alert('Gagal mencatat resep: ' + (json.message || 'Terjadi kesalahan.'));
        return;
    } catch (err) {
        console.warn('Gagal menghubungi backend saat mencatat resep:', err);
    }

    const fallbackLog = {
        id: Date.now(),
        ...payload
    };
    dailyLogs.unshift(fallbackLog);
    alert(`✅ "${recipe.title}" berhasil ditambahkan ke NutriTracker!`);
    updateTrackerUI();
}

async function deleteLogEntry(id) {
    try {
        const res = await fetch(`/api/daily-logs/${id}`, { method: 'DELETE' });
        const json = await res.json();
        if (json.status === 'success') {
            await loadDailyLogs();
            return;
        }
    } catch (err) {
        // Fallback local filter
    }

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

    const targetTdee = userProfile.daily_calorie_target || userProfile.tdee || 0;
    const percentage = targetTdee > 0 ? Math.min(Math.round((totCal / targetTdee) * 100), 100) : 0;

    const cVal = document.getElementById('current-calories-val');
    const tVal = document.getElementById('target-tdee-val');
    const bar = document.getElementById('progress-bar-fill');

    if (cVal) cVal.textContent = totCal;
    if (tVal) tVal.textContent = targetTdee > 0 ? targetTdee : 0;
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
// PROFILE & BMR/TDEE CALCULATOR (Connected to Backend)
// ==========================================
function updateProfileUI() {
    const bmrEl = document.getElementById('disp-bmr');
    const tdeeEl = document.getElementById('disp-tdee');
    const targetEl = document.getElementById('disp-daily-calorie-target');
    if (bmrEl) bmrEl.textContent = `${userProfile.bmr || 0} kcal`;
    if (tdeeEl) tdeeEl.textContent = `${userProfile.tdee || 0} kcal`;
    if (targetEl) targetEl.textContent = `${userProfile.daily_calorie_target || userProfile.tdee || 0} kcal`;
}

function calculateDailyCalorieTarget(tdee, bmr, goal) {
    if (goal === 'cutting') return Math.max(bmr, tdee - 300);
    if (goal === 'bulking') return tdee + 300;
    return tdee;
}

async function saveProfile(e) {
    e.preventDefault();

    const name = document.getElementById('prof-name').value.trim();
    const gender = document.getElementById('prof-gender').value;
    const weight = parseFloat(document.getElementById('prof-weight').value);
    const height = parseFloat(document.getElementById('prof-height').value);
    const age = parseInt(document.getElementById('prof-age').value);
    const activity = parseFloat(document.getElementById('prof-activity').value) || 1.375;
    const goal = document.getElementById('prof-goal').value;

    if (!weight || weight <= 0 || !height || height <= 0 || !age || age <= 0) {
        alert('Harap isi Berat Badan, Tinggi Badan, dan Usia yang valid (lebih dari 0).');
        return;
    }

    try {
        const res = await fetch('/api/calculate-bmr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                gender,
                weight,
                height,
                age,
                activity_level: activity,
                goal
            })
        });
        const json = await res.json();
        if (json.status === 'success') {
            userProfile = {
                name,
                gender,
                weight,
                height,
                age,
                activity_level: activity,
                bmr: json.data.bmr,
                tdee: json.data.tdee,
                goal: json.data.goal,
                daily_calorie_target: json.data.daily_calorie_target,
                target_macros: json.data.target_macros
            };

            const avatar = document.getElementById('user-avatar');
            if (avatar && name) {
                avatar.textContent = name[0].toUpperCase();
                avatar.title = name;
            }

            updateProfileUI();
            updateTrackerUI();
            alert('✅ Profil, BMR, dan target kalori harian berhasil disimpan!');
            return;
        } else {
            alert('Gagal: ' + (json.message || 'Terjadi kesalahan kalkulasi.'));
            return;
        }
    } catch (err) {
        console.warn('Gagal menghubungi backend:', err);
    }

    let bmr = 0;
    if (gender === 'male') {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }

    const tdee = Math.round(bmr * activity);
    bmr = Math.round(bmr);

    const dailyCalorieTarget = calculateDailyCalorieTarget(tdee, bmr, goal);
    userProfile = {
        name, gender, weight, height, age, activity_level: activity,
        bmr, tdee, goal, daily_calorie_target: dailyCalorieTarget
    };

    updateProfileUI();
    updateTrackerUI();
    alert('✅ Profil dan target kalori harian berhasil diperbarui!');
}

// ==========================================
// TAMBAH BAHAN MAKANAN KE PANTRY
// ==========================================
async function handleAddNewIngredient(e) {
    e.preventDefault();

    const nameInput = document.getElementById('manual-ingredient-name');
    const catSelect = document.getElementById('manual-ingredient-category');
    const calInput = document.getElementById('manual-ingredient-calories');

    const name = nameInput ? nameInput.value.trim() : '';
    const category = catSelect ? catSelect.value : 'Sayuran & Bumbu';
    const calories = calInput ? (parseInt(calInput.value) || 50) : 50;

    if (!name) {
        alert('Harap masukkan nama bahan makanan.');
        return;
    }

    try {
        const res = await fetch('/api/ingredients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                category,
                calories_per_100g: calories
            })
        });
        const json = await res.json();
        if (json.status === 'success') {
            const newItem = json.data;
            const itemCategory = json.category || category;

            if (!allIngredientsCategorized[itemCategory]) {
                allIngredientsCategorized[itemCategory] = [];
            }
            const exists = allIngredientsCategorized[itemCategory].some(i => i.id === newItem.id);
            if (!exists) {
                allIngredientsCategorized[itemCategory].push(newItem);
            }

            // Otomatis tandai/centang bahan baru ini di Pantry agar siap dicocokkan resep
            selectedIngredients.add(newItem.id);

            // Re-render Pantry & Ringkasan Bahan
            renderPantryGrid();
            updateSelectedCountBadge();
            renderIngredientsSummaryList();

            // Reset input form
            if (nameInput) nameInput.value = '';
            if (calInput) calInput.value = '50';

            alert(`✅ Bahan "${name}" berhasil ditambahkan ke kategori "${itemCategory}" di Pantry kulkas Anda!`);
            return;
        } else {
            alert('Gagal: ' + (json.message || 'Terjadi kesalahan'));
            return;
        }
    } catch (err) {
        console.warn('Backend request failed, fallback lokal:', err);
    }

    // Fallback lokal jika backend tidak terhubung
    const optionalIngredient = OPTIONAL_RECIPE_INGREDIENTS[name.toLowerCase()];
    const itemCategory = optionalIngredient ? optionalIngredient.category : category;
    const fallbackItem = optionalIngredient
        ? { ...optionalIngredient }
        : {
            id: Math.max(
                10,
                ...Object.values(allIngredientsCategorized)
                    .flat()
                    .map(ingredient => ingredient.id)
            ) + 1,
            name,
            calories_per_100g: calories
        };

    if (!allIngredientsCategorized[itemCategory]) {
        allIngredientsCategorized[itemCategory] = [];
    }
    if (!allIngredientsCategorized[itemCategory].some(item => item.id === fallbackItem.id)) {
        allIngredientsCategorized[itemCategory].push(fallbackItem);
    }
    selectedIngredients.add(fallbackItem.id);

    renderPantryGrid();
    updateSelectedCountBadge();
    renderIngredientsSummaryList();

    if (nameInput) nameInput.value = '';
    alert(`✅ Bahan "${name}" berhasil ditambahkan ke kategori "${itemCategory}" di Pantry kulkas Anda!`);
}

function renderIngredientsSummaryList() {
    const container = document.getElementById('all-ingredients-summary-list');
    if (!container) return;
    container.innerHTML = '';

    const categories = Object.keys(allIngredientsCategorized);
    if (categories.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:20px; color:#94a3b8; font-size:13px;">Belum ada bahan makanan di Pantry.</div>';
        return;
    }

    for (const [category, items] of Object.entries(allIngredientsCategorized)) {
        if (!items || items.length === 0) continue;

        const isProtein = category.toLowerCase().includes('protein') || category.toLowerCase().includes('daging');
        const badgeColor = isProtein ? '#ef4444' : '#10b981';
        const badgeBg = isProtein ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)';
        const icon = isProtein ? '🥩' : '🥦';

        const catBlock = document.createElement('div');
        catBlock.style.cssText = 'background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 14px; margin-bottom: 12px;';

        const itemsHtml = items.map(item => `
            <div style="display:flex; justify-content:space-between; align-items:center; background: rgba(15,23,42,0.5); padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:14px; color: var(--text-main); font-weight:600;">${item.name}</span>
                    <span style="font-size:11px; color:#94a3b8;">(${item.calories_per_100g} kcal/100g)</span>
                </div>
                <button onclick="handleDeleteIngredient(${item.id}, '${item.name.replace(/'/g, "\\'")}')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:14px; padding:4px 8px;" title="Hapus bahan">🗑️</button>
            </div>
        `).join('');

        catBlock.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                <span style="font-weight:700; font-size:13px; color: ${badgeColor}; display:flex; align-items:center; gap:6px;">
                    <span>${icon}</span> ${category}
                </span>
                <span style="font-size:11px; background:${badgeBg}; color:${badgeColor}; padding:2px 8px; border-radius:20px; font-weight:600;">
                    ${items.length} bahan
                </span>
            </div>
            <div>
                ${itemsHtml}
            </div>
        `;
        container.appendChild(catBlock);
    }
}

async function handleDeleteIngredient(id, name) {
    if (!confirm(`Hapus "${name}" dari Pantry kulkas?`)) return;

    try {
        const res = await fetch(`/api/ingredients/${id}`, { method: 'DELETE' });
        const json = await res.json();
        if (json.status === 'success') {
            for (const cat in allIngredientsCategorized) {
                allIngredientsCategorized[cat] = allIngredientsCategorized[cat].filter(i => i.id !== id);
            }
            selectedIngredients.delete(id);
            renderPantryGrid();
            updateSelectedCountBadge();
            renderIngredientsSummaryList();
            return;
        }
    } catch (err) {}

    for (const cat in allIngredientsCategorized) {
        allIngredientsCategorized[cat] = allIngredientsCategorized[cat].filter(i => i.id !== id);
    }
    selectedIngredients.delete(id);
    renderPantryGrid();
    updateSelectedCountBadge();
    renderIngredientsSummaryList();
}
