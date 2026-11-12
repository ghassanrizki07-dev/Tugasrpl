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
        "image_icon": "Sayur",
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
        "image_icon": "Telur",
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
        "image_icon": "Ayam",
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
        "image_icon": "Ayam",
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
        "image_icon": "Kukus",
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
        "image_icon": "Telur",
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
        "image_icon": "Tuna",
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
        "image_icon": "Sayur",
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
        "image_icon": "Telur",
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
    initAccountMenu();
    loadIngredients();
    loadDailyLogs();
    renderIngredientsSummaryList();
    updateTrackerUI();
    updateProfileUI();
    initCookingCalculator();
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
            const displayNameEl = document.getElementById('account-display-name');
            const usernameEl = document.getElementById('account-username');
            const activeDaysEl = document.getElementById('account-active-days');
            const joinedDateEl = document.getElementById('account-joined-date');
            if (avatar) {
                avatar.textContent = (displayName || '?')[0].toUpperCase();
                avatar.title = displayName;
            }
            if (displayNameEl) displayNameEl.textContent = displayName;
            if (usernameEl) usernameEl.textContent = `@${user.username}`;
            if (activeDaysEl) {
                const activeDays = Number(user.active_days) || 0;
                activeDaysEl.textContent = `${activeDays} hari`;
            }
            if (joinedDateEl && user.created_at) {
                const joinedDate = new Date(`${user.created_at.replace(' ', 'T')}Z`);
                joinedDateEl.textContent = Number.isNaN(joinedDate.getTime())
                    ? ''
                    : `Bergabung sejak ${joinedDate.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}`;
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

function initAccountMenu() {
    const avatar = document.getElementById('user-avatar');
    const menu = document.getElementById('account-menu');
    if (!avatar || !menu) return;

    avatar.addEventListener('click', () => {
        const isOpen = !menu.hidden;
        menu.hidden = isOpen;
        avatar.setAttribute('aria-expanded', String(!isOpen));
    });

    document.addEventListener('click', event => {
        if (!menu.hidden && !menu.parentElement.contains(event.target)) {
            menu.hidden = true;
            avatar.setAttribute('aria-expanded', 'false');
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !menu.hidden) {
            menu.hidden = true;
            avatar.setAttribute('aria-expanded', 'false');
            avatar.focus();
        }
    });
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
    populateCookingIngredientSelect();
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
                <div class="pantry-checkbox">${isSelected ? 'Ada' : ''}</div>
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

    listContainer.innerHTML = `<div style="text-align:center; padding: 40px; color: #94a3b8;">Menghitung kecocokan resep...</div>`;

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
                        <span>${r.prep_time} menit</span> • <span>${r.servings} porsi</span>
                    </div>
                </div>
            </div>

            <div class="nutri-pills">
                <div class="nutri-pill">Kalori: ${r.total_calories} <span>kcal</span></div>
                <div class="nutri-pill">Protein: ${r.total_protein}g</div>
                <div class="nutri-pill">Karbo: ${r.total_carbs}g</div>
                <div class="nutri-pill">Lemak: ${r.total_fat}g</div>
            </div>

            ${r.missing_ingredients && r.missing_ingredients.length > 0 ? `
                <div class="missing-box">
                    <div class="missing-title">Bahan kurang (${r.missing_ingredients.length})</div>
                    <div class="missing-list">${r.missing_ingredients.map(m => m.name).join(', ')}</div>
                </div>
            ` : `
                <div class="missing-box" style="background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3);">
                    <div class="missing-title" style="color: #34d399;">Semua bahan tersedia di Pantry</div>
                </div>
            `}

            <div class="recipe-actions">
                <button class="btn-secondary" onclick="viewRecipeDetail(${r.id})">Lihat resep</button>
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

    document.getElementById('modal-recipe-title').textContent = r.title;
    
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
            alert(`"${recipe.title}" berhasil ditambahkan ke catatan makan.`);
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
    alert(`"${recipe.title}" berhasil ditambahkan ke catatan makan.`);
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
                <div class="log-meta">${log.meal_type} • Protein ${log.protein}g · Karbo ${log.carbs}g · Lemak ${log.fat}g</div>
            </div>
            <div style="display:flex; align-items:center;">
                <div class="log-cal">+${log.calories} kcal</div>
                <button class="btn-del" onclick="deleteLogEntry(${log.id})">Hapus</button>
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
            alert('Profil, BMR, dan target kalori harian berhasil disimpan.');
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
    alert('Profil dan target kalori harian berhasil diperbarui.');
}

// ==========================================
// KALKULATOR TAKARAN MASAKAN & NUTRISI (PORTION CALCULATOR)
// ==========================================
let cookingRecipeItems = [];

const INGREDIENT_NUTRITION_PRESETS = {
    "dada ayam": { cal: 165.0, protein: 31.0, carbs: 0.0, fat: 3.6, unit: "gram", defaultAmount: 150 },
    "daging ayam": { cal: 190.0, protein: 27.0, carbs: 0.0, fat: 8.0, unit: "gram", defaultAmount: 150 },
    "daging sapi": { cal: 250.0, protein: 26.0, carbs: 0.0, fat: 15.0, unit: "gram", defaultAmount: 100 },
    "telur ayam": { cal: 155.0, protein: 13.0, carbs: 1.1, fat: 11.0, unit: "butir", defaultAmount: 2 },
    "tahu putih": { cal: 76.0, protein: 8.0, carbs: 1.9, fat: 4.8, unit: "gram", defaultAmount: 100 },
    "tempe": { cal: 190.0, protein: 19.0, carbs: 9.4, fat: 11.0, unit: "gram", defaultAmount: 100 },
    "kangkung": { cal: 19.0, protein: 2.6, carbs: 3.1, fat: 0.2, unit: "ikat", defaultAmount: 1 },
    "bayam": { cal: 23.0, protein: 2.9, carbs: 3.6, fat: 0.4, unit: "ikat", defaultAmount: 1 },
    "bawang merah & putih": { cal: 40.0, protein: 1.5, carbs: 9.0, fat: 0.1, unit: "siung", defaultAmount: 3 },
    "bawang merah": { cal: 40.0, protein: 1.4, carbs: 9.0, fat: 0.1, unit: "siung", defaultAmount: 3 },
    "bawang putih": { cal: 149.0, protein: 6.4, carbs: 33.0, fat: 0.5, unit: "siung", defaultAmount: 2 },
    "cabai red": { cal: 40.0, protein: 1.9, carbs: 8.8, fat: 0.4, unit: "buah", defaultAmount: 5 },
    "cabai": { cal: 40.0, protein: 1.9, carbs: 8.8, fat: 0.4, unit: "buah", defaultAmount: 5 },
    "wortel": { cal: 41.0, protein: 0.9, carbs: 9.6, fat: 0.2, unit: "gram", defaultAmount: 100 },
    "tomat": { cal: 18.0, protein: 0.9, carbs: 3.9, fat: 0.2, unit: "buah", defaultAmount: 1 },
    "kecap manis": { cal: 150.0, protein: 2.0, carbs: 35.0, fat: 0.0, unit: "sdm", defaultAmount: 1 },
    "minyak": { cal: 884.0, protein: 0.0, carbs: 0.0, fat: 100.0, unit: "sdm", defaultAmount: 1 },
    "nasi": { cal: 130.0, protein: 2.7, carbs: 28.0, fat: 0.3, unit: "gram", defaultAmount: 150 }
};

const UNIT_TO_GRAMS = {
    "gram": 1.0,
    "g": 1.0,
    "kg": 1000.0,
    "siung": 5.0,
    "butir": 50.0,
    "sdm": 15.0,
    "sdt": 5.0,
    "ikat": 150.0,
    "potong": 50.0,
    "buah": 50.0
};

function switchCalcSubtab(tab) {
    const btnCooking = document.getElementById('btn-subtab-cooking');
    const btnBmr = document.getElementById('btn-subtab-bmr');
    const viewCooking = document.getElementById('cooking-calc-view');
    const viewBmr = document.getElementById('bmr-calc-view');

    if (tab === 'cooking') {
        if (btnCooking) btnCooking.classList.add('active');
        if (btnBmr) btnBmr.classList.remove('active');
        if (viewCooking) viewCooking.style.display = 'block';
        if (viewBmr) viewBmr.style.display = 'none';
    } else {
        if (btnBmr) btnBmr.classList.add('active');
        if (btnCooking) btnCooking.classList.remove('active');
        if (viewCooking) viewCooking.style.display = 'none';
        if (viewBmr) viewBmr.style.display = 'block';
    }
}

function initCookingCalculator() {
    populateCookingIngredientSelect();
    updateLivePortionPreview();
    renderCookingIngredientsList();
}

function populateCookingIngredientSelect() {
    const sel = document.getElementById('cooking-ing-select');
    if (!sel) return;

    const currentVal = sel.value;
    sel.innerHTML = '';

    // Ambil bahan dari pantry pengguna
    const pantryItems = [];
    for (const [category, items] of Object.entries(allIngredientsCategorized)) {
        items.forEach(i => {
            if (!pantryItems.some(p => p.name.toLowerCase() === i.name.toLowerCase())) {
                pantryItems.push({ name: i.name, cal: i.calories_per_100g, category });
            }
        });
    }

    // Tambah optgroup untuk bahan di Pantry
    if (pantryItems.length > 0) {
        const groupPantry = document.createElement('optgroup');
        groupPantry.label = '🧺 Bahan dari Kulkas / Pantry:';
        pantryItems.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.name;
            opt.textContent = `${item.name} (${item.category})`;
            groupPantry.appendChild(opt);
        });
        sel.appendChild(groupPantry);
    }

    // Tambah optgroup untuk preset umum
    const groupCommon = document.createElement('optgroup');
    groupCommon.label = '🍳 Bahan Masakan Umum:';
    const commonNames = ["Dada Ayam", "Daging Sapi", "Telur Ayam", "Tahu Putih", "Tempe", "Kangkung", "Bawang Merah & Putih", "Cabai Red", "Wortel", "Kecap Manis", "Minyak"];
    commonNames.forEach(name => {
        if (!pantryItems.some(p => p.name.toLowerCase() === name.toLowerCase())) {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            groupCommon.appendChild(opt);
        }
    });
    sel.appendChild(groupCommon);

    // Opsi kustom
    const optCustom = document.createElement('option');
    optCustom.value = '__custom__';
    optCustom.textContent = '➕ [Ketik Nama Bahan Kustom Lainnya]';
    sel.appendChild(optCustom);

    if (currentVal && Array.from(sel.options).some(o => o.value === currentVal)) {
        sel.value = currentVal;
    }
    onCookingIngredientChange();
}

