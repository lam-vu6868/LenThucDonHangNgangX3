-- Lệnh SQL kiểm tra database có dữ liệu chưa

-- 1. Liệt kê tất cả các bảng
\dt

-- 2. Đếm số dòng trong mỗi bảng
SELECT 'users' as table_name, COUNT(*) as so_dong FROM users
UNION ALL
SELECT 'recipes', COUNT(*) FROM recipes
UNION ALL
SELECT 'ingredients', COUNT(*) FROM ingredients
UNION ALL
SELECT 'meal_plans', COUNT(*) FROM meal_plans
UNION ALL
SELECT 'ratings', COUNT(*) FROM ratings
ORDER BY so_dong DESC;

-- 3. Tổng số bản ghi
SELECT 
    (SELECT COUNT(*) FROM users) +
    (SELECT COUNT(*) FROM recipes) +
    (SELECT COUNT(*) FROM ingredients) +
    (SELECT COUNT(*) FROM meal_plans) +
    (SELECT COUNT(*) FROM ratings) as tong_ban_ghi;

