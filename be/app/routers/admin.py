from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
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
    update_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Cập nhật role hoặc trạng thái active của user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    if update_data.role is not None:
        if update_data.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Role không hợp lệ")
        user.role = update_data.role
    
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Xóa user (chỉ xóa nếu không phải admin hiện tại và không có dữ liệu liên kết)"""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính mình")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    # Kiểm tra dữ liệu liên kết
    related_data = []
    
    # Kiểm tra recipes
    recipes_count = db.query(models.Recipe).filter(models.Recipe.owner_id == user_id).count()
    if recipes_count > 0:
        related_data.append(f"{recipes_count} công thức món ăn")
    
    # Kiểm tra meal plans
    meal_plans_count = db.query(models.MealPlan).filter(models.MealPlan.owner_id == user_id).count()
    if meal_plans_count > 0:
        related_data.append(f"{meal_plans_count} lịch ăn")
    
    # Kiểm tra ratings
    ratings_count = db.query(models.Rating).filter(models.Rating.user_id == user_id).count()
    if ratings_count > 0:
        related_data.append(f"{ratings_count} đánh giá")
    
    # Kiểm tra shopping list items
    shopping_items_count = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.user_id == user_id).count()
    if shopping_items_count > 0:
        related_data.append(f"{shopping_items_count} mục danh sách mua sắm")
    
    # Nếu có dữ liệu liên kết, không cho xóa
    if related_data:
        detail_msg = f"Không thể xóa user này vì đang có dữ liệu liên kết: {', '.join(related_data)}. Vui lòng xóa hoặc chuyển quyền sở hữu các dữ liệu này trước khi xóa user."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )
    
    # Nếu không có dữ liệu liên kết, cho phép xóa
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
    from sqlalchemy.exc import IntegrityError
    
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe không tồn tại")
    
    # Kiểm tra xem recipe có đang được sử dụng không
    meal_plans_count = db.query(models.MealPlan).filter(models.MealPlan.recipe_id == recipe_id).count()
    ratings_count = db.query(models.Rating).filter(models.Rating.recipe_id == recipe_id).count()
    
    if meal_plans_count > 0 or ratings_count > 0:
        references = []
        if meal_plans_count > 0:
            references.append(f"{meal_plans_count} lịch ăn")
        if ratings_count > 0:
            references.append(f"{ratings_count} đánh giá")
        
        raise HTTPException(
            status_code=400, 
            detail=f"Không thể xóa món ăn này vì đang được tham chiếu bởi {' và '.join(references)}. Vui lòng xóa các tham chiếu trước."
        )
    
    try:
        db.delete(recipe)
        db.commit()
        return {"message": f"Đã xóa recipe '{recipe.name}' thành công"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa món ăn này vì đang được tham chiếu bởi dữ liệu khác trong hệ thống."
        )

# --- 4. QUẢN LÝ MEAL PLANS ---
@router.get("/meal-plans", response_model=List[schemas.MealPlan])
def get_all_meal_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Lấy danh sách tất cả meal plans"""
    # Filter ra những meal plan có owner_id hợp lệ (không null)
    plans = db.query(models.MealPlan).options(
        joinedload(models.MealPlan.recipe),
        joinedload(models.MealPlan.owner)
    ).filter(
        models.MealPlan.owner_id.isnot(None)
    ).offset(skip).limit(limit).all()
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
    # Filter ra những rating có recipe_id và user_id hợp lệ (không null)
    # và eager load relationships
    ratings = db.query(models.Rating).options(
        joinedload(models.Rating.user),
        joinedload(models.Rating.recipe)
    ).filter(
        models.Rating.recipe_id.isnot(None),
        models.Rating.user_id.isnot(None)
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

