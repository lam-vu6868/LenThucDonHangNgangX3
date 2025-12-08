import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# Cấu hình Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Chưa cấu hình GEMINI_API_KEY trong .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemma-3-4b-it')  # Model Gemma còn quota

def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """Tính BMR (Basal Metabolic Rate) theo công thức Mifflin-St Jeor"""
    if gender.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return round(bmr, 2)

def calculate_age(date_of_birth: date) -> int:
    """Tính tuổi từ ngày sinh"""
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

async def generate_recipe_from_ingredients(ingredients: list[str], dietary_preferences: str = "") -> dict:
    """
    Tạo công thức món ăn từ danh sách nguyên liệu
    
    Args:
        ingredients: Danh sách nguyên liệu có sẵn
        dietary_preferences: Hạn chế ăn uống (vegan, vegetarian, gluten_free...)
    
    Returns:
        dict chứa tên món, mô tả, hướng dẫn, dinh dưỡng
    """
    prompt = f"""
Bạn là đầu bếp chuyên nghiệp. Hãy tạo 1 công thức món ăn từ các nguyên liệu sau:

**Nguyên liệu có sẵn:** {', '.join(ingredients)}

**Hạn chế:** {dietary_preferences if dietary_preferences else "Không có"}

Trả về JSON với cấu trúc SAU (KHÔNG thêm markdown ```json):
{{
    "name": "Tên món ăn",
    "description": "Mô tả ngắn gọn về món",
    "instructions": "Các bước nấu chi tiết (mỗi bước xuống dòng)",
    "servings": 2,
    "prep_time": 30,
    "ingredients": [
        {{"name": "Gạ", "amount": 200, "unit": "gram"}},
        {{"name": "Thịt gà", "amount": 150, "unit": "gram"}}
    ],
    "nutrition": {{
        "calories": 450,
        "protein": 25,
        "carbs": 60,
        "fat": 12
    }},
    "tags": "Lunch,High-Protein"
}}
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Xử lý nếu Gemini trả về có markdown
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        recipe_data = json.loads(result_text)
        return recipe_data
    except Exception as e:
        raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")

async def suggest_weekly_meal_plan(user_data: dict) -> dict:
    """
    Gợi ý thực đơn cả tuần dựa trên BMR, sở thích, hạn chế ăn uống
    
    Args:
        user_data: {
            "gender": "male",
            "weight": 70,
            "height": 175,
            "date_of_birth": "2000-01-15",
            "dietary_preferences": "vegetarian",
            "activity_level": "moderate"  # sedentary, light, moderate, active, very_active
        }
    
    Returns:
        dict chứa 7 ngày thực đơn (breakfast, lunch, dinner)
    """
    age = calculate_age(date.fromisoformat(user_data["date_of_birth"]))
    bmr = calculate_bmr(user_data["gender"], user_data["weight"], user_data["height"], age)
    
    # Tính TDEE (Total Daily Energy Expenditure)
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    tdee = bmr * activity_multipliers.get(user_data.get("activity_level", "moderate"), 1.55)
    
    prompt = f"""
Bạn là chuyên gia dinh dưỡng. Hãy lên thực đơn 7 ngày cho người sau:

**Thông tin:**
- Giới tính: {user_data["gender"]}
- Cân nặng: {user_data["weight"]}kg
- Chiều cao: {user_data["height"]}cm
- Tuổi: {age}
- BMR: {bmr} kcal/ngày
- TDEE (calories cần): {round(tdee)} kcal/ngày
- Hạn chế: {user_data.get("dietary_preferences", "Không có")}

Trả về JSON với cấu trúc (KHÔNG thêm markdown):
{{
    "total_calories_per_day": {round(tdee)},
    "meal_plan": [
        {{
            "day": "Monday",
            "breakfast": {{"name": "Tên món", "calories": 400, "protein": 20, "carbs": 50, "fat": 10}},
            "lunch": {{"name": "Tên món", "calories": 600, "protein": 35, "carbs": 70, "fat": 18}},
            "dinner": {{"name": "Tên món", "calories": 500, "protein": 30, "carbs": 55, "fat": 15}}
        }}
    ]
}}

Lưu ý: 
- Đủ 7 ngày (Monday -> Sunday)
- Cân đối dinh dưỡng
- Phù hợp với hạn chế ăn uống
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        meal_plan = json.loads(result_text)
        return meal_plan
    except Exception as e:
        raise Exception(f"Lỗi khi tạo thực đơn: {str(e)}")

