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
    loadDailyLogs();
    loadShoppingList();
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
        loadShoppingList();
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
                <button class="btn-secondary" onclick="viewRecipeDetail(${r.id})">📖 Panduan</button>
                <button class="btn-outline-primary" onclick="logRecipeToTracker('${r.title.replace(/'/g, "\\'")}', ${r.total_calories}, ${r.total_protein}, ${r.total_carbs}, ${r.total_fat})">+ Log Makan</button>
                ${r.missing_ingredients && r.missing_ingredients.length > 0 ? `
                    <button class="btn-shop-recipe" onclick="addMissingToShopping(${r.id})">🛒 Beli Bahan</button>
                ` : ''}
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

async function logRecipeToTracker(title, calories, protein, carbs, fat) {
    const payload = {
        recipe_title: title,
        meal_type: 'Makan Siang',
        calories: calories,
        protein: protein,
        carbs: carbs,
        fat: fat
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
            alert(`✅ "${title}" berhasil ditambahkan ke NutriTracker!`);
            return;
        }
    } catch (err) {
        // Fallback client side
    }

    const fallbackLog = {
        id: Date.now(),
        ...payload
    };
    dailyLogs.unshift(fallbackLog);
    alert(`✅ "${title}" berhasil ditambahkan ke NutriTracker!`);
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
// PROFILE & BMR/TDEE CALCULATOR (Connected to Backend)
// ==========================================
function updateProfileUI() {
    const bmrEl = document.getElementById('disp-bmr');
    const tdeeEl = document.getElementById('disp-tdee');
    if (bmrEl) bmrEl.textContent = `${userProfile.bmr} kcal`;
    if (tdeeEl) tdeeEl.textContent = `${userProfile.tdee} kcal`;
}

async function saveProfile(e) {
    e.preventDefault();

    const name = document.getElementById('prof-name').value;
    const gender = document.getElementById('prof-gender').value;
    const weight = parseFloat(document.getElementById('prof-weight').value) || 60;
    const height = parseFloat(document.getElementById('prof-height').value) || 165;
    const age = parseInt(document.getElementById('prof-age').value) || 20;
    const activity = parseFloat(document.getElementById('prof-activity').value) || 1.375;

    try {
        const res = await fetch('/api/calculate-bmr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                gender,
                weight,
                height,
                age,
                activity_level: activity
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
                target_macros: json.data.target_macros
            };
            updateProfileUI();
            updateTrackerUI();
            alert('✅ Profil & Target TDEE Harian Berhasil Dihitung oleh Backend!');
            return;
        }
    } catch (err) {
        // Fallback local formula
    }

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

// ==========================================
// US-4: SHOPPING LIST LOGIC
// ==========================================
let shoppingItems = [];
let shoppingSummary = { total_items: 0, bought_count: 0, pending_count: 0, completion_percentage: 0 };

async function loadShoppingList() {
    try {
        const res = await fetch('/api/shopping-list');
        const json = await res.json();
        if (json.status === 'success') {
            shoppingItems = json.data.items || [];
            shoppingSummary = json.data.summary || {};
            renderShoppingList(shoppingItems, shoppingSummary);
            return;
        }
    } catch (err) {
        console.warn('Gagal memuat daftar belanja dari backend:', err);
    }
    renderShoppingList(shoppingItems, shoppingSummary);
}

