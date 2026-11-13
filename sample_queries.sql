-- =====================================================================
-- ShopQL Demo & Reference Script
-- Contains queries demonstrating searching, filtering, sorting,
-- logical operators, relational operators, and inventory management.
-- =====================================================================

-- 1. Prompt Example 1: Search and category filter
FIND PRODUCTS
WHERE PRICE < 2000
AND CATEGORY = "ELECTRONICS";

-- 2. Prompt Example 2: High rating filter and price sorting
SHOW PRODUCTS
WHERE RATING >= 4.5
ORDER BY PRICE ASC;

-- 3. Prompt Example 3: Adding a new product
ADD PRODUCT "Laptop" PRICE 55000;

-- 4. Adding a product with full attributes
ADD PRODUCT "Mechanical Numpad" PRICE 49.99 CATEGORY "ACCESSORIES" STOCK 30 RATING 4.8;

-- 5. Substring matching with CONTAINS
FIND PRODUCTS WHERE NAME CONTAINS "Pro";

-- 6. SQL-style wildcard pattern matching with LIKE
FIND PRODUCTS WHERE CATEGORY LIKE "ELEC%";

-- 7. Range filtering with BETWEEN
FIND PRODUCTS WHERE PRICE BETWEEN 50 AND 300;

-- 8. Set membership with IN
FIND PRODUCTS WHERE CATEGORY IN ("BOOKS", "ACCESSORIES") ORDER BY RATING DESC;

-- 9. Inventory Restock
RESTOCK PRODUCT "Laptop" QUANTITY 20;

-- 10. Customer Purchase
BUY PRODUCT "Laptop" QUANTITY 3;

-- 11. Complex Boolean Logic with parentheses
FIND PRODUCTS 
WHERE (CATEGORY = "ELECTRONICS" OR CATEGORY = "ACCESSORIES")
AND (PRICE < 500 AND STOCK > 10)
ORDER BY RATING DESC
LIMIT 5;

-- 12. Product Count
COUNT PRODUCTS WHERE STOCK > 0;

-- 13. Updating a product
UPDATE PRODUCT "Clean Code" SET PRICE = 32.00, STOCK = 85;

-- 14. Deleting out-of-stock items
DELETE PRODUCTS WHERE STOCK <= 0;

-- 15. Inspecting Schema
DESCRIBE PRODUCTS;

