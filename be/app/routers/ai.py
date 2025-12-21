
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
        for ing in recipe_data.get("ingredients", []):
            # Xử lý amount - có thể là string như "vừa ăn", "tùy ý"
            amount_value = ing.get("amount", 0)
            if isinstance(amount_value, str):
                # Nếu là string không phải số, đặt về 1
                try:
                    amount_value = float(amount_value)
                except (ValueError, TypeError):
                    # Các trường hợp như "vừa ăn", "tùy ý", "theo khẩu vị"
                    amount_value = 1.0  # Giá trị mặc định
            
            # Đảm bảo amount là số
            try:
                amount_value = float(amount_value)
            except (ValueError, TypeError):
                amount_value = 1.0
            
            ingredient = models.Ingredient(
                name=ing.get("name", "Nguyên liệu"),
                amount=amount_value,
                unit=ing.get("unit", ""),
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
        print(f"[AI] Bắt đầu tạo thực đơn cho user {current_user.id}")
        ai_result = await ai_service.suggest_weekly_meal_plan_with_recipes(user_data)
        print(f"[AI] Đã nhận kết quả từ AI: {len(ai_result.get('recipes', []))} recipes")
        
        # Log để debug: Kiểm tra tên recipes vs meal_plan
        recipe_names = [r["name"] for r in ai_result.get("recipes", [])]
        print(f"[AI] Tên recipes từ AI: {recipe_names}")
        
        meal_plan_names = []
        for day in ai_result.get("meal_plan", []):
            meal_plan_names.extend([
                day.get("breakfast", {}).get("name"),
                day.get("lunch", {}).get("name"),
                day.get("dinner", {}).get("name")
            ])
        print(f"[AI] Tên meal_plan từ AI: {meal_plan_names}")
        
        # Kiểm tra xem có tên nào trong meal_plan không có trong recipes không
        missing_names = [name for name in meal_plan_names if name and name not in recipe_names]
        if missing_names:
            print(f"[AI] CẢNH BÁO: Có {len(missing_names)} tên trong meal_plan không khớp với recipes: {missing_names}")
        
        # Lưu recipes vào database
        saved_recipes = {}
        try:
            for recipe_data in ai_result["recipes"]:
                # Tạo recipe
                new_recipe = models.Recipe(
                    name=recipe_data["name"],
                    description=recipe_data.get("description", ""),
                    instructions=recipe_data.get("instructions", ""),
                    servings=recipe_data.get("servings", 1),
                    prep_time=recipe_data.get("prep_time"),
                    calories=recipe_data["nutrition"]["calories"],
                    protein=recipe_data["nutrition"]["protein"],
                    carbs=recipe_data["nutrition"]["carbs"],
                    fat=recipe_data["nutrition"]["fat"],
                    tags=recipe_data.get("tags", ""),
                    owner_id=current_user.id
                )
                db.add(new_recipe)
                db.flush()  # Để lấy ID
                
                # Thêm ingredients
                for ing in recipe_data.get("ingredients", []):
                    # Xử lý amount - có thể là string như "vừa ăn", "tùy ý"
                    amount_value = ing.get("amount", 0)
                    if isinstance(amount_value, str):
                        # Nếu là string không phải số, đặt về 0 hoặc 1
                        try:
                            amount_value = float(amount_value)
                        except (ValueError, TypeError):
                            # Các trường hợp như "vừa ăn", "tùy ý", "theo khẩu vị"
                            amount_value = 1.0  # Giá trị mặc định
                    
                    # Đảm bảo amount là số
                    try:
                        amount_value = float(amount_value)
                    except (ValueError, TypeError):
                        amount_value = 1.0
                    
                    ingredient = models.Ingredient(
                        name=ing.get("name", "Nguyên liệu"),
                        amount=amount_value,
                        unit=ing.get("unit", ""),
                        recipe_id=new_recipe.id
                    )
                    db.add(ingredient)
                
                # Lưu recipe với tên gốc
                recipe_name = recipe_data["name"]
                saved_recipes[recipe_name] = new_recipe.id
                print(f"[AI] Đã lưu recipe: '{recipe_name}' (ID: {new_recipe.id})")
            
            print(f"[AI] Đã lưu {len(saved_recipes)} recipes vào database")
            print(f"[AI] Danh sách tên recipes đã lưu: {list(saved_recipes.keys())}")
        except Exception as e:
            db.rollback()
            print(f"[AI] Lỗi khi lưu recipes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu recipes vào database: {str(e)}")
        
        # Lưu meal_plans vào database
        from datetime import datetime, timedelta
        # Sử dụng start_date từ request, nếu không có thì dùng hôm nay
        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date).date()
        else:
            start_date = datetime.today().date()
        
        try:
            # XÓA các meal plans cũ trong khoảng 7 ngày này (nếu có)
            end_date = start_date + timedelta(days=6)
            old_plans = db.query(models.MealPlan).filter(
                models.MealPlan.owner_id == current_user.id,
                models.MealPlan.date >= start_date,
                models.MealPlan.date <= end_date
            ).all()
            deleted_count = len(old_plans)
            for plan in old_plans:
                db.delete(plan)
            db.flush()  # Xóa ngay để tránh conflict
            print(f"[AI] Đã xóa {deleted_count} meal plans cũ")
            
            # Hàm helper để tìm recipe_id từ tên (tìm gần đúng)
            def find_recipe_id(recipe_name, saved_recipes):
                """Tìm recipe_id từ tên, hỗ trợ tìm gần đúng"""
                recipe_name = recipe_name.strip()
                print(f"[AI] Đang tìm recipe: '{recipe_name}'")
                
                # Tìm chính xác
                if recipe_name in saved_recipes:
                    print(f"[AI] Tìm thấy chính xác: '{recipe_name}'")
                    return saved_recipes[recipe_name]
                
                # Tìm không phân biệt hoa thường
                for name, recipe_id in saved_recipes.items():
                    if name.lower().strip() == recipe_name.lower().strip():
                        print(f"[AI] Tìm thấy (case-insensitive): '{recipe_name}' -> '{name}'")
                        return recipe_id
                
                # Tìm chứa tên (fuzzy match) - kiểm tra từng từ
                recipe_words = set(recipe_name.lower().split())
                best_match = None
                best_score = 0
                
                for name, recipe_id in saved_recipes.items():
                    name_words = set(name.lower().split())
                    # Đếm số từ trùng
                    common_words = recipe_words.intersection(name_words)
                    score = len(common_words)
                    
                    # Nếu có nhiều từ trùng, ưu tiên
                    if score > best_score and score >= 2:  # Ít nhất 2 từ trùng
                        best_score = score
                        best_match = (name, recipe_id)
                
                if best_match:
                    print(f"[AI] Fuzzy match (score {best_score}): '{recipe_name}' -> '{best_match[0]}'")
                    return best_match[1]
                
                # Tìm chứa tên (substring match) - fallback
                for name, recipe_id in saved_recipes.items():
                    if recipe_name.lower() in name.lower() or name.lower() in recipe_name.lower():
                        print(f"[AI] Substring match: '{recipe_name}' -> '{name}'")
                        return recipe_id
                
                # Nếu không tìm thấy, trả về None
                print(f"[AI] KHÔNG tìm thấy recipe: '{recipe_name}'")
                return None
            
            for day_index, day_plan in enumerate(ai_result["meal_plan"]):
                current_date = start_date + timedelta(days=day_index)
                
                # Tìm recipe_id cho từng bữa
                breakfast_name = day_plan["breakfast"]["name"]
                lunch_name = day_plan["lunch"]["name"]
                dinner_name = day_plan["dinner"]["name"]
                
                breakfast_id = find_recipe_id(breakfast_name, saved_recipes)
                lunch_id = find_recipe_id(lunch_name, saved_recipes)
                dinner_id = find_recipe_id(dinner_name, saved_recipes)
                
                if breakfast_id is None:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Không tìm thấy recipe: '{breakfast_name}'. Các recipes có sẵn: {', '.join(list(saved_recipes.keys())[:5])}"
                    )
                if lunch_id is None:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Không tìm thấy recipe: '{lunch_name}'. Các recipes có sẵn: {', '.join(list(saved_recipes.keys())[:5])}"
                    )
                if dinner_id is None:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Không tìm thấy recipe: '{dinner_name}'. Các recipes có sẵn: {', '.join(list(saved_recipes.keys())[:5])}"
                    )
                
                # Breakfast
                breakfast_plan = models.MealPlan(
                    date=current_date,
                    meal_type="Breakfast",
                    servings=1,
                    owner_id=current_user.id,
                    recipe_id=breakfast_id
                )
                db.add(breakfast_plan)
                
                # Lunch
                lunch_plan = models.MealPlan(
                    date=current_date,
                    meal_type="Lunch",
                    servings=1,
                    owner_id=current_user.id,
                    recipe_id=lunch_id
                )
                db.add(lunch_plan)
                
                # Dinner
                dinner_plan = models.MealPlan(
                    date=current_date,
                    meal_type="Dinner",
                    servings=1,
                    owner_id=current_user.id,
                    recipe_id=dinner_id
                )
                db.add(dinner_plan)
            
            print(f"[AI] Đã tạo {len(ai_result['meal_plan']) * 3} meal plans")
            
            # Commit tất cả
            db.commit()
            print(f"[AI] Đã commit thành công vào database")
            
        except Exception as e:
            db.rollback()
            print(f"[AI] Lỗi khi lưu meal plans: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu meal plans vào database: {str(e)}")
        
        return {
            "message": "✅ Đã tạo thực đơn tuần và lưu vào database!",
            "total_calories_per_day": ai_result["total_calories_per_day"],
            "meal_plan": ai_result["meal_plan"],
            "recipes_created": len(saved_recipes),
            "meal_plans_created": len(ai_result["meal_plan"]) * 3
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"[AI] Lỗi tổng quát: {str(e)}")
        print(f"[AI] Traceback: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Lỗi tạo thực đơn: {str(e)}")

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