function onCookingIngredientChange() {
    const sel = document.getElementById('cooking-ing-select');
    const customBox = document.getElementById('cooking-custom-name-box');
    const calInput = document.getElementById('cooking-cal-100');
    const proteinInput = document.getElementById('cooking-protein-100');
    const unitSelect = document.getElementById('cooking-ing-unit');
    const amountInput = document.getElementById('cooking-ing-amount');

    if (!sel) return;

    if (sel.value === '__custom__') {
        if (customBox) customBox.style.display = 'block';
        if (calInput) calInput.value = '50';
        if (proteinInput) proteinInput.value = '2.0';
        updateLivePortionPreview();
        return;
    }

    if (customBox) customBox.style.display = 'none';

    const nameLower = sel.value.toLowerCase();
    let preset = INGREDIENT_NUTRITION_PRESETS[nameLower];
    if (!preset) {
        for (const [k, v] of Object.entries(INGREDIENT_NUTRITION_PRESETS)) {
            if (nameLower.includes(k) || k.includes(nameLower)) {
                preset = v;
                break;
            }
        }
    }

    // Cari di pantry jika ada
    let pantryCal = null;
    for (const items of Object.values(allIngredientsCategorized)) {
        const found = items.find(i => i.name.toLowerCase() === nameLower);
        if (found) {
            pantryCal = found.calories_per_100g;
            break;
        }
    }

    if (calInput) calInput.value = pantryCal !== null ? pantryCal : (preset ? preset.cal : 50);
    if (proteinInput) proteinInput.value = preset ? preset.protein : 2.0;

    if (preset && preset.unit && unitSelect) {
        unitSelect.value = preset.unit;
        if (amountInput && preset.defaultAmount) {
            amountInput.value = preset.defaultAmount;
        }
    }

    updateLivePortionPreview();
}

