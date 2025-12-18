from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app import models, schemas
from app.utils import get_current_user
from app.services.shopping import generate_shopping_list

router = APIRouter(
    prefix="/shopping",
    tags=["Shopping List"]
)

@router.get("/list")
def get_shopping_list(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Tạo shopping list tự động từ meal plans
    
    Query params:
    - start_date: Ngày bắt đầu (YYYY-MM-DD)
    - end_date: Ngày kết thúc (YYYY-MM-DD)
    
    Trả về danh sách nguyên liệu đã gộp theo tên + đơn vị
    """
    try:
        shopping_list = generate_shopping_list(db, current_user.id, start_date, end_date)
        return shopping_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SHOPPING LIST ITEMS (Lưu trạng thái đã mua) ---

@router.post("/items", response_model=schemas.ShoppingListItem)
def create_shopping_list_item(
    item: schemas.ShoppingListItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Tạo shopping list item từ nguyên liệu của món ăn"""
    # Kiểm tra nếu đã có item tương tự chưa mua
    existing = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == current_user.id,
        models.ShoppingListItem.ingredient_name == item.ingredient_name,
        models.ShoppingListItem.recipe_id == item.recipe_id,
        models.ShoppingListItem.is_purchased == False
    ).first()
    
    if existing:
        # Cập nhật số lượng nếu đã có
        existing.amount += item.amount
        db.commit()
        db.refresh(existing)
        return existing
    
    # Tạo mới
    new_item = models.ShoppingListItem(
        ingredient_name=item.ingredient_name,
        amount=item.amount,
        unit=item.unit,
        recipe_id=item.recipe_id,
        user_id=current_user.id,
        is_purchased=False
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.post("/items/from-recipe/{recipe_id}")
def create_shopping_list_from_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Tạo shopping list items từ tất cả nguyên liệu của một món ăn"""
    # Kiểm tra recipe tồn tại
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Không tìm thấy công thức")
    
    # Kiểm tra xem đã có items cho recipe này chưa (không phân biệt purchased)
    existing_items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == current_user.id,
        models.ShoppingListItem.recipe_id == recipe_id
    ).all()
    
    # Nếu đã có items rồi, không tạo lại
    if existing_items:
        return {
            "message": f"Đã có {len(existing_items)} nguyên liệu trong danh sách mua sắm",
            "items": existing_items,
            "already_exists": True
        }
    
    # Tạo mới items
    created_items = []
    for ingredient in recipe.ingredients:
        new_item = models.ShoppingListItem(
            ingredient_name=ingredient.name,
            amount=ingredient.amount,
            unit=ingredient.unit,
            recipe_id=recipe_id,
            user_id=current_user.id,
            is_purchased=False
        )
        db.add(new_item)
        created_items.append(new_item)
    
    db.commit()
    for item in created_items:
        db.refresh(item)
    
    return {"message": f"Đã thêm {len(created_items)} nguyên liệu vào danh sách mua sắm", "items": created_items, "already_exists": False}

@router.get("/items", response_model=List[schemas.ShoppingListItem])
def get_shopping_list_items(
    recipe_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Lấy danh sách shopping list items của user"""
    query = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.user_id == current_user.id
    )
    
    if recipe_id:
        query = query.filter(models.ShoppingListItem.recipe_id == recipe_id)
    
    items = query.order_by(models.ShoppingListItem.created_at.desc()).all()
    return items

@router.put("/items/{item_id}", response_model=schemas.ShoppingListItem)
def update_shopping_list_item(
    item_id: int,
    item_update: schemas.ShoppingListItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Cập nhật trạng thái đã mua của shopping list item"""
    item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == item_id,
        models.ShoppingListItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy item")
    
    item.is_purchased = item_update.is_purchased
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}")
def delete_shopping_list_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Xóa shopping list item"""
    item = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.id == item_id,
        models.ShoppingListItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy item")
    
    db.delete(item)
    db.commit()
    return {"message": "Đã xóa item"}

@router.delete("/items/recipe/{recipe_id}")
def clear_shopping_list_for_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Xóa tất cả shopping list items của một món ăn"""
    items = db.query(models.ShoppingListItem).filter(
        models.ShoppingListItem.recipe_id == recipe_id,
        models.ShoppingListItem.user_id == current_user.id
    ).all()
    
    for item in items:
        db.delete(item)
    
    db.commit()
    return {"message": f"Đã xóa {len(items)} items"}