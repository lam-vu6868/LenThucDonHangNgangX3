import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# Cấu hình Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Chưa cấu hình GEMINI_API_KEY trong .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemma-3-4b-it')  # Model Gemma còn quota

def _clean_json_text(text: str) -> str:
    """
    Làm sạch JSON text để tránh lỗi parsing
    - Loại bỏ trailing commas (dấu phẩy thừa trước } hoặc ])
    - Loại bỏ comments (//, /* */)
    - Sửa các lỗi JSON phổ biến
    """
    # Loại bỏ single-line comments (// ...)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    
    # Loại bỏ multi-line comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # Loại bỏ trailing commas trước } hoặc ]
    # Pattern: tìm dấu phẩy theo sau bởi whitespace và } hoặc ]
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # Sửa lỗi thiếu dấu phẩy giữa các elements trong array hoặc object
    # Tìm pattern: }" { hoặc ]" [ (thiếu dấu phẩy giữa các phần tử)
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)  # Sửa thiếu dấu phẩy giữa các strings
    text = re.sub(r'}\s*\n\s*{', '},\n{', text)  # Sửa thiếu dấu phẩy giữa các objects
    
    # Loại bỏ BOM (Byte Order Mark) nếu có
    if text.startswith('\ufeff'):
        text = text[1:]
    
    return text

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
        
        # Xử lý markdown và text thừa
        if "```" in result_text:
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            if start != -1 and end != 0:
                result_text = result_text[start:end]
        
        # Đảm bảo encoding UTF-8
        if isinstance(result_text, bytes):
            result_text = result_text.decode('utf-8')
        
        # Làm sạch JSON
        result_text = _clean_json_text(result_text)
        
        recipe_data = json.loads(result_text)
        return recipe_data
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON Parse Error in generate_recipe: {str(e)}")
        print(f"[ERROR] Response: {result_text[:500]}")
        raise Exception(f"AI trả về JSON không hợp lệ: {str(e)}")
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
        
        # Xử lý markdown và text thừa
        if "```" in result_text:
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            if start != -1 and end != 0:
                result_text = result_text[start:end]
        
        # Đảm bảo encoding UTF-8
        if isinstance(result_text, bytes):
            result_text = result_text.decode('utf-8')
        
        # Làm sạch JSON
        result_text = _clean_json_text(result_text)
        
        meal_plan = json.loads(result_text)
        return meal_plan
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON Parse Error in suggest_weekly_meal_plan: {str(e)}")
        print(f"[ERROR] Response: {result_text[:500]}")
        raise Exception(f"AI trả về JSON không hợp lệ: {str(e)}")
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
        
        # Xử lý markdown và text thừa
        if "```" in result_text:
            # Tìm array JSON [...]
            start = result_text.find("[")
            end = result_text.rfind("]") + 1
            if start != -1 and end != 0:
                result_text = result_text[start:end]
        
        # Đảm bảo encoding UTF-8
        if isinstance(result_text, bytes):
            result_text = result_text.decode('utf-8')
        
        # Làm sạch JSON
        result_text = _clean_json_text(result_text)
        
        suggestions = json.loads(result_text)
        return suggestions
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON Parse Error in get_recipe_suggestions: {str(e)}")
        print(f"[ERROR] Response: {result_text[:500]}")
        raise Exception(f"AI trả về JSON không hợp lệ: {str(e)}")
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
Bạn là chuyên gia dinh dưỡng. Tạo thực đơn 7 ngày KÈM CÔNG THỨC CHI TIẾT.

**Thông tin:**
- Giới tính: {user_data["gender"]}
- Cân nặng: {user_data["weight"]}kg, Chiều cao: {user_data["height"]}cm, Tuổi: {age}
- Calories mục tiêu: {target_calories} kcal/ngày
- Hạn chế: {user_data.get("dietary_preferences", "Không có")}
- Ghi chú: {user_data.get("notes", "Không có")}

**YÊU CẦU JSON - Tuân thủ chặt chẽ format sau:**

1. KHÔNG thêm markdown (```json hoặc ```)
2. KHÔNG thêm comments trong JSON
3. KHÔNG có trailing commas (dấu phẩy thừa trước }} hoặc ])
4. Với field "instructions": Dùng dấu \\n để xuống dòng (ví dụ: "Bước 1: Làm A\\nBước 2: Làm B")
5. Đảm bảo tất cả strings được đóng ngoặc kép đúng

**Format JSON:**