function onCookingUnitChange() {
    updateLivePortionPreview();
}

function updateLivePortionPreview() {
    const sel = document.getElementById('cooking-ing-select');
    const customNameInput = document.getElementById('cooking-custom-name');
    const amountInput = document.getElementById('cooking-ing-amount');
    const unitSelect = document.getElementById('cooking-ing-unit');
    const calInput = document.getElementById('cooking-cal-100');
    const proteinInput = document.getElementById('cooking-protein-100');
    const previewEl = document.getElementById('cooking-live-preview');

    if (!previewEl) return;

    const rawName = (sel && sel.value === '__custom__') 
        ? (customNameInput ? customNameInput.value.trim() || 'Bahan Kustom' : 'Bahan')
        : (sel ? sel.value : 'Bahan');

    const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;
    const unit = unitSelect ? unitSelect.value : 'gram';
    const cal100 = parseFloat(calInput ? calInput.value : 0) || 0;
    const p100 = parseFloat(proteinInput ? proteinInput.value : 0) || 0;

    const unitFactor = UNIT_TO_GRAMS[unit] || 1.0;
    const totalGrams = Math.round(amount * unitFactor * 10) / 10;
    const factor = totalGrams / 100.0;
    const totalCal = Math.round(factor * cal100 * 10) / 10;
    const totalP = Math.round(factor * p100 * 10) / 10;

    const unitLabel = unit === 'gram' ? `${totalGrams}g` : `${amount} ${unit} (${totalGrams}g)`;
    previewEl.innerHTML = `👉 <strong>${unitLabel} ${rawName}</strong> = <span style="color:#34d399;">${totalCal} kcal</span> • <span style="color:#60a5fa;">${totalP}g Protein</span>`;
}

