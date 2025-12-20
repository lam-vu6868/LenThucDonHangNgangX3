from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Để lấy thời gian hiện tại
from .database import Base

# --- 1. USERS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")

    # Thông tin nhân trắc học (Tính BMR)
    gender = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    
    # --- MỚI: Hạn chế ăn uống (Yêu cầu của thầy) ---
    # Lưu chuỗi: "vegan,peanut_free"
    dietary_preferences = Column(String, nullable=True) 

    recipes = relationship("Recipe", back_populates="owner")
    meal_plans = relationship("MealPlan", back_populates="owner")
    ratings = relationship("Rating", back_populates="user")

# --- 2. RECIPES (công thức và món ăn)--- 
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    
    # --- MỚI: Chi tiết dinh dưỡng & Khẩu phần ---
    servings = Column(Integer, default=1)  # Khẩu phần mặc định (VD: 2 người)
    prep_time = Column(Integer, nullable=True) # Thời gian nấu (phút)
    
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True) # Gam
    carbs = Column(Float, nullable=True)   # Gam
    fat = Column(Float, nullable=True)     # Gam
    
    tags = Column(String, nullable=True)   # VD: "Breakfast,Low-Carb"
    # --------------------------------------------

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    owner = relationship("User", back_populates="recipes")
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="recipe")
    ratings = relationship("Rating", back_populates="recipe")

# --- 3. INGREDIENTS (nguyên liệu) ---
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float)
    unit = Column(String)

    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = relationship("Recipe", back_populates="ingredients")

# --- 4. MEAL PLANS (KẾ HOẠCH ĂN UỐNG)---
class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    meal_type = Column(String) # Breakfast/Lunch/Dinner

    # --- MỚI: Số người ăn thực tế (để nhân Shopping List) ---
    servings = Column(Integer, default=1) 
    # -------------------------------------------------------

    owner_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    owner = relationship("User", back_populates="meal_plans")
    recipe = relationship("Recipe", back_populates="meal_plans")

# --- 5. RATINGS (đánh giá) ---
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    stars = Column(Integer)
    comment = Column(Text, nullable=True)
    
    # --- MỚI: Thời gian đánh giá ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # -------------------------------

    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    user = relationship("User", back_populates="ratings")
    recipe = relationship("Recipe", back_populates="ratings")

# --- 6. SHOPPING LIST ITEMS (danh sách mua sắm) ---
class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_name = Column(String, index=True)  # Tên nguyên liệu
    amount = Column(Float)  # Số lượng
    unit = Column(String)  # Đơn vị
    is_purchased = Column(Boolean, default=False)  # Đã mua chưa
    
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)  # Món ăn nào (có thể null nếu tự thêm)
    user_id = Column(Integer, ForeignKey("users.id"))  # User nào
    
    # Thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    recipe = relationship("Recipe")