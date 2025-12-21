from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Để lấy thời gian hiện tại
from .database import Base

# --- 1. USERS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # ID người dùng (tự tăng)
    email = Column(String, unique=True, index=True)  # Email đăng nhập (duy nhất)
    hashed_password = Column(String)  # Mật khẩu đã mã hóa (bcrypt)
    full_name = Column(String, nullable=True)  # Họ và tên
    is_active = Column(Boolean, default=True)  # Trạng thái tài khoản (active/banned)
    role = Column(String, default="user")  # Vai trò: "user" hoặc "admin"

    # Thông tin nhân trắc học (Tính BMR)
    gender = Column(String, nullable=True)  # Giới tính: "male" hoặc "female"
    date_of_birth = Column(Date, nullable=True)  # Ngày sinh (để tính tuổi)
    height = Column(Float, nullable=True)  # Chiều cao (cm)
    weight = Column(Float, nullable=True)  # Cân nặng (kg)
    
    # --- MỚI: Hạn chế ăn uống (Yêu cầu của thầy) ---
    # Lưu chuỗi: "vegan,peanut_free"
    dietary_preferences = Column(String, nullable=True)  # Hạn chế ăn uống (vegan, gluten-free...) 

    recipes = relationship("Recipe", back_populates="owner")
    meal_plans = relationship("MealPlan", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")

# --- 2. RECIPES (công thức và món ăn)--- 
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)  # ID món ăn (tự tăng)
    name = Column(String, index=True)  # Tên món ăn (VD: Phở bò, Cơm gà)
    description = Column(Text, nullable=True)  # Mô tả ngắn về món ăn
    instructions = Column(Text, nullable=True)  # Hướng dẫn nấu (các bước)
    image_url = Column(String, nullable=True)  # Link hình ảnh món ăn
    
    # --- MỚI: Chi tiết dinh dưỡng & Khẩu phần ---
    servings = Column(Integer, default=1)  # Khẩu phần mặc định (VD: 2 người)
    prep_time = Column(Integer, nullable=True)  # Thời gian nấu (phút)
    
    calories = Column(Float, nullable=True)  # Năng lượng (kcal)
    protein = Column(Float, nullable=True)  # Protein (gram)
    carbs = Column(Float, nullable=True)  # Carbohydrate (gram)
    fat = Column(Float, nullable=True)  # Chất béo (gram)
    
    tags = Column(String, nullable=True)  # Thẻ phân loại (VD: "Breakfast,Low-Carb")
    # --------------------------------------------

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ID người tạo món ăn
    
    owner = relationship("User", back_populates="recipes")
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="recipe")
    ratings = relationship("Rating", back_populates="recipe")

# --- 3. INGREDIENTS (nguyên liệu) ---
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)  # ID nguyên liệu (tự tăng)
    name = Column(String)  # Tên nguyên liệu (VD: Thịt bò, Bánh phở)
    amount = Column(Float)  # Số lượng (VD: 200, 300)
    unit = Column(String)  # Đơn vị (VD: gram, ml, muỗng)

    recipe_id = Column(Integer, ForeignKey("recipes.id"))  # ID món ăn chứa nguyên liệu này
    recipe = relationship("Recipe", back_populates="ingredients")

# --- 4. MEAL PLANS (KẾ HOẠCH ĂN UỐNG)---
class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)  # ID lịch ăn (tự tăng)
    date = Column(Date, index=True)  # Ngày ăn (VD: 2025-12-23)
    meal_type = Column(String)  # Bữa ăn: "Breakfast"/"Lunch"/"Dinner"

    # --- MỚI: Số người ăn thực tế (để nhân Shopping List) ---
    servings = Column(Integer, default=1)  # Số khẩu phần (VD: nấu cho 4 người)
    # -------------------------------------------------------

    owner_id = Column(Integer, ForeignKey("users.id"))  # ID người tạo lịch ăn
    recipe_id = Column(Integer, ForeignKey("recipes.id"))  # ID món ăn trong lịch

    owner = relationship("User", back_populates="meal_plans")
    recipe = relationship("Recipe", back_populates="meal_plans")

# --- 5. RATINGS (đánh giá) ---
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)  # ID đánh giá (tự tăng)
    stars = Column(Integer)  # Số sao đánh giá (1-5 sao)
    comment = Column(Text, nullable=True)  # Bình luận/nhận xét về món ăn
    
    # --- MỚI: Thời gian đánh giá ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Thời gian đánh giá (tự động)
    # -------------------------------

    user_id = Column(Integer, ForeignKey("users.id"))  # ID người đánh giá
    recipe_id = Column(Integer, ForeignKey("recipes.id"))  # ID món ăn được đánh giá

    user = relationship("User", back_populates="ratings")
    recipe = relationship("Recipe", back_populates="ratings")

# --- 6. SHOPPING LIST ITEMS (danh sách mua sắm) ---
class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)  # ID item mua sắm (tự tăng)
    ingredient_name = Column(String, index=True)  # Tên nguyên liệu cần mua
    amount = Column(Float)  # Số lượng cần mua
    unit = Column(String)  # Đơn vị (gram, ml, cái...)
    is_purchased = Column(Boolean, default=False)  # Đã mua chưa (checkbox)
    
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)  # Món ăn nào (có thể null nếu tự thêm)
    user_id = Column(Integer, ForeignKey("users.id"))  # ID người tạo shopping list
    
    # Thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Thời gian tạo
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # Thời gian cập nhật

    user = relationship("User")
    recipe = relationship("Recipe")