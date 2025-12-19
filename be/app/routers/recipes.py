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

# --- 1. LẤY CÔNG THỨC (Của tôi hoặc tất cả) ---
@router.get("/", response_model=List[schemas.Recipe])
def get_recipes(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    tags: str = "",
    my_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lấy công thức món ăn
    - skip: Bỏ qua bao nhiêu bản ghi
    - limit: Giới hạn số lượng trả về
    - search: Tìm kiếm theo tên món
    - tags: Lọc theo tags (VD: "Breakfast,Low-Carb")
    - my_only: Nếu True, chỉ lấy recipes của user hiện tại. Nếu False, lấy tất cả (của user + công khai)
    """
    from sqlalchemy import or_
    
    if my_only:
        # Chỉ lấy recipes của user hiện tại
        query = db.query(models.Recipe).filter(models.Recipe.owner_id == current_user.id)
    else:
        # Lấy recipes của user HOẶC recipes công khai (owner_id = NULL)
        query = db.query(models.Recipe).filter(
            or_(
                models.Recipe.owner_id == current_user.id,
                models.Recipe.owner_id.is_(None)
            )
        )
    
    if search:
        query = query.filter(models.Recipe.name.ilike(f"%{search}%"))
    
    if tags:
        query = query.filter(models.Recipe.tags.ilike(f"%{tags}%"))
    
    recipes = query.offset(skip).limit(limit).all()
    return recipes

# --- 1b. LẤY TẤT CẢ CÁC MÓN ĂN ĐÃ ĐƯỢC ĐÁNH GIÁ (BỞI BẤT KỲ USER NÀO) ---
@router.get("/rated", response_model=List[schemas.Recipe])
def get_rated_recipes(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    tags: str = "",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lấy TẤT CẢ các món ăn đã được đánh giá (bởi bất kỳ user nào)
    - skip: Bỏ qua bao nhiêu bản ghi
    - limit: Giới hạn số lượng trả về
    - search: Tìm kiếm theo tên món
    - tags: Lọc theo tags (VD: "Breakfast,Low-Carb")
    """
    from sqlalchemy import distinct
    
    # Lấy các recipe_id đã có rating (bởi bất kỳ user nào)
    rated_recipe_ids = db.query(distinct(models.Rating.recipe_id)).filter(
        models.Rating.recipe_id.isnot(None)
    ).all()
    
    # Extract recipe IDs từ kết quả
    recipe_ids = [r[0] for r in rated_recipe_ids] if rated_recipe_ids else []
    
    if not recipe_ids:
        return []
    
    # Query recipes đã được đánh giá
    query = db.query(models.Recipe).filter(
        models.Recipe.id.in_(recipe_ids)
    )
    
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
    """Lấy tất cả đánh giá của món ăn (của tất cả users)"""
    # Filter ra những rating có user_id hợp lệ (không null)
    ratings = db.query(models.Rating).filter(
        models.Rating.recipe_id == recipe_id,
        models.Rating.user_id.isnot(None)
    ).all()
    return ratings

# --- 8. LẤY ĐÁNH GIÁ CỦA USER HIỆN TẠI CHO MÓN ĂN ---
@router.get("/{recipe_id}/ratings/my", response_model=schemas.Rating)
def get_my_rating(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Lấy đánh giá của user hiện tại cho món ăn"""
    rating = db.query(models.Rating).filter(
        models.Rating.recipe_id == recipe_id,
        models.Rating.user_id == current_user.id
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Bạn chưa đánh giá món ăn này")
    
    return rating

# --- 9. XÓA ĐÁNH GIÁ CỦA USER HIỆN TẠI CHO MÓN ĂN ---
@router.delete("/{recipe_id}/ratings/my")
def delete_my_rating(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Xóa đánh giá của user hiện tại cho món ăn"""
    rating = db.query(models.Rating).filter(
        models.Rating.recipe_id == recipe_id,
        models.Rating.user_id == current_user.id
    ).first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Bạn chưa đánh giá món ăn này")
    
    db.delete(rating)
    db.commit()
    return {"message": "Đã xóa đánh giá của bạn"}