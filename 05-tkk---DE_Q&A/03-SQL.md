# SQL — Top 35 Practical & Programming Interview Questions

> **Target:** Senior / Lead / Staff Data Engineer
> **Goal:** 70+ LPA product-based companies
> **Focus:** Practical SQL, analytical SQL, window functions, CTEs, joins, deduplication, time-series problems, data-quality problems, ETL/ELT problems, performance tuning and interview coding.
>
> **Dialect used:** Mostly ANSI/PostgreSQL-style SQL because it is easy to adapt. Where Snowflake-specific syntax is useful, it is called out explicitly.
>
> **Important:** Do not memorize only the query. Memorize **how to think about the problem**.

---

# 0. SQL Interview Thinking Framework

When the interviewer gives you a SQL problem, think:

```text
1. What is the required output grain?
          ↓
2. What is the source grain?
          ↓
3. Which tables are required?
          ↓
4. What are the join keys?
          ↓
5. Can joins multiply rows?
          ↓
6. Filter before or after aggregation?
          ↓
7. Do I need GROUP BY?
          ↓
8. Do I need a window function?
          ↓
9. Do I need a CTE?
          ↓
10. How should NULLs behave?
          ↓
11. What happens with duplicates?
          ↓
12. What happens at large scale?
          ↓
13. Can I optimize the query?
```

The most important senior-level question is:

> **"What is the grain of the result?"**

For example:

```text
customer grain
order grain
order-item grain
day grain
customer-month grain
```

Many SQL bugs are actually **grain errors**.

---

# 1. Find the second-highest salary.

## Table

```text
employee
--------
employee_id
employee_name
salary
department
```

## Solution 1 — `DENSE_RANK()`

```sql
SELECT employee_id,
       employee_name,
       salary
FROM (
    SELECT e.*,
           DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employee e
) x
WHERE rnk = 2;
```

## Why `DENSE_RANK()`?

Suppose salaries are:

```text
100000
90000
90000
80000
```

The result for rank:

```text
100000 → 1
90000  → 2
90000  → 2
80000  → 3
```

So the second-highest **distinct** salary is returned correctly.

PostgreSQL documents `dense_rank` as ranking peer groups without gaps, which is exactly what is needed for the "second distinct value" interpretation.

## Alternative

```sql
SELECT MAX(salary) AS second_highest_salary
FROM employee
WHERE salary < (
    SELECT MAX(salary)
    FROM employee
);
```

## Follow-up

### Q: What if there is no second-highest salary?

The query returns `NULL`.

### Q: `RANK()` vs `DENSE_RANK()`?

For:

```text
100
90
90
80
```

`RANK()`:

```text
1
2
2
4
```

`DENSE_RANK()`:

```text
1
2
2
3
```

---

# 2. Find the top 3 highest-paid employees in each department.

## Solution

```sql
SELECT employee_id,
       employee_name,
       department,
       salary
FROM (
    SELECT e.*,
           DENSE_RANK() OVER (
               PARTITION BY department
               ORDER BY salary DESC
           ) AS rnk
    FROM employee e
) x
WHERE rnk <= 3;
```

## Why?

The interviewer is testing:

* Window functions.
* Partitioning.
* Ranking.
* Top-N per group.

Window functions calculate over related rows while preserving individual result rows.

## Follow-up

### Q: Return exactly 3 employees even if salary ties exist.

Use:

```sql
ROW_NUMBER() OVER (
    PARTITION BY department
    ORDER BY salary DESC, employee_id
)
```

Then:

```sql
WHERE row_number <= 3
```

### Key distinction

```text
RANK / DENSE_RANK
→ business ranking with ties

ROW_NUMBER
→ exactly N rows
```

---

# 3. Remove duplicate records and retain the latest record.

## Table

```text
customer
--------
customer_id
name
email
updated_at
```

## Solution

```sql
SELECT customer_id,
       name,
       email,
       updated_at
FROM (
    SELECT c.*,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id
               ORDER BY updated_at DESC
           ) AS rn
    FROM customer c
) x
WHERE rn = 1;
```

## Logic

```text
customer_id
     ↓
partition records
     ↓
latest first
     ↓
row_number = 1
```

## Production consideration

What if timestamps are identical?

Use a deterministic tie-breaker:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC,
             ingestion_id DESC
)
```

## Follow-up

### Q: How would you physically delete duplicates?

For example:

```sql
DELETE FROM customer
WHERE ...
```

But in production I would first identify duplicates in a CTE/staging query and validate the exact rows to be deleted.

---

# 4. Find employees whose salary is greater than their department average.

## Solution

```sql
SELECT employee_id,
       employee_name,
       department,
       salary
FROM (
    SELECT e.*,
           AVG(salary) OVER (
               PARTITION BY department
           ) AS dept_avg_salary
    FROM employee e
) x
WHERE salary > dept_avg_salary;
```

## Why window function?

A normal:

```sql
GROUP BY department
```

would collapse employees into one row per department.

A window function keeps the original employee rows while adding the department-level calculation.

## Follow-up

### Q: What if the company wants employees earning at least 20% above department average?

```sql
WHERE salary > dept_avg_salary * 1.20
```

---

# 5. Find customers who have never placed an order.

## Tables

```text
customer
--------
customer_id

orders
------
order_id
customer_id
```

## Preferred solution

```sql
SELECT c.customer_id
FROM customer c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;
```

## Alternative

```sql
SELECT customer_id
FROM customer
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM orders
    WHERE customer_id IS NOT NULL
);
```

## Better interview discussion

I generally prefer `NOT EXISTS` for anti-join logic because it avoids some NULL-related pitfalls of `NOT IN`.

```sql
SELECT c.customer_id
FROM customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

## Follow-up

### Q: Why can `NOT IN` behave unexpectedly with NULL?

