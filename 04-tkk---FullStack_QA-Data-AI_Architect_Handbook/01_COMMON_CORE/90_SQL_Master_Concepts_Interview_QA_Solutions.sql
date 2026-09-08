-- =====================================================================
-- FILE: 90_SQL_Master_Concepts_Interview_QA_Solutions.sql
-- PURPOSE: Comprehensive SQL practice for QA Engineers
--          Covers DWH, ETL, Data Testing, Analytics, Performance
-- AUDIENCE: Senior QA Engineers (7+ years) testing data platforms
-- STRUCTURE: 120+ Interview Questions with Solutions
-- =====================================================================

-- =====================================================================
-- SECTION 1: BASIC SQL FUNDAMENTALS (Questions 1-20)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1: Retrieve all customers from the customers table
-- Concept: Basic SELECT, testing table accessibility
-- ---------------------------------------------------------------------
SELECT * 
FROM customers;

-- QA Validation: Verify row count matches expected (e.g., 1000 customers)
-- SELECT COUNT(*) FROM customers; -- Expected: 1000


-- ---------------------------------------------------------------------
-- Q2: Find all orders placed in January 2024
-- Concept: WHERE clause with date filtering
-- ---------------------------------------------------------------------
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE order_date >= '2024-01-01' 
  AND order_date < '2024-02-01';

-- QA Validation: 
-- 1. No orders outside January 2024
-- 2. Min date >= 2024-01-01, Max date < 2024-02-01
-- SELECT MIN(order_date), MAX(order_date) FROM orders WHERE ...;


-- ---------------------------------------------------------------------
-- Q3: Count total number of products in each category
-- Concept: GROUP BY, COUNT aggregation
-- ---------------------------------------------------------------------
SELECT 
    category,
    COUNT(*) as product_count
FROM products
GROUP BY category
ORDER BY product_count DESC;

-- QA Validation:
-- 1. Sum of product_count = total products
-- 2. No NULL categories (or separate NULL group)
-- SELECT SUM(product_count) FROM (above query);


-- ---------------------------------------------------------------------
-- Q4: Find customers with more than 5 orders
-- Concept: GROUP BY, HAVING clause
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    COUNT(*) as order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 5
ORDER BY order_count DESC;

-- QA Validation: Verify all returned customers have >5 orders
-- Manual spot check: SELECT COUNT(*) FROM orders WHERE customer_id = <sample>;


-- ---------------------------------------------------------------------
-- Q5: List products sorted by price (highest to lowest)
-- Concept: ORDER BY with DESC
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    price
FROM products
ORDER BY price DESC;

-- QA Validation: First row has highest price, last row has lowest
-- SELECT MAX(price), MIN(price) FROM products;


-- ---------------------------------------------------------------------
-- Q6: Find customers whose email contains 'gmail.com'
-- Concept: LIKE pattern matching
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    customer_name,
    email
FROM customers
WHERE email LIKE '%gmail.com';

-- QA Validation: All returned emails end with 'gmail.com'
-- Anti-test: WHERE email LIKE '%yahoo.com' should return different set


-- ---------------------------------------------------------------------
-- Q7: Calculate total revenue from all orders
-- Concept: SUM aggregation
-- ---------------------------------------------------------------------
SELECT 
    SUM(total_amount) as total_revenue
FROM orders;

-- QA Validation: 
-- 1. Compare to sum of individual orders (spot check)
-- 2. Verify no negative amounts included (data quality)
-- SELECT COUNT(*) FROM orders WHERE total_amount < 0; -- Should be 0


-- ---------------------------------------------------------------------
-- Q8: Find average order value per customer
-- Concept: GROUP BY with AVG
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    AVG(total_amount) as avg_order_value,
    COUNT(*) as order_count
FROM orders
GROUP BY customer_id
ORDER BY avg_order_value DESC;

-- QA Validation: 
-- Manually calculate avg for sample customer:
-- SELECT SUM(total_amount)/COUNT(*) FROM orders WHERE customer_id = <sample>;


-- ---------------------------------------------------------------------
-- Q9: Retrieve top 10 most expensive products
-- Concept: ORDER BY with LIMIT/TOP
-- ---------------------------------------------------------------------
-- PostgreSQL/MySQL syntax
SELECT 
    product_id,
    product_name,
    price
FROM products
ORDER BY price DESC
LIMIT 10;

-- SQL Server syntax
-- SELECT TOP 10 product_id, product_name, price FROM products ORDER BY price DESC;

-- QA Validation: 11th product should have price <= 10th product's price


-- ---------------------------------------------------------------------
-- Q10: Find products with price between $50 and $100
-- Concept: BETWEEN operator
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    price
FROM products
WHERE price BETWEEN 50 AND 100
ORDER BY price;

-- QA Validation: All returned prices >= 50 AND <= 100
-- SELECT MIN(price), MAX(price) FROM products WHERE price BETWEEN 50 AND 100;


-- ---------------------------------------------------------------------
-- Q11: Get distinct customer cities
-- Concept: DISTINCT keyword
-- ---------------------------------------------------------------------
SELECT DISTINCT city
FROM customers
ORDER BY city;

-- QA Validation: No duplicate cities in result
-- Count should be <= total customers
-- SELECT COUNT(DISTINCT city) FROM customers;


-- ---------------------------------------------------------------------
-- Q12: Find orders placed on weekends
-- Concept: Date functions (DAYOFWEEK, DATEPART)
-- ---------------------------------------------------------------------
-- PostgreSQL
SELECT 
    order_id,
    customer_id,
    order_date,
    EXTRACT(DOW FROM order_date) as day_of_week  -- 0=Sunday, 6=Saturday
FROM orders
WHERE EXTRACT(DOW FROM order_date) IN (0, 6);

-- SQL Server
-- SELECT order_id, customer_id, order_date, DATEPART(WEEKDAY, order_date) as day_of_week
-- FROM orders WHERE DATEPART(WEEKDAY, order_date) IN (1, 7); -- 1=Sunday, 7=Saturday

-- QA Validation: All returned dates are Saturday or Sunday


-- ---------------------------------------------------------------------
-- Q13: Calculate age of customers
-- Concept: Date arithmetic, DATEDIFF
-- ---------------------------------------------------------------------
-- PostgreSQL
SELECT 
    customer_id,
    customer_name,
    date_of_birth,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) as age
FROM customers;

-- SQL Server
-- SELECT customer_id, customer_name, date_of_birth,
--        DATEDIFF(YEAR, date_of_birth, GETDATE()) as age
-- FROM customers;

-- QA Validation: Age should be between 18-120 (business rule)
-- SELECT COUNT(*) FROM customers WHERE age < 18 OR age > 120; -- Should be 0


-- ---------------------------------------------------------------------
-- Q14: Concatenate first and last name
-- Concept: String concatenation (CONCAT, ||)
-- ---------------------------------------------------------------------
-- PostgreSQL/MySQL
SELECT 
    customer_id,
    first_name || ' ' || last_name as full_name
FROM customers;

-- Or using CONCAT
-- SELECT customer_id, CONCAT(first_name, ' ', last_name) as full_name FROM customers;

-- SQL Server
-- SELECT customer_id, first_name + ' ' + last_name as full_name FROM customers;

-- QA Validation: Full name contains space, both parts present


-- ---------------------------------------------------------------------
-- Q15: Find orders with NULL shipping address
-- Concept: IS NULL
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    customer_id,
    order_date,
    shipping_address
FROM orders
WHERE shipping_address IS NULL;

-- QA Validation: All returned rows have NULL shipping_address
-- Business validation: Should these orders be allowed? (data quality issue)


-- ---------------------------------------------------------------------
-- Q16: Replace NULL values with default text
-- Concept: COALESCE, IFNULL
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    customer_id,
    COALESCE(shipping_address, 'Address Not Provided') as shipping_address
FROM orders;

-- SQL Server: Use ISNULL(shipping_address, 'Address Not Provided')
-- MySQL: Use IFNULL(shipping_address, 'Address Not Provided')

-- QA Validation: No NULL values in result


-- ---------------------------------------------------------------------
-- Q17: Extract year and month from order date
-- Concept: Date extraction functions
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    order_date,
    EXTRACT(YEAR FROM order_date) as order_year,
    EXTRACT(MONTH FROM order_date) as order_month
FROM orders;

-- SQL Server
-- SELECT order_id, order_date, YEAR(order_date) as order_year, MONTH(order_date) as order_month
-- FROM orders;

-- QA Validation: Year in range (2020-2025), Month in range (1-12)


-- ---------------------------------------------------------------------
-- Q18: Round prices to 2 decimal places
-- Concept: ROUND function
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    price,
    ROUND(price, 2) as rounded_price
FROM products;

-- QA Validation: Rounded prices have max 2 decimal places


-- ---------------------------------------------------------------------
-- Q19: Convert customer names to uppercase
-- Concept: UPPER function
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    customer_name,
    UPPER(customer_name) as name_uppercase
FROM customers;

-- QA Validation: All characters in uppercase (no lowercase letters)


