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




IMPORTANCE OF SQL & DATABASE - SQL IS WIDELY USED IN :
1. Data Management
1. Data Analysis
2. Business Intelligence (BI)
3. Web Development
4. E-commerce
5. Finance and Banking
6. Healthcare
7. Supply Chain Management
8. Government and Public Services
9. Education
10.Gaming
11.Telecommunications
12.Manufacturing
13.Energy and Utilities
14.Research and Academia

IMPORTANCE OF SQL & DATABASE IN ENGINEERING SECTORS:-
1. Data Storage and Retrieval
2. Web Development
3. Data-Driven Decision Making
4. Application Performance
5. Data Security
6. Scalability
7. Backend Development
8. Integration
9. Full-Stack Development
10.IoT and Big Data
11.Cloud Computing
12.DevOps and Automation
13.Machine Learning and Data Science

www.TechieKrishnaKayaking.com 2

SQL Notes

-- **********************************
-- DDL - DATA DEFINITION LANGUAGE - CREATE, ALTER, DROP, TRUNCATE
-- **********************************
-- CREATE TABLE
CREATE TABLE STUD (
ID NUMBER(5),
NAME VARCHAR(10),
CITY VARCHAR(10),
MOB NUMBER(10)
);

CREATE TABLE DOCTOR (
DOCTOR_ID NUMBER(5) PRIMARY KEY,
FIRST_NAME VARCHAR2(50),
LAST_NAME VARCHAR2(50),
SPECIALTY VARCHAR2(100),
EMAIL VARCHAR2(100),
PHONE_NUMBER VARCHAR2(20),
ADDRESS VARCHAR2(255)
);
SELECT * FROM STUD;

-- ALTER TABLE
ALTER TABLE STUD ADD MOB NUMBER(10);
ALTER TABLE STUD ADD(DNO NUMBER(10), DEP VARCHAR2(10));
DESC STUD;
SELECT * FROM STUD;
ALTER TABLE STUD MODIFY MOB NUMBER (20);
ALTER TABLE STUD MODIFY (MOB CHAR(10), DEP VARCHAR(100));
SELECT * FROM STUD;
ALTER TABLE STUD RENAME COLUMN DNO TO SNO;
ALTER TABLE STUD DROP COLUMN SNO;
ALTER TABLE STUD DROP (MOB, DEP);

www.TechieKrishnaKayaking.com 3

SQL Notes

SELECT * FROM DOCTOR;
-- DROP TABLE
DROP TABLE DOCTOR;
SELECT * FROM DBA_RECYCLEBIN;
DROP TABLE DOCTOR PURGE;
PURGE DBA_RECYCLEBIN;

-- TRUNCATE
CREATE TABLE CUSTOMER(ID NUMBER(5), NAME VARCHAR(10));
SELECT * FROM CUSTOMER;
TRUNCATE TABLE CUSTOMER;

ALTER TABLE STUD MODIFY CITY VARCHAR(20);
SELECT * FROM STUD;

-- **********************************
-- DML - DATA MANIPULATION LANGUAGE - INSERT, SELECT, UPDATE, DELETE
-- **********************************
-- INSERT
-- Inserting dummy data into the STUD table
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (1, 'John', 'New York',
1234567890);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (2, 'Alice', 'Los
Angeles', 9876543210);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (3, 'Bob', 'Chicago',
5555555555);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (4, 'Eva', 'San
Francisco', 7777777777);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (5, 'Mike', 'Houston',
8888888888);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (6, 'Sara', 'Seattle',
9999999999);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (7, 'Chris', 'Miami',
7777777777);

www.TechieKrishnaKayaking.com 4

SQL Notes

INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (8, 'Laura', 'Boston',
5555555555);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (9, 'Daniel', 'Denver',
4444444444);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (10, 'Sophia', 'Atlanta',
3333333333);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (11, 'Matthew', 'Phoenix',
2222222222);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (12, 'Olivia', 'San
Diego', 1111111111);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (13, 'Ethan', 'Dallas',
9999999999);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (14, 'Ava',
'Philadelphia', 8888888888);
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (15, 'William', 'Houston',
7777777777);

-- SELECT
SELECT * FROM STUD
WHERE CITY='Chicago';
SELECT NAME, CITY FROM STUD;
SELECT * FROM STUD WHERE ID IN(1,2,3);
SELECT CITY, NAME, ID FROM STUD;

-- UPDATE
INSERT INTO STUD (ID, NAME, CITY, MOB) VALUES (16, 'Krishna',
'Bangalore', 7777777777);
SELECT * FROM STUD WHERE NAME='Krishna';
UPDATE STUD SET NAME='KRISHNA k' WHERE ID=1;
SELECT * FROM STUD;
-- DELETE
DELETE STUD WHERE ID=1;
DELETE FROM STUD WHERE ID=2;
DELETE STUD;
DELETE FROM STUD;

www.TechieKrishnaKayaking.com 5

SQL Notes

-- **********************************
-- TCL - TRANSACTION CONTROL LANGUAGE
-- **********************************
COMMIT;
ROLLBACK;
DROP TABLE CUSTOMER;
DROP TABLE STUD;

--- #########################################################
--- #########################################################
create table dept(
deptno number(2,0),
dname varchar2(14),
loc varchar2(13),
constraint pk_dept primary key (deptno)
);

create table emp(
empno number(4,0),
ename varchar2(10),
job varchar2(9),
mgr number(4,0),
hiredate date,
sal number(7,2),
comm number(7,2),
deptno number(2,0),
constraint pk_emp primary key (empno),
constraint fk_deptno foreign key (deptno) references dept (deptno)
);

create table bonus(
ename varchar2(10),
job varchar2(9),
sal number,
comm number
);

create table salgrade(

www.TechieKrishnaKayaking.com 6

SQL
No
te
s

g
r
a
d
e
n
u
m
b
e
r
,

l
o
s
a
l
n
u
m
b
e
r
,

h
i
s
a
l
n
u
m
b
e
r

)
;

-
-
-
#
#
#
#
#
#
#
#
#
#
#
#
#

i
n
s
e
r
t
i
n
t
o
d
e
p
t

