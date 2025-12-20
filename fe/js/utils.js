// Utility Functions

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Kiểm tra và xử lý khi trang được load từ bfcache (back/forward cache)
// Điều này đảm bảo dữ liệu được load lại khi user đổi tài khoản
function setupPageReloadOnResume(reloadCallback) {
    // Lưu session ID khi trang được load lần đầu
    const currentSessionId = localStorage.getItem('session_id') || '';
    const pageLoadSessionId = currentSessionId;
    
    // Kiểm tra khi trang được hiện lại (từ bfcache hoặc tab switch)
    window.addEventListener('pageshow', function(event) {
        // Nếu trang được load từ bfcache
        if (event.persisted) {
            const newSessionId = localStorage.getItem('session_id') || '';
            // Nếu session ID khác, nghĩa là đã login user khác
            if (newSessionId !== pageLoadSessionId) {
                window.location.reload();
            }
        }
    });
    
    // Kiểm tra khi tab được focus lại
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            const newSessionId = localStorage.getItem('session_id') || '';
            const token = localStorage.getItem('token');
            
            // Nếu không còn token, redirect về login
            if (!token) {
                window.location.href = 'index.html';
                return;
            }
            
            // Nếu session ID khác, reload trang để load dữ liệu mới
            if (newSessionId !== pageLoadSessionId) {
                window.location.reload();
            }
        }
    });
}

// Logout function
function logout() {
    // Clear tất cả localStorage để tránh dữ liệu bị lẫn giữa các user
    localStorage.clear();
    
    // Clear sessionStorage nếu có
    sessionStorage.clear();
    
    // Force reload trang login để clear cache
    window.location.href = 'index.html?logout=' + Date.now();
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

// Format number
function formatNumber(num) {
    // Đảm bảo num luôn là số hợp lệ trước khi gọi toFixed
    if (num == null || isNaN(num)) {
        return '0.0';
    }
    return Number(num).toFixed(1);
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Tính toán thời gian hiển thị dựa trên độ dài message (tối thiểu 3s, tối đa 10s)
    const displayTime = Math.max(3000, Math.min(10000, message.length * 50));
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s;
        max-width: 500px;
        word-wrap: break-word;
        line-height: 1.5;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, displayTime);
}

// Loading indicator
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.innerHTML = '<div class="spinner"></div>';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('loader');
    if (loader) loader.remove();
}

// Get current week dates
function getCurrentWeek() {
    const today = new Date();
    const first = today.getDate() - today.getDay() + 1; // Monday
    const last = first + 6; // Sunday

    const monday = new Date(today.setDate(first));
    const sunday = new Date(today.setDate(last));

    return {
        start: monday.toISOString().split('T')[0],
        end: sunday.toISOString().split('T')[0]
    };
}

// Escape HTML to prevent XSS and preserve Vietnamese characters
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}