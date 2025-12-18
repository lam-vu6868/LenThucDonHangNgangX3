# 🍽️ Meal Planner - AI-Powered Recipe & Meal Planning System

## 🚀 LỆNH CHẠY WEB (WSL/Ubuntu)

### 1. Chạy backend + frontend (1 lệnh duy nhất)
Đứng trong thư mục project (ví dụ: `/mnt/d/LenThucDonHangNgangX3`) và chạy:
```bash
chmod +x start.sh   # chỉ cần làm 1 lần
./start.sh          # lần sau chỉ cần chạy lệnh này
```

Script `start.sh` sẽ:
- Khởi động **backend** (`uvicorn main:app --reload --host 127.0.0.1 --port 8000`)
- Khởi động **frontend** (`python3 -m http.server 3000` trong thư mục `fe/`)

### 2. Mở trình duyệt:
Mở link:
```text
http://localhost:3000
```

---

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
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env
nano .env
# Copy nội dung bên dưới và điền thông tin
```

### 3. Setup PostgreSQL

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
\c meal_planner_db
GRANT ALL PRIVILEGES ON SCHEMA public TO meal_user;
\q
```

### 4. Chạy Migration (Tạo tables)
```bash
cd be
source venv/bin/activate

# Chạy file main.py sẽ tự động tạo tables
python main.py
# Hoặc chạy với uvicorn:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Lưu ý**: Lần chạy đầu tiên, backend sẽ tự động tạo các bảng trong database.

Server sẽ chạy tại: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

### 5. Chạy Frontend
```bash
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
```

**Quan trọng - Thay đổi các giá trị sau:**
1. `your_password` → Mật khẩu PostgreSQL bạn đã tạo ở bước 3
2. `your-gemini-api-key-here` → API key từ Google

**Lấy Gemini API Key:**
1. Truy cập: https://aistudio.google.com/apikey
2. Đăng nhập bằng tài khoản Google
3. Click "Create API Key"
4. Copy key và paste vào file `.env`

**Tạo SECRET_KEY mới (khuyến nghị):**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```UTES=30
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