v
a
l
u
e
s
(
1
0
, 'A
C
C
O
U
N
T
I
N
G', 'N
E
W
Y
O
R
K')
;

i
n
s
e
r
t
i
n
t
o
d
e
p
t

v
a
l
u
e
s
(
2
0
, 'R
E
S
E
A
R
C
H', 'D
A
L
L
A
S')
;

i
n
s
e
r
t
i
n
t
o
d
e
p
t

v
a
l
u
e
s
(
3
0
, 'S
A
L
E
S', 'C
H
I
C
A
G
O')
;

i
n
s
e
r
t
i
n
t
o
d
e
p
t

v
a
l
u
e
s
(
4
0
, 'O
P
E
R
A
T
I
O
N
S', 'B
O
S
T
O
N')
;

i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
8
3
9
, 'K
I
N
G', 'P
R
E
S
I
D
E
N
T',
n
u
l
l
, '17-NOVEMBER-1981', 5000, null, 10
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
6
9
8
, 'B
L
A
K
E', 'M
A
N
A
G
E
R',
7
8
3
9
, '1-MAY-1981', 2850, null, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
7
8
2
, 'C
L
A
R
K', 'M
A
N
A
G
E
R',
7
8
3
9
, '9-JULY-1981', 2450, null, 10
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
5
6
6
, 'J
O
N
E
S', 'M
A
N
A
G
E
R',
7
8
3
9
, '2-APRIL-1981', 2975, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
7
8
8
, 'S
C
O
T
T', 'A
N
A
L
Y
S
T',
7
5
6
6
, '13-JUL-87', 3000, null, 20
)
;

w
w
w.Te
c
h
i
e
K
r
i
s
h
n
a
K
ay
a
k
i
n
g
.
c
o
m

7

SQL
No
te
s

i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
9
0
2
, 'F
O
R
D', 'A
N
A
L
Y
S
T',
7
5
6
6
, '3-DECEMBER-1981', 3000, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
3
6
9
, 'S
M
I
T
H', 'C
L
E
R
K',
7
9
0
2
, '17-DECEMBER-1980', 800, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
4
9
9
, 'A
L
L
E
N', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '20-FEBRUARY-1981', 1600, 300, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
5
2
1
, 'W
A
R
D', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '22-FEBRUARY-1981', 1250, 500, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
6
5
4
, 'M
A
R
T
I
N', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '28-SEPTEMBER-1981', 1250, 1400, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
8
4
4
, 'T
U
R
N
E
R', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '8-SEPTEMBER-1981', 1500, 0, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
8
7
6
, 'A
D
A
M
S', 'C
L
E
R
K',
7
7
8
8
, '13-JULY-87', 1100, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
9
0
0
, 'J
A
M
E
S', 'C
L
E
R
K',
7
6
9
8
, '3-DECEMBER-1981',

w
w
w.Te
c
h
i
e
K
r
i
s
h
n
a
K
ay
a
k
i
n
g
.
c
o
m

8

SQL Notes

950, null, 30
);
insert into emp
values(
7934, 'MILLER', 'CLERK', 7782,
'23-JANUARY-1982',
1300, null, 10
);
SELECT * FROM EMP;

insert into salgrade
values (1, 700, 1200);
insert into salgrade
values (2, 1201, 1400);
insert into salgrade
values (3, 1401, 2000);
insert into salgrade
values (4, 2001, 3000);
insert into salgrade
values (5, 3001, 9999);

commit;

-- **********************************
-- QUERIES
-- **********************************
SELECT * FROM EMP;
SELECT DISTINCT JOB FROM EMP;
SELECT * FROM EMP
ORDER BY SAL DESC;
SELECT * FROM EMP
WHERE JOB='MANAGER' AND DEPTNO=20;
SELECT * FROM EMP
WHERE JOB='MANAGER'
OR DEPTNO=20;
SELECT * FROM EMP
WHERE SAL BETWEEN 2000 AND 5000;

www.TechieKrishnaKayaking.com 9

SQL Notes

SELECT ENAME FROM EMP
WHERE ENAME LIKE '%I%';

-- **********************************
-- QUERIES - CHARACTER FUNCTIONS
-- **********************************
SELECT EMPNO, ENAME, INITCAP(ENAME) AS CAMELCASE_NAME FROM EMP;
insert into emp
values(
7778, ' KRISHNA ', 'DIRECTOR', null,
'17-NOVEMBER-1981',
5000, null, 10
);

SELECT EMPNO, ENAME, LTRIM(ENAME) FROM EMP;
SELECT EMPNO, ENAME, RTRIM(ENAME) FROM EMP;
SELECT EMPNO, ENAME, LTRIM(RTRIM(ENAME)) FROM EMP;
SELECT EMPNO,ENAME, TRIM(ENAME) FROM EMP;
SELECT EMPNO,ENAME, UPPER(ENAME) FROM EMP;
SELECT EMPNO,ENAME, LOWER(ENAME) FROM EMP;
SELECT * FROM EMP;
SELECT EMPNO,ENAME, COMM, NVL(COMM,0) AS COMM FROM EMP;
SELECT EMPNO,ENAME, COMM, NVL2(COMM,1000,100) AS COMM FROM EMP;
SELECT 'KRISHNA', LENGTH('KRISHNA') FROM DUAL;
SELECT EMPNO, ENAME, LENGTH(ENAME) AS LENGTH_ENAME FROM EMP;
SELECT INSTR('KRISHNA','S',2) FROM DUAL;
SELECT SUBSTR('KRISHNA',3,2) FROM DUAL;
SELECT ENAME, SUBSTR(ENAME,(LENGTH(ENAME)-1),2) FROM EMP;
SELECT NAME,CITY,
DECODE(CITY, 'New York','NY', 'Chicago','CH', 'Houston', 'HH') AS N_CITY

www.TechieKrishnaKayaking.com 10

SQL Notes

FROM STUD;
SELECT NAME,CITY,
DECODE(CITY, 'BNG','BANGLORE', 'DLH', 'DELHI', CITY) AS N_CITY
FROM STUD;
SELECT NAME,CITY,
DECODE(CITY, 'BNG','BANGLORE', 'DLH', 'DELHI', UPPER(CITY) )AS N_CITY
FROM STUD;
SELECT NAME,CITY,
DECODE(CITY, 'BNG','BANGLORE', 'DLH','DELHI', NVL(CITY ,'INDIA')) AS
N_CITY
FROM STUD;
SELECT NAME,CITY,
DECODE(CITY, 'BNG','BANGLORE', 'DLH','DELHI', NVL2(CITY
,'INDIA','SRILANKA')) AS N_CITY
FROM STUD;

-- **********************************
-- QUERIES - AGGREGATE FUNCTIONS
-- **********************************
SELECT COUNT (EMPNO) FROM EMP;
SELECT SUM (SAL) FROM EMP;
SELECT MAX(SAL) FROM EMP;
SELECT MIN(SAL) FROM EMP;
SELECT ROUND(AVG(SAL)) FROM EMP;
SELECT AVG(ROUND(SAL)) FROM EMP;

-- **********************************
-- QUERIES - DATE FUNCTIONS
-- **********************************
SELECT SYSDATE FROM DUAL;
OR +1 OR -1
SELECT TO_CHAR(SYSDATE,'DD/MONTH/YYYY') FROM DUAL;
SELECT ADD_MONTHS(SYSDATE,2) FROM DUAL;

www.TechieKrishnaKayaking.com 11

SQL Notes

SELECT MONTHS_BETWEEN('10-JUL-2018', '12-JUL-2014') FROM DUAL;

-- **********************************
-- GROUP BY & HAVING
-- **********************************
SELECT * FROM EMP;
SELECT JOB, SUM(SAL), MAX(SAL), MIN(SAL), ROUND(AVG(SAL)) FROM EMP
WHERE JOB IN ('MANAGER', 'CLERK')
GROUP BY JOB
HAVING MAX(SAL) < 3000
ORDER BY JOB;

-- **********************************
-- QUERIES - SET OPERATOR
-- **********************************
CREATE TABLE X (A NUMBER);
CREATE TABLE Y (A NUMBER);
INSERT INTO X VALUES (1);
INSERT INTO X VALUES (2);
INSERT INTO X VALUES (3);
INSERT INTO X VALUES (4);
INSERT INTO X VALUES (5);
INSERT INTO Y VALUES (1);
INSERT INTO Y VALUES (2);
INSERT INTO Y VALUES (5);
INSERT INTO Y VALUES (7);
SELECT * FROM X;
SELECT * FROM Y;
SELECT A FROM X
UNION
SELECT A FROM Y;
SELECT A FROM X
UNION ALL
SELECT A FROM Y;
SELECT A FROM X
INTERSECT

www.TechieKrishnaKayaking.com 12

SQL Notes

SELECT A FROM Y;
SELECT A FROM Y
MINUS
SELECT A FROM X;
(SELECT A FROM X
MINUS
SELECT A FROM Y)
INTERSECT
SELECT A FROM Y;

-- **********************************
-- QUERIES - CONSTRAINTS
-- **********************************
CREATE TABLE CUST(
ID NUMBER(5),
NAME VARCHAR(10) NOT NULL,
CITY VARCHAR(10));
CREATE TABLE CUST(
ID NUMBER(5) UNIQUE,
NAME VARCHAR(10) NOT NULL,
CITY VARCHAR(10));
CREATE TABLE CUST(
ID NUMBER(5) PRIMARY KEY,
NAME VARCHAR(10) NOT NULL,
CITY VARCHAR(10));
CHILD TABLE
CREATE TABLE EMP (
ENO NUMBER(10) PRIMARY KEY,
ENAME VARCHAR(10),
SAL NUMBER(10),
DEPTNO NUMBER(3) REFERENCES DEPT(DNO) );
CREATE TABLE EMP (
ENO NUMBER(10),
ENAME VARCHAR(10),
SAL NUMBER CHECK (SAL BETWEEN 5000 AND 50000) );
CREATE TABLE JET_AIR (
FNO VARCHAR(10),
SEAT VARCHAR(5),

www.TechieKrishnaKayaking.com 13

SQL Notes

JDT DATE,
STARTJ VARCHAR(10),
DEST VARCHAR(10),
PRIMARY KEY (FNO, SEAT, JDT) ) ;
CREATE TABLE JET_AIR (
FNO VARCHAR(10),
SEAT VARCHAR(5),
JDT DATE,
STARTJ VARCHAR(10),
DEST VARCHAR(10),
UNIQUE (FNO, SEAT, JDT) ) ;

CHILD TABLE
CREATE TABLE PROD (
PID NUMBER(10) PRIMARY KEY,
SUPID NUMBER(5) NOT NULL,
SUPNAME VARCHAR(10) NOT NULL,
CONSTRAINT PK_SUP
FOREIGN KEY (SUPID, SUPNAME)
REFERENCES SUP (SUPID, SUPNAME) );

-- **********************************
-- QUERIES - ROW
-- **********************************
SELECT ROWNUM AS SLNO,EMPNO, ENAME, SAL FROM EMP;
SELECT ROWNUM AS SLNO, EMP.* FROM EMP;
/
WHERE ROWNUM=1
UPDATE EMP SET SAL=SAL+100 WHERE ROW NUM<= 5;
SELECT ROW ID SLNO,EMPNO, ENAME, SAL FROM EMP;
SELECT ENO,ENAME, SAL
CASE WHEN SAL >4000
THEN 'GRADE-A'
WHEN SAL>2000 AND SAL<4000 THEN 'GRADE-B'
ELSE 'GRADE-C' END
GRADE FROM <TB NAME> ORDER BY SAL DESC;

-- **********************************
-- QUERIES - ANALYTICAL FUNTIONS
-- **********************************
SELECT SLNO, EMPNO, ENAME, SAL,

www.TechieKrishnaKayaking.com 14

SQL Notes

RANK( ) OVER(ORDER BY SAL DESC) AS ALLIAS FROM EMP;
SELECT SLNO, EMPNO, ENAME, SAL,
DENSE_RANK( ) OVER(ORDER BY SAL DESC) AS ALLIAS FROM EMP;
CREATE TABLE EMP'_BKP AS SELECT * FROM EMP1;

-- **********************************
-- QUERIES - JOINS
-- **********************************
/*
* 1. INNER JOIN OR EQUI JOIN
* 2. NON-EQUI JOIN
* 3. OUTER JOIN - LEFT, RIGHT, FULL
* 4. SELF JOIN
* 5. CROSS JOIN
*
*/

SELECT * FROM EMP;
SELECT * FROM DEPT;
-- EQUI JOIN - INNER JOIN
SELECT E.EMPNO, E.ENAME, E.DEPTNO, D.DNAME
FROM EMP E INNER JOIN DEPT D
ON E.DEPTNO = D.DEPTNO;
SELECT E.EMPNO, E.ENAME, E.DEPTNO, D.DNAME
FROM EMP E, DEPT D
WHERE E.DEPTNO = D.DEPTNO;
-- NON-EQUI JOIN
SELECT E.EMPNO, E.ENAME, E.DEPTNO, D.DNAME
FROM EMP E, DEPT D
WHERE E.DEPTNO <> D.DEPTNO;
-- LEFT-OUTER
SELECT X.A AS X, Y.A AS Y
FROM X LEFT OUTER JOIN Y
ON X.A = Y.A;
-- RIGHT-OUTER
SELECT X.A AS X, Y.A AS Y
FROM X RIGHT OUTER JOIN Y
ON X.A = Y.A;

www.TechieKrishnaKayaking.com 15

SQL Notes

-- SELF-JOIN
SELECT X.A X, X.A XX FROM X X, X XX
WHERE X.A = XX.A;
SELECT E.EMPNO, E.ENAME, E.MGR, M.ENAME FROM EMP E, EMP M
WHERE E.MGR = M.EMPNO;
DESC TABLE emp;

-- **********************************
-- QUERIES - SUB QUERY
-- **********************************
-- SUB-QUERY
SELECT * FROM EMP WHERE ID IN(SELECT ID FROM EMP WHERE SAL>__);
-- SECOND HIGHEST SALARY
SELECT * FROM EMP WHERE SAL=
(SELECT MAX(SAL) FROM EMP WHERE SAL<
(SELECT MAX(SAL) FROM EMP));
-- INLINE SUB-QUERY (INLINE VIEW)
SELECT * FROM (SELECT PID,PNAME,PRICE*10/100 AS DISCOUNT FROM PRODUCT);
-- INLINE SUB-QUERY - CONDITION
SELECT * FROM (SELECT PID,PNAME,PRICE*10/100 AS DISCOUNT FROM PRODUCT)
WHERE DISCOUNT>= ;
-- CO-RELATED QUERIES
SELECT * FROM EMP A WHERE A.SAL<
(SELECT AVG(SAL) FROM EMP B WHERE B.DEPNO=A.DEPNO);
-- FIND DUPLICATE DATA
SELECT * FROM NSR A WHERE A.ROWID>
(SELECT MIN(ROWID) FROM NSR B
WHERE B.ID=A.ID);
-- VIEWS
CREATE VIEW EMP_V AS SELECT * EMP;
CREATE OR REPLACE VIEW NSR_PCD_V AS
SELECT NAME,COMP,SKILL FROM NSR_PCO;
-- VIEW FROM MULTIPLE TABLES
CREATE VIEW EMP_VIEW_V AS SELECT

www.TechieKrishnaKayaking.com 16

SQL Notes

E.EMPNO,E.ENAME,E.JOB,E.MGR,E.HIREDATE,E.DEPNO,D.DNAME,D.LOC
FROM EMP E,DEPT D WHERE E.DEPNO=D.DEPTNO;

-- **********************************
-- QUERIES - WHERE CLAUSE
-- **********************************
CREATE TABLE EMP (ID NUMBER (5), NAME VARCHAR(10), CITY VARCHAR(10));
SELECT MAX(COMM) FROM EMP WHERE DEPT_NO = 10;
SELECT MIN(BONUS) FROM EMP WHERE DEPT_NO= 20;
SELECT COUNT(EMPNO) FROM EMP WHERE DEP_NO IN(10, 20, 60);
SELECT SUM(SAL) FROM EMP WHERE DEP_NO = 20;
SELECT AVG(SAL) FROM EMP WHERE DEP_NO = 30;
UPDATE EMP SET SAL =5000 WHERE ID = 6;
UPDATE EMP SET NAME = ' RADHIKA ', CITY = 'AP' WHERE ID = 6;
DELETE FROM EMP WHERE JOB = MANAGER ;
SELECT * FROM EMP WHERE DEPTNO = 10;
SELECT ENO, ENAME, SAL, JOB FROM EMP WHERE DEPNO = 10;
SELECT MAX(SAL) FROM EMP HAVING MAX(SAL)>=1000;
SELECT MIN(SAL) FROM EMP HAVING MIN(SAL)<6000;
SELECT AVG(SAL) FROM EMP HAVING AVG(SAL)>=5000;
SELECT SUM(SAL) FROM EMP HAVING SUM(SAL)>9000;
SELECT COUNT(EMPNO) FROM EMP HAVING COUNT(EMPNO)>50;
SELECT DEPT, SUM(SAL) FROM EMP GROUP BY DEPT;
SELECT JOB, COUNT(EMPNO) FROM EMP GROUP BY JOB;
SELECT DEPT, MAX(SAL) FROM EMP GROUP BY DEPT;
SELECT JOB, MIN(BONUS) FROM EMP GROUP BY JOB;

www.TechieKrishnaKayaking.com 17

SQL Notes

SELECT DEPT, AVG(SAL) FROM EMP GROUP BY DEPT;

-- **********************************
-- JOINS
-- **********************************
1. INNER JOIN / EQUI JOIN
2. NON EQUI JOIN
3. SELF JOIN
4. CROSS JOIN
5. OUTER JOIN - LEFT, RIGHT, FULL

SELECT * FROM SCOTT.EMP;
SELECT * FROM SCOTT.DEPT;
-- SYNTAX
SELECT T1.COL1, T2.COL2, COL3, COL4
FROM TAB1 T1 INNER JOIN TAB2 T2
ON TAB1.COLNAME = TAB2.COLNAME;
-- EXAMPLE - EMP & DEPT TABLES
SELECT E.ENAME, E.JOB, E.DEPTNO, D.DNAME, D.LOC
FROM EMP E INNER JOIN DEPT D
ON E.DEPTNO = D.DEPTNO;

250 QUESTIONS AND ANSWERS

create table dept(
deptno number(2,0),
dname varchar2(14),
loc varchar2(13),
constraint pk_dept primary key (deptno)
);

create table emp(

www.TechieKrishnaKayaking.com 18

SQL Notes

empno number(4,0),
ename varchar2(10),
job varchar2(9),
mgr number(4,0),
hiredate date,
sal number(7,2),
comm number(7,2),
deptno number(2,0),
constraint pk_emp primary key (empno),
constraint fk_deptno foreign key (deptno) references dept (deptno)
);

create table bonus(
ename varchar2(10),
job varchar2(9),
sal number,
comm number
);
create table salgrade(
grade number,
losal number,
hisal number
);

---#############
insert into dept
values(10, 'ACCOUNTING', 'NEW YORK');
insert into dept
values(20, 'RESEARCH', 'DALLAS');
insert into dept
values(30, 'SALES', 'CHICAGO');
insert into dept
values(40, 'OPERATIONS', 'BOSTON');

insert into emp
values(
7839, 'KING', 'PRESIDENT', null,
'17-11-1981',
5000, null, 10
);
insert into emp
values(
7698, 'BLAKE', 'MANAGER', 7839,

www.TechieKrishnaKayaking.com 19

SQL
No
te
s '1-5-
1
9
8
1',
2
8
5
0
,
n
u
l
l
,
3
0

)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
7
8
2
, 'C
L
A
R
K', 'M
A
N
A
G
E
R',
7
8
3
9
, '9-6-1981', 2450, null, 10
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
5
6
6
, 'J
O
N
E
S', 'M
A
N
A
G
E
R',
7
8
3
9
, '2-4-1981', 2975, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
7
8
8
, 'S
C
O
T
T', 'A
N
A
L
Y
S
T',
7
5
6
6
, '13-JUL-87', 3000, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
9
0
2
, 'F
O
R
D', 'A
N
A
L
Y
S
T',
7
5
6
6
, '3-12-1981', 3000, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
3
6
9
, 'S
M
I
T
H', 'C
L
E
R
K',
7
9
0
2
, '17-12-1980', 800, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
4
9
9
, 'A
L
L
E
N', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '20-2-1981', 1600, 300, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
5
2
1
, 'W
A
R
D', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '22-2-1981', 1250, 500, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

w
w
w.Te
c
h
i
e
K
r
i
s
h
n
a
K
ay
a
k
i
n
g
.
c
o
m

2
0

SQL
No
te
s

v
a
l
u
e
s
(
7
6
5
4
, 'M
A
R
T
I
N', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '28-9-1981', 1250, 1400, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
8
4
4
, 'T
U
R
N
E
R', 'S
A
L
E
S
M
A
N',
7
6
9
8
, '8-9-1981', 1500, 0, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
8
7
6
, 'A
D
A
M
S', 'C
L
E
R
K',
7
7
8
8
, '13-JUL-87', 1100, null, 20
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
9
0
0
, 'J
A
M
E
S', 'C
L
E
R
K',
7
6
9
8
, '3-12-1981', 950, null, 30
)
;
i
n
s
e
r
t
i
n
t
o
e
m
p

v
a
l
u
e
s
(
7
9
3
4
, 'M
I
L
L
E
R', 'C
L
E
R
K',
7
7
8
2
, '23-1-1982', 1300, null, 10
)
;

i
n
s
e
r
t
i
n
t
o
s
a
l
g
r
a
d
e

v
a
l
u
e
s
(
1
,
7
0
0
,
1
2
0
0
)
;

i
n
s
e
r
t
i
n
t
o
s
a
l
g
r
a
d
e

v
a
l
u
e
s
(
2
,
1
2
0
1
,
1
4
0
0
)
;

i
n
s
e
r
t
i
n
t
o
s
a
l
g
r
a
d
e

v
a
l
u
e
s
(
3
,
1
4
0
1
,
2
0
0
0
)
;

i
n
s
e
r
t
i
n
t
o
s
a
l
g
r
a
d
e

v
a
l
u
e
s
(
4
,
2
0
0
1
,
3
0
0
0
)
;

i
n
s
e
r
t
i
n
t
o
s
a
l
g
r
a
d
e

v
a
l
u
e
s
(
5
,
3
0
0
1
,
9
9
9
9
)
;

c
o
m
m
i
t
;

w
w
w.Te
c
h
i
e
K
r
i
s
h
n
a
K
ay
a
k
i
n
g
.
c
o
m

2
1

SQL Notes

SQL CRACKER
------------
1) Display the details of all employees
select * from emp;
2) Display the depart information from department table
select * from dept;
3) Display the name and job for all the employees
select ename, job from emp;
4) Display the name and salary for all the employees
select ename, sal from emp;
5) Display the employee no and totalsalary for all the employees
select empno, sal+NVL(comm,0) as total_sal from emp;
6) Display the employee name and salary for all empplyees.
select ename, sal from emp;
7) Display the names of all the employees who are working in depart number 10.
select ename from emp
where
deptno = 10;

