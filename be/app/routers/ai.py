from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app import models
from app.utils import get_current_user
from app.services import ai_service

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)

# --- SCHEMAS CHO AI APIs ---
class RecipeFromIngredientsRequest(BaseModel):
    ingredients: List[str]  # VD: ["chicken", "rice", "tomato"]

class WeeklyMealPlanRequest(BaseModel):
    activity_level: str = "moderate"  # sedentary, light, moderate, active, very_active
    goal: str = "maintain"  # maintain, lose, gain
    notes: str = ""  # Ghi chú của user
    start_date: str = ""  # Ngày bắt đầu tuần (YYYY-MM-DD), nếu rỗng thì dùng hôm nay

class RecipeSearchRequest(BaseModel):
    query: str  # VD: "món giảm cân", "món chay protein cao"

# --- 1. TẠO CÔNG THỨC TỪ NGUYÊN LIỆU ---
@router.post("/generate-recipe")
async def generate_recipe_from_ingredients(
    request: RecipeFromIngredientsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    AI tạo công thức món ăn từ các nguyên liệu có sẵn
    
    Request body:
    {
        "ingredients": ["chicken breast", "rice", "broccoli", "soy sauce"]
    }
    """
    try:
        recipe_data = await ai_service.generate_recipe_from_ingredients(
            ingredients=request.ingredients,
            dietary_preferences=current_user.dietary_preferences or ""
        )
        
        # Lưu vào database
        new_recipe = models.Recipe(
            name=recipe_data["name"],
            description=recipe_data["description"],
            instructions=recipe_data["instructions"],
            servings=recipe_data["servings"],
            prep_time=recipe_data["prep_time"],
            calories=recipe_data["nutrition"]["calories"],
            protein=recipe_data["nutrition"]["protein"],
            carbs=recipe_data["nutrition"]["carbs"],
            fat=recipe_data["nutrition"]["fat"],
            tags=recipe_data["tags"],
            owner_id=current_user.id
        )
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)
        
        # Thêm ingredients
        for ing in recipe_data["ingredients"]:
            ingredient = models.Ingredient(
                name=ing["name"],
                amount=ing["amount"],
                unit=ing["unit"],
                recipe_id=new_recipe.id
            )
            db.add(ingredient)
        
        db.commit()
        db.refresh(new_recipe)
        
        return {
            "message": "Đã tạo công thức món ăn thành công!",
            "recipe": new_recipe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. GỢI Ý THỰC ĐƠN CẢ TUẦN VÀ LƯU VÀO DATABASE ---
@router.post("/suggest-weekly-plan")
async def suggest_weekly_meal_plan(
    request: WeeklyMealPlanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    AI gợi ý thực đơn 7 ngày và TỰ ĐỘNG LƯU recipes + meal_plans vào database
    
    Request body:
    {
        "activity_level": "moderate",
        "goal": "maintain",
        "notes": "Muốn nhiều rau xanh"
    }
    """
    if not current_user.date_of_birth or not current_user.weight or not current_user.height:
        raise HTTPException(
            status_code=400, 
            detail="Cần cập nhật đầy đủ thông tin: ngày sinh, cân nặng, chiều cao trong profile"
        )
    
    try:
        user_data = {
            "gender": current_user.gender,
            "weight": current_user.weight,
            "height": current_user.height,
            "date_of_birth": str(current_user.date_of_birth),
            "dietary_preferences": current_user.dietary_preferences or "",
            "activity_level": request.activity_level,
            "goal": request.goal,
            "notes": request.notes
        }
        
        # Gọi AI service để tạo thực đơn
        ai_result = await ai_service.suggest_weekly_meal_plan_with_recipes(user_data)
        
        # Lưu recipes vào database
        saved_recipes = {}
        for recipe_data in ai_result["recipes"]:
            # Tạo recipe
            new_recipe = models.Recipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                instructions=recipe_data["instructions"],
                servings=recipe_data["servings"],
                prep_time=recipe_data["prep_time"],
                calories=recipe_data["nutrition"]["calories"],
                protein=recipe_data["nutrition"]["protein"],
                carbs=recipe_data["nutrition"]["carbs"],
                fat=recipe_data["nutrition"]["fat"],
                tags=recipe_data["tags"],
                owner_id=current_user.id
            )
            db.add(new_recipe)
            db.flush()  # Để lấy ID
            
            # Thêm ingredients
            for ing in recipe_data["ingredients"]:
                ingredient = models.Ingredient(
                    name=ing["name"],
                    amount=ing["amount"],
                    unit=ing["unit"],
                    recipe_id=new_recipe.id
                )
                db.add(ingredient)
            
            saved_recipes[recipe_data["name"]] = new_recipe.id
        
        # Lưu meal_plans vào database
        from datetime import datetime, timedelta
        # Sử dụng start_date từ request, nếu không có thì dùng hôm nay
        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date).date()
        else:
            start_date = datetime.today().date()
        
        # XÓA các meal plans cũ trong khoảng 7 ngày này (nếu có)
        end_date = start_date + timedelta(days=6)
        db.query(models.MealPlan).filter(
            models.MealPlan.owner_id == current_user.id,
            models.MealPlan.date >= start_date,
            models.MealPlan.date <= end_date
        ).delete()
        db.flush()  # Xóa ngay để tránh conflict
        
        for day_index, day_plan in enumerate(ai_result["meal_plan"]):
            current_date = start_date + timedelta(days=day_index)
            
            # Breakfast
            breakfast_plan = models.MealPlan(
                date=current_date,
                meal_type="Breakfast",
                servings=1,
                owner_id=current_user.id,
                recipe_id=saved_recipes[day_plan["breakfast"]["name"]]
            )
            db.add(breakfast_plan)
            
            # Lunch
            lunch_plan = models.MealPlan(
                date=current_date,
                meal_type="Lunch",
                servings=1,
                owner_id=current_user.id,
                recipe_id=saved_recipes[day_plan["lunch"]["name"]]
            )
            db.add(lunch_plan)
            
            # Dinner
            dinner_plan = models.MealPlan(
                date=current_date,
                meal_type="Dinner",
                servings=1,
                owner_id=current_user.id,
                recipe_id=saved_recipes[day_plan["dinner"]["name"]]
            )
            db.add(dinner_plan)
        
        db.commit()
        
        return {
            "message": "✅ Đã tạo thực đơn tuần và lưu vào database!",
            "total_calories_per_day": ai_result["total_calories_per_day"],
            "meal_plan": ai_result["meal_plan"],
            "recipes_created": len(saved_recipes),
            "meal_plans_created": len(ai_result["meal_plan"]) * 3
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. TÌM KIẾM GỢI Ý MÓN ĂN ---
@router.post("/search-recipes")
async def search_recipe_suggestions(
    request: RecipeSearchRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    AI gợi ý món ăn theo yêu cầu
    
    Request body:
    {
        "query": "món ăn giảm cân cho bữa sáng"
    }
    """
    try:
        suggestions = await ai_service.get_recipe_suggestions(
            query=request.query,
            dietary_preferences=current_user.dietary_preferences or ""
        )
        
        return {
            "message": f"Tìm thấy {len(suggestions)} món ăn phù hợp",
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))