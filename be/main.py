import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Import kết nối DB
from app.database import engine
from app import models 

# 2. Import các Router (API)
from app.routers import auth, recipes, plans, ai, shopping

load_dotenv()

# 3. Tạo bảng Database tự động
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meal Planner API",
    description="API quản lý thực đơn với AI Assistant (Google Gemini)",
    version="1.0.0"
)

# Cấu hình CORS
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. KÍCH HOẠT CÁC ROUTER ---
app.include_router(auth.router)       # Đăng ký/Đăng nhập
app.include_router(recipes.router)    # CRUD Recipes + Ratings
app.include_router(plans.router)      # Meal Plans (Calendar)
app.include_router(ai.router)         # AI Assistant (Gemini)
app.include_router(shopping.router)   # Shopping List
# -------------------------------

@app.get("/")
def read_root():
    return {"message": "Welcome to Meal Planner API - Database is Connected!"}

if __name__ == "__main__":
    port_from_env = int(os.getenv("PORT", 8000))
    print(f"🚀 Server đang khởi động tại port: {port_from_env}")
    uvicorn.run("main:app", host="127.0.0.1", port=port_from_env, reload=True)