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

    let response;
    try {
        response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers
        });
    } catch (error) {
        // Network error hoặc CORS error
        throw new Error('Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng hoặc đảm bảo backend đang chạy.');
    }

    // Kiểm tra content-type trước khi parse JSON
    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
        try {
            data = await response.json();
        } catch (error) {
            throw new Error('Lỗi khi đọc dữ liệu từ server');
        }
    } else {
        // Nếu không phải JSON, lấy text
        const text = await response.text();
        throw new Error(text || `HTTP ${response.status}: ${response.statusText}`);
    }

    if (!response.ok) {
        // Nếu token hết hạn hoặc không hợp lệ, tự động logout
        if (response.status === 401 && (data.detail?.includes('Token') || data.detail?.includes('hết hạn') || data.detail?.includes('không hợp lệ'))) {
            localStorage.removeItem('token');
            localStorage.removeItem('user_email');
            alert('⏰ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!');
            window.location.href = 'index.html';
            return;
        }
        // Tạo error với status code để có thể kiểm tra sau
        const error = new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
        error.status = response.status;
        throw error;
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

async function apiGetRatedRecipes(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiCall(`/recipes/rated?${query}`);
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
        // Nếu chưa có đánh giá (404), trả về null thay vì throw error
        // Kiểm tra status code hoặc error message
        if (error.status === 404 || 
            (error.message && (
                error.message.includes('chưa đánh giá') || 
                error.message.includes('404') || 
                error.message.includes('Not Found') ||
                error.message.toLowerCase().includes('not found')
            ))) {
            return null;
        }
        // Nếu là lỗi khác, vẫn throw để caller xử lý
        throw error;
    }
}

async function apiGetRecipeRatings(id) {
    return apiCall(`/recipes/${id}/ratings`);
}

async function apiDeleteMyRating(id) {
    return apiCall(`/recipes/${id}/ratings/my`, {
        method: 'DELETE'
    });
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

// Admin APIs
async function apiGetAdminStats() {
    return apiCall('/admin/stats');
}

async function apiGetAllUsers(skip = 0, limit = 100) {
    return apiCall(`/admin/users?skip=${skip}&limit=${limit}`);
}

async function apiGetUser(userId) {
    return apiCall(`/admin/users/${userId}`);
}

async function apiUpdateUser(userId, data) {
    return apiCall(`/admin/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function apiDeleteUser(userId) {
    return apiCall(`/admin/users/${userId}`, {
        method: 'DELETE'
    });
}

async function apiGetAllRecipes(skip = 0, limit = 100) {
    return apiCall(`/admin/recipes?skip=${skip}&limit=${limit}`);
}

async function apiDeleteRecipeAdmin(recipeId) {
    return apiCall(`/admin/recipes/${recipeId}`, {
        method: 'DELETE'
    });
}

async function apiGetAllMealPlans(skip = 0, limit = 100) {
    return apiCall(`/admin/meal-plans?skip=${skip}&limit=${limit}`);
}

async function apiDeleteMealPlanAdmin(planId) {
    return apiCall(`/admin/meal-plans/${planId}`, {
        method: 'DELETE'
    });
}

async function apiGetAllRatings(skip = 0, limit = 100) {
    return apiCall(`/admin/ratings?skip=${skip}&limit=${limit}`);
}

async function apiDeleteRatingAdmin(ratingId) {
    return apiCall(`/admin/ratings/${ratingId}`, {
        method: 'DELETE'
    });
}
