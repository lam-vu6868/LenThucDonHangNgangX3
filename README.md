# 🍽️ Meal Planner - AI-Powered Recipe & Meal Planning System

Hệ thống quản lý thực đơn thông minh với AI Assistant (Google Gemini), hỗ trợ tạo công thức món ăn, lên lịch bữa ăn, và tự động tạo danh sách mua sắm.

---

## 📁 CẤU TRÚC DỰ ÁN VÀ MÔ TẢ CHI TIẾT

### 📂 **Thư mục gốc**

```
LenThucDonHangNgangX3/
├── README.md          # File tài liệu hướng dẫn dự án (file này)
├── start.sh           # Script khởi động backend + frontend đồng thời
├── be/                # Thư mục Backend (FastAPI + PostgreSQL)
└── fe/                # Thư mục Frontend (HTML/CSS/JavaScript)
```

#### 📄 **start.sh**

- **Mục đích**: Script bash để chạy backend và frontend cùng lúc trong WSL/Ubuntu
- **Chức năng**:
  - Khởi động FastAPI backend trên port 8000
  - Khởi động HTTP server cho frontend trên port 3000
- **Cách dùng**:
  ```bash
  chmod +x start.sh   # Chỉ chạy 1 lần đầu tiên
  
  ./start.sh          # Chạy cả backend + frontend
  ```

---

## 📂 **BACKEND (be/)**

### 🗂️ Cấu trúc thư mục Backend

```
be/
├── main.py                 # File khởi chạy chính của FastAPI
├── requirements.txt        # Danh sách thư viện Python cần cài đặt
├── check_database.py       # Script kiểm tra kết nối database
├── check_db.sql           # SQL script kiểm tra cấu trúc DB
├── check_recipes.py       # Script kiểm tra dữ liệu recipes
├── list_users.py          # Script liệt kê users trong DB
├── test_ai.py             # Script test AI service (Google Gemini)
├── test_all_models.py     # Script test tất cả AI models
├── update_user_role.py    # Script cập nhật role của user
└── app/                   # Package chính chứa code ứng dụng
    ├── __init__.py
    ├── database.py        # Cấu hình kết nối PostgreSQL
    ├── models.py          # Định nghĩa các bảng database (SQLAlchemy)
    ├── schemas.py         # Pydantic schemas để validate dữ liệu
    ├── utils.py           # Các hàm tiện ích (JWT, password hashing)
    ├── routers/           # API endpoints theo từng module
    │   ├── __init__.py
    │   ├── admin.py       # API quản trị (chỉ admin)
    │   ├── ai.py          # API AI (tạo recipe, gợi ý thực đơn)
    │   ├── auth.py        # API đăng nhập/đăng ký
    │   ├── plans.py       # API quản lý meal plans
    │   ├── recipes.py     # API quản lý công thức món ăn
    │   └── shopping.py    # API tạo shopping list
    └── services/          # Business logic
        ├── __init__.py
        ├── ai_service.py  # Tích hợp Google Gemini AI
        └── shopping.py    # Logic tạo shopping list
```

### 📄 **Chi tiết các file Backend**

#### **main.py**

- **Vai trò**: Entry point của backend, khởi tạo FastAPI app
- **Chức năng**:
  - Tạo bảng database tự động khi start
  - Cấu hình CORS để frontend gọi API
  - Import và đăng ký các router (auth, recipes, plans, ai, shopping, admin)
  - Middleware xử lý UTF-8 encoding

#### **requirements.txt**

- **Vai trò**: Danh sách tất cả thư viện Python cần thiết
- **Các thư viện chính**:
  - `fastapi` - Framework web API
  - `uvicorn` - ASGI server để chạy FastAPI
  - `sqlalchemy` - ORM để thao tác database
  - `psycopg2-binary` - Driver kết nối PostgreSQL
  - `pydantic` - Validation dữ liệu
  - `python-jose[cryptography]` - Xử lý JWT token
  - `passlib[bcrypt]` - Mã hóa mật khẩu
  - `google-generativeai` - Tích hợp Google Gemini AI

#### **Scripts tiện ích** (check*\*.py, test*_.py, list\__.py, update\_\*.py)

