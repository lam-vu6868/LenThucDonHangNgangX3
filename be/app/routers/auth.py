from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, utils

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --- API 1: ĐĂNG KÝ TÀI KHOẢN ---
@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra Email trùng
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email này đã được sử dụng!"
        )
    
    # 2. Mã hóa mật khẩu
    hashed_password = utils.get_password_hash(user.password)
    
    # 3. Tạo User mới (Full thông tin theo Database mới)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role="user", # Mặc định là user thường
        gender=user.gender,
        date_of_birth=user.date_of_birth,
        height=user.height,
        weight=user.weight,
        dietary_preferences=user.dietary_preferences
    )
    
    # 4. Lưu vào DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# --- API 2: ĐĂNG NHẬP (Lấy Token) ---
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Lưu ý: OAuth2PasswordRequestForm sẽ gửi dữ liệu dưới dạng form-data.
    Nó có trường 'username' và 'password'.
    Chúng ta sẽ dùng 'username' để chứa 'email'.
    """
    
    # 1. Tìm user trong DB theo email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Kiểm tra: User không tồn tại HOẶC Mật khẩu sai
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Nếu đúng hết -> Tạo Token
    access_token = utils.create_access_token(data={"sub": user.email})
    
    # 4. Trả về Token cho Frontend dùng
    return {"access_token": access_token, "token_type": "bearer"}


# --- API 3: LẤY THÔNG TIN USER HIỆN TẠI ---
@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(utils.get_current_user)):
    """
    Lấy thông tin chi tiết của user đang đăng nhập
    """
    return current_user


# --- API 4: CẬP NHẬT THÔNG TIN USER ---
@router.put("/me", response_model=schemas.User)
def update_user_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user)
):
    """
    Cập nhật thông tin profile của user (tên, chiều cao, cân nặng, ngày sinh, giới tính)
    """
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.height is not None:
        current_user.height = profile_update.height
    if profile_update.weight is not None:
        current_user.weight = profile_update.weight
    if profile_update.date_of_birth is not None:
        current_user.date_of_birth = profile_update.date_of_birth
    if profile_update.gender is not None:
        current_user.gender = profile_update.gender
    if profile_update.dietary_preferences is not None:
        current_user.dietary_preferences = profile_update.dietary_preferences
    
    db.commit()
    db.refresh(current_user)
    return current_user
