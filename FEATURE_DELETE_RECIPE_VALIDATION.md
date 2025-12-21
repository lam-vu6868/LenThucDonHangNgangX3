# ✅ Cải tiến: Thông báo rõ ràng khi xóa món ăn có tham chiếu

## 🎯 Vấn đề đã giải quyết

Trước đây khi admin xóa món ăn đang được tham chiếu (có trong lịch ăn hoặc có đánh giá), hệ thống chỉ báo lỗi chung chung không rõ ràng.

## ✨ Cải tiến mới

### 1. **Backend - Kiểm tra tham chiếu trước khi xóa**

**File: `be/app/routers/admin.py`** (Admin delete recipe)

```python
# Kiểm tra tham chiếu
meal_plans_count = db.query(models.MealPlan).filter(models.MealPlan.recipe_id == recipe_id).count()
ratings_count = db.query(models.Rating).filter(models.Rating.recipe_id == recipe_id).count()

if meal_plans_count > 0 or ratings_count > 0:
    references = []
    if meal_plans_count > 0:
        references.append(f"{meal_plans_count} lịch ăn")
    if ratings_count > 0:
        references.append(f"{ratings_count} đánh giá")

    raise HTTPException(
        status_code=400,
        detail=f"Không thể xóa món ăn này vì đang được tham chiếu bởi {' và '.join(references)}. Vui lòng xóa các tham chiếu trước."
    )
```

**File: `be/app/routers/recipes.py`** (User delete own recipe)

- Tương tự, kiểm tra tham chiếu trước khi xóa
- Thông báo rõ ràng số lượng lịch ăn và đánh giá đang tham chiếu

### 2. **Frontend - Thông báo UX tốt hơn**

**File: `fe/admin.html`**

```javascript
async function deleteRecipe(recipeId) {
  // Confirm dialog cảnh báo trước
  if (
    !confirm(
      "⚠️ Bạn có chắc muốn xóa món ăn này?\n\nLưu ý: Không thể xóa nếu món ăn đang được sử dụng trong lịch ăn hoặc có đánh giá."
    )
  )
    return;

  try {
    await apiDeleteRecipeAdmin(recipeId);
    showToast("✅ Đã xóa món ăn thành công!", "success");
    await loadRecipes();
    await loadStats();
  } catch (error) {
    const errorMsg = error.message || "Không thể xóa món ăn";

    // Nếu là lỗi tham chiếu, hiển thị lâu hơn (8s)
    if (
      errorMsg.includes("tham chiếu") ||
      errorMsg.includes("lịch ăn") ||
      errorMsg.includes("đánh giá")
    ) {
      showToast("❌ " + errorMsg, "error", 8000);
    } else {
      showToast("❌ Lỗi xóa món ăn: " + errorMsg, "error");
    }
  }
}
```

### 3. **Utils - Cải thiện showToast**

**File: `fe/js/utils.js`**

```javascript
function showToast(message, type = "info", timeout = null) {
  // Timeout tùy chọn: nếu có thì dùng, không thì tự động tính
  const displayTime =
    timeout || Math.max(3000, Math.min(10000, message.length * 50));
  // ...
}
```

## 📋 Các trường hợp thông báo

### ✅ Trường hợp 1: Xóa thành công

```
✅ Đã xóa món ăn 'Cơm gà Hải Nam' thành công
```

### ❌ Trường hợp 2: Có tham chiếu lịch ăn

```
❌ Không thể xóa món ăn này vì đang được tham chiếu bởi 5 lịch ăn.
Vui lòng xóa các tham chiếu trước.
```

_Thông báo hiển thị trong 8 giây_

### ❌ Trường hợp 3: Có cả lịch ăn và đánh giá

```
❌ Không thể xóa món ăn này vì đang được tham chiếu bởi 3 lịch ăn và 7 đánh giá.
Vui lòng xóa các tham chiếu trước.
```

_Thông báo hiển thị trong 8 giây_

### ❌ Trường hợp 4: Lỗi database khác

```
❌ Lỗi xóa món ăn: Không thể xóa món ăn này vì đang được tham chiếu bởi dữ liệu khác trong hệ thống.
```

_Fallback message nếu IntegrityError_

## 🧪 Test cases

1. **Test xóa món ăn không có tham chiếu** → ✅ Xóa thành công
2. **Test xóa món ăn có trong lịch ăn** → ❌ Thông báo rõ "đang tham chiếu bởi X lịch ăn"
3. **Test xóa món ăn có đánh giá** → ❌ Thông báo rõ "đang tham chiếu bởi X đánh giá"
4. **Test xóa món ăn có cả 2** → ❌ Thông báo rõ "đang tham chiếu bởi X lịch ăn và Y đánh giá"

## 🚀 Cách sử dụng

1. Restart backend server:

   ```bash
   cd be
   python main.py
   ```

2. Vào trang Admin → Recipes
3. Thử xóa một món ăn đang có trong lịch ăn
4. Xem thông báo chi tiết!

## 📝 Files đã sửa

- ✅ `be/app/routers/admin.py` - Thêm validation cho admin
- ✅ `be/app/routers/recipes.py` - Thêm validation cho user
- ✅ `fe/admin.html` - Cải thiện UX thông báo
- ✅ `fe/js/utils.js` - Thêm timeout parameter cho showToast