function renderShoppingList(items, summary) {
    const container = document.getElementById('shopping-items-container');
    const badge = document.getElementById('nav-shopping-badge');
    const progText = document.getElementById('shopping-progress-text');
    const progBar = document.getElementById('shopping-progress-bar');

    const total = summary.total_items || items.length;
    const bought = summary.bought_count || items.filter(i => i.bought).length;
    const pct = summary.completion_percentage || (total > 0 ? Math.round((bought / total) * 100) : 0);

    if (badge) badge.textContent = total - bought;
    if (progText) progText.textContent = `${bought}/${total} Terbeli (${pct}%)`;
    if (progBar) progBar.style.width = `${pct}%`;

    if (!container) return;
    container.innerHTML = '';

    if (!items || items.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: var(--text-muted); background: var(--card-bg); border-radius: 14px; border: 1px dashed var(--card-border);">
                <div style="font-size: 32px; margin-bottom: 8px;">🛒</div>
                <div style="font-size: 14px; font-weight: 600; color: var(--text-main);">Daftar Belanja Masih Kosong</div>
                <div style="font-size: 12px; margin-top: 4px;">Pilih resep di tab "Resep Match" lalu klik "Beli Bahan", atau tambahkan manual di atas.</div>
            </div>
        `;
        return;
    }

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = `shopping-item-card ${item.bought ? 'bought' : ''}`;
        card.innerHTML = `
            <div class="shopping-item-left">
                <input type="checkbox" class="shopping-checkbox" ${item.bought ? 'checked' : ''} onchange="toggleShoppingItem(${item.id})">
                <div>
                    <div class="item-title">
                        ${item.name}
                        ${item.count > 1 ? `<span class="item-badge">x${item.count}</span>` : ''}
                    </div>
                    <div class="item-meta">
                        <span>📦 ${item.amount}</span> • <span style="color: #60a5fa;">${item.category}</span>
                        ${item.recipes && item.recipes.length > 0 ? ` • <span style="color: #fbbf24;">Resep: ${item.recipes.join(', ')}</span>` : ''}
                    </div>
                </div>
            </div>
            <div>
                <button class="btn-del" onclick="deleteShoppingItem(${item.id})" title="Hapus dari daftar belanja">✕</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function addMissingToShopping(recipeId) {
    const r = currentRecipes.find(item => item.id === recipeId) || FALLBACK_RECIPES.find(item => item.id === recipeId);
    if (!r || !r.missing_ingredients || r.missing_ingredients.length === 0) {
        alert('Semua bahan untuk resep ini sudah lengkap di dapur Anda!');
        return;
    }

    try {
        const res = await fetch('/api/shopping-list/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipe_title: r.title,
                missing_ingredients: r.missing_ingredients
            })
        });
        const json = await res.json();
        if (json.status === 'success') {
            alert(`✅ ${json.message}`);
            switchToTab('shopping-tab');
            return;
        }
    } catch (err) {
        console.warn('Backend offline, fallback lokal');
    }

    // Fallback lokal
    r.missing_ingredients.forEach(m => {
        const existing = shoppingItems.find(i => i.name.toLowerCase() === m.name.toLowerCase());
        if (existing) {
            existing.count += 1;
        } else {
            shoppingItems.push({
                id: Date.now() + Math.random(),
                name: m.name,
                category: 'Bahan Dapur',
                amount: 'secukupnya',
                bought: false,
                count: 1,
                recipes: [r.title]
            });
        }
    });
    alert(`✅ Bahan kurang untuk "${r.title}" ditambahkan ke daftar belanja!`);
    switchToTab('shopping-tab');
}

async function toggleShoppingItem(itemId) {
    try {
        const res = await fetch(`/api/shopping-list/${itemId}/toggle`, { method: 'PATCH' });
        const json = await res.json();
        if (json.status === 'success') {
            loadShoppingList();
            return;
        }
    } catch (err) {}

    const item = shoppingItems.find(i => i.id === itemId);
    if (item) {
        item.bought = !item.bought;
        renderShoppingList(shoppingItems, shoppingSummary);
    }
}

async function deleteShoppingItem(itemId) {
    try {
        const res = await fetch(`/api/shopping-list/${itemId}`, { method: 'DELETE' });
        const json = await res.json();
        if (json.status === 'success') {
            loadShoppingList();
            return;
        }
    } catch (err) {}

    shoppingItems = shoppingItems.filter(i => i.id !== itemId);
    renderShoppingList(shoppingItems, shoppingSummary);
}

async function addManualShoppingItem() {
    const nameEl = document.getElementById('manual-shopping-name');
    const amountEl = document.getElementById('manual-shopping-amount');
    const name = nameEl ? nameEl.value.trim() : '';
    const amount = amountEl ? amountEl.value.trim() : 'secukupnya';

    if (!name) {
        alert('Harap masukkan nama bahan yang ingin dibeli.');
        return;
    }

    try {
        const res = await fetch('/api/shopping-list/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, amount, category: 'Manual' })
        });
        const json = await res.json();
        if (json.status === 'success') {
            if (nameEl) nameEl.value = '';
            if (amountEl) amountEl.value = '';
            loadShoppingList();
            return;
        }
    } catch (err) {}

    shoppingItems.unshift({
        id: Date.now(),
        name,
        amount: amount || 'secukupnya',
        category: 'Manual',
        bought: false,
        count: 1,
        recipes: []
    });
    if (nameEl) nameEl.value = '';
    if (amountEl) amountEl.value = '';
    renderShoppingList(shoppingItems, shoppingSummary);
}

async function clearCompletedShopping() {
    try {
        const res = await fetch('/api/shopping-list/clear?completed_only=true', { method: 'DELETE' });
        const json = await res.json();
        if (json.status === 'success') {
            loadShoppingList();
            return;
        }
    } catch (err) {}

    shoppingItems = shoppingItems.filter(i => !i.bought);
    renderShoppingList(shoppingItems, shoppingSummary);
}

async function clearAllShopping() {
    if (!confirm('Yakin ingin mengosongkan seluruh daftar belanjaan?')) return;
    try {
        const res = await fetch('/api/shopping-list/clear', { method: 'DELETE' });
        const json = await res.json();
        if (json.status === 'success') {
            loadShoppingList();
            return;
        }
    } catch (err) {}

    shoppingItems = [];
    renderShoppingList(shoppingItems, shoppingSummary);
}