-- ---------------------------------------------------------------------
-- Q20: Find length of product descriptions
-- Concept: LENGTH/LEN function
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    description,
    LENGTH(description) as description_length
FROM products
ORDER BY description_length DESC;

-- SQL Server: Use LEN(description)

-- QA Validation: 
-- 1. Longest description within expected range (e.g., <1000 chars)
-- 2. No descriptions with 0 length (unless allowed)


-- =====================================================================
-- SECTION 2: INTERMEDIATE SQL (Questions 21-60)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q21: INNER JOIN - Find all orders with customer details
-- Concept: Basic INNER JOIN
-- ---------------------------------------------------------------------
SELECT 
    o.order_id,
    o.order_date,
    o.total_amount,
    c.customer_name,
    c.email
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC;

-- QA Validation:
-- 1. Row count <= MIN(orders count, customers count)
-- 2. All order_ids from orders table present (if every order has customer)
-- 3. No NULL customer_name (INNER JOIN excludes orphans)


-- ---------------------------------------------------------------------
-- Q22: LEFT JOIN - Find all customers including those without orders
-- Concept: LEFT OUTER JOIN
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as order_count,
    COALESCE(SUM(o.total_amount), 0) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- QA Validation:
-- 1. Row count = total customers
-- 2. Customers with order_count = 0 exist (those without orders)
-- 3. Sum of order_count = total orders


-- ---------------------------------------------------------------------
-- Q23: Find customers who have never placed an order
-- Concept: LEFT JOIN with NULL check
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- QA Validation:
-- Anti-test: These customer_ids should NOT appear in orders table
-- SELECT COUNT(*) FROM orders WHERE customer_id IN (result customer_ids); -- Should be 0


-- ---------------------------------------------------------------------
-- Q24: Self JOIN - Find customers from the same city
-- Concept: Self JOIN
-- ---------------------------------------------------------------------
SELECT 
    c1.customer_name as customer1,
    c2.customer_name as customer2,
    c1.city
FROM customers c1
INNER JOIN customers c2 
    ON c1.city = c2.city 
    AND c1.customer_id < c2.customer_id  -- Avoid duplicates and self-pairs
ORDER BY c1.city, c1.customer_name;

-- QA Validation:
-- 1. No customer paired with themselves
-- 2. Each pair appears only once (not both A-B and B-A)


-- ---------------------------------------------------------------------
-- Q25: Multiple JOINs - Orders with customer and product details
-- Concept: Joining 3+ tables
-- ---------------------------------------------------------------------
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) as line_total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_date DESC, o.order_id;

-- QA Validation:
-- 1. Sum of line_total per order = order.total_amount (reconciliation)
-- 2. All order_ids in result exist in orders table


-- ---------------------------------------------------------------------
-- Q26: Subquery in WHERE - Find customers with above-average spending
-- Concept: Scalar subquery
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.total_amount) as total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING SUM(o.total_amount) > (
    SELECT AVG(customer_total) 
    FROM (
        SELECT SUM(total_amount) as customer_total
        FROM orders
        GROUP BY customer_id
    ) as customer_totals
)
ORDER BY total_spent DESC;

-- QA Validation:
-- 1. All returned customers have total_spent > overall average
-- 2. Calculate avg manually and compare


-- ---------------------------------------------------------------------
-- Q27: Subquery in SELECT - Show product with its category count
-- Concept: Correlated subquery
-- ---------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    (
        SELECT COUNT(*) 
        FROM products p2 
        WHERE p2.category = p.category
    ) as products_in_category
FROM products p
ORDER BY products_in_category DESC, p.product_name;

-- QA Validation:
-- Sum all products should equal total products
-- Products in same category have same products_in_category value


-- ---------------------------------------------------------------------
-- Q28: EXISTS - Find categories with at least one product
-- Concept: EXISTS operator
-- ---------------------------------------------------------------------
SELECT DISTINCT category
FROM products p1
WHERE EXISTS (
    SELECT 1 
    FROM products p2 
    WHERE p2.category = p1.category 
      AND p2.price > 100
)
ORDER BY category;

-- QA Validation:
-- All returned categories have at least one product with price > 100


-- ---------------------------------------------------------------------
-- Q29: NOT EXISTS - Find products never ordered
-- Concept: NOT EXISTS
-- ---------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.price
FROM products p
WHERE NOT EXISTS (
    SELECT 1 
    FROM order_items oi 
    WHERE oi.product_id = p.product_id
)
ORDER BY p.product_name;

-- QA Validation:
-- These product_ids should NOT appear in order_items
-- SELECT COUNT(*) FROM order_items WHERE product_id IN (result); -- Should be 0


-- ---------------------------------------------------------------------
-- Q30: UNION - Combine active and inactive customers
-- Concept: UNION (removes duplicates), UNION ALL (keeps duplicates)
-- ---------------------------------------------------------------------
SELECT customer_id, customer_name, 'Active' as status
FROM customers
WHERE last_order_date >= CURRENT_DATE - INTERVAL '90 days'

UNION

SELECT customer_id, customer_name, 'Inactive' as status
FROM customers
WHERE last_order_date < CURRENT_DATE - INTERVAL '90 days'
    OR last_order_date IS NULL

ORDER BY status, customer_name;

-- QA Validation:
-- 1. Total rows = total customers (each customer in one category)
-- 2. No customer appears twice (UNION removes duplicates)


-- ---------------------------------------------------------------------
-- Q31: CASE statement - Categorize customers by spending
-- Concept: CASE WHEN THEN
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.total_amount) as total_spent,
    CASE 
        WHEN SUM(o.total_amount) >= 10000 THEN 'VIP'
        WHEN SUM(o.total_amount) >= 5000 THEN 'Gold'
        WHEN SUM(o.total_amount) >= 1000 THEN 'Silver'
        ELSE 'Bronze'
    END as customer_tier
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- QA Validation:
-- 1. All customers with total_spent >= 10000 are VIP
-- 2. Customers with total_spent = 0 are Bronze
-- 3. Tier logic matches business rules


-- ---------------------------------------------------------------------
-- Q32: RANK() - Rank products by price within category
-- Concept: Window function RANK()
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    category,
    price,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) as price_rank
FROM products
ORDER BY category, price_rank;

-- QA Validation:
-- 1. Within each category, highest price has rank = 1
-- 2. Tied prices have same rank (e.g., two products at $100 both rank 1)


-- ---------------------------------------------------------------------
-- Q33: ROW_NUMBER() - Assign unique row numbers to orders
-- Concept: Window function ROW_NUMBER()
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    order_id,
    order_date,
    total_amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as order_sequence
FROM orders
ORDER BY customer_id, order_sequence;

-- QA Validation:
-- 1. Each customer's first order has order_sequence = 1
-- 2. No duplicate order_sequence within same customer


-- ---------------------------------------------------------------------
-- Q34: LAG() - Compare each order with previous order
-- Concept: Window function LAG()
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    order_id,
    order_date,
    total_amount,
    LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) as previous_order_amount,
    total_amount - LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) as amount_change
FROM orders
ORDER BY customer_id, order_date;

-- QA Validation:
-- 1. First order per customer has NULL previous_order_amount
-- 2. amount_change = total_amount - previous_order_amount


-- ---------------------------------------------------------------------
-- Q35: LEAD() - Show next order date for each customer
-- Concept: Window function LEAD()
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    order_id,
    order_date,
    LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as next_order_date,
    LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) - order_date as days_to_next_order
FROM orders
ORDER BY customer_id, order_date;

-- QA Validation:
-- 1. Last order per customer has NULL next_order_date
-- 2. days_to_next_order is positive (next order is after current)


-- ---------------------------------------------------------------------
-- Q36: Running total - Calculate cumulative revenue
-- Concept: Window function SUM() OVER
-- ---------------------------------------------------------------------
SELECT 
    order_date,
    order_id,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date, order_id) as running_total
FROM orders
ORDER BY order_date, order_id;

-- QA Validation:
-- 1. Last row's running_total = total revenue (sum of all orders)
-- 2. Running total always increases (or stays same if amount = 0)


-- ---------------------------------------------------------------------
-- Q37: Moving average - 7-day moving average of daily sales
-- Concept: Window function with ROWS BETWEEN
-- ---------------------------------------------------------------------
SELECT 
    order_date::DATE as date,
    SUM(total_amount) as daily_revenue,
    AVG(SUM(total_amount)) OVER (
        ORDER BY order_date::DATE 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM orders
GROUP BY order_date::DATE
ORDER BY order_date::DATE;

-- QA Validation:
-- 1. First 6 days have moving average calculated on fewer days
-- 2. After day 7, moving average uses exactly 7 days


-- ---------------------------------------------------------------------
-- Q38: NTILE() - Divide customers into quartiles by spending
-- Concept: Window function NTILE()
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    customer_name,
    total_spent,
    NTILE(4) OVER (ORDER BY total_spent DESC) as spending_quartile
FROM (
    SELECT 
        c.customer_id,
        c.customer_name,
        COALESCE(SUM(o.total_amount), 0) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
) customer_spending
ORDER BY spending_quartile, total_spent DESC;

-- QA Validation:
-- 1. Quartile 1 has highest spenders
-- 2. Approximately 25% of customers in each quartile


-- ---------------------------------------------------------------------
-- Q39: CTE (Common Table Expression) - Calculate monthly revenue
-- Concept: WITH clause
-- ---------------------------------------------------------------------
WITH monthly_revenue AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(total_amount) as revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
)
SELECT 
    year,
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY year, month) as previous_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY year, month) as revenue_change
FROM monthly_revenue
ORDER BY year, month;