8) Display the names of all the employees who are working as clerks and drawing a salary
more than 3000.
select ename from emp

where job = 'CLERKS' AND sal > 3000;

9) Display the employee number and name who are earning comm.
select empno, ename from emp
where comm IS NOT NULL;

10) Display the employee number and name who do not earn any comm.
select empno, ename from emp
where comm IS NULL;

11) Display the names of employees who are working as clerks, salesman or analyst and
drawing a salary more than 3000.
select enmae from emp
where
job IN ('CLERK','SALESMAN', 'ANALYST')
AND sal > 3000;

www.TechieKrishnaKayaking.com 22

SQL Notes

12) Display the names of the employees selewho are working in the company for the past 5
years;
select ename from emp
where
(TO_CHAR(sysdate, 'YYYY') - TO_CHAR(hiredate,'YYYY')) > 5;
13) Display the list of employees who have joined the company before 30-JUN-90 or after
31-DEC-90.
select * from emp
where
hiredate < '30-JUN-90'
OR
hiredate > '31-DEC-90';
14) Display current Date.
select sysdate from dual;
15) Display the list of all users in your database (use catalog table).
select * from all_users;
16) Display the names of all tables from current user;
select * from tab;
17) Display the name of the current user.
show user;
18) Display the names of employees working in depart number 10 or 20 or 40 or employees
working as CLERKS,SALESMAN or ANALYST.
select ename from emp
where
job IN ('CLERK', 'SALESMAN', 'ANALYST')
AND
deptno IN (10, 20, 40);
19) Display the names of employees whose name starts with alaphabet S.
select ename from emp
where
ename LIKE 'S%';
20) Display the Employee names for employees whose name ends with alaphabet S.
select ename from emp
where
ename LIKE '%S';
21) Display the names of employees whose names have second alphabet A in their names.
select ename from emp
where
ename LIKE '_A%';