SQL uses three-valued logic:

```text
TRUE
FALSE
UNKNOWN
```

A NULL comparison can result in `UNKNOWN`, affecting filtering behavior.

---

# 6. Find duplicate emails.

## Solution

```sql
SELECT email,
       COUNT(*) AS cnt
FROM customer
GROUP BY email
HAVING COUNT(*) > 1;
```

## Find the complete duplicate rows

```sql
SELECT *
FROM customer
WHERE email IN (
    SELECT email
    FROM customer
    GROUP BY email
    HAVING COUNT(*) > 1
);
```

## Better scalable pattern

```sql
SELECT *
FROM (
    SELECT c.*,
           COUNT(*) OVER (
               PARTITION BY email
           ) AS email_count
    FROM customer c
) x
WHERE email_count > 1;
```

## Follow-up

### Q: What if email should be case-insensitive?

Normalize:

```sql
LOWER(TRIM(email))
```

For example:

```sql
PARTITION BY LOWER(TRIM(email))
```

---

# 7. Calculate running total of sales.

## Table

```text
sales
-----
sale_date
amount
```

## Solution

```sql
SELECT sale_date,
       amount,
       SUM(amount) OVER (
           ORDER BY sale_date
           ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
       ) AS running_total
FROM sales
ORDER BY sale_date;
```

## Output concept

```text
Date       Amount     Running Total

Jan 1       100          100
Jan 2       200          300
Jan 3       150          450
```

## Follow-up

### Q: Running total per customer?

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING
             AND CURRENT ROW
)
```

---

# 8. Calculate a 7-day rolling average.

## Solution

```sql
SELECT sale_date,
       amount,
       AVG(amount) OVER (
           ORDER BY sale_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS rolling_7_day_avg
FROM daily_sales;
```

## Important interview trap

`ROWS BETWEEN 6 PRECEDING` means **7 rows**, not necessarily **7 calendar days**.

If dates have gaps:

```text
Oct 1
Oct 2
Oct 5
Oct 10
```

then 7 rows ≠ 7 calendar days.

## Senior answer

> "Before writing the query, I would clarify whether the business means the previous seven records or the previous seven calendar days."

That distinction is exactly the kind of detail senior interviewers look for.

Window frames are part of standard window-function semantics; PostgreSQL and Snowflake document `ORDER BY` and window-frame behavior explicitly.

---

# 9. Find the highest-selling product each month.

## Table

```text
sales
-----
product_id
sale_date
amount
```

## Step 1 — Aggregate

```sql
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', sale_date) AS month,
        product_id,
        SUM(amount) AS total_sales
    FROM sales
    GROUP BY
        DATE_TRUNC('month', sale_date),
        product_id
)
```

## Step 2 — Rank

```sql
SELECT month,
       product_id,
       total_sales
FROM (
    SELECT ms.*,
           RANK() OVER (
               PARTITION BY month
               ORDER BY total_sales DESC
           ) AS rnk
    FROM monthly_sales ms
) x
WHERE rnk = 1;
```

## Thinking pattern

```text
Raw data
   ↓
Aggregate to month + product
   ↓
Rank within month
   ↓
Take rank 1
```

This **aggregate → rank** pattern is extremely important.

---

# 10. Find employees who earn more than their manager.

## Table

```text
employee
--------
employee_id
employee_name
manager_id
salary
```

## Solution

```sql
SELECT
    e.employee_id,
    e.employee_name,
    e.salary,
    m.employee_name AS manager_name,
    m.salary AS manager_salary
FROM employee e
JOIN employee m
    ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

## Why?

This is a **self join**.

```text
employee
   ↙     ↘
employee employee
  employee      manager
```

## Follow-up

### Q: How would you find employees without managers?

```sql
WHERE manager_id IS NULL
```

### Q: How would you find the highest paid employee under each manager?

Use:

```text
self join
+
ROW_NUMBER / RANK
```

---

# 11. Find consecutive login days.

## Table

```text
login
-----
user_id
login_date
```

This is a classic **gaps-and-islands** problem.

## Step 1 — Number rows

```sql
WITH x AS (
    SELECT
        user_id,
        login_date,
        login_date
          - ROW_NUMBER() OVER (
                PARTITION BY user_id
                ORDER BY login_date
            ) * INTERVAL '1 day' AS grp
    FROM login
)
```

## Step 2 — Group

```sql
SELECT
    user_id,
    MIN(login_date) AS start_date,
    MAX(login_date) AS end_date,
    COUNT(*) AS consecutive_days
FROM x
GROUP BY user_id, grp;
```

## Find users with at least 5 consecutive days

```sql
WITH x AS (
    SELECT
        user_id,
        login_date,
        login_date
          - ROW_NUMBER() OVER (
                PARTITION BY user_id
                ORDER BY login_date
            ) * INTERVAL '1 day' AS grp
    FROM login
)
SELECT user_id
FROM x
GROUP BY user_id, grp
HAVING COUNT(*) >= 5;
```

## Pattern to memorize

```text
ordered rows
    ↓
ROW_NUMBER()
    ↓
create grouping key
    ↓
GROUP BY
    ↓
islands
```

---

# 12. Find customers who purchased in January but not February.

## Solution

```sql
SELECT DISTINCT customer_id
FROM orders
WHERE EXTRACT(MONTH FROM order_date) = 1

EXCEPT

SELECT DISTINCT customer_id
FROM orders
WHERE EXTRACT(MONTH FROM order_date) = 2;
```

## Alternative — conditional aggregation

```sql
SELECT customer_id
FROM orders
GROUP BY customer_id
HAVING
    SUM(
        CASE WHEN EXTRACT(MONTH FROM order_date) = 1
             THEN 1 ELSE 0 END
    ) > 0
AND
    SUM(
        CASE WHEN EXTRACT(MONTH FROM order_date) = 2
             THEN 1 ELSE 0 END
    ) = 0;
```