-- QA Validation:
-- 1. Sum of all monthly revenues = total revenue
-- 2. First month has NULL previous_month_revenue


-- ---------------------------------------------------------------------
-- Q40: Recursive CTE - Generate date series
-- Concept: Recursive CTE
-- ---------------------------------------------------------------------
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' as date
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < DATE '2024-01-31'
)
SELECT 
    ds.date,
    COALESCE(SUM(o.total_amount), 0) as daily_revenue
FROM date_series ds
LEFT JOIN orders o ON ds.date = o.order_date::DATE
GROUP BY ds.date
ORDER BY ds.date;

-- QA Validation:
-- 1. All dates in January 2024 present (31 rows)
-- 2. Days with no orders show revenue = 0


-- ---------------------------------------------------------------------
-- Q41: PIVOT simulation - Show sales by category per month
-- Concept: CASE + GROUP BY to simulate PIVOT
-- ---------------------------------------------------------------------
SELECT 
    EXTRACT(MONTH FROM o.order_date) as month,
    SUM(CASE WHEN p.category = 'Electronics' THEN oi.quantity * oi.unit_price ELSE 0 END) as electronics_sales,
    SUM(CASE WHEN p.category = 'Clothing' THEN oi.quantity * oi.unit_price ELSE 0 END) as clothing_sales,
    SUM(CASE WHEN p.category = 'Home' THEN oi.quantity * oi.unit_price ELSE 0 END) as home_sales,
    SUM(oi.quantity * oi.unit_price) as total_sales
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE EXTRACT(YEAR FROM o.order_date) = 2024
GROUP BY EXTRACT(MONTH FROM o.order_date)
ORDER BY month;

-- QA Validation:
-- 1. Sum of category sales = total_sales per month
-- 2. All months (1-12) present


-- ---------------------------------------------------------------------
-- Q42: Data quality check - Find duplicate customers
-- Concept: GROUP BY + HAVING for duplicate detection
-- ---------------------------------------------------------------------
SELECT 
    email,
    COUNT(*) as duplicate_count,
    STRING_AGG(customer_id::TEXT, ', ') as customer_ids
FROM customers
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- QA Validation:
-- Should be 0 rows (no duplicate emails allowed)
-- If rows exist, data quality issue


-- ---------------------------------------------------------------------
-- Q43: Data quality check - Find orders with invalid dates
-- Concept: WHERE clause for date validation
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    customer_id,
    order_date,
    ship_date
FROM orders
WHERE order_date > CURRENT_DATE  -- Future orders
   OR ship_date < order_date     -- Shipped before ordered
   OR order_date < DATE '2020-01-01';  -- Too old

-- QA Validation:
-- Should be 0 rows (all dates valid)
-- If rows exist, data quality issue


-- ---------------------------------------------------------------------
-- Q44: Data quality check - Find negative prices or quantities
-- Concept: WHERE clause for range validation
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    price
FROM products
WHERE price < 0
UNION ALL
SELECT 
    oi.order_id::TEXT as product_id,
    'Order Item' as product_name,
    oi.quantity::NUMERIC as price
FROM order_items oi
WHERE oi.quantity < 0;

-- QA Validation:
-- Should be 0 rows (no negative values)


-- ---------------------------------------------------------------------
-- Q45: Data reconciliation - Compare order totals
-- Concept: Reconciling aggregated vs detail data
-- ---------------------------------------------------------------------
SELECT 
    o.order_id,
    o.total_amount as order_total,
    SUM(oi.quantity * oi.unit_price) as calculated_total,
    o.total_amount - SUM(oi.quantity * oi.unit_price) as difference
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount
HAVING ABS(o.total_amount - SUM(oi.quantity * oi.unit_price)) > 0.01
ORDER BY ABS(difference) DESC;

-- QA Validation:
-- Should be 0 rows (all order totals match line items)
-- Tolerance of $0.01 for rounding


-- ---------------------------------------------------------------------
-- Q46: Performance optimization - Index effectiveness check
-- Concept: EXPLAIN ANALYZE
-- ---------------------------------------------------------------------
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC
LIMIT 100;

-- QA Validation:
-- 1. Check execution time (should be <100ms for 1M rows)
-- 2. Verify index usage on customer_id (no Seq Scan on large tables)
-- 3. Look for "Index Scan" or "Index Only Scan" in plan


-- ---------------------------------------------------------------------
-- Q47: Date dimension testing - Check for gaps in dates
-- Concept: Date continuity validation
-- ---------------------------------------------------------------------
WITH expected_dates AS (
    SELECT generate_series(
        DATE '2024-01-01',
        DATE '2024-12-31',
        INTERVAL '1 day'
    )::DATE as expected_date
)
SELECT 
    ed.expected_date as missing_date
FROM expected_dates ed
LEFT JOIN (
    SELECT DISTINCT order_date::DATE as actual_date 
    FROM orders 
    WHERE EXTRACT(YEAR FROM order_date) = 2024
) od ON ed.expected_date = od.actual_date
WHERE od.actual_date IS NULL
ORDER BY ed.expected_date;

-- QA Validation:
-- Lists all dates in 2024 with no orders (expected for weekends, holidays)


-- ---------------------------------------------------------------------
-- Q48: Slowly Changing Dimension Type 2 - Track historical changes
-- Concept: SCD Type 2 implementation
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    customer_name,
    email,
    address,
    valid_from,
    valid_to,
    is_current,
    CASE 
        WHEN is_current = TRUE THEN 'Current'
        ELSE 'Historical'
    END as record_status
FROM customer_history
WHERE customer_id = 12345
ORDER BY valid_from DESC;

-- QA Validation:
-- 1. Only one record with is_current = TRUE per customer
-- 2. valid_from < valid_to for historical records
-- 3. No overlapping date ranges for same customer


-- ---------------------------------------------------------------------
-- Q49: Fact table grain validation
-- Concept: Verify fact table at correct granularity
-- ---------------------------------------------------------------------
SELECT 
    order_date::DATE,
    customer_id,
    product_id,
    COUNT(*) as record_count
FROM fact_sales
GROUP BY order_date::DATE, customer_id, product_id
HAVING COUNT(*) > 1
ORDER BY record_count DESC;

-- QA Validation:
-- Should be 0 rows if grain is (date, customer, product)
-- If rows exist, duplicate fact records (data quality issue)


-- ---------------------------------------------------------------------
-- Q50: Surrogate key validation
-- Concept: Check for surrogate key uniqueness and gaps
-- ---------------------------------------------------------------------
WITH key_sequence AS (
    SELECT 
        customer_key,
        LAG(customer_key) OVER (ORDER BY customer_key) as previous_key,
        customer_key - LAG(customer_key) OVER (ORDER BY customer_key) as gap
    FROM dim_customer
)
SELECT 
    customer_key,
    previous_key,
    gap
FROM key_sequence
WHERE gap > 1  -- Find gaps in sequence
ORDER BY customer_key;

-- QA Validation:
-- Identifies missing surrogate keys (gap > 1)
-- Expected: small gaps are OK, large gaps indicate issue


-- ---------------------------------------------------------------------
-- Q51: Star schema validation - Dimension foreign keys
-- Concept: Referential integrity in star schema
-- ---------------------------------------------------------------------
SELECT 
    f.order_id,
    f.customer_key,
    f.product_key,
    f.date_key
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
LEFT JOIN dim_product p ON f.product_key = p.product_key
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE c.customer_key IS NULL
   OR p.product_key IS NULL
   OR d.date_key IS NULL;

-- QA Validation:
-- Should be 0 rows (all foreign keys have matching dimension records)
-- Orphan fact records indicate ETL issue


-- ---------------------------------------------------------------------
-- Q52: Bridge table validation - Many-to-many relationships
-- Concept: Testing bridge tables
-- ---------------------------------------------------------------------
SELECT 
    o.order_id,
    COUNT(DISTINCT oi.product_id) as product_count,
    COUNT(*) as line_item_count
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id
HAVING COUNT(DISTINCT oi.product_id) != COUNT(*)
ORDER BY o.order_id;

-- QA Validation:
-- Identifies orders with duplicate products (same product multiple times)
-- Expected: 0 rows if one product per line item


-- ---------------------------------------------------------------------
-- Q53: Aggregate table validation
-- Concept: Reconcile aggregate to detail
-- ---------------------------------------------------------------------
WITH detail_agg AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(total_amount) as revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
)
SELECT 
    a.year,
    a.month,
    a.revenue as aggregate_revenue,
    d.revenue as detail_revenue,
    a.revenue - d.revenue as difference