www.TechieKrishnaKayaking.com 23

SQL Notes

22) select the names of the employee whose names is exactly five characters in length.
select ename from emp
where
LENGTH(ename) = 5;
23) Display the names of the employee who are not working as MANAGERS.
select ename from emp
where
job NOT IN ('MANAGER');
----
select ename from emp
where
job <> 'MANAGER';
24) Display the names of the employee who are not working as SALESMAN OR CLERK OR
ANALYST.
select ename from emp
where
JOB NOT IN ('SALESMAN', 'CLERK', 'ANALYST');
25) Display all rows from emp table. The system should wait after every screen full of
information.
set pause on;
select * from emp;
26) Display the total number of employee working in the company.
select count(*) from emp;
27) Display the total salary being paid to all employees.
select sum(sal) from emp;
28) Display the maximum salary from emp table.
select max(sal) from emp;
29) Display the minimum salary from emp table.
select min(sal) from emp;
30) Display the average salary from emp table.
select avg(sal) from emp;
31) Display the maximum salary being paid to CLERK.
select max(sal) from emp
where job = 'CLERK';
32) Display the maximum salary being paid to depart number 20.
select max(sal) from emp

www.TechieKrishnaKayaking.com 24

SQL Notes

where deptno = 20;
33) Display the minimum salary being paid to any SALESMAN.
select min(sal) from emp
where job = 'SALESMAN';
34) Display the average salary drawn by MANAGERS.
select avg(sal) from emp
where job = 'MANAGER';
35) Display the total salary drawn by ANALYST working in depart number 40.
select sum(sal) from emp
where
job = 'ANALYST'
and deptno = 40;
36) Display the names of the employee in order of salary i.e the name of the employee
earning lowest salary should appear first.
select ename from emp
order sal;
37) Display the names of the employee in descending order of salary.
select ename from emp
order by sal desc;
38) Display the names of the employee in order of employee name.
select ename from emp
order by ename;
39) Display empno,ename,deptno,sal sort the output first base on name and within name by
deptno and with in deptno by sal.
select empno, ename, deptno, sal from emp
order by ename, deptno, sal;
40) Display the name of the employee along with their annual salary(sal*12). The name of
the employee earning highest annual salary should apper first.
select ename, sal*12 as aanualsal from emp
order by sal desc;
41) Display name,salary,hra,pf,da,total salary for each employee. The output should be in
the order of total salary,hra 15% of salary,da 10% of salary,pf 5% salary,total salary will
be(salary+hra+da)-pf.
select ename, sal, sal*.15 as hra, sal*.5 as pf, sal*.10 as da, (sal + (sal*.15) +
(sal*.10) - (sal*.05)) as totsal
from emp
order by (sal + sal*.15 + sal*.10) - (sal*.05);
42) Display depart numbers and total number of employees working in each department.

www.TechieKrishnaKayaking.com 25

SQL Notes

select deptno, count(deptno) from emp
group by deptno;
43) Display the various jobs and total number of employees within each job group.
select job, count(job) from emp
group by job;
44) Display the depart numbers and total salary for each department.
select deptno, sum(sal) from emp
group by deptno;
45) Display the depart numbers and max salary for each department.
select deptno, max(sal) from emp
group by deptno;
46) Display the various jobs and total salary for each job
select job, sum(sal) from emp
group by job;
47) Display the various jobs and max salary for each job
select job, max(sal) from emp
group by job;
48) Display the depart numbers with more than three employees in each dept.
select deptno, count(deptno) from emp
group by deptno
having count(*) > 3;
49) Display the various jobs along with total salary for each of the jobs. Where total salary is
greater than 40000.
select job, sum(sal) from emp
group by job
having sum(sal) > 40000;
50) Display the various jobs along with total number of employees in each job. The output
should contain only those jobs with more than three employees.
select job, count(empno) from emp
group by job
having count(job) > 3;
51) Display the name of the employee who earns highest salary.
select ename from emp
where
sal = (select max(sal) from emp);
52) Display the employee number and name for employee working as clerk and earning
highest salary among clerks.
select ename, empno from emp

www.TechieKrishnaKayaking.com 26

SQL Notes

where
sal = (select max(sal) from emp where job = 'CLERK');
53) Display the names of salesman who earns a salary more than the highest salary of any
clerk.
select ename, sal from emp
where
job = 'SALESMAN' AND
sal > (select max(sal) from emp where job = 'CLERK');
54) Display the names of clerks who earn a salary more than the lowest salary of any
salesman.
select ename from emp
where job = 'CLERK' AND
sal > (select min(sal) from emp where job = 'SALESMAN');
54.1) Display the names of employees who earn a salary more than that of Jones or that of
salary greater than that of scott.
select ename, sal from emp
where
sal > (select sal from emp where ename = 'SCOTT')
OR
sal > (select sal from emp where ename = 'JONES');
55) Display the names of the employees who earn highest salary in their respective
departments.
select ename, sal from emp
where
sal IN (select max(sal) from emp group by deptno);
SELECT ename, deptno, sal, rank() OVER (PARTITION BY deptno ORDER BY sal
desc)
FROM emp;
SELECT deptno, ename, sal
FROM emp
WHERE (deptno,sal) IN (SELECT deptno, max(sal) FROM emp GROUP BY deptno)
ORDER BY deptno;
56) Display the names of the employees who earn highest salaries in their respective job
groups.
select ename, sal from emp
where
sal IN (select max(sal) from emp group by job);
57) Display the employee names who are working in accounting department.
select ename from emp
where

www.TechieKrishnaKayaking.com 27

SQL Notes

deptno = (select deptno from dept where dname = 'ACCOUNTING');
------
select e.ename from emp e, dept d
where
e.deptno = d.deptno
AND
d.dname = 'ACCOUNTING';
58) Display the employee names who are working in Chicago.
select ename from emp
where
deptno = (select deptno from dept where loc = 'CHICAGO');
-------
select e.ename from emp e, dept d
where
d.deptno = e.deptno
AND
d.loc = 'CHICAGO';
59) Display the Job groups having total salary greater than the maximum salary for
managers.
select job, sum(sal) from emp
GROUP BY job
HAVING
sum(sal) > (select max(sal) from emp where job = 'MANAGER');
60) Display the names of employees from department number 10 with salary grether than
that of any employee working in other department.
select ename from emp
where
deptno = 10
AND
sal > (select max(sal) from emp where deptno <> 10);
61) Display the names of the employees from department number 10 with salary greater
than that of all employee working in other departments.
select ename from emp
where deptno = 10
AND
sal > (select max(sal) from emp where deptno <> 10);
62) Display the names of the employees in Uppercase.
select UPPER(ename) from emp;
63) Display the names of the employees in Lowecase.
select LOWER(ename) from emp;
64) Display the names of the employees in Propercase.

www.TechieKrishnaKayaking.com 28

SQL Notes

select INITCAP(ename) from emp;
65) Display the length of Your name using appropriate function.
select LENGTH('KRISHNA') from dual;
66) Display the length of all the employee names.
select LENGTH(ename) from emp;
67) select name of the employee concatenate with employee number.
select CONCAT(ename, empno) from emp;
select CONCAT(CONCAT(ename,' '),empno) from emp;
68) Use appropriate function and extract 3 characters starting from 2 characters from the
following string 'Oracle'. i.e the out put should be 'ac'.
select SUBSTR('ORACLE',3,2) from dual;
69) Find the First occurrence of character 'a' from the following string i.e 'Computer
Maintenance Corporation'.
select INSTR('Computer Maintenance Corporation','a',1) from dual;
70) Replace every occurrence of alphabet A with B in the string Allens(use translate
function)
select REPLACE('Allens','A','B') from dual;
71) Display the information from emp table. Where job manager is found it should be
displayed as boss(Use replace function).
select ename, empno, deptno, REPLACE(job,'MANAGER','BOSS') from emp;
72) Display empno,ename,deptno from emp table. Instead of display department numbers
display the related department name(Use decode function).
select empno, ename, e.deptno,
DECODE(e.deptno, d.deptno, d.dname) as DEPT
from emp e, dept d
where
e.deptno = d.deptno;
73) Display your age in days.
select TO_DATE(sysdate) - TO_DATE('16-JUN-1994') as ageinday from dual;
-----
select ROUND(SYSDATE - TO_DATE('16-JUN-1994')) as ageinday from dual;
74) Display your age in months.
select MONTHS_BETWEEN(sysdate,'07-JAN-1996') as ageinmon from dual;
75) Display the current date as DATE MONTH DAY YEAR.
select TO_CHAR(sysdate, 'dd month day yy') from dual;

www.TechieKrishnaKayaking.com 29

SQL Notes