- **Mục đích**: Các script hỗ trợ debug, test và quản lý database
- **Chức năng**:
  - `check_database.py`: Kiểm tra kết nối database có hoạt động không
  - `check_recipes.py`: Xem danh sách recipes trong DB
  - `list_users.py`: Liệt kê tất cả users và thông tin
  - `test_ai.py`: Test AI service (Gemini)
  - `update_user_role.py`: Thay đổi role user (user -> admin)

---

### 📦 **app/database.py**

- **Vai trò**: Cấu hình kết nối PostgreSQL
- **Chức năng**:
  - Đọc `DATABASE_URL` từ file `.env`
  - Tạo SQLAlchemy engine
  - Tạo SessionLocal để thao tác database
  - Hàm `get_db()` - dependency injection cho FastAPI

#### **app/models.py**

- **Vai trò**: Định nghĩa cấu trúc các bảng database (SQLAlchemy ORM)
- **Các Model (Bảng)**:

  1. **User** - Quản lý người dùng

     - Thông tin: email, password, full_name, role (user/admin)
     - Nhân trắc học: gender, date_of_birth, height, weight (để tính BMR)
     - Dietary preferences: hạn chế ăn uống (vegan, gluten-free...)

  2. **Recipe** - Công thức món ăn

     - Thông tin: name, description, instructions, image_url
     - Dinh dưỡng: calories, protein, carbs, fat
     - Khác: servings (khẩu phần), prep_time, tags

  3. **Ingredient** - Nguyên liệu của mỗi món

     - name, amount, unit
     - Liên kết với Recipe (nhiều-một)

  4. **MealPlan** - Kế hoạch bữa ăn

     - date, meal_type (Breakfast/Lunch/Dinner)
     - servings (số người ăn)
     - Liên kết user và recipe

  5. **Rating** - Đánh giá món ăn
     - stars (1-5), comment, created_at
     - Liên kết user và recipe

#### **app/schemas.py**

- **Vai trò**: Pydantic schemas để validate request/response
- **Các Schema**:
  - `Token`, `TokenData` - Xử lý JWT
  - `UserCreate`, `UserBase`, `User` - User data validation
  - `RecipeCreate`, `Recipe` - Recipe validation
  - `IngredientCreate`, `Ingredient` - Ingredient validation
  - `MealPlanCreate`, `MealPlan` - Meal plan validation
  - `RatingCreate`, `Rating` - Rating validation

#### **app/utils.py**

- **Vai trò**: Các hàm tiện ích dùng chung
- **Chức năng**:
  - `get_password_hash()` - Mã hóa mật khẩu bằng bcrypt
  - `verify_password()` - Kiểm tra mật khẩu
  - `create_access_token()` - Tạo JWT token
  - `get_current_user()` - Lấy thông tin user từ token (dependency)

---

### 🛣️ **app/routers/** - API Endpoints

#### **auth.py** - Authentication API

- `POST /auth/register` - Đăng ký tài khoản mới
- `POST /auth/login` - Đăng nhập, trả về JWT token
- `GET /auth/me` - Lấy thông tin user hiện tại
- `PUT /auth/me` - Cập nhật profile (tên, cân nặng, chiều cao...)

#### **recipes.py** - Recipe Management API

- `GET /recipes/` - Lấy danh sách recipes (có filter: search, tags, my_only)
- `GET /recipes/rated` - Lấy recipes đã được đánh giá
- `GET /recipes/{id}` - Xem chi tiết 1 recipe
- `POST /recipes/` - Tạo recipe mới
- `PUT /recipes/{id}` - Sửa recipe
- `DELETE /recipes/{id}` - Xóa recipe
- `POST /recipes/{id}/rate` - Đánh giá recipe
- `GET /recipes/{id}/ratings` - Xem các đánh giá của recipe

#### **plans.py** - Meal Planning API

- `GET /plans/` - Lấy meal plans (filter theo start_date, end_date)
- `POST /plans/` - Thêm món vào lịch (drag & drop từ frontend)
- `PUT /plans/{id}` - Sửa meal plan (đổi món hoặc số khẩu phần)
- `DELETE /plans/{id}` - Xóa meal plan

