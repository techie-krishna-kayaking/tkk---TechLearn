-- ============================================================
-- CHAPTER 1: ADVANCED SQL - CTEs, Subqueries & Query Optimization
-- Practice in: Databricks SQL
-- Topics: CTEs, Recursive CTEs, correlated subqueries,
--         EXPLAIN, query optimization tricks
-- ============================================================

-- ==============================
-- 1. CTEs vs Subqueries
-- ==============================

-- Q: Find departments where avg salary > company avg salary
-- Using CTE (preferred in interviews — readable)
WITH dept_avg AS (
    SELECT dept, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY dept
),
company_avg AS (
    SELECT AVG(salary) AS company_avg_sal FROM employees
)
SELECT d.dept, d.avg_sal, c.company_avg_sal
FROM dept_avg d
CROSS JOIN company_avg c
WHERE d.avg_sal > c.company_avg_sal;

-- Same using subquery (understand both)
SELECT dept, AVG(salary) AS avg_sal
FROM employees
GROUP BY dept
HAVING AVG(salary) > (SELECT AVG(salary) FROM employees);

-- ==============================
-- 2. Recursive CTE
-- ==============================

-- Q: Build employee → manager hierarchy (org chart)
-- Table: emp_hierarchy(emp_id, name, manager_id)
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level employees (no manager)
    SELECT emp_id, name, manager_id, 0 AS level, name AS path
    FROM emp_hierarchy
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: join to children
    SELECT e.emp_id, e.name, e.manager_id,
           o.level + 1,
           o.path || ' > ' || e.name
    FROM emp_hierarchy e
    JOIN org_chart o ON e.manager_id = o.emp_id
)
SELECT * FROM org_chart ORDER BY path;

-- Q: Generate a number series 1-10 (useful trick)
WITH RECURSIVE nums AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 10
)
SELECT * FROM nums;

-- ==============================
-- 3. Correlated Subqueries
-- ==============================

-- Q: For each employee, find if their salary > dept average
SELECT name, dept, salary
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.dept = e1.dept   -- correlated on outer query's dept
);

-- Q: Find customers who placed an order in every month of 2023
SELECT customer_id
FROM orders
WHERE YEAR(order_date) = 2023
GROUP BY customer_id
HAVING COUNT(DISTINCT MONTH(order_date)) = 12;

-- ==============================
-- 4. Complex JOINs
-- ==============================

-- Q: Self-join — find pairs of employees in same dept with salary diff > 10000
SELECT a.name AS emp1, b.name AS emp2, a.dept, ABS(a.salary - b.salary) AS sal_diff
FROM employees a
JOIN employees b ON a.dept = b.dept AND a.emp_id < b.emp_id
WHERE ABS(a.salary - b.salary) > 10000;

-- Q: CROSS JOIN use case — all combinations for A/B test assignment
SELECT u.user_id, v.variant
FROM users u
CROSS JOIN (SELECT 'control' AS variant UNION ALL SELECT 'treatment') v;

-- ==============================
-- 5. CASE WHEN + Pivoting
-- ==============================

-- Q: Pivot monthly revenue into columns (manual pivot)
SELECT
    salesperson,
    SUM(CASE WHEN MONTH(sale_date) = 1  THEN revenue ELSE 0 END) AS Jan,
    SUM(CASE WHEN MONTH(sale_date) = 2  THEN revenue ELSE 0 END) AS Feb,
    SUM(CASE WHEN MONTH(sale_date) = 3  THEN revenue ELSE 0 END) AS Mar,
    SUM(CASE WHEN MONTH(sale_date) = 12 THEN revenue ELSE 0 END) AS Dec
FROM sales
WHERE YEAR(sale_date) = 2023
GROUP BY salesperson;

-- Q: Classify customers by spend tier
SELECT
    customer_id,
    total_spend,
    CASE
        WHEN total_spend >= 10000 THEN 'Platinum'
        WHEN total_spend >= 5000  THEN 'Gold'
        WHEN total_spend >= 1000  THEN 'Silver'
        ELSE 'Bronze'
    END AS tier
FROM (
    SELECT customer_id, SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
) t;

-- ==============================
-- 6. NULL Handling (Interview Trap!)
-- ==============================

-- NULLIF — avoid division by zero
SELECT revenue / NULLIF(impressions, 0) AS ctr FROM ads;

-- COALESCE — fallback values
SELECT name, COALESCE(phone, email, 'no_contact') AS contact FROM users;

-- IS NULL vs = NULL (= NULL never works!)
SELECT * FROM employees WHERE manager_id IS NULL;  -- correct
-- SELECT * FROM employees WHERE manager_id = NULL; -- WRONG

-- ==============================
-- 7. Query Optimization Tips (Know These!)
-- ==============================
/*
  1. Avoid SELECT * — always specify columns
  2. Filter early — push WHERE before JOIN
  3. Use EXPLAIN / EXPLAIN ANALYZE to check query plan
  4. Avoid functions on indexed columns in WHERE clause
     BAD:  WHERE YEAR(order_date) = 2023
     GOOD: WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31'
  5. Prefer JOIN over correlated subqueries for large datasets
  6. Use CTEs for readability; use subqueries inline for performance
  7. Partition pruning — filter on partition columns (Spark/Hive)
  8. Z-Ordering in Delta Lake for multi-column filtering
*/

-- EXPLAIN example (Databricks)
EXPLAIN SELECT * FROM orders WHERE customer_id = 101;