76) Display the following output for each row from emp table. scott has joined the company
on wednesday 13th August ninten nintey.
select ename, TO_CHAR(hiredate,'day dd month yyyy') as hiredate from emp;
77) Find the date for nearest saturday after current date.
select NEXT_DAY(sysdate,'SATURDAY') from dual;
78) Display current time.
select TO_CHAR(sysdate, 'HH:MI:SS') from dual;
79) Display the date three months Before the current date.
select ADD_MONTHS(sysdate, -3) from dual;
80) Display the common jobs from department number 10 and 20.
select e.job from emp e where deptno = 10
INTERSECT
select d.job from emp d where deptno = 20;
81) Display the jobs found in department 10 and 20 Eliminate duplicate jobs.
select distinct(job) from emp
where deptno = 10 and deptno = 20;
select distinct(job) from emp
where deptno IN (10, 20);
82) Display the jobs which are unique to department 10.
select distinct(job) from emp
where deptno = 10;
83) Display the details of those employees who do not have any person working under them.
select * from emp
where
empno NOT IN (select mgr from emp where mgr IS NOT NULL);
84) Display the details of those employees who are in sales department and grade is 3.
select e.empno, e.ename, e.job, e.deptno, d.dname, d.loc, s.grade from emp e, dept
d, salgrade s
where
e.deptno = d.deptno
and
d.dname = 'SALES'
and
e.sal BETWEEN s.losal and s.hisal
and
s.losal = 1401 and s.hisal = 2000;
85) Display those i) who are managers.
select distinct(e.empno), e.ename, e.job, e.mgr, e.sal, e.deptno

www.TechieKrishnaKayaking.com 30

SQL Notes

from emp e, emp b
where
e.empno = b.mgr;
ii) display the who are not managers
select * from emp
where
empno NOT IN (select mgr from emp where mgr IS NOT NULL);
86) Display those employee whose name contains not less than 4 characters.
select ename from emp
where
LENGTH(ename) > 4;
87) Display those department whose name start with "S" while the location name ends with
"O".
SQL>
select dname from dept
where
dname LIKE 'S%'
and
loc LIKE '%O';
88) Display those employees whose manager name is JONES.
SQL>
select e.ename from emp e, emp m
where
e.mgr = m.empno
and
m.ename = 'JONES';
89) Display those employees whose salary is more than 3000 after giving 20% increment.
SQL>
select ename, sal from emp
where (sal + sal*0.2) > 3000;
90) Display all employees with their dept names;
SQL>
select e.ename, d.dname from emp e, dept d
where
e.deptno = d.deptno;
91) Display ename who are working in sales dept.
SQL>
select ename from emp e, dept d
where
e.deptno = d.deptno
and

www.TechieKrishnaKayaking.com 31

SQL Notes

d.dname = 'SALES';
92) Display employee name,deptname,salary and comm for those sal in between 2000 to
5000 while location is chicago.
SQL>
select e.ename, d.dname, e.sal, e.comm from emp e, dept d
where
e.sal BETWEEN 2000 and 5000
and
d.loc = 'CHICAGO'
and
e.deptno = d.deptno;
93)Display those employees whose salary greater than his manager salary.
SQL>
select e.* from emp e, emp m
where
e.mgr = m.empno
and
e.sal > m.sal;
94) Display those employees who are working in the same dept where his manager is work.
SQL>
select e.* from emp e, emp m
where
e.mgr = m.empno
and
m.deptno = e.deptno;
95) Display those employees who are not working under any manager.
SQL>
select ename from emp
where
mgr IS NULL;
96) Display grade and employees name for the dept no 10 or 30 but grade is not 4 while
joined the company before 31-dec-82.
SQL>
select e.ename, s.grade from emp e, salgrade s
where
sal BETWEEN s.losal and s.hisal
and
s.grade <> 4
and
e.deptno IN (10, 30)
and
e.hiredate < '31-DEC-82';

www.TechieKrishnaKayaking.com 32

SQL Notes

97) Update the salary of each employee by 10% increment who are not eligiblw for
commission.
SQL>
UPDATE emp set sal = (sal + sal*.1)
where
comm IS NULL;
98) SELECT those employee who joined the company before 31-dec-82 while their dept
location is newyork or Chicago.
SQL>
select * from emp, dept
where
emp.deptno = dept.deptno
and
hiredate < '31-Dec-82'
and
dept.loc IN ('Chicago', 'Newyork');
99) DISPLAY EMPLOYEE NAME,JOB,DEPARTMENT,LOCATION FOR ALL WHO ARE
WORKING AS MANAGER?
SQL>
select ename, job, e.deptno, loc from emp e, dept d
where
job = 'MANAGER'
and
d.deptno = e.deptno;
100) Display those employees whose manager name is jones?
SQL>
select e.ename from emp e, emp m
where
e.mgr = m.empno
and
m.ename = 'JONES';
100.1) And also display their manager name?
SQL>
select e.ename, m.ename from emp e, emp m
where
e.mgr = m.empno
and
m.ename = 'JONES';
101) Display name and salary of ford if his salary is equal to hisal of his grade.
SQL>
select e.ename, e.sal from emp e, salgrade s
where
s.hisal = e.sal

www.TechieKrishnaKayaking.com 33

SQL Notes

and
e.ename = 'FORD';
102) Display employee name,job,depart name ,manager name,his grade and make out an
under department wise?
SQL>
select e.ename, e.job, m.ename, d.dname, s.grade from emp e, dept d, salgrade s
where
e.deptno = d.deptno
and
e.mgr = m.empno
and
sal between losal and hisal
ORDER BY deptno;
103) List out all employees name,job,salary,grade and depart name for every one in the
company except 'CLERK'. Sort on salary display the highest salary?
SQL>
select e.ename, e.job, e.sal, s.grade, d.dname
from emp e, dept d, salgrade s
where
e.job <> 'CLERK'
and
d.deptno = e.deptno
and
sal BETWEEN losal AND hisal
order by e.sal desc;
104) Display the employee name, job and his manager.
SQL>
select e.ename, e.job, m.ename from emp e, emp m
where
e.mgr = m.empno;
104.1) Display also employee who are without manager?
SQL>

105) Find out the top 5 earners of company?
SQL>
select * from (select * from emp order by sal desc)
where
rownum < 6;
106) Display name of those employee who are getting the highest salary?
SQL>
select ename from emp
where sal = (select max(sal) from emp);

www.TechieKrishnaKayaking.com 34

SQL Notes

107) Display those employees whose salary is equal to average of maximum and minimum?
SQL>
select * from emp
where
sal = (select (max(sal) + min(sal))/2 from emp);
108) Select count of employee in each department where count greater than 3?
SQL>
select count(*) from emp
GROUP BY dept
HAVING count(*) > 3;
109) Display dname where at least 3 are working and display only department name?
SQL>
select d.dname from emp e, dept d
where
d.deptno = e.deptno
group by dname
having count(e.ename) > 3;
110) Display name of those managers whose salary is more than average salary of his
company?
SQL>
select ename from emp
where
job = 'MANAGER'
and
sal > (select avg(sal) from emp);
111)Display those managers name whose salary is more than average salary of his
employee?
SQL>
select distinct(m.ename), m.sal from emp m, emp e
where
e.mgr = m.empno
and
m.sal > any(select avg(e.sal) from emp e, emp m
where
e.mgr = m.empno);
112) Display employee name, sal, comm and net pay for those employees whose net pay is
greater than or equal to any other employee salary of the company?
SQL>
select ename, sal, comm, NVL(sal,sal+comm) as netsal
from emp
where
NVL(sal,sal+comm) > ANY(select sal from emp);

www.TechieKrishnaKayaking.com 35

SQL Notes

113) Display all employees’ names with total sal of company with each employee name?
SQL>
select ename, (select sum(sal) from emp) as totsal from emp;
113.1) Displaying Ename & Sal together.
SQL>
select CONCAT(ename,sal) from emp;
select CONCAT(CONCAT(ename,' '), sal) from emp;
114) Find out last 5(least)earners of the company.?
SQL>
select ename, sal from emp
where rownum < 6 order by sal;
115) Find out the number of employees whose salary is greater than their manager salary?
SQL>
select count(*) from
(select e.ename from emp e, emp m
where
e.mgr = m.empno
and
e.sal > m.sal);
116) Display those department where no employee working?
SQL>
select deptno from dept
where
deptno NOT IN (select deptno from emp);
117) Display those employees whose salary is ODD value?
SQL>
select * from emp
where
MOD(sal,2) = 1;
118) Display those employees whose salary contains alleast 3 digits?
SQL>
select * from emp
where
LENGTH(sal) >= 3;
119) Display those employee who joined in the company in the month of Dec?
SQL>
select * from emp
where
TO_CHAR(hiredate, 'MON') = 'DEC';

www.TechieKrishnaKayaking.com 36

SQL Notes

120) Display those employees whose name contains "A"?
SQL>
select * from emp
where
ename LIKE '%A%';
121) Display those employee whose deptno is available in salary?
SQL>
select * from emp
where
sal LIKE '%`deptno`%';
122) Display employee first 2 characters from hiredate -last 2 characters of salary?
SQL>
select CONCAT(substr(hiredate,0,2), substr(sal,-2,2)) from emp;
123) Display those employees whose 10% of salary is equal to the year of joining?
SQL>
select * from emp
where sal*0.1 = TO_CHAR(hiredate,'yyyy');
124) Display those employees who are working in sales or research?
SQL>
select * from emp
where deptno IN (select deptno from dept where dname IN ('SALES', 'RESEARCH'));
---
select e.* from emp e, dept d
where
e.deptno = d.deptno
where
d.dname IN ('SALES', 'RESEARCH');
125) Display the grade of jones?
SQL>
select e.ename, s.grade from emp e, salgrade s
where
e.ename = 'JONES'
and
e.sal BETWEEN s.losal and s.hisal;
126) Display those employees who joined the company before 450 months?
SQL>
select * from emp
where
MONTHS_BETWEEN(sysdate,hiredate) > 450;
---
select * from emp
where

