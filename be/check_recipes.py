#!/usr/bin/env python3
"""Script để kiểm tra recipes và owner_id trong database"""
import sys
sys.path.insert(0, '/mnt/d/LenThucDonHangNgangX3/be')

from app.database import SessionLocal
from app import models

def main():
    db = SessionLocal()
    try:
        # Lấy tất cả users
        print("\n=== DANH SÁCH USERS ===")
        users = db.query(models.User).all()
        for user in users:
            print(f"  ID: {user.id}, Email: {user.email}, Name: {user.full_name}")
        
        # Lấy tất cả recipes
        print("\n=== DANH SÁCH RECIPES ===")
        recipes = db.query(models.Recipe).all()
        for recipe in recipes:
            owner_info = f"User ID: {recipe.owner_id}" if recipe.owner_id else "PUBLIC (No owner)"
            print(f"  ID: {recipe.id}, Name: {recipe.name}, Owner: {owner_info}")
        
        # Thống kê
        print("\n=== THỐNG KÊ ===")
        public_recipes = db.query(models.Recipe).filter(models.Recipe.owner_id.is_(None)).count()
        private_recipes = db.query(models.Recipe).filter(models.Recipe.owner_id.isnot(None)).count()
        print(f"  Recipes công khai (owner_id = NULL): {public_recipes}")
        print(f"  Recipes riêng tư (có owner_id): {private_recipes}")
        
        # Shopping list items
        print("\n=== SHOPPING LIST ITEMS ===")
        items = db.query(models.ShoppingListItem).all()
        for item in items:
            print(f"  ID: {item.id}, User: {item.user_id}, Recipe: {item.recipe_id}, Name: {item.ingredient_name}, Purchased: {item.is_purchased}")
        
        # Meal plans
        print("\n=== MEAL PLANS ===")
        plans = db.query(models.MealPlan).all()
        for plan in plans:
            print(f"  ID: {plan.id}, User: {plan.owner_id}, Recipe: {plan.recipe_id}, Date: {plan.date}, Type: {plan.meal_type}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()