FROM monthly_revenue_aggregate a
FULL OUTER JOIN detail_agg d ON a.year = d.year AND a.month = d.month
WHERE ABS(COALESCE(a.revenue, 0) - COALESCE(d.revenue, 0)) > 0.01
ORDER BY a.year, a.month;

-- QA Validation:
-- Should be 0 rows (aggregate matches detail)
-- If rows exist, aggregate table out of sync


-- ---------------------------------------------------------------------
-- Q54: Time travel query - Query data as of specific date
-- Concept: Temporal queries (if DB supports versioning)
-- ---------------------------------------------------------------------
-- PostgreSQL with temporal tables
SELECT 
    customer_id,
    customer_name,
    address,
    sys_period
FROM customer_history
WHERE customer_id = 12345
  AND sys_period @> TIMESTAMP '2023-06-15 00:00:00'  -- Data as of June 15, 2023
ORDER BY sys_period;

-- QA Validation:
-- Returns customer record valid on 2023-06-15
-- Verify address matches historical records


-- ---------------------------------------------------------------------
-- Q55: Data lineage query - Trace data from source to target
-- Concept: Metadata querying
-- ---------------------------------------------------------------------
SELECT 
    source_table,
    source_column,
    transformation_logic,
    target_table,
    target_column,
    last_updated
FROM data_lineage_metadata
WHERE target_table = 'fact_sales'
  AND target_column = 'revenue'
ORDER BY transformation_sequence;

-- QA Validation:
-- Documents complete transformation path
-- Verify all transformations documented


-- ---------------------------------------------------------------------
-- Q56: ETL job monitoring - Find failed ETL runs
-- Concept: Operational metadata
-- ---------------------------------------------------------------------
SELECT 
    job_name,
    run_date,
    start_time,
    end_time,
    status,
    rows_processed,
    rows_failed,
    error_message
FROM etl_job_log
WHERE status = 'FAILED'
  AND run_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY run_date DESC, start_time DESC;

-- QA Validation:
-- Identify recent ETL failures
-- Verify error handling working


-- ---------------------------------------------------------------------
-- Q57: Incremental load validation - Check for missed records
-- Concept: Watermark validation
-- ---------------------------------------------------------------------
WITH source_max AS (
    SELECT MAX(updated_date) as max_source_date
    FROM source_system.orders
),
target_max AS (
    SELECT MAX(source_updated_date) as max_target_date
    FROM dwh.fact_sales
)
SELECT 
    s.max_source_date,
    t.max_target_date,
    s.max_source_date - t.max_target_date as time_lag
FROM source_max s, target_max t;

-- QA Validation:
-- time_lag should be < 1 hour (or SLA threshold)
-- Large lag indicates missed incremental loads


-- ---------------------------------------------------------------------
-- Q58: Delta detection - Find changed records
-- Concept: CDC (Change Data Capture) simulation
-- ---------------------------------------------------------------------
SELECT 
    s.customer_id,
    s.email as source_email,
    t.email as target_email,
    s.updated_date as source_updated,
    t.source_updated_date as target_updated
FROM source_system.customers s
INNER JOIN dwh.dim_customer t ON s.customer_id = t.customer_id
WHERE s.updated_date > t.source_updated_date
   OR s.email != t.email;

-- QA Validation:
-- Identifies records changed in source but not yet synced to target


-- ---------------------------------------------------------------------
-- Q59: Full load vs incremental reconciliation
-- Concept: Data integrity check
-- ---------------------------------------------------------------------
WITH full_count AS (
    SELECT COUNT(*) as count FROM source_system.orders
),
incremental_count AS (
    SELECT COUNT(*) as count FROM dwh.fact_sales
)
SELECT 
    f.count as source_count,
    i.count as target_count,
    f.count - i.count as missing_records
FROM full_count f, incremental_count i;

-- QA Validation:
-- missing_records should be 0 (or match expected exclusions)


-- ---------------------------------------------------------------------
-- Q60: Row count validation by partition
-- Concept: Partition-level reconciliation
-- ---------------------------------------------------------------------
SELECT 
    order_date::DATE as partition_date,
    COUNT(*) as source_count,
    (SELECT COUNT(*) FROM dwh.fact_sales WHERE order_date::DATE = o.order_date::DATE) as target_count,
    COUNT(*) - (SELECT COUNT(*) FROM dwh.fact_sales WHERE order_date::DATE = o.order_date::DATE) as difference
FROM source_system.orders o
GROUP BY order_date::DATE
HAVING COUNT(*) != (SELECT COUNT(*) FROM dwh.fact_sales WHERE order_date::DATE = o.order_date::DATE)
ORDER BY partition_date DESC;

-- QA Validation:
-- Should be 0 rows (all partitions match)


-- =====================================================================
-- SECTION 3: ADVANCED SQL (Questions 61-100)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q61: Window function - Identify best selling product per category
-- Concept: RANK() OVER PARTITION BY
-- ---------------------------------------------------------------------
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(oi.quantity) as total_quantity_sold,
        SUM(oi.quantity * oi.unit_price) as total_revenue
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT 
    product_id,
    product_name,
    category,
    total_quantity_sold,
    total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) as revenue_rank
FROM product_sales
QUALIFY revenue_rank = 1  -- PostgreSQL 15+ or use WHERE in outer query
ORDER BY category;

-- QA Validation:
-- One product per category (top seller)


-- ---------------------------------------------------------------------
-- Q62: Cohort analysis - Monthly retention by signup month
-- Concept: Complex window functions + pivoting
-- ---------------------------------------------------------------------
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', signup_date) as cohort_month,
        DATE_TRUNC('month', order_date) as order_month
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
)
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN order_month = cohort_month THEN customer_id END) as month_0,
    COUNT(DISTINCT CASE WHEN order_month = cohort_month + INTERVAL '1 month' THEN customer_id END) as month_1,
    COUNT(DISTINCT CASE WHEN order_month = cohort_month + INTERVAL '2 months' THEN customer_id END) as month_2,
    COUNT(DISTINCT CASE WHEN order_month = cohort_month + INTERVAL '3 months' THEN customer_id END) as month_3
FROM customer_cohorts
GROUP BY cohort_month
ORDER BY cohort_month;

-- QA Validation:
-- month_0 >= month_1 >= month_2 >= month_3 (retention decreases)


-- ---------------------------------------------------------------------
-- Q63: RFM (Recency, Frequency, Monetary) Analysis
-- Concept: Customer segmentation
-- ---------------------------------------------------------------------
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        CURRENT_DATE - MAX(o.order_date)::DATE as recency_days,
        COUNT(o.order_id) as frequency,
        SUM(o.total_amount) as monetary
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT 
    customer_id,
    customer_name,
    recency_days,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency_days ASC) as recency_score,
    NTILE(5) OVER (ORDER BY frequency DESC) as frequency_score,
    NTILE(5) OVER (ORDER BY monetary DESC) as monetary_score
FROM customer_rfm;

-- QA Validation:
-- Scores range 1-5, approximately 20% in each quintile


-- ---------------------------------------------------------------------
-- Q64: Funnel analysis - Conversion at each step
-- Concept: Multi-step conversion tracking
-- ---------------------------------------------------------------------
WITH funnel_steps AS (
    SELECT 
        COUNT(DISTINCT user_id) as step1_visitors,
        COUNT(DISTINCT CASE WHEN added_to_cart = TRUE THEN user_id END) as step2_add_cart,
        COUNT(DISTINCT CASE WHEN started_checkout = TRUE THEN user_id END) as step3_checkout,
        COUNT(DISTINCT CASE WHEN completed_order = TRUE THEN user_id END) as step4_purchase
    FROM user_sessions
    WHERE session_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    step1_visitors,
    step2_add_cart,
    step3_checkout,
    step4_purchase,
    ROUND(100.0 * step2_add_cart / step1_visitors, 2) as cart_conversion_rate,
    ROUND(100.0 * step3_checkout / step2_add_cart, 2) as checkout_conversion_rate,
    ROUND(100.0 * step4_purchase / step3_checkout, 2) as purchase_conversion_rate,
    ROUND(100.0 * step4_purchase / step1_visitors, 2) as overall_conversion_rate
FROM funnel_steps;

-- QA Validation:
-- step1 >= step2 >= step3 >= step4
-- Overall conversion = (step4 / step1) * 100


-- ---------------------------------------------------------------------
-- Q65: Sessionization - Group events into sessions
-- Concept: Session windowing with gaps
-- ---------------------------------------------------------------------
WITH event_gaps AS (
    SELECT 
        user_id,
        event_timestamp,
        event_type,
        LAG(event_timestamp) OVER (PARTITION BY user_id ORDER BY event_timestamp) as prev_event_time,
        event_timestamp - LAG(event_timestamp) OVER (PARTITION BY user_id ORDER BY event_timestamp) as time_gap
    FROM user_events
),
session_starts AS (
    SELECT 
        user_id,
        event_timestamp,
        event_type,
        CASE 
            WHEN time_gap > INTERVAL '30 minutes' OR time_gap IS NULL THEN 1
            ELSE 0
        END as is_session_start
    FROM event_gaps
),
sessions AS (
    SELECT 
        user_id,
        event_timestamp,
        event_type,
        SUM(is_session_start) OVER (PARTITION BY user_id ORDER BY event_timestamp) as session_id
    FROM session_starts
)
SELECT 
    user_id,
    session_id,
    MIN(event_timestamp) as session_start,
    MAX(event_timestamp) as session_end,
    COUNT(*) as event_count,
    MAX(event_timestamp) - MIN(event_timestamp) as session_duration
FROM sessions
GROUP BY user_id, session_id
ORDER BY user_id, session_id;

-- QA Validation:
-- Sessions with gap >30 min are separate


-- ---------------------------------------------------------------------
-- Q66: ABC analysis - Classify products by revenue contribution
-- Concept: Pareto principle (80/20 rule)
-- ---------------------------------------------------------------------
WITH product_revenue AS (
    SELECT 
        p.product_id,
        p.product_name,
        SUM(oi.quantity * oi.unit_price) as revenue
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name
),
revenue_ranked AS (
    SELECT 
        product_id,
        product_name,
        revenue,
        SUM(revenue) OVER () as total_revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) as cumulative_revenue,
        ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 2) as cumulative_pct
    FROM product_revenue
)
SELECT 
    product_id,
    product_name,
    revenue,
    cumulative_pct,
    CASE 
        WHEN cumulative_pct <= 80 THEN 'A'
        WHEN cumulative_pct <= 95 THEN 'B'
        ELSE 'C'
    END as abc_class
