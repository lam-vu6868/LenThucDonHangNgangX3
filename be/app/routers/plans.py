from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import date
from app.database import get_db
from app import models, schemas
from app.utils import get_current_user

router = APIRouter(
    prefix="/plans",
    tags=["Meal Plans"]
)

# --- 1. LẤY KẾ HOẠCH BỮA ĂN CỦA USER ---
@router.get("/", response_model=List[schemas.MealPlan])
def get_meal_plans(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lấy kế hoạch bữa ăn của user
    - start_date: Ngày bắt đầu (YYYY-MM-DD)
    - end_date: Ngày kết thúc (YYYY-MM-DD)
    """
    query = db.query(models.MealPlan).options(
        joinedload(models.MealPlan.recipe)
    ).filter(models.MealPlan.owner_id == current_user.id)
    
    if start_date:
        query = query.filter(models.MealPlan.date >= start_date)
    if end_date:
        query = query.filter(models.MealPlan.date <= end_date)
    
    plans = query.order_by(models.MealPlan.date, models.MealPlan.meal_type).all()
    return plans

# --- 2. THÊM MÓN ĂN VÀO LỊCH (Drag & Drop từ Frontend) ---
@router.post("/", response_model=schemas.MealPlan)
def create_meal_plan(
    plan: schemas.MealPlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Thêm món ăn vào kế hoạch
    - date: Ngày ăn (YYYY-MM-DD)
    - meal_type: "Breakfast", "Lunch", "Dinner"
    - recipe_id: ID của món ăn
    - servings: Số khẩu phần (mặc định 1)
    """
    # Kiểm tra recipe tồn tại
    recipe = db.query(models.Recipe).filter(models.Recipe.id == plan.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức món ăn")
    
    # Kiểm tra trùng lặp (cùng ngày, cùng bữa)
    existing = db.query(models.MealPlan).filter(
        models.MealPlan.owner_id == current_user.id,
        models.MealPlan.date == plan.date,
        models.MealPlan.meal_type == plan.meal_type
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Đã có món ăn cho {plan.meal_type} ngày {plan.date}. Hãy xóa hoặc cập nhật."
        )
    
    # Tạo meal plan mới
    new_plan = models.MealPlan(
        date=plan.date,
        meal_type=plan.meal_type,
        recipe_id=plan.recipe_id,
        servings=plan.servings,
        owner_id=current_user.id
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

# --- 3. CẬP NHẬT KẾ HOẠCH (Thay đổi món hoặc số khẩu phần) ---
@router.put("/{plan_id}", response_model=schemas.MealPlan)
def update_meal_plan(
    plan_id: int,
    plan_update: schemas.MealPlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    plan = db.query(models.MealPlan).filter(models.MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Không tìm thấy kế hoạch")
    
    if plan.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa kế hoạch này")
    
    # Cập nhật
    plan.date = plan_update.date
    plan.meal_type = plan_update.meal_type
    plan.recipe_id = plan_update.recipe_id
    plan.servings = plan_update.servings
    
    db.commit()
    db.refresh(plan)
    return plan

# --- 4. XÓA KẾ HOẠCH ---
@router.delete("/{plan_id}")
def delete_meal_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    plan = db.query(models.MealPlan).filter(models.MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Không tìm thấy kế hoạch")
    
    if plan.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa kế hoạch này")
    
    db.delete(plan)
    db.commit()
    return {"message": "Đã xóa kế hoạch bữa ăn"}