#### **ai.py** - AI Assistant API (Google Gemini)

- `POST /ai/generate-recipe` - Tạo recipe từ nguyên liệu có sẵn
- `POST /ai/weekly-meal-plan` - Gợi ý thực đơn tuần dựa trên BMR
- `POST /ai/recipe-search` - Tìm kiếm recipe thông minh bằng AI

#### **shopping.py** - Shopping List API

- `GET /shopping/list` - Tạo shopping list tự động từ meal plans
- `POST /shopping/items` - Tạo shopping list item
- `GET /shopping/items` - Lấy shopping list items
- `PUT /shopping/items/{id}` - Cập nhật trạng thái (đã mua/chưa)
- `DELETE /shopping/items/{id}` - Xóa item

#### **admin.py** - Admin Management API

- `GET /admin/users` - Liệt kê tất cả users (chỉ admin)
- `PUT /admin/users/{id}/role` - Thay đổi role user
- `GET /admin/stats` - Thống kê hệ thống

---

### 🤖 **app/services/** - Business Logic

#### **ai_service.py**

- **Vai trò**: Tích hợp Google Gemini AI
- **Chức năng**:
  - `calculate_bmr()` - Tính BMR theo công thức Mifflin-St Jeor
  - `calculate_age()` - Tính tuổi từ ngày sinh
  - `generate_recipe_from_ingredients()` - AI tạo recipe từ nguyên liệu
  - `generate_weekly_meal_plan()` - AI gợi ý thực đơn tuần dựa BMR & dietary preferences
  - `search_recipe_with_ai()` - Tìm kiếm recipe thông minh

#### **shopping.py**

- **Vai trò**: Logic tạo shopping list
- **Chức năng**:
  - `generate_shopping_list()` - Gộp nguyên liệu từ meal plans theo date range
  - Nhân số lượng nguyên liệu theo servings
  - Gộp các nguyên liệu trùng tên + unit

---

## 📂 **FRONTEND (fe/)**

### 🗂️ Cấu trúc thư mục Frontend

```
fe/
├── index.html         # Trang đăng nhập/đăng ký
├── dashboard.html     # Trang tổng quan sau khi đăng nhập
├── recipes.html       # Trang quản lý công thức món ăn
├── planner.html       # Trang lên lịch bữa ăn (calendar)
├── shopping.html      # Trang shopping list
├── ratings.html       # Trang đánh giá món ăn
├── admin.html         # Trang quản trị (chỉ admin)
├── css/               # Thư mục chứa CSS
│   ├── style.css      # CSS chính cho layout, form, button...
│   └── components.css # CSS cho các component (card, sidebar, modal...)
└── js/                # Thư mục chứa JavaScript
    ├── config.js      # Cấu hình API URL
    ├── api.js         # Các hàm gọi API (fetch wrapper)
    ├── sidebar.js     # Logic sidebar navigation
    └── utils.js       # Các hàm tiện ích (hiển thị thông báo...)
```

### 📄 **Chi tiết các file Frontend**

#### **HTML Pages**

**index.html** - Trang đăng nhập/đăng ký

- Form đăng nhập với email + password
- Form đăng ký với thông tin đầy đủ:
  - Email, password, full name
  - Gender, date of birth, height, weight
  - Dietary preferences (vegan, vegetarian, gluten-free...)
- Sau khi login thành công -> lưu JWT token vào localStorage

**dashboard.html** - Trang chủ

- Hiển thị thông tin user
- Quick stats: số recipes, meal plans, shopping items
- Quick access đến các trang chính

**recipes.html** - Quản lý Recipes

- Danh sách recipes dạng card
- Search & filter (tên món, tags)
- Tạo recipe mới (form modal)
- Chỉnh sửa/xóa recipe
- **AI Feature**: Tạo recipe từ nguyên liệu có sẵn

**planner.html** - Lên lịch bữa ăn

- Calendar view (7 ngày)
- Drag & drop recipe vào các bữa (Breakfast/Lunch/Dinner)
- Chỉnh sửa số khẩu phần (servings)
- **AI Feature**: Gợi ý thực đơn tuần tự động

**shopping.html** - Shopping List

