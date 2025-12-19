// Sidebar Component - Dùng chung cho tất cả các trang
async function renderSidebar(activePage = '') {
    // Dashboard có thêm thông tin chiều cao và cân nặng
    const isDashboard = activePage === 'dashboard';
    const extraInfoHTML = isDashboard ? `
        <p id="user-height">Chiều cao: N/A</p>
        <p id="user-weight">Cân nặng: N/A</p>
    ` : '';
    
    // Kiểm tra user có phải admin không
    let isAdmin = false;
    let navMenuHTML = '';
    try {
        const user = await apiGetCurrentUser();
        isAdmin = user.role === 'admin';
        
        if (isAdmin) {
            // Admin chỉ thấy link Admin
            navMenuHTML = `
                <li><a href="admin.html" class="${activePage === 'admin' ? 'active' : ''}"><span>🔐</span> Admin</a></li>
                <li><a href="#" onclick="logout()"><span>🚪</span> Đăng xuất</a></li>
            `;
        } else {
            // User thường thấy các link bình thường
            navMenuHTML = `
                <li><a href="dashboard.html" class="${activePage === 'dashboard' ? 'active' : ''}"><span>🏠</span> Dashboard</a></li>
                <li><a href="recipes.html" class="${activePage === 'recipes' ? 'active' : ''}"><span>📖</span> Công thức</a></li>
                <li><a href="ratings.html" class="${activePage === 'ratings' ? 'active' : ''}"><span>⭐</span> Đánh giá</a></li>
                <li><a href="planner.html" class="${activePage === 'planner' ? 'active' : ''}"><span>📅</span> Lịch ăn</a></li>
                <li><a href="shopping.html" class="${activePage === 'shopping' ? 'active' : ''}"><span>🛒</span> Shopping List</a></li>
                <li><a href="#" onclick="logout()"><span>🚪</span> Đăng xuất</a></li>
            `;
        }
    } catch (error) {
        console.error('Error checking admin role:', error);
        // Mặc định hiển thị menu user thường nếu có lỗi
        navMenuHTML = `
            <li><a href="dashboard.html" class="${activePage === 'dashboard' ? 'active' : ''}"><span>🏠</span> Dashboard</a></li>
            <li><a href="recipes.html" class="${activePage === 'recipes' ? 'active' : ''}"><span>📖</span> Công thức</a></li>
            <li><a href="ratings.html" class="${activePage === 'ratings' ? 'active' : ''}"><span>⭐</span> Đánh giá</a></li>
            <li><a href="planner.html" class="${activePage === 'planner' ? 'active' : ''}"><span>📅</span> Lịch ăn</a></li>
            <li><a href="shopping.html" class="${activePage === 'shopping' ? 'active' : ''}"><span>🛒</span> Shopping List</a></li>
            <li><a href="#" onclick="logout()"><span>🚪</span> Đăng xuất</a></li>
        `;
    }
    
    const sidebarHTML = `
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>🍽️ Meal Planner</h2>
                <div class="user-info">
                    <p><strong id="user-name">Người dùng</strong></p>
                    ${extraInfoHTML}
                </div>
            </div>
            
            <nav>
                <ul class="nav-menu">
                    ${navMenuHTML}
                </ul>
            </nav>
        </aside>
    `;
    
    // Tìm và thay thế sidebar
    const mainLayout = document.querySelector('.main-layout');
    if (mainLayout) {
        const existingSidebar = mainLayout.querySelector('.sidebar');
        if (existingSidebar) {
            existingSidebar.outerHTML = sidebarHTML;
        } else {
            // Nếu chưa có sidebar, thêm vào đầu main-layout
            mainLayout.insertAdjacentHTML('afterbegin', sidebarHTML);
        }
    }
    
    // Load user info
    loadSidebarUserInfo(activePage);
}

// Load user info vào sidebar
async function loadSidebarUserInfo(activePage = '') {
    try {
        const userInfo = await apiGetCurrentUser();
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            userNameElement.textContent = userInfo.full_name || userInfo.email || 'Người dùng';
        }
        
        // Dashboard có thêm thông tin chiều cao và cân nặng
        if (activePage === 'dashboard') {
            const userHeightElement = document.getElementById('user-height');
            const userWeightElement = document.getElementById('user-weight');
            if (userHeightElement) {
                userHeightElement.textContent = `Chiều cao: ${userInfo.height || 'N/A'} cm`;
            }
            if (userWeightElement) {
                userWeightElement.textContent = `Cân nặng: ${userInfo.weight || 'N/A'} kg`;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Auto-detect active page from current URL
function getActivePage() {
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    if (currentPage.includes('dashboard')) return 'dashboard';
    if (currentPage.includes('recipes')) return 'recipes';
    if (currentPage.includes('ratings')) return 'ratings';
    if (currentPage.includes('planner')) return 'planner';
    if (currentPage.includes('shopping')) return 'shopping';
    return '';
}