FROM revenue_ranked
ORDER BY revenue DESC;

-- QA Validation:
-- A products generate 80% revenue
-- A + B products generate 95% revenue


-- ---------------------------------------------------------------------
-- Q67: Year-over-year comparison
-- Concept: Self JOIN on time-shifted data
-- ---------------------------------------------------------------------
WITH monthly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(total_amount) as revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
)
SELECT 
    current_year.year,
    current_year.month,
    current_year.revenue as current_year_revenue,
    prior_year.revenue as prior_year_revenue,
    current_year.revenue - prior_year.revenue as yoy_change,
    ROUND(100.0 * (current_year.revenue - prior_year.revenue) / prior_year.revenue, 2) as yoy_growth_pct
FROM monthly_sales current_year
LEFT JOIN monthly_sales prior_year 
    ON current_year.month = prior_year.month 
    AND current_year.year = prior_year.year + 1
ORDER BY current_year.year, current_year.month;

-- QA Validation:
-- yoy_growth_pct = (current - prior) / prior * 100


-- ---------------------------------------------------------------------
-- Q68: Gap and island problem - Find consecutive date ranges
-- Concept: Advanced window functions
-- ---------------------------------------------------------------------
WITH date_groups AS (
    SELECT 
        customer_id,
        order_date::DATE as order_date,
        order_date::DATE - ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date::DATE)::INTEGER as group_id
    FROM orders
)
SELECT 
    customer_id,
    MIN(order_date) as range_start,
    MAX(order_date) as range_end,
    COUNT(*) as days_in_range
FROM date_groups
GROUP BY customer_id, group_id
HAVING COUNT(*) >= 3  -- Only ranges with 3+ consecutive days
ORDER BY customer_id, range_start;

-- QA Validation:
-- All dates in each range are consecutive (no gaps)


-- ---------------------------------------------------------------------
-- Q69: Percentile analysis - Find 90th percentile order value
-- Concept: PERCENTILE_CONT window function
-- ---------------------------------------------------------------------
SELECT 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_amount) as p50_median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_amount) as p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_amount) as p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_amount) as p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY total_amount) as p99
FROM orders;

-- QA Validation:
-- p50 < p75 < p90 < p95 < p99


-- ---------------------------------------------------------------------
-- Q70: Median calculation (alternative method)
-- Concept: MEDIAN or manual calculation
-- ---------------------------------------------------------------------
WITH ordered_values AS (
    SELECT 
        total_amount,
        ROW_NUMBER() OVER (ORDER BY total_amount) as row_num,
        COUNT(*) OVER () as total_rows
    FROM orders
)
SELECT 
    AVG(total_amount) as median_value
FROM ordered_values
WHERE row_num IN (
    (total_rows + 1) / 2,
    (total_rows + 2) / 2
);

-- QA Validation:
-- Result should match PERCENTILE_CONT(0.5)


-- ---------------------------------------------------------------------
-- Q71: Market basket analysis - Find frequently bought together
-- Concept: Self JOIN to find product pairs
-- ---------------------------------------------------------------------
WITH product_pairs AS (
    SELECT 
        oi1.product_id as product_a,
        oi2.product_id as product_b,
        COUNT(DISTINCT oi1.order_id) as times_bought_together
    FROM order_items oi1
    INNER JOIN order_items oi2 
        ON oi1.order_id = oi2.order_id 
        AND oi1.product_id < oi2.product_id  -- Avoid duplicates and self-pairs
    GROUP BY oi1.product_id, oi2.product_id
    HAVING COUNT(DISTINCT oi1.order_id) >= 10  -- At least 10 times together
)
SELECT 
    pp.product_a,
    p1.product_name as product_a_name,
    pp.product_b,
    p2.product_name as product_b_name,
    pp.times_bought_together,
    RANK() OVER (ORDER BY pp.times_bought_together DESC) as pair_rank
FROM product_pairs pp
INNER JOIN products p1 ON pp.product_a = p1.product_id
INNER JOIN products p2 ON pp.product_b = p2.product_id
ORDER BY pp.times_bought_together DESC
LIMIT 20;

-- QA Validation:
-- No product paired with itself (product_a != product_b)


-- ---------------------------------------------------------------------
-- Q72: Time zone conversion
-- Concept: AT TIME ZONE
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    order_date as utc_time,
    order_date AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York' as ny_time,
    order_date AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Tokyo' as tokyo_time,
    order_date AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/London' as london_time
FROM orders
WHERE order_id = 12345;

-- QA Validation:
-- Time differences match expected time zones


-- ---------------------------------------------------------------------
-- Q73: JSON data extraction
-- Concept: JSON operators (->>, ->, jsonb_array_elements)
-- ---------------------------------------------------------------------
-- Assuming orders table has a jsonb column called metadata
SELECT 
    order_id,
    metadata->>'shipping_method' as shipping_method,
    metadata->>'gift_message' as gift_message,
    (metadata->'discount'->>'amount')::NUMERIC as discount_amount
FROM orders
WHERE metadata->>'shipping_method' = 'express'
LIMIT 10;

-- QA Validation:
-- Extracted values match JSON structure


-- ---------------------------------------------------------------------
-- Q74: Array operations
-- Concept: ARRAY functions (array_agg, unnest)
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    customer_name,
    ARRAY_AGG(order_id ORDER BY order_date DESC) as order_ids,
    ARRAY_AGG(total_amount ORDER BY order_date DESC) as order_amounts
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_id, customer_name
LIMIT 10;

-- QA Validation:
-- Array length matches order count per customer


-- ---------------------------------------------------------------------
-- Q75: Unpivot data - Convert columns to rows
-- Concept: UNION ALL to unpivot
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    'Subtotal' as metric,
    subtotal as value
FROM order_summary
UNION ALL
SELECT 
    order_id,
    'Tax' as metric,
    tax as value
FROM order_summary
UNION ALL
SELECT 
    order_id,
    'Shipping' as metric,
    shipping as value
FROM order_summary
ORDER BY order_id, metric;

-- QA Validation:
-- 3 rows per order_id (one for each metric)


-- ---------------------------------------------------------------------
-- Q76: Dynamic SQL - Generate SQL from metadata
-- Concept: String manipulation to build queries
-- ---------------------------------------------------------------------
-- Example: Generate INSERT statements from table data
SELECT 
    'INSERT INTO products (product_id, product_name, price) VALUES (' ||
    product_id || ', ' ||
    '''' || product_name || '''' || ', ' ||
    price || ');' as insert_statement
FROM products
LIMIT 5;

-- QA Validation:
-- Generated SQL is valid (copy and execute)


-- ---------------------------------------------------------------------
-- Q77: Regular expression matching
-- Concept: REGEXP, SIMILAR TO, POSIX operators
-- ---------------------------------------------------------------------
-- Find emails with specific pattern
SELECT 
    customer_id,
    email
FROM customers
WHERE email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  -- Valid email pattern
  AND email !~ '@(gmail|yahoo|hotmail)\.com$';  -- Exclude common providers

-- QA Validation:
-- All returned emails match pattern


-- ---------------------------------------------------------------------
-- Q78: Full text search
-- Concept: to_tsvector, to_tsquery (PostgreSQL)
-- ---------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    description,
    ts_rank(to_tsvector('english', description), to_tsquery('english', 'wireless & bluetooth')) as relevance_score
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'wireless & bluetooth')
ORDER BY relevance_score DESC
LIMIT 10;

