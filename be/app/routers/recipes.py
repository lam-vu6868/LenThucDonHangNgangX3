from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.utils import get_current_user

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)

# --- 1. LẤY TẤT CẢ CÔNG THỨC (Public + của user) ---
@router.get("/", response_model=List[schemas.Recipe])
def get_recipes(
    skip: int = 0,
    limit: int = 50,
    search: str = "",
    tags: str = "",
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách công thức món ăn
    - skip: Bỏ qua bao nhiêu bản ghi
    - limit: Giới hạn số lượng trả về
    - search: Tìm kiếm theo tên món
    - tags: Lọc theo tags (VD: "Breakfast,Low-Carb")
    """
    query = db.query(models.Recipe)
    
    if search:
        query = query.filter(models.Recipe.name.ilike(f"%{search}%"))
    
    if tags:
        query = query.filter(models.Recipe.tags.ilike(f"%{tags}%"))
    
    recipes = query.offset(skip).limit(limit).all()
    return recipes

# --- 2. LẤY CHI TIẾT 1 CÔNG THỨC ---
@router.get("/{recipe_id}", response_model=schemas.Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức này")
    return recipe

# --- 3. TẠO CÔNG THỨC MỚI (Cần đăng nhập) ---
@router.post("/", response_model=schemas.Recipe)
def create_recipe(
    recipe: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Tạo công thức món ăn mới"""
    # Tạo recipe
    new_recipe = models.Recipe(
        name=recipe.name,
        description=recipe.description,
        instructions=recipe.instructions,
        image_url=recipe.image_url,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
        calories=recipe.calories,
        protein=recipe.protein,
        carbs=recipe.carbs,
        fat=recipe.fat,
        tags=recipe.tags,
        owner_id=current_user.id
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    
    # Thêm ingredients
    for ing in recipe.ingredients:
        new_ingredient = models.Ingredient(
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit,
            recipe_id=new_recipe.id
        )
        db.add(new_ingredient)
    
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

# --- 4. CẬP NHẬT CÔNG THỨC (Chỉ owner) ---
@router.put("/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(
    recipe_id: int,
    recipe_update: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức")
    
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa công thức này")
    
    # Cập nhật thông tin
    recipe.name = recipe_update.name
    recipe.description = recipe_update.description
    recipe.instructions = recipe_update.instructions
    recipe.image_url = recipe_update.image_url
    recipe.servings = recipe_update.servings
    recipe.prep_time = recipe_update.prep_time
    recipe.calories = recipe_update.calories
    recipe.protein = recipe_update.protein
    recipe.carbs = recipe_update.carbs
    recipe.fat = recipe_update.fat
    recipe.tags = recipe_update.tags
    
    # Xóa ingredients cũ và thêm mới
    db.query(models.Ingredient).filter(models.Ingredient.recipe_id == recipe_id).delete()
    for ing in recipe_update.ingredients:
        new_ingredient = models.Ingredient(
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit,
            recipe_id=recipe.id
        )
        db.add(new_ingredient)
    
    db.commit()
    db.refresh(recipe)
    return recipe

# --- 5. XÓA CÔNG THỨC (Chỉ owner) ---
@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức")
    
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa công thức này")
    
    db.delete(recipe)
    db.commit()
    return {"message": f"Đã xóa công thức: {recipe.name}"}

# --- 6. ĐÁNH GIÁ CÔNG THỨC ---
@router.post("/{recipe_id}/ratings", response_model=schemas.Rating)
def rate_recipe(
    recipe_id: int,
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Đánh giá món ăn (1-5 sao + comment)
    """
    # Kiểm tra recipe tồn tại
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức")
    
    # Kiểm tra đã đánh giá chưa
    existing_rating = db.query(models.Rating).filter(
        models.Rating.user_id == current_user.id,
        models.Rating.recipe_id == recipe_id
    ).first()
    
    if existing_rating:
        # Cập nhật rating cũ
        existing_rating.stars = rating.stars
        existing_rating.comment = rating.comment
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    # Tạo rating mới
    new_rating = models.Rating(
        stars=rating.stars,
        comment=rating.comment,
        user_id=current_user.id,
        recipe_id=recipe_id
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

# --- 7. LẤY ĐÁNH GIÁ CỦA MÓN ĂN ---
@router.get("/{recipe_id}/ratings", response_model=List[schemas.Rating])
def get_recipe_ratings(recipe_id: int, db: Session = Depends(get_db)):
    """Lấy tất cả đánh giá của món ăn"""
    ratings = db.query(models.Rating).filter(models.Rating.recipe_id == recipe_id).all()
    return ratings