www.TechieKrishnaKayaking.com 37

SQL Notes

12*(TO_CHAR(sysdate,'yyyy')-TO_CHAR(hiredate,'yyyy')) > 450;
127) Display those employee who has joined before 15th of the month.
SQL>
select * from emp
where
TO_CHAR(hiredae,'dd') < 15;
128) Delete those records where no of employees in a particular department is less than 3.
SQL>
delete from emp
where
deptno = (select deptno from emp group by deptno having count(deptno) < 3);
129) Display the name of the department where no employee working.
SQL>
select dname from dept
where
deptno NOT IN (select deptno from emp);
---
select d.dname from dept d, emp e
where
e.deptno = d.deptno
having count(e.deptno)=0;
130) Display those employees who are working as manager.
SQL>
select ename from emp
where
job = 'MANAGER';
131) Display those employees whose grade is equal to any number of sal but not equal to
first number of sal?
SQL>
select e.ename, e.sal, s.grade from emp e, salgrade s
where
e.sal between s.losal and s.hisal
and
INSTR(e.sal,s.grade,1,1) <> 0;
---
select e.ename, e.sal, s.grade from emp e, salgrade s
where
e.sal between s.losal and s.hisal
and
s.grade = SUBSTR(e.sal,1,1);
132) Print the details of all the employees who are Sub-ordinate to BLAKE?
SQL>

www.TechieKrishnaKayaking.com 38

SQL Notes

select * from emp
where
mgr = (select empno from emp where ename = 'BLAKE');
133) Display employee name and his salary whose salary is greater than highest average of
department number?
SQL>
select ename, sal from emp
where
sal > (select max(avg(sal)) from emp GROUP BY deptno);
134) Display the 10th record of emp table (without using rowid).
SQL>
select * from emp where ROWNUM < 11
MINUS
select * from emp where ROWNUM < 10;
135) Display the half of the ename's in upper case and remaining lowercase?
SQL>
select ename,
CONCAT(
UPPER(substr(ename,1,LENGTH(ename)/2+1)),
LOWER(substr(ename,LENGTH(ename)/2)))
from emp;
136) Display the 10th record of emp table without using group by and rowid?
SQL>
select * from emp where ROWNUM < 11
MINUS
select * from emp where ROWNUM < 10;
136.1) Delete the 10th record of emp table.
SQL>
DELETE FROM EMP
where
empno =
(select empno from emp where ROWNUM < 11
MINUS
select empno from emp where ROWNUM < 10);
137) Create a copy of emp table;
SQL>
CREATE TABLE EMP1 as (select * from emp);
138) Select ename if ename exists more than once.
SQL>
select ename from emp
group by ename

www.TechieKrishnaKayaking.com 39

SQL Notes

having count(ename) > 1;
139) Display all enames in reverse order? (SMITH:HTIMS).
SQL>
select REVERSE(ename) from emp;
140) Display those employees whose joining of month and grade is equal.
SQL>
select e.ename, s.grade from emp e, salgrade s
where
e.sal between s.losal and s.hisal
and
s.grade = TO_CHAR(e.hiredate,'MM');
141) Display those employees whose joining DATE is available in deptno.
SQL>
select ename from emp
where TO_CHAR(hiredate,'dd') = deptno;
142) Display those employees name as follows
A ALLEN
B BLAKE
SQL>
select substr(ename,1,1), ename from emp;
143) List out the employees ename,sal,PF(20% OF SAL) from emp;
SQL>
select ename, sal, sal*.2 pf from emp;
144) Create table emp with only one column empno;
SQL>
create table emp (empno varchar(10));
145) Add this column to emp table ename vrachar2(20).
SQL>
alter table emp ADD ename varchar(20);
146) Oops I forgot give the primary key constraint. Add in now.
SQL>
alter table emp ADD PRIMARY KEY (empno);
147) Now increase the length of ename column to 30 characters.
SQL>
alter table emp MODIFY (ename varchar(30));
148) Add salary column to emp table.
SQL>
alter table emp ADD sal number(10);

www.TechieKrishnaKayaking.com 40

SQL Notes

149) I want to give a validation saying that salary cannot be greater 10,000 (note give a
name to this constraint)
SQL>
alter table emp MODIFY (sal number(10) CHECK sal >10000);
150) For the time being I have decided that I will not impose this validation. My boss has
agreed to pay more than 10,000.
SQL>
alter table emp
DISABLE constraint <constratin_name>;
151) My boss has changed his mind. Now he doesn't want to pay more than 10,000.so
revoke that salary constraint.
SQL>
alter table emp
ENABLE constraint <constratin_name>;
152) Add column called as mgr to your emp table;
SQL>
alter table emp ADD mgr number(5);
153) Oh! This column should be related to empno. Give a command to add this constraint.
SQL>
alter table emp ADD mgr REFERENCES emp(empno);
154) Add deptno column to your emp table;
SQL>
alter table emp ADD deptno number(5);
155) This deptno column should be related to deptno column of dept table;
SQL>
alter table emp
MODIFY (deptno number(5) REFERENCES dept(deptno));
156) Give the command to add the constraint.
SQL>
alter table tb_name
ADD <CONSTRAINT> (col_name);
157) Create table called as newemp. Using single command create this table as well as get
data into this table(use create table as);
SQL>
create table newemp AS (select * from emp);
158) Delete the rows of employees who are working in the company for more than 2 years.
SQL>
delete from emp

www.TechieKrishnaKayaking.com 41

SQL Notes

where
(TO_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate,'yyyy')) > 2;
159) Provide a commission(10% Comm Of Sal) to employees who are not earning any
commission.
SQL>
select sal*.1 from emp
where comm IS NULL;
160) If any employee has commission his commission should be incremented by 10% of his
salary.
SQL>
update emp set
comm = sal*.1 where comm IS NOT NULL;
161) Display employee name and department name for each employee.
SQL>
select ename, dname from emp, dept
where
emp.deptno = dept.deptno;
162)Display employee number,name and location of the department in which he is working.
SQL>
select empno, ename, loc from emp, dept
where
emp.deptno = dept.deptno;
163) Display ename,dname even if there are no employees working in a particular
department(use outer join).
SQL>
select ename, dname
from emp, dept
where
emp.deptno = dept.deptno(+);
164) Display employee name and his manager name.
SQL>
select e.ename, m.ename from emp e, emp m
where
e.mgr = m.empno;
165) Display the department name and total number of employees in each department.
SQL>
select d.dname, count(e.ename) from dept d, emp e
where
d.deptno = e.deptno
group by d.dname;

www.TechieKrishnaKayaking.com 42

SQL Notes

166)Display the department name along with total salary in each department.
SQL>
select dname, sum(sal) from emp, dept
where
emp.deptno = dept.deptno
group by dname;
167) Display itemname and total sales amount for each item.
SQL>
select itemname, sum(sale) from item
group by itemname;
168) Write a Query To Delete The Repeted Rows from emp table;
SQL>
DELETE emp
where
empno IN
(select empno from emp
INTERSECT
select empno from emp);
-----
DELETE emp
where
empno IN
(select empno from emp group by empno having count(empno) > 1);
169) TO DISPLAY 5 TO 7 ROWS FROM A TABLE
SQL>
select * from emp where rownum <= 7
MINUS
select * from emp where rownum < 5;
170) DISPLAY TOP N ROWS FROM TABLE?
SQL>
select * from emp where rownum <= N;
171) DISPLAY TOP 3 SALARIES FROM EMP;
SQL>
select * from (select * from emp order by sal desc)
where
rownum < 4;
172) DISPLAY 9th RECORD FROM THE EMP TABLE?
SQL>
SELECT *
FROM (
SELECT e.*, ROWNUM AS rnum
FROM EMP e

www.TechieKrishnaKayaking.com 43

SQL Notes

)
WHERE rnum = 9;
select * from emp where rownum < 10
MINUS
select * from emp where rownum < 9;
----
ALITER
select * from (select * from emp order by rowid) where rownum < 10
minus
select * from (select * from emp order by rowid) where rownum < 9;
173) Write a query to find list the name of those employees starting with 'A' and with 5
character in length.
SQL>
select ename from emp where ename like 'A%' and length (ename)=5;
174) Write a query to calculate nth number of salary.
SQL>
select ename,sal from emp e where 3-1=(select count(distinct sal) from emp p where
p.sal>e.sal);
175) Write a query to display the employee no and total salary for all the employee.
SQL>
select empno, sal+nvl(comm,0) as total_sal from emp;
176) Display the department number and total number of employee working in each
department.
SQL>
select deptno,count(deptno) from emp group by deptno;
177) Display the name of employee who are working as clerk ,salesman, or analyst and
salary more then 3000.
SQL>
select ename from emp where job='CLERK' or job='SALESMAN' or job='ANALYST'
and sal>3000;
178) Write a query to calculate empno,ename,sal daily sal of all employee in the asc order of
annual sal.
SQL>
select empno,ename,sal,sal/30,12*sal annsal from emp order by annsal asc;
179) Write a query to display the current date.
SQL>
select sysdate from dual;
180) select the name of the employee whose name is exactly five charcater in length.
SQL>

www.TechieKrishnaKayaking.com 44

SQL Notes

select ename from emp where length(ename)=5;
181) Display the names of the employee in propercase.
SQL>
select initcap(ename) from emp;
182).find out the top 5 earners of company?
SQL>
select * from (select * from emp order by sal) where rownum<=5;
183).Display those employee who are working in sales or research?
SQL>
SELECT ENAME FROM EMP WHERE DEPTNO IN(SELECT DEPTNO FROM
DEPT WHERE
DNAME IN('SALES','RESEARCH'));
184).Display those employees who joined the company before 15 of the month?
SQL>
select ename from emp where to_char(hiredate,'DD')<15;
185).Display the name of the department where no employee working.
SQL>
select dname from dept where deptno not in (select deptno from emp);
186).How to create duplicate table in sql?
SQL>
create table ashu as select * from emp;
187).Display all enames in reverse order?(KRISHNA:ANHSIRK).
SQL>
SELECT REVERSE(ENAME)FROM EMP;
188).Now increase the length of ename column to 30 characters.
SQL>
alter table emp modify(ename varchar2(30));
189).Now increase the length of ename column to 30 characters.
SQL>
alter table emp modify(ename varchar2(30));
190). Get names & marks of top 3 students.
SQL>
select sname, rank() over (over by maarks desc) from stud
where
rownum < 4;
191). Display empoyee details of top 3 sal and their sal diffenence.
SQL>

