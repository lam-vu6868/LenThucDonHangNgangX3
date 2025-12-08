from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app import models
from app.utils import get_current_user
from app.services.shopping import generate_shopping_list

router = APIRouter(
    prefix="/shopping",
    tags=["Shopping List"]
)

@router.get("/list")
def get_shopping_list(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Tạo shopping list tự động từ meal plans
    
    Query params:
    - start_date: Ngày bắt đầu (YYYY-MM-DD)
    - end_date: Ngày kết thúc (YYYY-MM-DD)
    
    Trả về danh sách nguyên liệu đã gộp theo tên + đơn vị
    """
    try:
        shopping_list = generate_shopping_list(db, current_user.id, start_date, end_date)
        return shopping_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))