{{
    "total_calories_per_day": {target_calories},
    "recipes": [
        {{
            "name": "Cơm gà Hải Nam",
            "description": "Món cơm gà thơm ngon đơn giản",
            "instructions": "Bước 1: Rửa gà và ướp với muối\\nBước 2: Hấp gà 25 phút\\nBước 3: Nấu cơm với nước luộc gà",
            "servings": 1,
            "prep_time": 35,
            "ingredients": [
                {{"name": "Gạo", "amount": 100, "unit": "gram"}},
                {{"name": "Thịt gà", "amount": 150, "unit": "gram"}},
                {{"name": "Tỏi", "amount": 10, "unit": "gram"}}
            ],
            "nutrition": {{
                "calories": 450,
                "protein": 35,
                "carbs": 55,
                "fat": 10
            }},
            "tags": "Lunch"
        }}
    ],
    "meal_plan": [
        {{
            "day": "Monday",
            "breakfast": {{"name": "Cháo yến mạch chuối", "calories": 350, "protein": 12, "carbs": 60, "fat": 8}},
            "lunch": {{"name": "Cơm gà Hải Nam", "calories": 450, "protein": 35, "carbs": 55, "fat": 10}},
            "dinner": {{"name": "Bún cá", "calories": 400, "protein": 28, "carbs": 50, "fat": 12}}
        }}
    ]
}}

**LƯU Ý BẮT BUỘC:**
- Dùng tiếng Việt CÓ DẤU đầy đủ
- Đủ 7 ngày (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
- Tên món trong meal_plan PHẢI KHỚP 100% với tên trong recipes
- Tổng calories/ngày ≈ {target_calories}
- CHỈ trả về JSON, không thêm text nào khác
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Xử lý markdown và text thừa
        # Loại bỏ markdown wrapper (```json ... ``` hoặc ``` ... ```)
        if "```" in result_text:
            # Tìm vị trí bắt đầu và kết thúc của JSON
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            if start != -1 and end != 0:
                result_text = result_text[start:end]
        
        # Đảm bảo encoding UTF-8
        if isinstance(result_text, bytes):
            result_text = result_text.decode('utf-8')
        
        # Làm sạch JSON: loại bỏ comments, trailing commas
        result_text = _clean_json_text(result_text)
        
        # Log để debug
        print(f"[AI] Response length: {len(result_text)} chars")
        print(f"[AI] First 500 chars: {result_text[:500]}")
        
        # Parse JSON (mặc định Python json.loads() đã hỗ trợ UTF-8)
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as parse_error:
            # Nếu vẫn lỗi, thử xử lý thêm
            print(f"[WARN] First JSON parse failed: {str(parse_error)}")
            print(f"[WARN] Attempting additional cleanup...")
            
            # Thử loại bỏ các ký tự không hợp lệ
            result_text = result_text.encode('utf-8', 'ignore').decode('utf-8')
            
            # Thử parse lại
            try:
                result = json.loads(result_text)
                print(f"[SUCCESS] JSON parsed after additional cleanup")
            except json.JSONDecodeError as second_error:
                # Log chi tiết lỗi
                print(f"[ERROR] JSON Parse Error: {str(second_error)}")
                print(f"[ERROR] Line {second_error.lineno}, Column {second_error.colno}")
                print(f"[ERROR] Error position {second_error.pos}")
                print(f"[ERROR] Context (200 chars around error):")
                error_start = max(0, second_error.pos - 100)
                error_end = min(len(result_text), second_error.pos + 100)
                print(f"[ERROR] ...{result_text[error_start:error_end]}...")
                
                # Lưu full response để debug
                print(f"[ERROR] Full response saved for debugging")
                with open("/tmp/ai_response_error.txt", "w", encoding="utf-8") as f:
                    f.write(result_text)
                
                raise Exception(f"AI trả về JSON không hợp lệ. Vui lòng thử lại. Chi tiết: {str(second_error)}")
        
        return result
    except json.JSONDecodeError as e:
        # Log lỗi chi tiết
        print(f"[ERROR] JSON Parse Error: {str(e)}")
        print(f"[ERROR] Line {e.lineno}, Column {e.colno}")
        print(f"[ERROR] Problem context (50 chars before/after):")
        print(f"[ERROR] {result_text[max(0, e.pos-100):e.pos+100]}")
        print(f"[ERROR] Full response:\n{result_text}")
        raise Exception(f"AI trả về JSON không hợp lệ. Vui lòng thử lại. Chi tiết: {str(e)}")
    except Exception as e:
        print(f"[ERROR] General error: {str(e)}")
        raise Exception(f"Lỗi khi gọi AI: {str(e)}")