- Hiển thị danh sách nguyên liệu cần mua
- Filter theo date range
- Checkbox đánh dấu đã mua
- Tự động gộp nguyên liệu từ meal plans

**ratings.html** - Đánh giá món ăn

- Danh sách các món đã được đánh giá
- Form đánh giá: 1-5 sao + comment
- Xem rating của từng món

**admin.html** - Trang quản trị (chỉ admin)

- Quản lý users
- Thay đổi role (user -> admin)
- Thống kê hệ thống

---

#### **CSS Files**

**css/style.css**

- **Vai trò**: CSS chính cho toàn bộ website
- **Chứa**:
  - Reset CSS, typography, color scheme
  - Layout: grid, flexbox, container
  - Form styles: input, button, select...
  - Auth page styles (login/register)
  - Responsive design (mobile-first)

**css/components.css**

- **Vai trò**: CSS cho các component riêng biệt
- **Chứa**:
  - Sidebar navigation
  - Recipe cards
  - Calendar planner
  - Modal dialogs
  - Loading spinner
  - Toast notifications
  - Shopping list items

---

#### **JavaScript Files**

**js/config.js**

- **Vai trò**: Cấu hình chung cho frontend
- **Chứa**:
  - `API_URL` - URL của backend API (http://localhost:8000)
  - Các constants khác

**js/api.js**

- **Vai trò**: Wrapper functions để gọi backend API
- **Chức năng**:
  - `apiCall()` - Hàm gọi API chung (tự động thêm JWT token vào header)
  - `login()` - Gọi API đăng nhập
  - `register()` - Gọi API đăng ký
  - `getRecipes()` - Lấy danh sách recipes
  - `createRecipe()` - Tạo recipe mới
  - `getMealPlans()` - Lấy meal plans
  - `createMealPlan()` - Thêm món vào lịch
  - `getShoppingList()` - Lấy shopping list
  - `generateRecipeFromAI()` - Gọi AI tạo recipe
  - `generateWeeklyMealPlan()` - Gọi AI gợi ý thực đơn tuần

**js/sidebar.js**

- **Vai trò**: Logic cho sidebar navigation
- **Chức năng**:
  - Highlight menu item hiện tại
  - Toggle sidebar (mobile)
  - Logout handler

**js/utils.js**

- **Vai trò**: Các hàm tiện ích dùng chung
- **Chức năng**:
  - `showToast()` - Hiển thị thông báo (success/error/info)
  - `formatDate()` - Format ngày tháng
  - `checkAuth()` - Kiểm tra user đã login chưa
  - `logout()` - Xóa token và redirect về login
  - `calculateBMR()` - Tính BMR (client-side)

---

## 🚀 HƯỚNG DẪN CHẠY DỰ ÁN

### 1. Chạy backend + frontend (WSL/Ubuntu)

Đứng trong thư mục project và chạy:

```bash
chmod +x start.sh   # chỉ cần làm 1 lần
sed -i 's/\r$//' start.sh
./start.sh          # lần sau chỉ cần chạy lệnh này
```

### 2. Mở trình duyệt:

```
http://localhost:3000
```

Script `start.sh` sẽ:

- Khởi động **backend** (uvicorn) trên port 8000
- Khởi động **frontend** (http.server) trên port 3000

---

## 🚀 Tính năng Chính

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

---

## 📋 Yêu cầu Hệ thống

- Python 3.8+
- PostgreSQL 12+
- Google Gemini API Key (free tier)

---

## 🛠️ Cài đặt Chi tiết

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

### 3. Tạo file .env trong thư mục be/

```bash
nano .env  # hoặc dùng text editor bất kỳ
```

Nội dung file `.env`:

```env
# Database
DATABASE_URL=postgresql://meal_user:your_password@localhost/meal_planner_db

# JWT Secret (thay bằng chuỗi ngẫu nhiên)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. Setup PostgreSQL

**Cài đặt PostgreSQL (nếu chưa có):**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Kiểm tra PostgreSQL đã chạy chưa
sudo systemctl status postgresql
```

**Tạo Database:**

```bash
# Đăng nhập PostgreSQL
sudo -u postgres psql

# Trong psql, chạy các lệnh sau:
CREATE DATABASE meal_planner_db;
CREATE USER meal_user WITH PASSWORD 'your_password';
ALTER USER meal_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE meal_planner_db TO meal_user;
\q  # Thoát psql
```

### 5. Chạy ứng dụng

```bash
# Cách 1: Dùng script start.sh (recommended)
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

## 🔑 Lấy Google Gemini API Key (Miễn phí)

1. Truy cập: https://aistudio.google.com/
2. Đăng nhập bằng Google account
3. Click "Get API Key" -> "Create API Key"
4. Copy API key và paste vào file `.env`

---

## 📚 API Documentation

Sau khi chạy backend, truy cập:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints chính:

#### Authentication

- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `GET /auth/me` - Thông tin user

#### Recipes

- `GET /recipes/` - Danh sách recipes
- `POST /recipes/` - Tạo recipe
- `PUT /recipes/{id}` - Sửa recipe
- `DELETE /recipes/{id}` - Xóa recipe

#### Meal Plans

- `GET /plans/` - Danh sách meal plans
- `POST /plans/` - Thêm meal plan
- `DELETE /plans/{id}` - Xóa meal plan

#### AI Assistant

- `POST /ai/generate-recipe` - AI tạo recipe
- `POST /ai/weekly-meal-plan` - AI gợi ý thực đơn tuần

#### Shopping List

- `GET /shopping/list?start_date=2024-01-01&end_date=2024-01-07` - Tạo shopping list

---

## 🗂️ Database Schema

### Tables:

1. **users** - Người dùng

   - id, email, hashed_password, full_name, role
   - gender, date_of_birth, height, weight (tính BMR)
   - dietary_preferences

2. **recipes** - Công thức món ăn

   - id, name, description, instructions, image_url
   - servings, prep_time
   - calories, protein, carbs, fat
   - tags, owner_id

3. **ingredients** - Nguyên liệu

   - id, name, amount, unit, recipe_id

4. **meal_plans** - Kế hoạch bữa ăn

   - id, date, meal_type, servings
   - owner_id, recipe_id

5. **ratings** - Đánh giá món ăn
   - id, stars, comment, created_at
   - user_id, recipe_id

---

## 🧪 Testing & Debugging

### Test AI Service:

```bash
cd be
python test_ai.py
```

### Kiểm tra Database:

```bash
python check_database.py
python check_recipes.py
python list_users.py
```

### Xem logs Backend:

Backend sẽ tự động in logs khi có request. Kiểm tra terminal đang chạy uvicorn.

---

## 🎯 Các Use Case Chính

1. **Người dùng mới**:

   - Đăng ký tài khoản với thông tin nhân trắc học
   - Chọn hạn chế ăn uống (vegan, gluten-free...)

2. **Tạo Recipe**:

   - Thủ công: Nhập tên, mô tả, nguyên liệu, cách làm
   - AI: Nhập nguyên liệu có sẵn -> AI gợi ý recipe

3. **Lên lịch bữa ăn**:

   - Xem calendar 7 ngày
   - Drag & drop recipe vào các bữa (Breakfast/Lunch/Dinner)
   - AI gợi ý thực đơn tuần dựa BMR và dietary preferences

4. **Shopping List**:

   - Chọn date range
   - Hệ thống tự động gộp nguyên liệu từ các meal plans
   - Đánh dấu đã mua

5. **Rating**:
   - Đánh giá món ăn đã thử (1-5 sao + comment)
   - Xem rating của cộng đồng

---

## 🐛 Troubleshooting

### Lỗi: "Không kết nối được database"

```bash
# Kiểm tra PostgreSQL có chạy không
sudo systemctl status postgresql

# Nếu không chạy, start lại
sudo systemctl start postgresql

# Kiểm tra file .env có đúng DATABASE_URL không
cat be/.env
```

### Lỗi: "CORS error"

- Kiểm tra frontend đang chạy đúng port 3000
- Kiểm tra `main.py` có config CORS cho port 3000

### Lỗi: "Token hết hạn"

- Đăng nhập lại
- Token mặc định hết hạn sau 8 giờ

### Lỗi: "Gemini API không hoạt động"

- Kiểm tra GEMINI_API_KEY trong `.env`
- Kiểm tra quota API key tại Google AI Studio

---

## 📝 Ghi chú Phát triển

### Thêm Recipe mẫu:

```bash
cd be
python -c "
from app.database import SessionLocal
from app.models import Recipe, Ingredient

db = SessionLocal()
recipe = Recipe(
    name='Cơm gà Hải Nam',
    description='Món cơm gà truyền thống',
    servings=2,
    calories=500,
    protein=30,
    carbs=60,
    fat=15
)
db.add(recipe)
db.commit()
"
```

### Update User Role (user -> admin):

```bash
cd be
python update_user_role.py
# Nhập email user cần update
```

---

## 🤝 Contributing

Contributions are welcome! Vui lòng tạo issue hoặc pull request.

---

## 📄 License

MIT License - Free to use

---

## 👨‍💻 Author

Developed by **Your Name**

---

## 📞 Support

- Email: your@email.com
- GitHub Issues: [Create Issue](https://github.com/your-repo/issues)

---

**Happy Cooking! 🍳👨‍🍳**
GRANT ALL PRIVILEGES ON SCHEMA public TO meal_user;
\q

````

### 4. Chạy Migration (Tạo tables)
```bash
cd be
source venv/bin/activate

# Chạy file main.py sẽ tự động tạo tables
python main.py
# Hoặc chạy với uvicorn:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
````

**Lưu ý**: Lần chạy đầu tiên, backend sẽ tự động tạo các bảng trong database.

Server sẽ chạy tại: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

### 5. Chạy Frontend

````bash
Tạo file `be/.env` với nội dung:

```env
# Database
DATABASE_URL=postgresql://meal_user:your_password@localhost:5432/meal_planner_db

# JWT Authentication
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# Server
PORT=8000
````

**Quan trọng - Thay đổi các giá trị sau:**

1. `your_password` → Mật khẩu PostgreSQL bạn đã tạo ở bước 3
2. `your-gemini-api-key-here` → API key từ Google

**Lấy Gemini API Key:**

1. Truy cập: https://aistudio.google.com/apikey
2. Đăng nhập bằng tài khoản Google
3. Click "Create API Key"
4. Copy key và paste vào file `.env`

**Tạo SECRET_KEY mới (khuyến nghị):**

````bash
python -c "import secrets; print(secrets.token_hex(32))"
```UTES=30
GEMINI_API_KEY=your-gemini-api-key
PORT=8000
````

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
- `✅ Kiểm tra cài đặt

### 1. Test Backend

```bash
# Kiểm tra server đang chạy
curl http://127.0.0.1:8000/

# Test đăng ký user mới
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Test đăng nhập
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

### 2. Test Frontend

1. Mở browser vào: http://localhost:3000
2. Đăng nhập bằng: `vul59170@gmail.com` / `123456` (hoặc tài khoản vừa tạo)
3. Thử các chức năng:
   - Xem danh sách recipes
   - Tạo meal plan
   - Sử dụng AI generator

### 3. Test Gemini AI

```bash
cd be
source venv/bin/activate

# Chạy script test
python -c "
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('✅ Gemini API hoạt động:', response.text[:50])
"
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

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "Could not connect to database"

- Kiểm tra PostgreSQL đã chạy: `sudo systemctl status postgresql`
- Kiểm tra thông tin trong `.env` đúng chưa
- Test kết nối: `psql -U meal_user -d meal_planner_db -h localhost`

### Lỗi: "ModuleNotFoundError"

- Đảm bảo đã activate venv: `source venv/bin/activate`
- Cài lại dependencies: `pip install -r requirements.txt`

### Lỗi: "Port 8000 already in use"

```bash
# Tìm và kill process đang dùng port
lsof -ti:8000 | xargs kill -9
```

### Lỗi: "GEMINI_API_KEY not found"

- Kiểm tra file `.env` có tồn tại trong folder `be/`
- Kiểm tra API key có đúng format không

### Frontend không load được

- Đảm bảo backend đang chạy ở port 8000
- Kiểm tra `fe/js/config.js` có đúng URL backend
- Mở DevTools (F12) xem lỗi trong Console

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