-- QA Validation:
-- All returned products mention 'wireless' AND 'bluetooth'


-- ---------------------------------------------------------------------
-- Q79: Hierarchical data - Recursive CTE for org chart
-- Concept: Recursive CTE with parent-child relationships
-- ---------------------------------------------------------------------
WITH RECURSIVE org_hierarchy AS (
    -- Anchor: Top-level employees (no manager)
    SELECT 
        employee_id,
        employee_name,
        manager_id,
        1 as level,
        employee_name::TEXT as path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: Employees reporting to previous level
    SELECT 
        e.employee_id,
        e.employee_name,
        e.manager_id,
        oh.level + 1,
        oh.path || ' > ' || e.employee_name
    FROM employees e
    INNER JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT 
    employee_id,
    REPEAT('  ', level - 1) || employee_name as indented_name,
    level,
    path
FROM org_hierarchy
ORDER BY path;

-- QA Validation:
-- 1. All employees appear exactly once
-- 2. CEO (no manager) at level 1
-- 3. No circular references (query should not hang)


-- ---------------------------------------------------------------------
-- Q80: Cartesian product simulation for test data
-- Concept: CROSS JOIN
-- ---------------------------------------------------------------------
-- Generate all combinations of categories and price ranges
SELECT 
    c.category,
    pr.price_range,
    COUNT(p.product_id) as product_count
FROM (SELECT DISTINCT category FROM products) c
CROSS JOIN (
    VALUES ('0-50'), ('51-100'), ('101-500'), ('500+')
) pr(price_range)
LEFT JOIN products p 
    ON p.category = c.category
    AND CASE pr.price_range
        WHEN '0-50' THEN p.price BETWEEN 0 AND 50
        WHEN '51-100' THEN p.price BETWEEN 51 AND 100
        WHEN '101-500' THEN p.price BETWEEN 101 AND 500
        WHEN '500+' THEN p.price > 500
    END
GROUP BY c.category, pr.price_range
ORDER BY c.category, pr.price_range;

-- QA Validation:
-- All category × price_range combinations present


-- ---------------------------------------------------------------------
-- Q81: Generate test data - Random data generation
-- Concept: generate_series, random()
-- ---------------------------------------------------------------------
INSERT INTO test_orders (order_id, customer_id, order_date, total_amount)
SELECT 
    gs.id as order_id,
    (random() * 1000)::INTEGER + 1 as customer_id,
    CURRENT_DATE - (random() * 365)::INTEGER as order_date,
    (random() * 1000)::NUMERIC(10,2) as total_amount
FROM generate_series(1, 10000) gs(id);

-- QA Validation:
-- 10,000 rows inserted
-- customer_id between 1-1000
-- order_date within last year


-- ---------------------------------------------------------------------
-- Q82: Conditional aggregation for KPI dashboard
-- Concept: FILTER clause or CASE in aggregation
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) as total_orders,
    COUNT(*) FILTER (WHERE status = 'Completed') as completed_orders,
    COUNT(*) FILTER (WHERE status = 'Cancelled') as cancelled_orders,
    SUM(total_amount) as total_revenue,
    SUM(total_amount) FILTER (WHERE status = 'Completed') as completed_revenue,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Completed') / COUNT(*), 2) as completion_rate
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days';

-- QA Validation:
-- total_orders = completed_orders + cancelled_orders + (other statuses)


-- ---------------------------------------------------------------------
-- Q83: Deduplication - Remove duplicates keeping latest
-- Concept: ROW_NUMBER() with DELETE
-- ---------------------------------------------------------------------
WITH duplicates AS (
    SELECT 
        customer_id,
        email,
        created_date,
        ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_date DESC) as rn
    FROM customers
)
DELETE FROM customers
WHERE customer_id IN (
    SELECT customer_id 
    FROM duplicates 
    WHERE rn > 1
);

-- QA Validation:
-- After delete, each email appears only once
-- SELECT email, COUNT(*) FROM customers GROUP BY email HAVING COUNT(*) > 1; -- Should be 0


-- ---------------------------------------------------------------------
-- Q84: Upsert (INSERT or UPDATE)
-- Concept: INSERT ... ON CONFLICT (PostgreSQL)
-- ---------------------------------------------------------------------
INSERT INTO customer_summary (customer_id, total_orders, total_spent, last_order_date)
SELECT 
    customer_id,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_spent,
    MAX(order_date) as last_order_date
FROM orders
GROUP BY customer_id
ON CONFLICT (customer_id) 
DO UPDATE SET
    total_orders = EXCLUDED.total_orders,
    total_spent = EXCLUDED.total_spent,
    last_order_date = EXCLUDED.last_order_date,
    updated_at = CURRENT_TIMESTAMP;

-- QA Validation:
-- Existing customers updated, new customers inserted


-- ---------------------------------------------------------------------
-- Q85: Bulk delete with logging
-- Concept: DELETE with RETURNING
-- ---------------------------------------------------------------------
WITH deleted_rows AS (
    DELETE FROM orders
    WHERE order_date < CURRENT_DATE - INTERVAL '7 years'  -- Data retention policy
    RETURNING order_id, customer_id, order_date, total_amount
)
INSERT INTO deleted_orders_archive (order_id, customer_id, order_date, total_amount, deleted_at)
SELECT 
    order_id,
    customer_id,
    order_date,
    total_amount,
    CURRENT_TIMESTAMP
FROM deleted_rows;

-- QA Validation:
-- Deleted rows archived before removal


-- ---------------------------------------------------------------------
-- Q86: Transaction isolation level testing
-- Concept: SET TRANSACTION ISOLATION LEVEL
-- ---------------------------------------------------------------------
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

SELECT balance FROM accounts WHERE account_id = 123 FOR UPDATE;
-- Simulate business logic: balance check, debit, credit
UPDATE accounts SET balance = balance - 100 WHERE account_id = 123;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 456;

COMMIT;

-- QA Validation:
-- Concurrent transactions don't cause lost updates or dirty reads


-- ---------------------------------------------------------------------
-- Q87: Deadlock simulation and detection
-- Concept: Lock ordering
-- ---------------------------------------------------------------------
-- Session 1:
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- Wait here...
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- Session 2 (concurrent):
BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE account_id = 2;
-- This will wait for Session 1 to release lock on account 2
UPDATE accounts SET balance = balance + 50 WHERE account_id = 1;
-- Deadlock detected, one transaction rolled back
COMMIT;

-- QA Validation:
-- Deadlock detection works, one transaction succeeds


-- ---------------------------------------------------------------------
-- Q88: Constraint validation - Check constraint
-- Concept: CHECK constraints
-- ---------------------------------------------------------------------
ALTER TABLE products
ADD CONSTRAINT price_positive CHECK (price > 0);

ALTER TABLE orders
ADD CONSTRAINT order_date_valid CHECK (order_date >= '2020-01-01' AND order_date <= CURRENT_DATE);

-- QA Validation:
-- INSERT INTO products (price) VALUES (-10); -- Should fail
-- INSERT INTO orders (order_date) VALUES ('2050-01-01'); -- Should fail


-- ---------------------------------------------------------------------
-- Q89: Foreign key cascade testing
-- Concept: ON DELETE CASCADE
-- ---------------------------------------------------------------------
-- When customer deleted, all orders deleted automatically
ALTER TABLE orders
ADD CONSTRAINT fk_customer 
FOREIGN KEY (customer_id) 
REFERENCES customers(customer_id) 
ON DELETE CASCADE;

-- QA Validation:
-- DELETE FROM customers WHERE customer_id = 123;
-- SELECT COUNT(*) FROM orders WHERE customer_id = 123; -- Should be 0