www.TechieKrishnaKayaking.com 45

SQL Notes

select * from
(select e.*, (select max(sal) from emp)-e.sal as saldiff
from emp e order by sal desc)

where rownum < 4;
192). WAQ to delete the duplicate data, original should be there.
SQL>
DELETE FROM emp
where
EMPNO IN (select empno from emp group by empno having count(empno) > 1);
193). Display all duplicate records.
SQL>
select * from emp
where
empno IN (select empno from emp
group by empno
having count(empno) > 3);
194). WAQ to show the top 5 employee names in order in upper case.
SQL>
Select rownum, UPPER(ename) from emp where rownum between 1 and 5;
---
select upper(ename) from (select ename, row_number() over (order by ename) from
emp where rownum < 6;
---
select upper(ename) from
(select ename, row_number() over (order by ename) from emp
where rownum < 6
order by ename);
---
Select UPPER(ename) from(select ename, rank() over (order by ename asc) as rk
from emp) where rk<6;
195). WAQ to display the details of the employees who are in a department where at least 3
employees are working.
SQL>
select * from emp
where
deptno IN (select deptno from emp
group by deptno
having count(deptno) > 3);

196). Get all those empolyees who worked in all these 3 location (CHN, BNG, HYD).
SQL>
select id from pwc where loc = 'BNG'
INTERSECT
select id from pwc where loc = 'HYD'

www.TechieKrishnaKayaking.com 46

SQL Notes

INTERSECT
select id from pwc where loc = 'CHN';
197). Display running salaries. Sal of the emplyess in order, the next salary should be
summed with the previous salary.
SQL>
select ename, sal,
sum(sal) over (order by sal) as runsal
from emp;
198). Delete duplicate records.
SQL>
DELETE emp where
empno IN
(select empno from emp group by empno having count(empno) > 1);
199). Display the original records.
SQL>
select id from pwc where
rowid IN (select min(rowid) from pwc group by id);
200). Display the duplicates records.
SQL>
select id from pwc where
rowid NOT IN (select min(rowid) from pwc group by id);
201). Delete the duplicate records.
SQL>
DELETE PWC where
rowid NOT IN (select min(rowid) from pwc group by id);
=====
DELETE emp where
empno IN
(select empno from emp group by empno having count(empno) > 1);
202). Write an SQL query to fetch the no. of workers for each department in the descending
order.
SQL>
select deptno, count(empno) from emp group by deptno order by count(empno) desc;
203). DISPLAY ALL THE JOBS THOSE EXIST IN DEPT 20 & NOT IN DEPT 10, 30.
SQL>
select job from emp where deptno = 20
minus
select job from emp where deptno in (10,30);
204). Write an SQL query that fetches the unique values of DEPARTMENT from Worker
table and prints its length.

www.TechieKrishnaKayaking.com 47

SQL Notes

SQL>
select distinct(length(deptno)) from emp;
205). WAQ TO DISPLAY LAST 10 RECORDS IN EMP.
SQL>
select * from (select * from emp order by rowid desc) where rownum < 11;
206). Nth Higest salary
SQL>
select empno, ename, sal from emp e1
where 5-1 = (select count(distinct sal)
from emp e2
where e2.sal > e1.sal);
207). Display 1st 50% data
SQL>
select * from (select * from emp order by rowid)
where rownum < (select count(empno)/2 from emp);

208). Display last 50% data
SQL>
select * from (select * from emp order by rowid desc)
where
rownum < (select count(empno)/2 from emp);
209). Display alternate records from the table.
SQL>
SELECT * FROM (
SELECT emp.*, Row_Number() OVER(ORDER BY empno) AS RowNumber FROM emp)
t
WHERE mod(t.RowNumber,2) <> 0;
210). Display all the dulicates in the table.
SQL>
select * from emp
where
rowid not in (select min(rowid) from emp group by rowid);
---
select * from pwc
where
rowid not in (select min(rowid) from pwc group by id);
211). WAQ to find the heighest salary whose job ends with 'man' letter.
sql>
select max(sal) from emp
where job like '%man';

www.TechieKrishnaKayaking.com 48

SQL Notes

select substr(job,length(job)-2) from emp;
select * from emp
where substr(job,length(job)-2) = 'MAN';
212). What is output of this query - Select INSTR('Mississippi','i',3,3) FROM DUAL;
SQL>
11 -- starts from 3 & finds the 3rd occurance
213). DEPT wise highest salary in an org
SQL>
select deptno, max(sal) from emp group by deptno;
select d.dname, max(e.sal)
from emp e, dept d
where e.deptno = d.deptno
group by d.dname;
select e.deptno, d.dname, max(sal) over (partition by e.deptno) as dsal
from emp e, dept d
where e.deptno = d.deptno;
select e.deptno, d.dname, rank() over (order by sal) as rank
from emp e, dept d
where e.deptno = d.deptno;
214). TABLE1
a b c
1 2 1
2 3 5
5 4 6
1 2 1
7 6 3
2 3 5
7 4 2
WAQ to find the duplicate rows and how many times it is present in the above table
SQL>
select a, count(a) from table1 group by a having count(a) > 1
union all
select b, count(b) from table1 group by b having count(b) > 1
union all
select c, count(c) from table1 group by c having count(c) > 1;
---------
select a,b,c from table1 group by a,b,c; --having count(a) >1 and count(b) >1 and
count(c)>2;

www.TechieKrishnaKayaking.com 49

SQL Notes

215). The table contains First name and Last name both one below another single column.
Expected result Should be like this.
TAB_NAME: NAME
FNLNAME
--------------------
PRAYAG
VERMA
ASHOK
KUMAR
RAHUL
RAWAT
SACHIN
KUMAR
RAKESH
KUMAR
VIKASH
ORAON
SHIV
PRASAD

NAME
--------------------
PRAYAG VERMA
ASHOK KUMAR
RAHUL RAWAT
SACHIN KUMAR
RAKESH KUMAR
VIKASH ORAON
SHIV PRASAD
SQL>
select substr(wm_concat(ename),0,instr(wm_concat(ename),',')-1) || ' ' ||
substr(wm_concat(ename),instr(wm_concat(ename),',')+1)
as fullname from empname group by eno;
=========
select wm_concat(ename) as fullname from empname group by eno;
---
select a.ename ||' ' || b.ename as FULLNAME from empname a, empname b
where
a.eno = b.eno
and
a.eno IN
(
SELECT distinct(eno) FROM (

www.TechieKrishnaKayaking.com 50

SQL Notes

SELECT eno, row_number() over (order by eno) AS rn FROM empname) s
where mod(s.rn,2) = 0
INTERSECT
SELECT distinct(eno) FROM (
SELECT eno, row_number() over (order by eno) AS rn FROM empname) t
where mod(t.rn,2) <> 0
)
;

216). WAQ to display if the salary is positive/negative or neutral.
SQL>
select sal,
case
when sal < 0 then 'Negative'
when sal > 0 then 'Positive'
else 'Neutral'
end pos_or_neg
from emp;
217). WAQ to display the running salary & department by running salary.
SQL>
select deptno, empno, ename, sal,
sum(sal) over (order by sal) as running_salary,
sum(sal) over (partition by deptno) as dept_salary
from emp;
218). WAQ to display top 3 earners in a dept.
SQL>
select deptno, empno, ename, sal from emp
where deptno IN
(select distinct(deptno) from emp
where empno IN
(select empno from emp
where sal IN (select max(sal) from emp group by deptno))
and rownum < 3);
219). WAQ to display higest sal and their deptarment.
SQL>
select a.deptno, b.dname,
row_number() over (order by sal desc) as num,
max(sal) over (partition by a.deptno) as sal
from emp a, dept b
where a.deptno = b.deptno;
220). WAQ to display the max & minimum salary in a single row.
SQL>
select

www.TechieKrishnaKayaking.com 51

SQL Notes

min(ename) keep (dense_rank first order by sal) as min_name, min(sal),
max(ename) keep (dense_rank last order by sal) as max_name, max(sal)
from emp;
221). WAQ to display the max & minimum salary in a single row department wise.
SQL>
select
min(ename) keep (dense_rank first order by sal) as min_name, min(sal),
max(ename) keep (dense_rank last order by sal) as max_name, max(sal)
from emp group by deptno;
222). WAQ to to display all the employees with the lowest & higest salary in the emp table
department wise.
SQL>
select empno, ename, deptno, sal,
min(ename) keep (dense_rank first order by sal) over (partition by deptno) as lowsal,
min(sal) keep (dense_rank first order by sal) over (partition by deptno) as lowsal,
max(ename) keep (dense_rank last order by sal) over (partition by deptno) as
highestsal,
max(sal) keep (dense_rank last order by sal) over (partition by deptno) as highsal
from emp;

=============== VARIABLE PAY
223). WAQ to give bonus to all employees who have
1. experience more then 10 years. Give 10%
2. Experience 5 years 5%
Others no bonus.
Also display the total sal with bonus & variable pay.
SQL>
select e.id, e.name, e.ph, e.g, e.city, e.dep, e.sal, b.bonus,
TO_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate, 'yyyy') as exp,
CASE
WHEN (TO_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate, 'yyyy')) > 10 THEN sal*.10
WHEN (TO_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate, 'yyyy') < 10 AND
TO_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate, 'yyyy') < 5 THEN sal*.5
ELSE sal*0.3crea
END as VAR_PAY
from emp e, bonus b order by id;
--------
VIEW -
1. VIEW - 20 years
create view vpay2_v as (select * from emp where TO_CHAR(sysdate,'yyyy') -
TO_CHAR(hiredate, 'yyyy') > 20);