## Senior point

The second approach makes the business logic explicit and can be generalized to many month-based conditions.

---

# 13. Calculate month-over-month revenue growth.

## Query

```sql
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
),
x AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_revenue
    FROM monthly
)
SELECT
    month,
    revenue,
    previous_revenue,
    ROUND(
        100.0 * (revenue - previous_revenue)
        / NULLIF(previous_revenue, 0),
        2
    ) AS growth_pct
FROM x;
```

## Important

Use:

```sql
NULLIF(previous_revenue, 0)
```

to avoid division by zero.

## Follow-up

### Q: What if the previous month's revenue is NULL?

The growth result should typically remain NULL unless the business defines a special rule.

---

# 14. Find the first order for every customer.

## Solution

```sql
SELECT customer_id,
       order_id,
       order_date
FROM (
    SELECT
        o.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
        ) AS rn
    FROM orders o
) x
WHERE rn = 1;
```

## Alternative

```sql
SELECT
    customer_id,
    MIN(order_date) AS first_order_date
FROM orders
GROUP BY customer_id;
```

## Key difference

`MIN()` only gives the date.

`ROW_NUMBER()` lets you retrieve the **entire corresponding row**.

---

# 15. Find the second order for every customer.

## Solution

```sql
SELECT customer_id,
       order_id,
       order_date
FROM (
    SELECT
        o.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
        ) AS rn
    FROM orders o
) x
WHERE rn = 2;
```

## Follow-up

### Find customers whose second order happened within 30 days of the first.

```sql
WITH ranked AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
        ) AS rn
    FROM orders
),
orders_1_2 AS (
    SELECT
        customer_id,
        MAX(CASE WHEN rn = 1 THEN order_date END) AS first_order,
        MAX(CASE WHEN rn = 2 THEN order_date END) AS second_order
    FROM ranked
    GROUP BY customer_id
)
SELECT *
FROM orders_1_2
WHERE second_order <= first_order + INTERVAL '30 days';
```

---

# 16. Find overlapping date ranges.

## Table

```text
employee_project
----------------
employee_id
start_date
end_date
```

## Two records overlap when:

```text
range1.start <= range2.end
AND
range2.start <= range1.end
```

## Query

```sql
SELECT
    a.employee_id,
    a.start_date AS a_start,
    a.end_date   AS a_end,
    b.start_date AS b_start,
    b.end_date   AS b_end
FROM employee_project a
JOIN employee_project b
    ON a.employee_id = b.employee_id
   AND a.start_date <= b.end_date
   AND b.start_date <= a.end_date
   AND a.start_date < b.start_date;
```

## Why the last condition?

Without it:

```text
A joins B
B joins A
```

creating duplicate mirror pairs.

---

# 17. Find customers with purchases on three consecutive days.

## Solution

```sql
WITH x AS (
    SELECT DISTINCT
        customer_id,
        order_date
    FROM orders
),
r AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date, 1) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS prev_date,
        LAG(order_date, 2) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS prev_2_date
    FROM x
)
SELECT DISTINCT customer_id
FROM r
WHERE order_date = prev_date + INTERVAL '1 day'
  AND prev_date = prev_2_date + INTERVAL '1 day';
```

## Why `DISTINCT` first?

If a customer has multiple orders on the same day, duplicate dates could invalidate the consecutive-day logic.

## Senior point

Always ask:

> "Can there be multiple records per business day?"

---

# 18. Calculate customer retention.

Suppose:

```text
signup_date
activity_date
customer_id
```

We want:

> Percentage of customers active in month N who are active again in month N+1.

## Step 1 — Monthly activity

```sql
WITH activity AS (
    SELECT DISTINCT
        customer_id,
        DATE_TRUNC('month', activity_date) AS month
    FROM customer_activity
)
```

## Step 2 — Match next month

```sql
SELECT
    a.month,
    COUNT(DISTINCT a.customer_id) AS active_customers,
    COUNT(DISTINCT b.customer_id) AS retained_customers,
    100.0 * COUNT(DISTINCT b.customer_id)
        / NULLIF(COUNT(DISTINCT a.customer_id), 0)
        AS retention_pct
FROM activity a
LEFT JOIN activity b
    ON b.customer_id = a.customer_id
   AND b.month = a.month + INTERVAL '1 month'
GROUP BY a.month
ORDER BY a.month;
```

## Interview discussion

Clarify the definition:

* User signed up and returned?
* User purchased again?
* User logged in?
* User performed a meaningful action?

Retention is a **business definition**, not merely a SQL problem.

---

# 19. Calculate conversion through a funnel.

Suppose events:

```text
user_id
event_name
event_time
```

Events:

```text
view_product
add_to_cart
checkout
purchase
```

## Solution

```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN event_name = 'view_product'
        THEN user_id END
    ) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event_name = 'add_to_cart'
        THEN user_id END
    ) AS cart_users,

    COUNT(DISTINCT CASE
        WHEN event_name = 'checkout'
        THEN user_id END
    ) AS checkout_users,

    COUNT(DISTINCT CASE
        WHEN event_name = 'purchase'
        THEN user_id END
    ) AS purchasers
FROM events;
```

## Conversion rates

```sql
100.0 * cart_users / NULLIF(viewers, 0)
```

etc.

## Follow-up

### Q: Why `COUNT(DISTINCT user_id)`?

Because one user can generate multiple events.

---

# 20. Find the longest period of inactivity for each customer.

This tests:

* `LAG`
* Date arithmetic
* Window functions
* Aggregation

## Solution