-- ---------------------------------------------------------------------
-- Q90: Trigger for audit logging
-- Concept: AFTER INSERT/UPDATE/DELETE trigger
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION audit_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO order_audit (order_id, action, changed_by, changed_at)
        VALUES (NEW.order_id, 'INSERT', current_user, CURRENT_TIMESTAMP);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO order_audit (order_id, action, old_value, new_value, changed_by, changed_at)
        VALUES (NEW.order_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), current_user, CURRENT_TIMESTAMP);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO order_audit (order_id, action, old_value, changed_by, changed_at)
        VALUES (OLD.order_id, 'DELETE', row_to_json(OLD), current_user, CURRENT_TIMESTAMP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION audit_order_changes();

-- QA Validation:
-- All order changes logged in order_audit table


-- ---------------------------------------------------------------------
-- Q91: Materialized view refresh
-- Concept: MATERIALIZED VIEW
-- ---------------------------------------------------------------------
CREATE MATERIALIZED VIEW monthly_revenue_mv AS
SELECT 
    EXTRACT(YEAR FROM order_date) as year,
    EXTRACT(MONTH FROM order_date) as month,
    SUM(total_amount) as revenue,
    COUNT(*) as order_count
FROM orders
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW monthly_revenue_mv;

-- QA Validation:
-- SELECT * FROM monthly_revenue_mv; -- Fast query (pre-aggregated)
-- Compare to base query for accuracy


-- ---------------------------------------------------------------------
-- Q92: Partitioning validation - Range partitioning
-- Concept: Table partitions
-- ---------------------------------------------------------------------
-- Create partitioned table (PostgreSQL 10+)
CREATE TABLE orders_partitioned (
    order_id BIGINT,
    customer_id INTEGER,
    order_date DATE,
    total_amount NUMERIC(10,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2023 PARTITION OF orders_partitioned
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- QA Validation:
-- INSERT data, verify routed to correct partition
-- SELECT tableoid::regclass, COUNT(*) FROM orders_partitioned GROUP BY tableoid;


-- ---------------------------------------------------------------------
-- Q93: Query plan analysis for optimization
-- Concept: EXPLAIN (ANALYZE, BUFFERS)
-- ---------------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    c.customer_name,
    SUM(o.total_amount) as total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 100;

-- QA Validation:
-- 1. Look for Index Scan (not Seq Scan on large tables)
-- 2. Check buffers hit ratio (high = good cache usage)
-- 3. Actual time vs estimated time (accurate statistics?)


-- ---------------------------------------------------------------------
-- Q94: Parallel query testing
-- Concept: Parallel execution plans
-- ---------------------------------------------------------------------
-- Enable parallel execution
SET max_parallel_workers_per_gather = 4;

EXPLAIN (ANALYZE)
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category;

-- QA Validation:
-- EXPLAIN shows "Parallel Seq Scan" or "Parallel Aggregate"
-- Execution time reduced with parallelism


-- ---------------------------------------------------------------------
-- Q95: Index usage validation
-- Concept: pg_stat_user_indexes (PostgreSQL)
-- ---------------------------------------------------------------------
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    CASE 
        WHEN idx_scan = 0 THEN 'UNUSED INDEX - Consider dropping'
        WHEN idx_scan < 100 THEN 'LOW USAGE'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan;

-- QA Validation:
-- Identify unused indexes (idx_scan = 0)


-- ---------------------------------------------------------------------
-- Q96: Table bloat detection
-- Concept: Dead tuples, autovacuum monitoring
-- ---------------------------------------------------------------------
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000  -- Significant dead tuples
ORDER BY dead_tuple_pct DESC;

-- QA Validation:
-- Tables with high dead_tuple_pct need VACUUM


-- ---------------------------------------------------------------------
-- Q97: Lock monitoring
-- Concept: pg_locks, blocking queries
-- ---------------------------------------------------------------------
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- QA Validation:
-- Identify blocking queries causing waits


-- ---------------------------------------------------------------------
-- Q98: Cache hit ratio monitoring
-- Concept: Buffer cache effectiveness
-- ---------------------------------------------------------------------
SELECT 
    SUM(heap_blks_read) as heap_read,
    SUM(heap_blks_hit) as heap_hit,
    ROUND(100.0 * SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit) + SUM(heap_blks_read), 0), 2) as cache_hit_ratio
FROM pg_statio_user_tables;

-- QA Validation:
-- Cache hit ratio should be >95% for optimal performance


-- ---------------------------------------------------------------------
-- Q99: Long-running query identification
-- Concept: pg_stat_activity
-- ---------------------------------------------------------------------
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    NOW() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND NOW() - query_start > INTERVAL '5 minutes'
ORDER BY duration DESC;

-- QA Validation:
-- Identify queries running >5 minutes (potential issues)


-- ---------------------------------------------------------------------
-- Q100: Database size monitoring
-- Concept: pg_database_size, pg_total_relation_size
-- ---------------------------------------------------------------------
SELECT 
    pg_database.datname as database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) as database_size,
    pg_database_size(pg_database.datname) as size_bytes
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Individual table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- QA Validation:
-- Track database growth over time


-- =====================================================================
-- SECTION 4: BONUS QUESTIONS (101-120)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q101: Data sampling for testing
-- Concept: TABLESAMPLE
-- ---------------------------------------------------------------------
SELECT *
FROM orders TABLESAMPLE BERNOULLI (10);  -- 10% random sample

-- QA Validation:
-- Sample size approximately 10% of total rows


-- ---------------------------------------------------------------------
-- Q102: Approximate counting for large tables
-- Concept: pg_class.reltuples
-- ---------------------------------------------------------------------
SELECT 
    relname as table_name,
    reltuples::BIGINT as estimated_row_count
FROM pg_class
WHERE relname = 'orders';

-- QA Validation:
-- Much faster than COUNT(*) for large tables
-- Accuracy within 5-10% of actual count


-- ---------------------------------------------------------------------
-- Q103: NULL handling in aggregations
-- Concept: NULLs in COUNT, SUM, AVG
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) as total_rows,
    COUNT(shipping_address) as rows_with_address,
    COUNT(*) - COUNT(shipping_address) as rows_without_address,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    AVG(COALESCE(discount, 0)) as avg_discount_including_null_as_zero
FROM orders;

-- QA Validation:
-- COUNT(*) includes NULLs, COUNT(column) excludes NULLs


-- ---------------------------------------------------------------------
-- Q104: Complex date arithmetic
-- Concept: INTERVAL, DATE_TRUNC
-- ---------------------------------------------------------------------
SELECT 
    order_id,
    order_date,
    DATE_TRUNC('month', order_date) as first_day_of_month,
    DATE_TRUNC('month', order_date) + INTERVAL '1 month - 1 day' as last_day_of_month,
    EXTRACT(DOW FROM order_date) as day_of_week,
    EXTRACT(QUARTER FROM order_date) as quarter,
    EXTRACT(WEEK FROM order_date) as week_number
FROM orders
LIMIT 10;

-- QA Validation:
-- First/last day of month calculations correct


-- ---------------------------------------------------------------------
-- Q105: String aggregation with delimiters
-- Concept: STRING_AGG, array_to_string
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    STRING_AGG(order_id::TEXT, ', ' ORDER BY order_date) as order_ids,
    STRING_AGG(order_date::TEXT, ' | ' ORDER BY order_date) as order_dates
FROM orders
WHERE customer_id IN (SELECT customer_id FROM customers LIMIT 10)
GROUP BY customer_id;

-- QA Validation:
-- Concatenated strings contain all order IDs


-- ---------------------------------------------------------------------
-- Q106: Conditional UPDATE
-- Concept: UPDATE with CASE
-- ---------------------------------------------------------------------
UPDATE products
SET price = CASE 
    WHEN category = 'Electronics' THEN price * 1.10  -- 10% increase
    WHEN category = 'Clothing' THEN price * 1.05     -- 5% increase
    ELSE price
END,
last_updated = CURRENT_TIMESTAMP
WHERE category IN ('Electronics', 'Clothing');

-- QA Validation:
-- Verify price changes match expected percentages


-- ---------------------------------------------------------------------
-- Q107: Batch UPDATE with JOIN
-- Concept: UPDATE FROM
-- ---------------------------------------------------------------------
UPDATE customer_summary cs
SET 
    total_orders = o.order_count,
    total_spent = o.total_amount,
    last_order_date = o.last_order
FROM (
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_amount,
        MAX(order_date) as last_order
    FROM orders
    GROUP BY customer_id
) o
WHERE cs.customer_id = o.customer_id;

-- QA Validation:
-- Verify summary table matches aggregated orders


-- ---------------------------------------------------------------------
-- Q108: Soft delete pattern
-- Concept: is_deleted flag instead of DELETE
-- ---------------------------------------------------------------------
-- Mark as deleted instead of physical delete
UPDATE customers
SET 
    is_deleted = TRUE,
    deleted_at = CURRENT_TIMESTAMP,
    deleted_by = current_user
WHERE customer_id = 12345;

-- Queries exclude soft-deleted records
SELECT * FROM customers WHERE is_deleted = FALSE;

-- QA Validation:
-- Deleted records still in table but excluded from queries


-- ---------------------------------------------------------------------
-- Q109: Version control for data changes
-- Concept: SCD Type 2 INSERT
-- ---------------------------------------------------------------------
-- Close current version
UPDATE customer_history
SET 
    valid_to = CURRENT_TIMESTAMP,
    is_current = FALSE
WHERE customer_id = 12345 AND is_current = TRUE;

-- Insert new version
INSERT INTO customer_history (customer_id, customer_name, email, address, valid_from, valid_to, is_current)
VALUES (12345, 'John Doe', 'new_email@example.com', '123 New St', CURRENT_TIMESTAMP, NULL, TRUE);

-- QA Validation:
-- Only one current version per customer


-- ---------------------------------------------------------------------
-- Q110: Performance comparison: IN vs EXISTS
-- Concept: Query optimization
-- ---------------------------------------------------------------------
-- Using IN (materialized subquery)
EXPLAIN ANALYZE
SELECT * FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE order_date >= '2024-01-01'
);

-- Using EXISTS (correlated subquery)
EXPLAIN ANALYZE
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
      AND o.order_date >= '2024-01-01'
);