function handleAddCookingIngredient(e) {
    e.preventDefault();

    const sel = document.getElementById('cooking-ing-select');
    const customNameInput = document.getElementById('cooking-custom-name');
    const amountInput = document.getElementById('cooking-ing-amount');
    const unitSelect = document.getElementById('cooking-ing-unit');
    const calInput = document.getElementById('cooking-cal-100');
    const proteinInput = document.getElementById('cooking-protein-100');

    let name = sel ? sel.value : '';
    if (name === '__custom__') {
        name = customNameInput ? customNameInput.value.trim() : '';
        if (!name) {
            alert('Harap ketikkan nama bahan makanan kustom.');
            return;
        }
    }

    const amount = parseFloat(amountInput ? amountInput.value : 0);
    if (!amount || amount <= 0) {
        alert('Harap masukkan takaran yang valid (lebih dari 0).');
        return;
    }

    const unit = unitSelect ? unitSelect.value : 'gram';
    const cal100 = parseFloat(calInput ? calInput.value : 50) || 50;
    const p100 = parseFloat(proteinInput ? proteinInput.value : 2) || 2;

    const unitFactor = UNIT_TO_GRAMS[unit] || 1.0;
    const totalGrams = Math.round(amount * unitFactor * 10) / 10;
    const factor = totalGrams / 100.0;
    const calories = Math.round(factor * cal100 * 10) / 10;
    const protein = Math.round(factor * p100 * 10) / 10;
    const carbs = Math.round(factor * (cal100 > 100 ? 5 : 2) * 10) / 10;
    const fat = Math.round(factor * (cal100 > 150 ? 8 : 1) * 10) / 10;

    cookingRecipeItems.push({
        id: Date.now() + Math.random(),
        name,
        amount,
        unit,
        totalGrams,
        calories,
        protein,
        carbs,
        fat,
        cal_per_100g: cal100,
        protein_per_100g: p100
    });

    renderCookingIngredientsList();
}