```sql
WITH x AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS previous_order_date
    FROM orders
),
gaps AS (
    SELECT
        customer_id,
        previous_order_date,
        order_date,
        order_date - previous_order_date AS gap_days
    FROM x
    WHERE previous_order_date IS NOT NULL
)
SELECT
    customer_id,
    MAX(gap_days) AS longest_gap_days
FROM gaps
GROUP BY customer_id;
```

## Follow-up

### Q: What if you want the exact start/end orders?

Return the row associated with the maximum gap using `ROW_NUMBER()` over:

```sql
ORDER BY gap_days DESC
```

---

# 21. Find the median salary.

A common approach using a percentile function:

```sql
SELECT
    PERCENTILE_CONT(0.5)
    WITHIN GROUP (ORDER BY salary) AS median_salary
FROM employee;
```

## Why median instead of average?

Average:

```text
100
100
100
10,000
```

is highly affected by the outlier.

Median is more robust.

## Follow-up

### Q: What if the database doesn't support `PERCENTILE_CONT`?

You can derive the middle row(s) using:

```text
ROW_NUMBER()
COUNT() OVER ()
```

and average the middle values.

## Important

This is one place where SQL dialect support differs. Check the target database syntax before using it in production.

---

# 22. Find the nth highest salary.

## Solution

```sql
SELECT employee_id,
       employee_name,
       salary
FROM (
    SELECT
        e.*,
        DENSE_RANK() OVER (
            ORDER BY salary DESC
        ) AS rnk
    FROM employee e
) x
WHERE rnk = 5;
```

For nth highest distinct salary:

```text
N = 5
→ rnk = 5
```

## Follow-up

### Q: What if interviewer wants exactly N rows?

Use `ROW_NUMBER()`.

### Q: What if ties should all be returned?

Use `DENSE_RANK()`.

---

# 23. Identify customers whose total spending is above the average customer spending.

This is a **two-level aggregation** problem.

## Step 1

```sql
WITH customer_spend AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
```

## Step 2

```sql
SELECT *
FROM customer_spend
WHERE total_spend > (
    SELECT AVG(total_spend)
    FROM customer_spend
);
```

## Key insight

You cannot directly do:

```sql
AVG(SUM(amount))
```

at the same grouping level.

You first aggregate to:

```text
customer
```

then aggregate those customer totals:

```text
average customer spend
```

This is a very important SQL reasoning pattern.

---

# 24. Find products that were never sold.

## Solution

```sql
SELECT p.product_id,
       p.product_name
FROM product p
LEFT JOIN order_item oi
    ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;
```

## Alternative

```sql
SELECT p.product_id,
       p.product_name
FROM product p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_item oi
    WHERE oi.product_id = p.product_id
);
```

## Interview discussion

This is an **anti-join** problem.

Remember:

```text
LEFT JOIN + NULL check
```

or:

```text
NOT EXISTS
```

---

# 25. Find duplicate rows after a join.

This is extremely important in Data Engineering interviews.

Suppose:

```text
customer
1 → John

order
100 → customer 1
101 → customer 1
```

If you expect one customer row but join:

```sql
customer
JOIN orders
```

then:

```text
John
John
```

is correct relationally.

It is only a bug if the **expected output grain was customer-level**.

## Senior answer

Before using `DISTINCT`, ask:

> "Why are multiple rows being generated?"

## Debug query

```sql
SELECT
    c.customer_id,
    COUNT(*) AS joined_rows
FROM customer c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING COUNT(*) > 1;
```

## Key principle

```text
Unexpected duplicates
        ↓
Check join cardinality
        ↓
Check source grain
        ↓
Check many-to-many relationships
```

Do not blindly fix with:

```sql
SELECT DISTINCT
```

---

# 26. Solve a many-to-many join without multiplying measures.

Suppose:

```text
orders
------
order_id
customer_id
amount

order_tags
----------
order_id
tag
```

One order can have many tags.

This query:

```sql
SELECT
    customer_id,
    SUM(amount)
FROM orders o
JOIN order_tags t
    ON o.order_id = t.order_id
GROUP BY customer_id;
```

can double-count order amounts.

## Why?

Example:

```text
Order 100 = ₹1,000

Tags:
A
B
C
```

Join produces:

```text
100 1000 A
100 1000 B
100 1000 C
```

`SUM(amount)` = ₹3,000 ❌

## Correct approach

Aggregate the one-to-many side first:

```sql
WITH tags AS (
    SELECT
        order_id,
        COUNT(*) AS tag_count
    FROM order_tags
    GROUP BY order_id
)
SELECT
    o.customer_id,
    SUM(o.amount)
FROM orders o
GROUP BY o.customer_id;
```

Or build separate measures at their proper grain.

## Senior statement

> "Every measure must be aggregated at the correct grain before crossing a one-to-many or many-to-many relationship."

This is one of the most valuable SQL concepts for analytics engineering.

---

# 27. Find records present in source but missing from target.

This is directly relevant to your reconciliation/data-quality experience. Your resume explicitly includes file-to-table, table-to-table and cross-system reconciliation.

## Solution

```sql
SELECT s.business_key
FROM source_table s
LEFT JOIN target_table t
    ON s.business_key = t.business_key
WHERE t.business_key IS NULL;
```

## Or

```sql
SELECT s.business_key
FROM source_table s
WHERE NOT EXISTS (
    SELECT 1
    FROM target_table t
    WHERE t.business_key = s.business_key
);
```

## Find target-only records

Reverse the logic.

```text
Source - Target
```

and:

```text
Target - Source
```

## Stronger reconciliation

Add aggregates:

```sql
SELECT
    COUNT(*) AS row_count,
    SUM(amount) AS total_amount,
    MIN(event_date),
    MAX(event_date)
FROM source_table;
```

and compare with target.

---

# 28. Compare source and target counts, sums and duplicates.

