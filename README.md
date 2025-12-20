# 🍽️ Meal Planner - AI-Powered Recipe & Meal Planning System

Hệ thống quản lý thực đơn thông minh với AI Assistant (Google Gemini), hỗ trợ tạo công thức món ăn, lên lịch bữa ăn, và tự động tạo danh sách mua sắm.

---

## ✨ Tính năng chính

- ✅ **Quản lý công thức món ăn**: Tạo, chỉnh sửa, tìm kiếm công thức với đầy đủ thông tin dinh dưỡng
- ✅ **Lên lịch bữa ăn**: Calendar view với drag & drop, quản lý bữa ăn theo tuần
- ✅ **Shopping List**: Tự động tạo danh sách mua sắm từ meal plans
- ✅ **AI Assistant**: Tạo công thức từ nguyên liệu, gợi ý thực đơn tuần dựa trên BMR
- ✅ **Đánh giá món ăn**: Rating 1-5 sao với comments
- ✅ **Quản trị hệ thống**: Admin panel quản lý users, recipes, meal plans

---

## 📁 Cấu trúc dự án

```
LenThucDonHangNgangX3/
├── README.md          # File này
├── start.sh           # Script khởi động backend + frontend
├── be/                # Backend (FastAPI + PostgreSQL)
│   ├── main.py        # Entry point FastAPI
│   ├── requirements.txt
│   └── app/
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routers/   # API endpoints
│       └── services/  # Business logic
└── fe/                # Frontend (HTML/CSS/JavaScript)
    ├── index.html
    ├── dashboard.html
    ├── recipes.html
    ├── planner.html
    ├── shopping.html
    ├── admin.html
    ├── css/
    └── js/
```

---

## 🛠️ Cài đặt và cấu hình

### Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+
- Google Gemini API Key (miễn phí)

### 1. Clone repository

```bash
git clone <your-repo-url>
cd LenThucDonHangNgangX3
```

### 2. Setup Backend

```bash
cd be

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu hình Database

**Tạo Database PostgreSQL:**

```bash
sudo -u postgres psql

# Trong psql:
CREATE DATABASE meal_planner_db;
CREATE USER meal_user WITH PASSWORD 'your_password';
ALTER USER meal_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE meal_planner_db TO meal_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO meal_user;
\q
```

### 4. Tạo file `.env`

Tạo file `be/.env` với nội dung:

```env
# Database
DATABASE_URL=postgresql://meal_user:your_password@localhost/meal_planner_db

# JWT Secret
SECRET_KEY=your-super-secret-key-change-this-in-production

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here
```

**Lấy Gemini API Key:**
1. Truy cập: https://aistudio.google.com/apikey
2. Đăng nhập bằng Google account
3. Click "Create API Key"
4. Copy và paste vào file `.env`

**Tạo SECRET_KEY mới:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Chạy ứng dụng

```bash
# Cách 1: Dùng script (recommended)
chmod +x start.sh
./start.sh

# Cách 2: Chạy thủ công
# Terminal 1: Backend
cd be
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd fe
python3 -m http.server 3000
```

### 6. Truy cập ứng dụng

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

---

## 📚 API Endpoints chính

### Authentication
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `GET /auth/me` - Thông tin user hiện tại

### Recipes
- `GET /recipes/` - Danh sách recipes
- `POST /recipes/` - Tạo recipe
- `PUT /recipes/{id}` - Sửa recipe
- `DELETE /recipes/{id}` - Xóa recipe

### Meal Plans
- `GET /plans/` - Danh sách meal plans  
- `POST /plans/` - Thêm meal plan
- `DELETE /plans/{id}` - Xóa meal plan

### AI Assistant
- `POST /ai/generate-recipe` - AI tạo recipe từ nguyên liệu
- `POST /ai/weekly-meal-plan` - AI gợi ý thực đơn tuần

### Shopping List
- `GET /shopping/list?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Tạo shopping list

### Admin
- `GET /admin/users` - Danh sách users (chỉ admin)
- `PUT /admin/users/{id}` - Cập nhật role/status user
- `GET /admin/stats` - Thống kê hệ thống

Xem đầy đủ API documentation tại: http://localhost:8000/docs

---

## 🗄️ Database Schema

- **users**: Thông tin user (email, password, role, BMR data, dietary preferences)
- **recipes**: Công thức món ăn (name, description, instructions, nutrition info)
- **ingredients**: Nguyên liệu của recipes
- **meal_plans**: Lịch bữa ăn (date, meal_type, servings)
- **ratings**: Đánh giá món ăn (stars, comment)
- **shopping_list_items**: Danh sách mua sắm

---

## 👨‍💻 Tác giả

**Lý Lâm Vũ & Châu Khang Duy** - Meal Planner Project

---

## 📄 License

MIT License - Free to use

---

**Happy Cooking! 🍳👨‍🍳**