-- QA Validation:
-- Compare execution times, EXISTS often faster for large datasets


-- ---------------------------------------------------------------------
-- Q111: LATERAL JOIN - Correlated subquery in FROM
-- Concept: LATERAL keyword
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    recent_orders.order_id,
    recent_orders.order_date,
    recent_orders.total_amount
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, order_date, total_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_date DESC
    LIMIT 3
) recent_orders
WHERE c.customer_id IN (1, 2, 3);

-- QA Validation:
-- Each customer shows max 3 most recent orders


-- ---------------------------------------------------------------------
-- Q112: Identify slow queries from pg_stat_statements
-- Concept: Query performance monitoring
-- ---------------------------------------------------------------------
-- Requires pg_stat_statements extension
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- QA Validation:
-- Identify queries to optimize (high mean_exec_time)


-- ---------------------------------------------------------------------
-- Q113: Bitwise operations
-- Concept: Bit manipulation
-- ---------------------------------------------------------------------
-- Using bitmask for permissions: 1=read, 2=write, 4=delete, 8=admin
SELECT 
    user_id,
    permissions,
    (permissions & 1) > 0 as has_read,
    (permissions & 2) > 0 as has_write,
    (permissions & 4) > 0 as has_delete,
    (permissions & 8) > 0 as is_admin
FROM user_permissions;

-- QA Validation:
-- Bitmask correctly decodes permissions


-- ---------------------------------------------------------------------
-- Q114: Generate calendar table
-- Concept: Utility table creation
-- ---------------------------------------------------------------------
CREATE TABLE dim_date AS
SELECT 
    date::DATE as date_key,
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(MONTH FROM date) as month,
    EXTRACT(DAY FROM date) as day,
    EXTRACT(DOW FROM date) as day_of_week,
    EXTRACT(QUARTER FROM date) as quarter,
    TO_CHAR(date, 'Month') as month_name,
    TO_CHAR(date, 'Day') as day_name,
    EXTRACT(WEEK FROM date) as week_number,
    CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend
FROM generate_series(
    DATE '2020-01-01',
    DATE '2030-12-31',
    INTERVAL '1 day'
) date;

-- QA Validation:
-- 3653 days (2020-2030), no missing dates


-- ---------------------------------------------------------------------
-- Q115: Compare two tables for differences
-- Concept: EXCEPT, data reconciliation
-- ---------------------------------------------------------------------
-- Records in source but not in target
SELECT * FROM source_table
EXCEPT
SELECT * FROM target_table;

-- Records in target but not in source
SELECT * FROM target_table
EXCEPT
SELECT * FROM source_table;

-- QA Validation:
-- Both queries should return 0 rows if tables identical


-- ---------------------------------------------------------------------
-- Q116: Generate sequence numbers with gaps filled
-- Concept: Anti-join with number series
-- ---------------------------------------------------------------------
WITH all_ids AS (
    SELECT generate_series(1, (SELECT MAX(order_id) FROM orders)) as id
)
SELECT ai.id as missing_order_id
FROM all_ids ai
LEFT JOIN orders o ON ai.id = o.order_id
WHERE o.order_id IS NULL
ORDER BY ai.id;

-- QA Validation:
-- Lists all gaps in order_id sequence


-- ---------------------------------------------------------------------
-- Q117: Complex HAVING with multiple aggregates
-- Concept: Multiple conditions in HAVING
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    COUNT(*) as order_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_order_value,
    MAX(order_date) as last_order_date
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 5
   AND SUM(total_amount) > 1000
   AND MAX(order_date) >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY total_spent DESC;

-- QA Validation:
-- All returned customers meet all 3 criteria


-- ---------------------------------------------------------------------
-- Q118: Cumulative distinct count
-- Concept: Running distinct count with window functions
-- ---------------------------------------------------------------------
WITH daily_customers AS (
    SELECT 
        order_date::DATE as date,
        customer_id
    FROM orders
    WHERE order_date >= '2024-01-01'
)
SELECT DISTINCT
    date,
    COUNT(DISTINCT customer_id) OVER (
        ORDER BY date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as cumulative_unique_customers
FROM daily_customers
ORDER BY date;

-- QA Validation:
-- Cumulative count always increases or stays same


-- ---------------------------------------------------------------------
-- Q119: Pivot with dynamic columns
-- Concept: crosstab (PostgreSQL tablefunc extension)
-- ---------------------------------------------------------------------
-- Requires CREATE EXTENSION tablefunc;
SELECT * FROM crosstab(
    'SELECT 
        category,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(quantity) as total_quantity
     FROM products p
     INNER JOIN order_items oi ON p.product_id = oi.product_id
     INNER JOIN orders o ON oi.order_id = o.order_id
     WHERE EXTRACT(YEAR FROM order_date) = 2024
     GROUP BY category, EXTRACT(MONTH FROM order_date)
     ORDER BY 1, 2',
    'SELECT generate_series(1, 12)'
) AS ct (
    category TEXT,
    jan BIGINT, feb BIGINT, mar BIGINT, apr BIGINT, may BIGINT, jun BIGINT,
    jul BIGINT, aug BIGINT, sep BIGINT, oct BIGINT, nov BIGINT, dec BIGINT
);

-- QA Validation:
-- Categories as rows, months as columns


-- ---------------------------------------------------------------------
-- Q120: End-to-end ETL validation query
-- Concept: Comprehensive data pipeline test
-- ---------------------------------------------------------------------
-- Compare source to target across multiple dimensions
WITH source_summary AS (
    SELECT 
        COUNT(*) as row_count,
        SUM(total_amount) as total_revenue,
        MIN(order_date) as min_date,
        MAX(order_date) as max_date,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM source_system.orders
),
target_summary AS (
    SELECT 
        COUNT(*) as row_count,
        SUM(total_amount) as total_revenue,
        MIN(order_date) as min_date,
        MAX(order_date) as max_date,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM dwh.fact_sales
)
SELECT 
    'Row Count' as metric,
    s.row_count as source_value,
    t.row_count as target_value,
    s.row_count - t.row_count as difference,
    CASE WHEN s.row_count = t.row_count THEN 'PASS' ELSE 'FAIL' END as status
FROM source_summary s, target_summary t
UNION ALL
SELECT 
    'Total Revenue',
    s.total_revenue,
    t.total_revenue,
    s.total_revenue - t.total_revenue,
    CASE WHEN ABS(s.total_revenue - t.total_revenue) < 0.01 THEN 'PASS' ELSE 'FAIL' END
FROM source_summary s, target_summary t
UNION ALL
SELECT 
    'Min Date',
    s.min_date::NUMERIC,
    t.min_date::NUMERIC,
    NULL,
    CASE WHEN s.min_date = t.min_date THEN 'PASS' ELSE 'FAIL' END
FROM source_summary s, target_summary t
UNION ALL
SELECT 
    'Max Date',
    s.max_date::NUMERIC,
    t.max_date::NUMERIC,
    NULL,
    CASE WHEN s.max_date = t.max_date THEN 'PASS' ELSE 'FAIL' END
FROM source_summary s, target_summary t
UNION ALL
SELECT 
    'Unique Customers',
    s.unique_customers,
    t.unique_customers,
    s.unique_customers - t.unique_customers,
    CASE WHEN s.unique_customers = t.unique_customers THEN 'PASS' ELSE 'FAIL' END
FROM source_summary s, target_summary t;

-- QA Validation:
-- All metrics should show status = 'PASS'
-- Any 'FAIL' indicates data quality issue in ETL pipeline


-- =====================================================================
-- END OF FILE: 90_SQL_Master_Concepts_Interview_QA_Solutions.sql
-- Total Questions: 120
-- Coverage: Basic SQL → Advanced Analytics → DWH/ETL Testing
-- =====================================================================

-- RECOMMENDED NEXT STEPS FOR QA ENGINEERS:
-- 1. Practice each query category (Basic, Intermediate, Advanced)
-- 2. Modify queries for your actual data models
-- 3. Create reusable test scripts from validation queries
-- 4. Combine multiple patterns for complex test scenarios
-- 5. Integrate queries into automated testing frameworks
-- 6. Document expected results for regression testing
-- 7. Build query library for common QA validation tasks

-- INTERVIEW PREPARATION:
-- - Understand execution plans (EXPLAIN ANALYZE)
-- - Know when to use indexes, materialized views
-- - Practice on actual DWH schemas (star, snowflake)
-- - Learn window functions deeply (80% of advanced questions)
-- - Master JOINs (INNER, LEFT, CROSS, LATERAL)
-- - Understand transaction isolation levels
-- - Know data quality validation patterns

-- KEY QA FOCUS AREAS:
-- ✓ Data reconciliation (source vs target)
-- ✓ Referential integrity (FK validation)
-- ✓ Data quality checks (nulls, duplicates, ranges)
-- ✓ ETL pipeline validation
-- ✓ Performance testing (indexes, partitions)
-- ✓ Slowly Changing Dimensions (SCD Type 2)
-- ✓ Aggregate vs detail reconciliation