A production reconciliation query might calculate:

```sql
SELECT
    'SOURCE' AS system_name,
    COUNT(*) AS row_count,
    COUNT(DISTINCT business_key) AS distinct_keys,
    SUM(amount) AS total_amount,
    SUM(CASE WHEN business_key IS NULL THEN 1 ELSE 0 END) AS null_keys
FROM source_table

UNION ALL

SELECT
    'TARGET' AS system_name,
    COUNT(*) AS row_count,
    COUNT(DISTINCT business_key) AS distinct_keys,
    SUM(amount) AS total_amount,
    SUM(CASE WHEN business_key IS NULL THEN 1 ELSE 0 END) AS null_keys
FROM target_table;
```

## Expected output

```text
SYSTEM    ROWS    DISTINCT_KEYS    TOTAL_AMOUNT    NULL_KEYS

SOURCE    1M      1M               50M             0
TARGET    1M      1M               50M             0
```

## Senior answer

Do not rely only on:

```text
COUNT(*)
```

Two datasets can have identical counts but completely different records.

Use progressive reconciliation:

```text
Count
 ↓
Distinct keys
 ↓
Aggregates
 ↓
Key differences
 ↓
Row-level/hash comparison
```

---

# 29. Find records whose value changed between source and target.

Suppose:

```text
source
------
customer_id
status
amount
```

and target has the same fields.

## Query

```sql
SELECT
    s.customer_id,
    s.status AS source_status,
    t.status AS target_status,
    s.amount AS source_amount,
    t.amount AS target_amount
FROM source s
JOIN target t
    ON s.customer_id = t.customer_id
WHERE
       s.status <> t.status
    OR s.amount <> t.amount;
```

## Important NULL issue

This fails to detect some differences involving NULL.

Use explicit NULL-safe logic depending on the database.

PostgreSQL, for example, supports:

```sql
s.amount IS DISTINCT FROM t.amount
```

Example:

```sql
WHERE s.status IS DISTINCT FROM t.status
   OR s.amount IS DISTINCT FROM t.amount;
```

## Senior point

When building reconciliation frameworks, NULL semantics must be deliberately defined.

---

# 30. Write an SCD Type 2 SQL merge.

Suppose target:

```text
customer_dim
------------
customer_sk
customer_id
city
start_date
end_date
is_current
```

Source:

```text
customer_source
---------------
customer_id
city
```

## Concept

```text
Existing current record
        ↓
Compare attributes
        ↓
Changed?
   /       \
 No         Yes
 ↓           ↓
Nothing   expire old
             ↓
        insert new version
```

## Conceptual SQL

```sql
-- 1. Expire changed current records

UPDATE customer_dim d
SET
    end_date = CURRENT_DATE - INTERVAL '1 day',
    is_current = FALSE
FROM customer_source s
WHERE d.customer_id = s.customer_id
  AND d.is_current = TRUE
  AND d.city IS DISTINCT FROM s.city;
```

Then insert the new/current version:

```sql
INSERT INTO customer_dim (
    customer_sk,
    customer_id,
    city,
    start_date,
    end_date,
    is_current
)
SELECT
    next_surrogate_key,
    s.customer_id,
    s.city,
    CURRENT_DATE,
    DATE '9999-12-31',
    TRUE
FROM customer_source s
LEFT JOIN customer_dim d
    ON d.customer_id = s.customer_id
   AND d.is_current = TRUE
WHERE d.customer_id IS NULL
   OR d.city IS DISTINCT FROM s.city;
```

## Important

Exact implementation differs by database.

Snowflake can simplify some patterns with `MERGE`, while an explicit two-step approach can make Type 2 behavior easier to reason about.

## Follow-up

### What if the same source record arrives twice?

The pipeline must be idempotent and should not create unnecessary new versions.

---

# 31. Find the latest record for every business key using `QUALIFY`.

This is especially useful for Snowflake interviews.

## Snowflake

```sql
SELECT *
FROM customer
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC
) = 1;
```

Snowflake documents `QUALIFY` specifically as a way to filter after window functions are computed, which avoids nesting the window-function query in another subquery.

## ANSI-style equivalent

```sql
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id
               ORDER BY updated_at DESC
           ) AS rn
    FROM customer
) x
WHERE rn = 1;
```

## Interview point

Know both.

If interviewing for Snowflake-heavy roles, `QUALIFY` is worth knowing extremely well.

---

# 32. Find the first and last event for every user.

## Solution

```sql
SELECT
    user_id,
    MIN(event_time) AS first_event,
    MAX(event_time) AS last_event
FROM user_events
GROUP BY user_id;
```

## But what if we need the actual event rows?

Use:

```sql
WITH ranked AS (
    SELECT
        e.*,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY event_time
        ) AS first_rn,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY event_time DESC
        ) AS last_rn
    FROM user_events e
)
SELECT *
FROM ranked
WHERE first_rn = 1
   OR last_rn = 1;
```

## Follow-up

### What if timestamps tie?

Use a deterministic event ID:

```sql
ORDER BY event_time, event_id
```

---

# 33. Sessionize user events.

This is a high-value senior SQL problem.

## Requirement

Start a new session when the gap between two events is greater than 30 minutes.

Input:

```text
user_id
event_time
```

## Step 1 — Previous event

```sql
WITH x AS (
    SELECT
        user_id,
        event_time,
        LAG(event_time) OVER (
            PARTITION BY user_id
            ORDER BY event_time
        ) AS previous_event
    FROM events
)
```

## Step 2 — Identify session starts

```sql
, flags AS (
    SELECT
        *,
        CASE
            WHEN previous_event IS NULL THEN 1
            WHEN event_time - previous_event
                 > INTERVAL '30 minutes'
            THEN 1
            ELSE 0
        END AS new_session
    FROM x
)
```

