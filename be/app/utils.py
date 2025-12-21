from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db  # Import ở đầu
import os
from dotenv import load_dotenv

load_dotenv()

# CẤU HÌNH BẢO MẬT
# Lấy Secret Key từ .env, nếu không có thì dùng chuỗi mặc định (chỉ dùng khi dev)
SECRET_KEY = os.getenv("SECRET_KEY", "chuoi_bi_mat_mac_dinh_khong_ai_biet")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # Token hết hạn sau 8 giờ (thay vì 30 phút)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 1. XỬ LÝ MẬT KHẨU ---
def verify_password(plain_password, hashed_password):
    """Kiểm tra mật khẩu nhập vào có khớp với DB không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Mã hóa mật khẩu"""
    return pwd_context.hash(password)

# --- 2. XỬ LÝ TOKEN (JWT) ---
def create_access_token(data: dict):
    """Tạo ra chuỗi Token chứa thông tin user (email)"""
    to_encode = data.copy()
    
    # Tính thời gian hết hạn
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Mã hóa thành chuỗi JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 3. XÁC THỰC USER TỪ TOKEN ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Lấy thông tin user hiện tại từ token
    Dùng làm dependency cho các API cần đăng nhập
    """
    from app import models  # Import ở đây để tránh circular import
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Tìm user trong database
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

# --- 4. KIỂM TRA ADMIN ROLE ---
def get_admin_user(current_user = Depends(get_current_user)):
    """Kiểm tra user có phải admin không"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập"
        )
    return current_user