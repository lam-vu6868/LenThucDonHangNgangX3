from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

# --- 1. SCHEMAS CHO TOKEN (PHẦN BẠN ĐANG THIẾU) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- 2. SCHEMAS CHO USER ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    dietary_preferences: Optional[str] = None

class UserCreate(UserBase):
    password: str 

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    dietary_preferences: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    role: str
    class Config:
        from_attributes = True

# --- 3. SCHEMAS CHO INGREDIENT ---
class IngredientBase(BaseModel):
    name: str
    amount: float
    unit: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    recipe_id: int
    class Config:
        from_attributes = True

# --- 4. SCHEMAS CHO RECIPE ---
class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    image_url: Optional[str] = None
    servings: int = 1
    prep_time: Optional[int] = None
    calories: Optional[float] = 0
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    tags: Optional[str] = None

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate] = []

class Recipe(RecipeBase):
    id: int
    owner_id: Optional[int] = None
    ingredients: List[Ingredient] = []
    class Config:
        from_attributes = True

# --- 5. SCHEMAS CHO MEAL PLAN ---
class MealPlanBase(BaseModel):
    date: date
    meal_type: str
    recipe_id: int
    servings: int = 1

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    owner_id: int
    recipe: Optional[Recipe] = None
    owner: Optional[User] = None
    class Config:
        from_attributes = True

# --- 6. SCHEMAS CHO RATING ---
class RatingBase(BaseModel):
    stars: int
    comment: Optional[str] = None
    recipe_id: int

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[User] = None
    recipe: Optional[Recipe] = None
    class Config:
        from_attributes = True

# --- 7. SCHEMAS CHO SHOPPING LIST ITEM ---
class ShoppingListItemBase(BaseModel):
    ingredient_name: str
    amount: float
    unit: str
    recipe_id: Optional[int] = None

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItemUpdate(BaseModel):
    is_purchased: bool

class ShoppingListItem(ShoppingListItemBase):
    id: int
    user_id: int
    is_purchased: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True