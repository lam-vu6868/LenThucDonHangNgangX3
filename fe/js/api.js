// API Calls cho Meal Planner
const API_URL = CONFIG.API_URL;

// Helper function
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token && !options.noAuth) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        // Nếu token hết hạn hoặc không hợp lệ, tự động logout
        if (response.status === 401 && (data.detail?.includes('Token') || data.detail?.includes('hết hạn') || data.detail?.includes('không hợp lệ'))) {
            localStorage.removeItem('token');
            localStorage.removeItem('user_email');
            alert('⏰ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!');
            window.location.href = 'index.html';
            return;
        }
        throw new Error(data.detail || 'API Error');
    }

    return data;
}

// Auth APIs
async function apiLogin(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Đăng nhập thất bại');
    }
    return data;
}

async function apiRegister(userData) {
    return apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
        noAuth: true
    });
}

async function apiGetCurrentUser() {
    return apiCall('/auth/me');
}

// Recipe APIs
async function apiGetRecipes(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiCall(`/recipes/?${query}`);
}

async function apiGetRecipe(id) {
    return apiCall(`/recipes/${id}`);
}

async function apiCreateRecipe(recipeData) {
    return apiCall('/recipes/', {
        method: 'POST',
        body: JSON.stringify(recipeData)
    });
}

async function apiUpdateRecipe(id, recipeData) {
    return apiCall(`/recipes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(recipeData)
    });
}

async function apiDeleteRecipe(id) {
    return apiCall(`/recipes/${id}`, {
        method: 'DELETE'
    });
}

async function apiRateRecipe(id, rating) {
    return apiCall(`/recipes/${id}/ratings`, {
        method: 'POST',
        body: JSON.stringify(rating)
    });
}

async function apiGetMyRating(id) {
    try {
        return await apiCall(`/recipes/${id}/ratings/my`);
    } catch (error) {
        // Nếu chưa có đánh giá, trả về null thay vì throw error
        if (error.message.includes('chưa đánh giá') || error.message.includes('404')) {
            return null;
        }
        throw error;
    }
}

async function apiGetRecipeRatings(id) {
    return apiCall(`/recipes/${id}/ratings`);
}

// Meal Plan APIs
async function apiGetMealPlans(startDate, endDate) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return apiCall(`/plans/?${params}`);
}

async function apiCreateMealPlan(planData) {
    return apiCall('/plans/', {
        method: 'POST',
        body: JSON.stringify(planData)
    });
}

async function apiUpdateMealPlan(id, planData) {
    return apiCall(`/plans/${id}`, {
        method: 'PUT',
        body: JSON.stringify(planData)
    });
}

async function apiDeleteMealPlan(id) {
    return apiCall(`/plans/${id}`, {
        method: 'DELETE'
    });
}

// Shopping List API
async function apiGetShoppingList(startDate, endDate) {
    return apiCall(`/shopping/list?start_date=${startDate}&end_date=${endDate}`);
}

// Shopping List Items API
async function apiCreateShoppingListFromRecipe(recipeId) {
    return apiCall(`/shopping/items/from-recipe/${recipeId}`, {
        method: 'POST'
    });
}

async function apiGetShoppingListItems(recipeId = null) {
    const url = recipeId 
        ? `/shopping/items?recipe_id=${recipeId}`
        : '/shopping/items';
    return apiCall(url);
}

async function apiUpdateShoppingListItem(itemId, isPurchased) {
    return apiCall(`/shopping/items/${itemId}`, {
        method: 'PUT',
        body: JSON.stringify({ is_purchased: isPurchased })
    });
}

async function apiDeleteShoppingListItem(itemId) {
    return apiCall(`/shopping/items/${itemId}`, {
        method: 'DELETE'
    });
}

// AI APIs
async function apiGenerateRecipe(ingredients) {
    return apiCall('/ai/generate-recipe', {
        method: 'POST',
        body: JSON.stringify({ ingredients })
    });
}

async function apiSuggestWeeklyPlan(activityLevel = 'moderate') {
    return apiCall('/ai/suggest-weekly-plan', {
        method: 'POST',
        body: JSON.stringify({ activity_level: activityLevel })
    });
}

async function apiSearchRecipes(query) {
    return apiCall('/ai/search-recipes', {
        method: 'POST',
        body: JSON.stringify({ query })
    });
}