www.TechieKrishnaKayaking.com 52

SQL Notes

2. VIEW - 10 years
create view vpay10_v as (select * from emp where TO_CHAR(sysdate,'yyyy') -
TO_CHAR(hiredate, 'yyyy') > 10);
/
select * from emp where id in (select id from vpay2_v);select * from emp where id in (select
id from vpay2_v);
/
Alter table emp add var_sal
Update table emp
/
=============
*EXPERIENCE*
Update emp set exp = O_CHAR(sysdate,'yyyy') - TO_CHAR(hiredate, 'yyyy');
/
*NOW GIVE VARIABLE PAY*
Update emp
set varpay =
(Case
When exp > 20 then sal * 0.1
When exp > 10 and exp < 20 then sal * 0.5
Else sal * 0.3
End);
/
*DISPLAY ALL INFO*
Select E.ID, E.NAME, E.CITY, (E.SAL *12) as YEARSAL, E.DEP, E.EXP, E.VARPAY,
((E.SAL*12) + (E.VARPAY*12) + (select B.bonus from bonus B where B.EID = E.ID)*12) as
TOTPAY from emp E order by TOTPAY
Select E.ID, E.NAME, E.CITY, (E.SAL *12) as YEARSAL, E.DEP, E.EXP, E.VARPAY,
((E.SAL*12) + (E.VARPAY*12) + NVL((select B.bonus from bonus B where B.EID =
E.ID),0)*12) as TOTPAY from emp E order by TOTPAY desc;

224). CREATE TABLE WHERE PHONE NUMBER IS 10 DIGIT ONLY
SQL>
create table emp1
(eid number(10) primary key,
ename varchar(10) not null,
sal number(10) not null,
city varchar(5),
ph number(10) check (length(ph)>9 and length(ph)<11));

225). There are 3 tabes - EMP, DEPT, INCENTIVE
WAQ to find the higest paid incentive for emplyoee of each dept.
SQL>
select e.ename, d.dname,

www.TechieKrishnaKayaking.com 53

SQL Notes

(max(e.sal) + nvl(i.amt,0)) over (partition by e.deptid) as sal2020
from emp e, dept d, incen i
where to_char(i.date,'yyyy') = 2020
and
e.deptid = d.deptid
and
e.empid = i.empid;
226). WAQ to get the latest incentive paid to each employee, the dates should be in MON &
YEAR Format only.
SQL>
select e.ename, i.amt, to_char(e.idate, 'MON-YYYY') as incen_date
from emp e, incen i
where
i.date in (select max(date) from incen group by empid);

227). WAQ to display the phone number which has total outgoing call duration greater than
total incoming call duration. Only one phone number should be displayed.
SQL>
select ph_num from calldetail
where
(select sum(duration) from calldetails where type = 'IN' group by type) < (select
sum(duration) from calldetails where type = 'OUT')
and
rownum = 1
group by ph_num;
EMP TRY
select empno from emp
where
((select sum(sal) from emp where job = 'ANALYST') < (select sum(sal) from emp))
and
rownum = 1
group by empno;

SELECT DISTINCT(PH_NUM) FROM
(SELECT PH_NUM, SUM(DURATION) over (partition by ph_num order by duration)
AD FROM CALLDETAILS
WHERE TYPE='OUT'),
(SELECT SUM(DURATION) AD1 FROM CALLDETAILS
WHERE TYPE='IN'
GROUP BY PH_NUM)
WHERE AD>AD1
and
rownum = 1;

www.TechieKrishnaKayaking.com 54

SQL Notes

228). Top 5 license from each state in US. Table - LIC_DETAILS - Columns - LIC_NUM |
STATE
SQL>
select lic_num
from vehicle_info
where lic_num IN
(select lic_num from vehicle_info
where rownum < 6
group by state
order by lic_num);
-----------------------------------------
229). Source & Target
Source
KRISHNA007DUDE
Target
KRISHNA | 007 | DUDE
SQL>
select regexp_instr('KRISHNA007','[0-9]')
from dual;
select substr('KRISHNA007',0, regexp_instr('KRISHNA007','[0-9]')-1)
from dual;
select
substr('KRISHNA007DUDE',0,regexp_instr('KRISHNA007DUDE','[0-9]')-1)
,substr('KRISHNA007DUDE',regexp_instr('KRISHNA007DUDE','[0-9]'),)
,
substr('KRISHNA007DUDE',regexp_instr('KRISHNA007DUDE','[0-9]'),regexp_instr('KRISHN
A007','[0-9]'),-1)
from dual;

select
substr('KRISHNA007DUDE',regexp_instr('KRISHNA007DUDE','[0-9]'),
regexp_instr('KRISHNA007DUDE','[A-Z]'))
FROM DUAL;
-----------------------------------------
230)
/*
QUESTION - What is the query to retrieve the maximum salary for each department
where employees have job titles of 'Clerk', 'Salesman', or 'Manager',
and only include departments where the maximum salary is greater than 2000,
order the data in descending order of the maximum salary?

www.TechieKrishnaKayaking.com 55

SQL Notes

*/
SELECT DEPTNO, MAX(SAL)
FROM EMP
WHERE JOB IN ('CLERK', 'SALESMAN', 'MANAGER')
GROUP BY DEPTNO
HAVING MAX(SAL) > 2000
ORDER BY MAX(SAL) DESC;
SELECT deptno, MAX(SAL) FROM EMP
WHERE JOB IN ('CLERK', 'SALESMAN', 'MANAGER')
GROUP BY DEPTNO
HAVING MAX(SAL) > 2000
ORDER BY MAX(SAL) DESC;

-----------------------------------------
231)
/* *** TECHIE KRISHNA KAYAKING ***
QUESTION - ANALYTICAL FUNCTIONS - Difference between RANK(), DENSE_RANK(),
ROW_NUMBER()
*/
SELECT * FROM [DATABASE_NAME].[SCHEMA_NAME].[TABLE_NAME];
SELECT ENAME, JOB, SAL,
RANK() OVER (ORDER BY SAL) RANKK,
DENSE_RANK() OVER (ORDER BY SAL) DENSE_RANKK,
ROW_NUMBER() OVER (ORDER BY SAL) ROW_NUMBERR
FROM SCOTT.EMP;

SELECT SAL, DENSE_RANK() OVER (ORDER BY SAL) DENSE_RANKK
FROM SCOTT.EMP;
SELECT SAL, ROW_NUMBER() OVER (ORDER BY SAL) ROW_NUMBERR
FROM SCOTT.EMP;

-----------------------------------------
232)
/*
QUESTION - display id & comment.
Display the non matching from source & target & mismatch.

www.TechieKrishnaKayaking.com 56

SQL Notes

SOURCE
id | name
1 | A
2 | B
3 | C
4 | D
TARGET
id | name
1 | A
2 | B
4 | F
5 | G
OUTPUT
id | comment
3 | new in source
5 | new in target
4 | mismatch
*/
CREATE TABLE src (id NUMBER(2) PRIMARY KEY , name varchar(5));
INSERT INTO src VALUES (1, 'A');
INSERT INTO src VALUES (2, 'B');
INSERT INTO src VALUES (3, 'C');
INSERT INTO src VALUES (4, 'D');
CREATE TABLE tgt (id NUMBER(2) PRIMARY KEY , name varchar(5));
INSERT INTO tgt VALUES (1, 'A');
INSERT INTO tgt VALUES (2, 'B');
INSERT INTO tgt VALUES (4, 'F');
INSERT INTO tgt VALUES (5, 'G');

SELECT * FROM src;
SELECT * FROM tgt;
-- DELETE FROM tgt WHERE id = 6;
SELECT s.id, s.name,
CASE
WHEN (s.id, s.name) NOT IN (SELECT id, name FROM tgt) THEN 'New to source'
WHEN (t.id, t.name) NOT IN (SELECT id, name FROM src) THEN 'New to target'
WHEN (s.id = t.id AND s.name <> t.name) THEN 'Mismatch'

www.TechieKrishnaKayaking.com 57

SQL Notes

END
FROM src s , tgt t;

SELECT DISTINCT (id) ,
CASE
WHEN id IN (SELECT id FROM SRC MINUS SELECT id FROM tgt) THEN 'New to
Source'
WHEN id IN (SELECT id FROM TGT MINUS SELECT id FROM SRC) THEN 'New to
Target'
WHEN (id, name) IN (SELECT id, name FROM SRC MINUS SELECT id, name
FROM TGT) THEN 'Mismatch'
WHEN (id, name) IN (SELECT id, name FROM TGT MINUS SELECT id, name
FROM SRC) THEN 'Mismatch'
END
FROM ((
SELECT id, name FROM SRC
UNION
SELECT id, name FROM tgt)
MINUS
(SELECT id, name FROM src
INTERSECT
SELECT id, name FROM tgt));

-----------------------------------------
233)
/*
* nameofperson | name_of_parent | status
* A | x | Alive
* B | y | Dead
* x | x1 | Alive
* y | y1 | Alive
* x1 | x2 | Alive
* y1 | y2 | Dead
*
* Find all person who's grandparent is alive
*
*/
-- DROP TABLE parent;
CREATE TABLE parent
(name char(2), parent char(2), status varchar (5));
INSERT INTO parent VALUES ('a', 'x', 'Alive');
INSERT INTO parent VALUES ('b', 'y', 'Dead');

www.TechieKrishnaKayaking.com 58

SQL Notes

INSERT INTO parent VALUES ('x', 'x1', 'Alive');
INSERT INTO parent VALUES ('y', 'y1', 'Alive');
INSERT INTO parent VALUES ('x1', 'x2', 'Alive');
INSERT INTO parent VALUES ('y1', 'y2', 'Dead');
SELECT * FROM parent;
-- SOLUTION
SELECT DISTINCT p.name
FROM parent p
JOIN parent parent ON p.name = parent.name
JOIN parent grandparent ON parent.name = grandparent.name
WHERE grandparent.status = 'Alive';