async def get_recipe_suggestions(query: str, dietary_preferences: str = "") -> list[dict]:
    """
    Tìm kiếm gợi ý món ăn theo từ khóa
    
    Args:
        query: Từ khóa tìm kiếm (VD: "món ăn giảm cân", "món chay protein cao")
        dietary_preferences: Hạn chế ăn uống
    
    Returns:
        list chứa 5 món ăn gợi ý
    """
    prompt = f"""
Gợi ý 5 món ăn cho yêu cầu: "{query}"
Hạn chế: {dietary_preferences if dietary_preferences else "Không có"}

Trả về JSON (KHÔNG markdown):
[
    {{
        "name": "Tên món",
        "description": "Mô tả ngắn",
        "calories": 450,
        "protein": 25,
        "carbs": 50,
        "fat": 15,
        "tags": "Breakfast,Low-Carb"
    }}
]
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        suggestions = json.loads(result_text)
        return suggestions
    except Exception as e:
        raise Exception(f"Lỗi khi tìm kiếm món ăn: {str(e)}")

async def suggest_weekly_meal_plan_with_recipes(user_data: dict) -> dict:
    """
    Tạo thực đơn 7 ngày KÈM THEO CÔNG THỨC CHI TIẾT để lưu vào database
    
    Args:
        user_data: {
            "gender": "male",
            "weight": 70,
            "height": 175,
            "date_of_birth": "2000-01-15",
            "dietary_preferences": "vegetarian",
            "activity_level": "moderate",
            "goal": "maintain",  # maintain, lose, gain
            "notes": "Muốn nhiều rau xanh"
        }
    
    Returns:
        {
            "total_calories_per_day": 2200,
            "recipes": [list of full recipe objects],
            "meal_plan": [7 days with breakfast/lunch/dinner]
        }
    """
    age = calculate_age(date.fromisoformat(user_data["date_of_birth"]))
    bmr = calculate_bmr(user_data["gender"], user_data["weight"], user_data["height"], age)
    
    # Tính TDEE
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    tdee = bmr * activity_multipliers.get(user_data.get("activity_level", "moderate"), 1.55)
    
    # Điều chỉnh theo mục tiêu
    goal_adjustments = {
        "maintain": 0,
        "lose": -500,
        "gain": 500
    }
    target_calories = round(tdee + goal_adjustments.get(user_data.get("goal", "maintain"), 0))
    
    prompt = f"""
Bạn là chuyên gia dinh dưỡng và đầu bếp chuyên nghiệp. Tạo thực đơn 7 ngày KÈM CÔNG THỨC CHI TIẾT cho:

**Thông tin người dùng:**
- Giới tính: {user_data["gender"]}
- Cân nặng: {user_data["weight"]}kg
- Chiều cao: {user_data["height"]}cm
- Tuổi: {age}
- BMR: {bmr} kcal/ngày
- TDEE: {round(tdee)} kcal/ngày
- Mục tiêu: {user_data.get("goal", "maintain")}
- Calories mục tiêu: {target_calories} kcal/ngày
- Hạn chế ăn uống: {user_data.get("dietary_preferences", "Không có")}
- Ghi chú thêm: {user_data.get("notes", "Không có")}

**YÊU CẦU QUAN TRỌNG:**
1. Tạo CÔNG THỨC ĐẦY ĐỦ cho mỗi món (nguyên liệu, cách nấu, dinh dưỡng)
2. Mỗi món PHẢI có tên KHÁC NHAU (không trùng lặp)
3. Cân đối dinh dưỡng theo tỷ lệ: 30% protein, 50% carbs, 20% fat
4. Món ăn phù hợp văn hóa Việt Nam
5. Dễ nấu, nguyên liệu dễ kiếm

Trả về JSON với cấu trúc SAU (KHÔNG thêm markdown ```json):
{{
    "total_calories_per_day": {target_calories},
    "recipes": [
        {{
            "name": "Cơm gà hấp nấm đông cô",
            "description": "Món cơm gà hấp thơm ngon, giàu protein",
            "instructions": "Bước 1: Ướp gà với muối, tiêu\\nBước 2: Hấp gà với nấm 20 phút\\nBước 3: Nấu cơm và trộn đều",
            "servings": 1,
            "prep_time": 30,
            "ingredients": [
                {{"name": "Gạo", "amount": 100, "unit": "gram"}},
                {{"name": "Thịt gà", "amount": 150, "unit": "gram"}},
                {{"name": "Nấm đông cô", "amount": 50, "unit": "gram"}}
            ],
            "nutrition": {{
                "calories": 450,
                "protein": 35,
                "carbs": 55,
                "fat": 10
            }},
            "tags": "Lunch,High-Protein"
        }}
    ],
    "meal_plan": [
        {{
            "day": "Monday",
            "breakfast": {{"name": "Cháo yến mạch chuối", "calories": 350, "protein": 12, "carbs": 60, "fat": 8}},
            "lunch": {{"name": "Cơm gà hấp nấm đông cô", "calories": 450, "protein": 35, "carbs": 55, "fat": 10}},
            "dinner": {{"name": "Bún cá dinh dưỡng", "calories": 400, "protein": 28, "carbs": 50, "fat": 12}}
        }}
    ]
}}

LƯU Ý:
- PHẢI có đủ 7 ngày (Monday -> Sunday)
- Mỗi món trong "recipes" phải khớp với tên món trong "meal_plan"
- Tổng calories/ngày = breakfast + lunch + dinner ≈ {target_calories}
- Ingredients phải có đơn vị cụ thể (gram, ml, cái...)
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(result_text)
        return result
    except Exception as e:
        raise Exception(f"Lỗi khi tạo thực đơn: {str(e)}")
