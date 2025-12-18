from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app import models, schemas, utils

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# --- HELPER: Kiểm tra admin ---
def require_admin(current_user: models.User = Depends(utils.get_admin_user)):
    return current_user

# --- 1. THỐNG KÊ TỔNG QUAN ---
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy thống kê tổng quan cho admin"""
    stats = {
        "total_users": db.query(models.User).count(),
        "total_recipes": db.query(models.Recipe).count(),
        "total_meal_plans": db.query(models.MealPlan).count(),
        "total_ratings": db.query(models.Rating).count(),
        "total_shopping_items": db.query(models.ShoppingListItem).count(),
        "active_users": db.query(models.User).filter(models.User.is_active == True).count(),
        "admin_users": db.query(models.User).filter(models.User.role == "admin").count(),
    }
    return stats

# --- 2. QUẢN LÝ USERS ---
@router.get("/users", response_model=List[schemas.User])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy danh sách tất cả users"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy thông tin chi tiết 1 user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return user

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Cập nhật role hoặc trạng thái active của user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    if role is not None:
        if role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Role không hợp lệ")
        user.role = role
    
    if is_active is not None:
        user.is_active = is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Xóa user (chỉ xóa nếu không phải admin hiện tại)"""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính mình")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    db.delete(user)
    db.commit()
    return {"message": "Đã xóa user thành công"}

# --- 3. QUẢN LÝ RECIPES ---
@router.get("/recipes", response_model=List[schemas.Recipe])
def get_all_recipes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy danh sách tất cả recipes"""
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes

@router.delete("/recipes/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Xóa recipe (admin có thể xóa bất kỳ recipe nào)"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe không tồn tại")
    
    db.delete(recipe)
    db.commit()
    return {"message": "Đã xóa recipe thành công"}

# --- 4. QUẢN LÝ MEAL PLANS ---
@router.get("/meal-plans", response_model=List[schemas.MealPlan])
def get_all_meal_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy danh sách tất cả meal plans"""
    plans = db.query(models.MealPlan).offset(skip).limit(limit).all()
    return plans

@router.delete("/meal-plans/{plan_id}")
def delete_meal_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Xóa meal plan"""
    plan = db.query(models.MealPlan).filter(models.MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan không tồn tại")
    
    db.delete(plan)
    db.commit()
    return {"message": "Đã xóa meal plan thành công"}

# --- 5. QUẢN LÝ RATINGS ---
@router.get("/ratings", response_model=List[schemas.Rating])
def get_all_ratings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy danh sách tất cả ratings"""
    # Filter ra những rating có recipe_id hợp lệ (không null)
    ratings = db.query(models.Rating).filter(
        models.Rating.recipe_id.isnot(None)
    ).offset(skip).limit(limit).all()
    return ratings

@router.delete("/ratings/{rating_id}")
def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Xóa rating"""
    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating không tồn tại")
    
    db.delete(rating)
    db.commit()
    return {"message": "Đã xóa rating thành công"}

