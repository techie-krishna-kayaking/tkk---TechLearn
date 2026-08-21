-- ============================================================
-- CHAPTER 1: ADVANCED SQL - Classic Interview Problems
-- Practice in: Databricks SQL
-- These exact patterns appear at Google, Meta, Amazon, Flipkart
-- ============================================================

-- ==============================
-- PROBLEM 1: Consecutive Login Days
-- ==============================
-- Table: user_logins(user_id, login_date)
-- Q: Find users who logged in for 3+ consecutive days

WITH numbered AS (
    SELECT
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
    FROM (SELECT DISTINCT user_id, login_date FROM user_logins) t
),
grouped AS (
    SELECT
        user_id,
        login_date,
        DATE_SUB(login_date, rn) AS grp   -- same group = consecutive
    FROM numbered
),
streaks AS (
    SELECT user_id, grp, COUNT(*) AS streak_len
    FROM grouped
    GROUP BY user_id, grp
)
SELECT DISTINCT user_id
FROM streaks
WHERE streak_len >= 3;

-- ==============================
-- PROBLEM 2: Median Salary
-- ==============================
-- Q: Find median salary (SQL has no MEDIAN in all dialects)

WITH ordered AS (
    SELECT salary,
           ROW_NUMBER() OVER (ORDER BY salary)                     AS rn,
           COUNT(*) OVER ()                                        AS total
    FROM employees
)
SELECT AVG(salary) AS median_salary
FROM ordered
WHERE rn IN (FLOOR((total + 1) / 2.0), CEIL((total + 1) / 2.0));

-- ==============================
-- PROBLEM 3: Retention Rate
-- ==============================
-- Table: user_activity(user_id, activity_date)
-- Q: What % of Jan users were active in Feb? (Month-1 retention)

WITH jan_users AS (
    SELECT DISTINCT user_id
    FROM user_activity
    WHERE activity_date BETWEEN '2024-01-01' AND '2024-01-31'
),
feb_users AS (
    SELECT DISTINCT user_id
    FROM user_activity
    WHERE activity_date BETWEEN '2024-02-01' AND '2024-02-29'
)
SELECT
    COUNT(f.user_id) AS retained_users,
    COUNT(j.user_id) AS jan_users,
    ROUND(COUNT(f.user_id) * 100.0 / COUNT(j.user_id), 2) AS retention_pct
FROM jan_users j
LEFT JOIN feb_users f ON j.user_id = f.user_id;

-- ==============================
-- PROBLEM 4: Nth Highest Salary
-- ==============================
-- Q: Find 3rd highest salary (without LIMIT — interview style)

SELECT MIN(salary) AS third_highest
FROM (
    SELECT DISTINCT salary
    FROM employees
    ORDER BY salary DESC
    LIMIT 3
) t;

-- Alternative with DENSE_RANK:
WITH ranked AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
    FROM employees
)
SELECT salary FROM ranked WHERE dr = 3 LIMIT 1;

-- ==============================
-- PROBLEM 5: Duplicate Detection
-- ==============================
-- Q: Find duplicate rows in orders table

SELECT order_id, COUNT(*) AS cnt
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Q: Delete duplicates, keep the one with highest order_id (Databricks)
WITH deduped AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id, order_date, amount
                              ORDER BY order_id DESC) AS rn
    FROM orders
)
SELECT * FROM deduped WHERE rn = 1;  -- in Databricks, use CREATE OR REPLACE TABLE

-- ==============================
-- PROBLEM 6: First Purchase per Customer
-- ==============================
WITH first_orders AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS rn
    FROM orders
)
SELECT customer_id, order_id, order_date, amount
FROM first_orders
WHERE rn = 1;

-- ==============================
-- PROBLEM 7: Gaps in Data / Missing Dates
-- ==============================
-- Q: Find dates with no sales between Jan and Mar 2024

WITH all_dates AS (
    -- Generate all dates (use calendar table or recursive CTE)
    SELECT EXPLODE(SEQUENCE(DATE('2024-01-01'), DATE('2024-03-31'), INTERVAL 1 DAY)) AS dt
),
sale_dates AS (
    SELECT DISTINCT DATE(sale_date) AS dt FROM sales
    WHERE sale_date BETWEEN '2024-01-01' AND '2024-03-31'
)
SELECT a.dt AS missing_date
FROM all_dates a
LEFT JOIN sale_dates s ON a.dt = s.dt
WHERE s.dt IS NULL;

-- ==============================
-- PROBLEM 8: Market Share per Category
-- ==============================
SELECT
    product_category,
    SUM(revenue)                                   AS category_revenue,
    SUM(SUM(revenue)) OVER ()                      AS total_revenue,
    ROUND(SUM(revenue) * 100.0
          / SUM(SUM(revenue)) OVER (), 2)          AS market_share_pct
FROM sales
GROUP BY product_category
ORDER BY market_share_pct DESC;

-- ==============================
-- PROBLEM 9: Sessionization (hard - asked at Meta/Google)
-- ==============================
-- Table: page_views(user_id, event_time)
-- Session = gap of > 30 min between events = new session

WITH lagged AS (
    SELECT
        user_id,
        event_time,
        LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_time
    FROM page_views
),
session_flags AS (
    SELECT *,
        CASE WHEN prev_time IS NULL
                  OR TIMESTAMPDIFF(MINUTE, prev_time, event_time) > 30
             THEN 1 ELSE 0 END AS new_session
    FROM lagged
),
sessions AS (
    SELECT *,
        SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
    FROM session_flags
)
SELECT user_id, session_id,
       MIN(event_time) AS session_start,
       MAX(event_time) AS session_end,
       COUNT(*) AS events_in_session
FROM sessions
GROUP BY user_id, session_id;
