-- ============================================================
-- CHAPTER 1: ADVANCED SQL - Window Functions
-- Practice in: Databricks SQL / Any SQL Engine
-- Topics: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD,
--         FIRST_VALUE, LAST_VALUE, NTILE, RUNNING TOTALS
-- ============================================================

-- -------------------------------------------------------------
-- SETUP: Sample Tables
-- -------------------------------------------------------------
-- employees(emp_id, name, dept, salary, hire_date)
-- orders(order_id, customer_id, order_date, amount, region)
-- sales(sale_id, salesperson, sale_date, revenue, product)

-- ==============================
-- 1. ROW_NUMBER, RANK, DENSE_RANK
-- ==============================

-- Q: Rank employees by salary within each department
SELECT
    emp_id,
    name,
    dept,
    salary,
    ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS row_num,
    RANK()       OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dense_rnk
FROM employees;

-- Q: Get top 2 earners per department (interview classic!)
WITH ranked AS (
    SELECT *,
        DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dr
    FROM employees
)
SELECT * FROM ranked WHERE dr <= 2;

-- ==============================
-- 2. LAG and LEAD — MoM / YoY comparisons
-- ==============================

-- Q: Compare each month's revenue to the previous month
SELECT
    sale_date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY sale_date)               AS prev_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY sale_date)     AS mom_change,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY sale_date))
        / NULLIF(LAG(revenue, 1) OVER (ORDER BY sale_date), 0) * 100, 2
    )                                                        AS mom_pct_change
FROM sales;

-- Q: For each order, show the next order date for the same customer
SELECT
    order_id,
    customer_id,
    order_date,
    LEAD(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_date
FROM orders;

-- ==============================
-- 3. Running Totals & Moving Averages
-- ==============================

-- Q: Running total of revenue by salesperson
SELECT
    salesperson,
    sale_date,
    revenue,
    SUM(revenue) OVER (PARTITION BY salesperson ORDER BY sale_date
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM sales;

-- Q: 3-day moving average of revenue
SELECT
    sale_date,
    revenue,
    AVG(revenue) OVER (ORDER BY sale_date
                       ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3d
FROM sales;

-- ==============================
-- 4. FIRST_VALUE / LAST_VALUE
-- ==============================

-- Q: Show each employee's salary vs. the highest earner in their dept
SELECT
    name,
    dept,
    salary,
    FIRST_VALUE(salary) OVER (PARTITION BY dept ORDER BY salary DESC
                               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS dept_max_salary
FROM employees;

-- ==============================
-- 5. NTILE — Percentile buckets
-- ==============================

-- Q: Bucket employees into salary quartiles
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS salary_quartile
FROM employees;

-- ==============================
-- 6. PERCENT_RANK / CUME_DIST
-- ==============================

-- Q: What percentile is each employee's salary?
SELECT
    name,
    salary,
    ROUND(PERCENT_RANK() OVER (ORDER BY salary) * 100, 2) AS percentile_rank,
    ROUND(CUME_DIST()    OVER (ORDER BY salary) * 100, 2) AS cumulative_dist
FROM employees;

-- ==============================
-- INTERVIEW PATTERNS TO KNOW
-- ==============================
-- 1. "Find Nth highest salary" → DENSE_RANK or OFFSET
-- 2. "Find consecutive login days" → ROW_NUMBER + date - ROW_NUMBER trick
-- 3. "Find gaps in sequences" → LAG/LEAD
-- 4. "Running total by category" → SUM OVER PARTITION
-- 5. "Compare current vs previous period" → LAG with date truncation