## Step 3 — Cumulative session number

```sql
, sessions AS (
    SELECT
        *,
        SUM(new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_time
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS session_id
    FROM flags
)
SELECT *
FROM sessions;
```

## Output

```text
user  event_time      session

A     10:00           1
A     10:05           1
A     10:20           1
A     11:10           2
A     11:15           2
```

## Why this matters

This tests:

* `LAG`
* `CASE`
* Windowed `SUM`
* Time arithmetic
* Stateful thinking

This is exactly the type of problem where an interviewer is evaluating whether you can translate a business rule into a sequence of SQL transformations.

---

# 34. A query is suddenly running 20× slower. How do you debug it?

This is not merely a syntax question.

## Step 1 — Confirm the regression

Compare:

```text
Before
After
```

Look at:

* Runtime.
* Rows returned.
* Data volume.
* Execution plan.
* Statistics.
* Concurrent workload.

## Step 2 — Inspect execution plan

Use:

```sql
EXPLAIN
SELECT ...;
```

For PostgreSQL:

```sql
EXPLAIN ANALYZE
SELECT ...;
```

PostgreSQL's `EXPLAIN` shows the planner's chosen scan and join strategies, while `EXPLAIN ANALYZE` actually executes the query and exposes actual row counts and runtime for comparison with estimates.

SQL Server similarly exposes estimated and actual execution plans, including runtime information in actual plans.

## Look for

```text
Full table scan
        ↓
Wrong join strategy
        ↓
Huge row estimate mismatch
        ↓
Missing / ineffective index
        ↓
Large sort
        ↓
Large aggregation
        ↓
Bad cardinality
        ↓
Data skew
```

## Step 3 — Check statistics

Query optimizers use table/data statistics when selecting plans. PostgreSQL's `ANALYZE` collects these statistics for the planner.

## Step 4 — Check query changes

Common regressions:

```text
new JOIN
new OR condition
function on filter column
SELECT *
new ORDER BY
data distribution change
statistics became stale
```

## Senior answer

> "I would not optimize based on the SQL text alone. I would compare the execution plan, actual versus estimated cardinality, data distribution and recent schema/statistics/query changes."

---

# 35. Optimize this query for a 5-billion-row fact table.

Suppose:

```sql
SELECT *
FROM sales
WHERE DATE(order_timestamp) = '2026-10-01'
  AND customer_id IN (
      SELECT customer_id
      FROM customers
      WHERE country = 'IN'
  );
```

## Problems

### Problem 1

```sql
SELECT *
```

reads unnecessary columns.

### Problem 2

```sql
DATE(order_timestamp)
```

applies a function to the column.

Depending on database/physical design, this can prevent effective use of an index or pruning mechanism.

### Problem 3

A large `IN` subquery may not be the best expression for the optimizer/workload.

## Better form

```sql
SELECT
    s.order_id,
    s.customer_id,
    s.order_timestamp,
    s.amount
FROM sales s
JOIN customers c
    ON s.customer_id = c.customer_id
WHERE c.country = 'IN'
  AND s.order_timestamp >= TIMESTAMP '2026-10-01 00:00:00'
  AND s.order_timestamp <  TIMESTAMP '2026-10-02 00:00:00';
```

## Why?

### 1. Avoid unnecessary columns

```text
SELECT *
```

→ potentially huge I/O.

### 2. Use a range predicate

Instead of:

```sql
DATE(order_timestamp) = ...
```

use:

```sql
>= start
AND < next_day
```

### 3. Push selective filtering early

Country filter:

```text
country = 'IN'
```

reduces the relevant customer set.

### 4. Evaluate join strategy using the actual database

Do not assume a rewrite is automatically faster.

Inspect the execution plan.

SQL Server's query optimizer considers table access order, access methods, joins, filtering and aggregation when choosing an execution plan.

## Senior answer

> "I would first understand table size, partitioning, indexes/clustering, data distribution and query frequency. Then I'd use the execution plan to verify whether the rewrite actually reduced scan, join or sort cost."

---

# TOP SQL FOLLOW-UP QUESTIONS

These can come immediately after the 35 questions above.

## Window Functions

```text
ROW_NUMBER vs RANK vs DENSE_RANK?

LAG vs LEAD?

ROWS vs RANGE?

PARTITION BY vs GROUP BY?

Can aggregate functions be used as window functions?

What is a window frame?

How does NULL ordering affect ranking?
```

PostgreSQL and Snowflake both document window functions around the `OVER` clause, including partitioning, ordering and window-frame concepts.

---

# JOIN QUESTIONS

You should be able to explain:

```text
INNER JOIN
LEFT JOIN
RIGHT JOIN
FULL OUTER JOIN
CROSS JOIN
SELF JOIN
SEMI JOIN
ANTI JOIN
```

And more importantly:

```text
1-to-1
1-to-many
many-to-1
many-to-many
```

## Critical interview question

> "Why did this join increase my row count from 10 million to 80 million?"

Your answer should immediately be:

> "I would check join cardinality and whether either side contains duplicate join keys."

---

# NULL QUESTIONS

Know all of these:

```sql
IS NULL
IS NOT NULL
COALESCE()
NULLIF()
CASE
```

## Example

```sql
SELECT
    COALESCE(phone, 'UNKNOWN')
FROM customer;
```

## Division safety

```sql
revenue / NULLIF(order_count, 0)
```

---

# GROUP BY vs HAVING vs WHERE

## WHERE

Filters rows **before aggregation**.

```sql
WHERE country = 'IN'
```

## GROUP BY

Creates groups.

```sql
GROUP BY customer_id
```

## HAVING

Filters groups **after aggregation**.

```sql
HAVING SUM(amount) > 100000
```

