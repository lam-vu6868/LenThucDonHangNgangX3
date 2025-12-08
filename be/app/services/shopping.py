from sqlalchemy.orm import Session
from app import models
from datetime import date
from collections import defaultdict

def generate_shopping_list(db: Session, user_id: int, start_date: date, end_date: date) -> dict:
    """
    Tạo shopping list từ meal plans trong khoảng thời gian
    
    Args:
        db: Database session
        user_id: ID của user
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
    
    Returns:
        dict chứa danh sách nguyên liệu đã gộp
    """
    # Lấy tất cả meal plans trong khoảng thời gian
    meal_plans = db.query(models.MealPlan).filter(
        models.MealPlan.owner_id == user_id,
        models.MealPlan.date >= start_date,
        models.MealPlan.date <= end_date
    ).all()
    
    if not meal_plans:
        return {"items": [], "message": "Chưa có kế hoạch bữa ăn nào"}
    
    # Gộp nguyên liệu theo tên + đơn vị
    ingredient_map = defaultdict(lambda: {"amount": 0, "unit": "", "recipes": []})
    
    for plan in meal_plans:
        recipe = plan.recipe
        if not recipe:
            continue
        
        # Nhân khẩu phần
        multiplier = plan.servings / recipe.servings
        
        for ing in recipe.ingredients:
            key = f"{ing.name.lower()}_{ing.unit.lower()}"
            ingredient_map[key]["name"] = ing.name
            ingredient_map[key]["amount"] += ing.amount * multiplier
            ingredient_map[key]["unit"] = ing.unit
            if recipe.name not in ingredient_map[key]["recipes"]:
                ingredient_map[key]["recipes"].append(recipe.name)
    
    # Chuyển về list
    shopping_items = [
        {
            "name": data["name"],
            "amount": round(data["amount"], 2),
            "unit": data["unit"],
            "recipes": data["recipes"]
        }
        for key, data in ingredient_map.items()
    ]
    
    return {
        "items": shopping_items,
        "total_items": len(shopping_items),
        "date_range": f"{start_date} to {end_date}"
    }