function renderCookingIngredientsList() {
    const container = document.getElementById('cooking-ingredients-list');
    const totCalEl = document.getElementById('cooking-total-cal');
    const totPEl = document.getElementById('cooking-total-protein');
    const totCEl = document.getElementById('cooking-total-carbs');
    const totFEl = document.getElementById('cooking-total-fat');
    const totWEl = document.getElementById('cooking-total-weight');

    let totCal = 0, totP = 0, totC = 0, totF = 0, totG = 0;
    cookingRecipeItems.forEach(item => {
        totCal += item.calories;
        totP += item.protein;
        totC += item.carbs;
        totF += item.fat;
        totG += item.totalGrams;
    });

    totCal = Math.round(totCal * 10) / 10;
    totP = Math.round(totP * 10) / 10;
    totC = Math.round(totC * 10) / 10;
    totF = Math.round(totF * 10) / 10;
    totG = Math.round(totG * 10) / 10;

    if (totCalEl) totCalEl.textContent = `${totCal} kcal`;
    if (totPEl) totPEl.textContent = `${totP}g`;
    if (totCEl) totCEl.textContent = `${totC}g`;
    if (totFEl) totFEl.textContent = `${totF}g`;
    if (totWEl) totWEl.textContent = `${totG}g`;

    if (!container) return;

    if (cookingRecipeItems.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 24px; color: var(--text-muted); background: var(--card-bg); border-radius: 14px; border: 1px dashed var(--card-border); font-size: 13px;">
                Belum ada bahan masakan ditambahkan. Pilih bahan dan masukkan takaran di atas.
            </div>
        `;
        return;
    }

    container.innerHTML = '';
    cookingRecipeItems.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'portion-item-card';
        const unitDesc = item.unit === 'gram' ? `${item.totalGrams}g` : `${item.amount} ${item.unit} (${item.totalGrams}g)`;
        card.innerHTML = `
            <div>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-main);">${item.name}</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                    <span>Takaran: <strong style="color:var(--text-main);">${unitDesc}</strong></span> • 
                    <span style="color: #34d399; font-weight: 600;">🔥 ${item.calories} kcal</span> • 
                    <span style="color: #60a5fa; font-weight: 600;">🥩 ${item.protein}g Protein</span>
                </div>
            </div>
            <button onclick="removeCookingIngredient(${idx})" style="background: none; border: none; color: #ef4444; font-size: 16px; cursor: pointer; padding: 4px 8px;" title="Hapus">✕</button>
        `;
        container.appendChild(card);
    });
}

function removeCookingIngredient(index) {
    cookingRecipeItems.splice(index, 1);
    renderCookingIngredientsList();
}

function resetCookingIngredients() {
    cookingRecipeItems = [];
    renderCookingIngredientsList();
}

async function logCookingDishToTracker() {
    if (cookingRecipeItems.length === 0) {
        alert('Harap tambahkan minimal 1 bahan masakan terlebih dahulu.');
        return;
    }

    let totCal = 0, totP = 0, totC = 0, totF = 0;
    cookingRecipeItems.forEach(item => {
        totCal += item.calories;
        totP += item.protein;
        totC += item.carbs;
        totF += item.fat;
    });

    const dishNameInput = document.getElementById('cooking-dish-name');
    const customTitle = dishNameInput ? dishNameInput.value.trim() : '';
    const title = customTitle || `Masakan Buatan (${cookingRecipeItems.map(i => i.name).slice(0, 2).join(' & ')})`;

    await logRecipeToTracker(title, Math.round(totCal), Math.round(totP), Math.round(totC), Math.round(totF));
    switchToTab('tracker-tab');
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

            alert(`Bahan "${name}" berhasil ditambahkan ke kategori "${itemCategory}" di Pantry Anda.`);
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
    alert(`Bahan "${name}" berhasil ditambahkan ke kategori "${itemCategory}" di Pantry Anda.`);
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
        const categoryLabel = isProtein ? 'Protein' : 'Sayuran';

        const catBlock = document.createElement('div');
        catBlock.style.cssText = 'background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 14px; margin-bottom: 12px;';

        const itemsHtml = items.map(item => `
            <div style="display:flex; justify-content:space-between; align-items:center; background: rgba(15,23,42,0.5); padding: 8px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:14px; color: var(--text-main); font-weight:600;">${item.name}</span>
                    <span style="font-size:11px; color:#94a3b8;">(${item.calories_per_100g} kcal/100g)</span>
                </div>
                <button onclick="handleDeleteIngredient(${item.id}, '${item.name.replace(/'/g, "\\'")}')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:12px; padding:4px 8px;" title="Hapus bahan">Hapus</button>
            </div>
        `).join('');

        catBlock.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                <span style="font-weight:700; font-size:13px; color: ${badgeColor}; display:flex; align-items:center; gap:6px;">
                    <span>${categoryLabel}</span> ${category}
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