## Example

```sql
SELECT
    customer_id,
    SUM(amount) AS total
FROM orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 100000;
```

Think:

```text
FROM
 ↓
WHERE
 ↓
GROUP BY
 ↓
HAVING
 ↓
SELECT
 ↓
WINDOW
 ↓
ORDER BY
```

Exact execution/planning can be more nuanced, but this logical-processing model is essential for reasoning about SQL.

---

# CTE vs SUBQUERY

## CTE

```sql
WITH customer_sales AS (
    SELECT ...
)
SELECT ...
FROM customer_sales;
```

Useful for:

* Readability.
* Breaking complex logic into steps.
* Reusing intermediate logic in the query.

## Subquery

```sql
SELECT *
FROM (
    SELECT ...
) x;
```

Useful for:

* Local/nested logic.
* Small transformations.

## Senior point

Do not claim:

> "CTEs are always faster."

They are primarily a query-structuring mechanism; optimizer behavior depends on the database and query.

---

# UNION vs UNION ALL

## UNION

Removes duplicates.

```sql
SELECT ...
UNION
SELECT ...
```

## UNION ALL

Keeps duplicates.

```sql
SELECT ...
UNION ALL
SELECT ...
```

`UNION ALL` is generally preferable when deduplication is not required because it avoids the extra duplicate-removal work.

---

# EXISTS vs IN vs JOIN

## EXISTS

Good for existence checks:

```sql
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
)
```

## JOIN

Use when you need columns from the other table.

## IN

Convenient for membership conditions.

## Senior answer

> "I choose based on semantics first and then verify performance with the database's optimizer and execution plan."

---

# SQL PERFORMANCE CHECKLIST

When a query is slow:

```text
□ Is the query scanning too much data?
□ Am I selecting unnecessary columns?
□ Can I filter earlier?
□ Is a function applied to a filter/join column?
□ Is the join cardinality correct?
□ Are there duplicate join keys?
□ Is the join selective?
□ Is there a missing/ineffective index?
□ Is partition pruning happening?
□ Is clustering/distribution appropriate?
□ Is a sort expensive?
□ Is aggregation expensive?
□ Is cardinality estimation wrong?
□ Are statistics current?
□ Is there data skew?
□ Is the query running concurrently with heavy workloads?
```

The optimizer chooses plans based on schema, indexes/statistics and query structure; examining execution plans is therefore central to diagnosing performance.

---

# 20 SQL PATTERNS YOU MUST MEMORIZE

These patterns appear again and again in senior Data Engineering interviews.

```text
1. Top N per group
2. Deduplication
3. Latest record
4. First record
5. Second record
6. Running total
7. Rolling average
8. LAG / LEAD
9. Gaps and islands
10. Consecutive days
11. Anti-join
12. Semi-join
13. Self join
14. Conditional aggregation
15. Two-level aggregation
16. Sessionization
17. Funnel analysis
18. Retention
19. Reconciliation
20. SCD Type 2
```

---

# 15 SQL CODING QUESTIONS TO PRACTICE WITHOUT LOOKING AT THE ANSWER

After studying the chapter, close your notes and solve these yourself:

```text
1. Find the 3rd highest distinct salary.

2. Find top 2 products by revenue in every region.

3. Remove duplicate transactions keeping the latest ingestion.

4. Find customers whose spending increased every month for 3 months.

5. Find the longest consecutive login streak.

6. Find employees who joined before their manager.

7. Find users who logged in this week but not last week.

8. Find the first purchase after signup.

9. Find the percentage of customers making a second purchase.

10. Find the largest day-over-day revenue increase.

11. Find the top 5% customers by revenue.

12. Find customers whose latest order amount is higher than their previous order.

13. Detect gaps greater than 30 days in customer activity.

14. Reconcile source and target datasets using keys + aggregates.

15. Build a Type 2 dimension from a source snapshot.
```

---

# 10 SQL QUESTIONS THAT TEST SENIOR-LEVEL THINKING

These don't have a single "trick query."

The interviewer wants to see your reasoning.

## 1

> "Why did the query suddenly become slower after the table grew from 100 GB to 5 TB?"

Think:

```text
Data volume
↓
Partitioning
↓
Statistics
↓
Cardinality
↓
Join strategy
↓
Physical layout
```

## 2

> "Why did a LEFT JOIN double the revenue?"

Think:

```text
One-to-many multiplication
```

## 3

> "Why does COUNT(*) look correct but SUM(amount) is wrong?"

Think:

```text
Duplicated fact rows
```

## 4

> "How do you prove source and target are identical?"

Think:

```text
Count
+
Distinct keys
+
Aggregates
+
Difference sets
+
Hash/row comparison
```

## 5

> "How do you query 5 billion rows efficiently?"

Think:

```text
Partition pruning
+
Column pruning
+
Selective predicates
+
Efficient joins
+
Physical layout
+
Execution plan
```

## 6

> "How do you handle late-arriving corrections?"

Think:

```text
Business key
+
version/timestamp
+
MERGE/upsert
+
idempotency
```

## 7

> "How would you find the latest valid state?"

Think:

```text
ROW_NUMBER
+
business key
+
ordering columns
```

## 8

> "Why did DISTINCT hide your bug?"

Think:

```text
Wrong grain
+
many-to-many join
```

## 9

> "How would you make this query incremental?"

Think:

```text
watermark
+
changed records
+
partition pruning
+
merge
```

## 10

> "Would you add an index?"

Never automatically say yes.

Think:

```text
Read frequency
+
write frequency
+
selectivity
+
table size
+
storage
+
maintenance
+
query pattern
```

---

# YOUR RESUME → SQL INTERVIEW STORY BANK

Your resume gives you unusually strong real-world material for SQL interviews.

