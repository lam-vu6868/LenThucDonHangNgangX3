from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 1. Load biến môi trường
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("❌ LỖI: Chưa cấu hình DATABASE_URL trong file .env")

# 2. Tạo Engine (Động cơ kết nối)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Tạo SessionLocal (Phiên làm việc)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base Model (Để các models kế thừa)
Base = declarative_base()

# 5. Hàm dependency để lấy DB session (Dùng cho API)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()