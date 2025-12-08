# 🍽️ Meal Planner - AI-Powered Recipe & Meal Planning System

Hệ thống quản lý thực đơn thông minh với AI Assistant, hỗ trợ tạo công thức món ăn, lên lịch bữa ăn, và tự động tạo danh sách mua sắm.

## 🚀 Tính năng

### Backend (FastAPI + PostgreSQL)
- ✅ **Authentication**: JWT-based đăng ký/đăng nhập
- ✅ **Recipes Management**: CRUD công thức món ăn với ingredients
- ✅ **Meal Planning**: Lên lịch bữa ăn theo calendar (drag & drop support)
- ✅ **Shopping List**: Tự động gộp nguyên liệu từ meal plans
- ✅ **Recipe Ratings**: Đánh giá món ăn 1-5 sao với comments
- ✅ **Nutrition Calculator**: Tính toán calories, protein, carbs, fat
- ✅ **AI Assistant**: 
  - Tạo công thức từ nguyên liệu có sẵn
  - Gợi ý thực đơn tuần dựa trên BMR
  - Tìm kiếm món ăn thông minh
- ✅ **Dietary Restrictions**: Hỗ trợ vegetarian, vegan, gluten-free...

### Frontend (HTML/CSS/JavaScript)
- Recipe cards với search & filter
- Calendar planner (drag & drop)
- AI recipe generator
- Shopping list auto-generation

## 📋 Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+
- Node.js (optional, cho frontend development)

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone <your-repo-url>
cd meal-planner
```

### 2. Setup Backend
```bash
cd be

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env từ template
cp .env.example .env
# Sau đó điền thông tin vào .env
```

### 3. Setup PostgreSQL
```bash
# Tạo database
sudo -u postgres psql
CREATE DATABASE meal_planner_db;
CREATE USER meal_user WITH PASSWORD 'your_password';
ALTER USER meal_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE meal_planner_db TO meal_user;
\c meal_planner_db
GRANT ALL PRIVILEGES ON SCHEMA public TO meal_user;
\q
```

### 4. Chạy Backend Server
```bash
cd be
source venv/bin/activate
python main.py
```

Server sẽ chạy tại: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

### 5. Chạy Frontend
```bash
cd fe
# Mở file HTML bằng Live Server hoặc trực tiếp trong browser
```

## 🔑 Cấu hình môi trường (.env)

```env
DATABASE_URL=postgresql://meal_user:your_password@localhost:5432/meal_planner_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your-gemini-api-key
PORT=8000
```

**Lấy Gemini API Key:**
1. Vào: https://aistudio.google.com/apikey
2. Đăng nhập Google
3. Tạo API key mới
4. Copy và dán vào .env

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký tài khoản
- `POST /auth/login` - Đăng nhập (nhận JWT token)

### Recipes
- `GET /recipes/` - Lấy danh sách recipes
- `GET /recipes/{id}` - Chi tiết recipe
- `POST /recipes/` - Tạo recipe mới
- `PUT /recipes/{id}` - Cập nhật recipe
- `DELETE /recipes/{id}` - Xóa recipe
- `POST /recipes/{id}/ratings` - Đánh giá recipe
- `GET /recipes/{id}/ratings` - Xem đánh giá

### Meal Plans
- `GET /plans/` - Lấy meal plans
- `POST /plans/` - Thêm món vào lịch
- `PUT /plans/{id}` - Cập nhật plan
- `DELETE /plans/{id}` - Xóa plan

### AI Assistant
- `POST /ai/generate-recipe` - Tạo recipe từ nguyên liệu
- `POST /ai/suggest-weekly-plan` - Gợi ý thực đơn tuần
- `POST /ai/search-recipes` - Tìm kiếm món ăn AI

### Shopping List
- `GET /shopping/list` - Tạo shopping list tự động

## 🧪 Test APIs

### Test API thủ công
```bash
cd be

# Test đăng ký
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Test đăng nhập
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

### Test AI Keys
```bash
cd be
python test_ai.py  # Test Gemini API keys
python test_all_models.py  # Tìm models còn quota
```

## 📂 Cấu trúc dự án

```
meal-planner/
├── be/                          # Backend
│   ├── app/
│   │   ├── routers/            # API endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── recipes.py      # Recipes CRUD
│   │   │   ├── plans.py        # Meal plans
│   │   │   ├── ai.py           # AI features
│   │   │   └── shopping.py     # Shopping list
│   │   ├── services/
│   │   │   ├── ai_service.py   # Gemini AI logic
│   │   │   └── shopping.py     # Shopping calculations
│   │   ├── database.py         # DB connection
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── utils.py            # JWT utilities
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Dependencies
│   └── .env                    # Environment config
├── fe/                         # Frontend
│   ├── index.html
│   ├── recipes.html
│   ├── planner.html
│   ├── shopping.html
│   ├── ai-generator.html
│   ├── css/
│   └── js/
├── .gitignore
└── README.md
```

## 🗄️ Database Schema

- **users**: Thông tin user (email, password, BMR data, dietary preferences)
- **recipes**: Công thức món ăn (name, instructions, nutrition)
- **ingredients**: Nguyên liệu của recipes
- **meal_plans**: Lịch bữa ăn (date, meal_type, recipe)
- **ratings**: Đánh giá món ăn (stars, comment)

## 🤝 Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Tạo Pull Request

## 📝 License

MIT License

## 👨‍💻 Tác giả

Lý Lâm Vũ & Châu Khang Duy- Meal Planner Project

## 🙏 Credits

- FastAPI framework
- Google Gemini AI
- PostgreSQL
- SQLAlchemy