| SQL Area       | Your Experience                              |
| -------------- | -------------------------------------------- |
| Reconciliation | Source-to-target / table-to-table validation |
| Data quality   | Null, duplicate, schema, mismatch checks     |
| Redshift SQL   | Metadata + schema governance                 |
| Snowflake      | PostgreSQL → Snowflake pipelines             |
| Big Data SQL   | Hive analytical datasets                     |
| Azure          | SQL Server + ADF + Databricks                |
| GCP            | BigQuery analytical workloads                |
| Migration      | Data reconciliation and cutover validation   |
| Metadata       | YAML/config-driven validation                |
| BI             | Tableau / Power BI trusted datasets          |

Your resume specifically identifies Redshift, BigQuery, Snowflake, SQL Server, Hive, ADF and Databricks across your projects.

---

# YOUR 60-SECOND SQL INTRODUCTION IN AN INTERVIEW

When asked:

> "How strong are you in SQL?"

Do not answer:

> "I know joins, subqueries, group by and window functions."

Use your production experience:

> "SQL has been one of my core data-engineering skills across warehouse, big-data and cloud platforms. I've used it for source-to-target reconciliation, data-quality validation, analytical transformations, data migration and warehouse optimization across technologies such as Redshift, Snowflake, BigQuery, SQL Server and Hive. For complex problems, I'm comfortable with window functions, CTEs, multi-level aggregations, deduplication, SCD patterns and incremental processing. From a production perspective, I also focus on join cardinality, query plans, partition pruning, data volume and correctness rather than only writing a syntactically correct query."

---

# THE 10 GOLDEN SQL STATEMENTS

Memorize these.

### 1

> "Before writing the query, I identify the grain of the source and expected result."

### 2

> "I check join cardinality before assuming duplicate rows are a data issue."

### 3

> "I use window functions when I need calculations across related rows without collapsing the result set."

### 4

> "For top-N-per-group problems, I usually think in terms of partitioning plus ranking."

### 5

> "For reconciliation, count equality alone is not sufficient."

### 6

> "I avoid using DISTINCT as a blanket fix for unexpected duplicates."

### 7

> "I optimize queries based on execution plans and actual workload behavior rather than assumptions."

### 8

> "For large datasets, I want to minimize the amount of data scanned and moved."

### 9

> "I make NULL behavior explicit in data-quality and reconciliation logic."

### 10

> "For production SQL, correctness, scalability and explainability are equally important."

---

# FINAL SQL REVISION SHEET

```text
WINDOW FUNCTIONS
├── ROW_NUMBER
├── RANK
├── DENSE_RANK
├── LAG
├── LEAD
├── SUM OVER
├── AVG OVER
└── Window Frames

JOINS
├── INNER
├── LEFT
├── RIGHT
├── FULL
├── CROSS
├── SELF
├── SEMI
└── ANTI

AGGREGATION
├── GROUP BY
├── HAVING
├── Conditional Aggregation
├── Multi-level Aggregation
└── Distinct Aggregation

ADVANCED PATTERNS
├── Gaps & Islands
├── Sessionization
├── Funnel
├── Retention
├── SCD Type 2
├── Reconciliation
└── Incremental Processing

PERFORMANCE
├── EXPLAIN
├── Execution Plan
├── Indexes
├── Partition Pruning
├── Statistics
├── Cardinality
├── Join Strategy
└── Data Volume

DATA ENGINEERING SQL
├── Deduplication
├── Source/Target Validation
├── Schema Validation
├── Incremental Loads
├── MERGE / UPSERT
└── Audit Queries
```

---

# SQL INTERVIEW SELF-TEST

You should be able to solve these **from a blank editor**:

```text
□ Second highest salary
□ Nth highest salary
□ Top 3 by department
□ Latest record per key
□ Deduplicate table
□ Customers with no orders
□ Products never sold
□ Running total
□ Rolling 7-day average
□ Month-over-month growth
□ First order
□ Second order
□ Consecutive days
□ Longest inactivity
□ Gaps and islands
□ Sessionization
□ Funnel conversion
□ Customer retention
□ Median
□ SCD Type 2
□ Source vs target reconciliation
□ Source-only records
□ Target-only records
□ Changed records
□ Many-to-many double counting
□ Query-performance debugging
□ Execution-plan interpretation
□ Incremental SQL
□ NULL-safe comparison
□ Top-N analytical reporting
```

---

# MOST IMPORTANT TAKEAWAY

At 70+ LPA level, the interviewer is usually not impressed merely because you can write:

```sql
SELECT ...
FROM ...
JOIN ...
GROUP BY ...
```

The stronger signal is:

```text
I understand the data grain
        ↓
I understand join cardinality
        ↓
I understand business semantics
        ↓
I handle NULLs and duplicates
        ↓
I can solve analytical problems
        ↓
I can make it incremental
        ↓
I can reconcile source and target
        ↓
I can diagnose performance
        ↓
I can explain the trade-off
```

That is the SQL level you should target.

---

# RESEARCH BASIS

The technical concepts in this chapter were cross-checked against current database documentation, including:

* PostgreSQL 18 documentation for window functions.
* PostgreSQL 18 documentation for `EXPLAIN`, `EXPLAIN ANALYZE`, execution plans and statistics.
* Microsoft SQL Server documentation for execution plans, optimizer behavior and actual vs estimated plans.
* Snowflake documentation for window-function syntax and `QUALIFY`.

---

# END OF TOPIC 3

```text
1. Data Engineering           ✅
2. Big Data Engineering       ✅
3. SQL                        ✅

NEXT
4. Python — Practical + Programming
5. PySpark — Practical + Programming
6. DevOps — Top 10
7. AI — Data Engineering
8. Databricks
9. Snowflake
10. AWS
11. Azure
12. GCP
```
