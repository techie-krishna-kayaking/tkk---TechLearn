# SQL Interview Masterbook — Lead / Staff / Principal Data Engineer

> **Target:** Lead, Staff, Principal Data Engineer and Data Architect roles at product companies; calibrated for ₹70+ LPA interviews in India.
> **Goal:** Demonstrate correctness, scalability, performance, reliability, and architectural judgment—not just syntax.
> **Dataset:** All questions use one consistent e-commerce dataset. It deliberately includes one-to-many relationships, retries, late updates, refunds, status history, NULLs, and behavioral events.
> **Dialect:** PostgreSQL-style SQL for core examples, with Snowflake and BigQuery notes. Verify actual syntax and plans on the target engine.
>
> These are representative high-value senior interview patterns, not a claim that a named company asked each question recently.

## How to use

For every question: clarify the business definition, declare result grain, write the simplest correct SQL, test ties/NULLs/missing periods/duplicates, compare alternatives, then discuss scale and operations.

| Dimension | Lead | Staff | Principal |
|---|---|---|---|
| SQL | Correct maintainable queries | Reusable patterns and standards | Organization-wide semantic contracts |
| Performance | Reads plans and tunes | Diagnoses skew, concurrency, cost | Platform workload/storage strategy |
| Reliability | Retries and data checks | Replay, backfill, recovery | SLOs, ownership, risk |
| Leadership | Mentors engineers | Influences teams across domains | Aligns architecture with business strategy |

# 1. The single e-commerce dataset

## Scenario

A multi-region e-commerce product supports customers, products, orders, line items, payment attempts, status transitions, and behavioral events. The warehouse powers revenue, retention, funnels, reconciliation, CDC, and operational monitoring.

## Table grain

| Table | Grain | Key |
|---|---|---|
| customers | One current row per customer | customer_id |
| products | One current row per product | product_id |
| orders | One row per order | order_id |
| order_items | One row per order line | order_item_id |
| payments | One row per payment attempt/transaction | payment_id |
| order_status_history | One row per status transition | status_event_id |
| events | One row per tracked event | event_id |
| customer_snapshot | One customer per extract date | customer_id + snapshot_date |

An order with 3 item rows and 2 payment attempts can produce 6 rows in a raw join. Aggregate child facts to the intended grain before joining measures.

## PostgreSQL reference DDL

```sql
CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,
  customer_name TEXT,
  email TEXT,
  country_code CHAR(2),
  signup_ts TIMESTAMP,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE products (
  product_id BIGINT PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT,
  brand TEXT,
  list_price NUMERIC(12,2),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE orders (
  order_id BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_ts TIMESTAMP NOT NULL,
  order_status TEXT NOT NULL,
  currency_code CHAR(3) NOT NULL,
  shipping_country CHAR(2),
  discount_amount NUMERIC(12,2) DEFAULT 0,
  tax_amount NUMERIC(12,2) DEFAULT 0,
  shipping_amount NUMERIC(12,2) DEFAULT 0,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
  order_item_id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price NUMERIC(12,2) NOT NULL,
  item_discount NUMERIC(12,2) DEFAULT 0,
  item_status TEXT NOT NULL,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE payments (
  payment_id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  payment_attempt INTEGER NOT NULL,
  payment_ts TIMESTAMP NOT NULL,
  payment_status TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  payment_method TEXT,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE order_status_history (
  status_event_id BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  order_status TEXT NOT NULL,
  status_ts TIMESTAMP NOT NULL,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE events (
  event_id BIGINT PRIMARY KEY,
  customer_id BIGINT,
  session_id TEXT,
  event_name TEXT NOT NULL,
  event_ts TIMESTAMP NOT NULL,
  product_id BIGINT,
  order_id BIGINT,
  page_url TEXT,
  event_properties JSONB,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL
);

CREATE TABLE customer_snapshot (
  customer_id BIGINT NOT NULL,
  customer_name TEXT,
  email TEXT,
  country_code CHAR(2),
  snapshot_date DATE NOT NULL,
  source_updated_at TIMESTAMP,
  ingested_at TIMESTAMP NOT NULL,
  PRIMARY KEY (customer_id, snapshot_date)
);
```

This is a teaching model. Some analytical platforms treat declared constraints as informational rather than enforced. Validate data types, timestamp semantics, and constraint behavior on your engine.

## Sample data

### customers

| customer_id | name | email | country | signup_ts |
|---:|---|---|---|---|
| 1 | Asha | asha@example.com | IN | 2025-01-02 09:00 |
| 2 | Ben | ben@example.com | US | 2025-01-05 10:00 |
| 3 | Chen | chen@example.com | SG | 2025-02-01 08:00 |
| 4 | Diya | diya@example.com | IN | 2025-02-10 12:00 |
| 5 | Eli | NULL | IN | 2025-03-01 11:00 |

### orders

| order_id | customer_id | order_ts | status | currency |
|---:|---:|---|---|---|
| 101 | 1 | 2025-01-10 10:00 | COMPLETED | INR |
| 102 | 1 | 2025-01-15 12:00 | COMPLETED | INR |
| 103 | 2 | 2025-01-20 09:00 | CANCELLED | USD |
| 104 | 2 | 2025-02-05 15:00 | COMPLETED | USD |
| 105 | 3 | 2025-02-07 13:00 | COMPLETED | SGD |
| 106 | 1 | 2025-03-01 17:00 | COMPLETED | INR |
| 107 | 4 | 2025-03-03 08:00 | PENDING | INR |
| 108 | 5 | 2025-03-05 19:00 | COMPLETED | INR |

### order_items

| item_id | order_id | product_id | qty | unit_price | discount | status |
|---:|---:|---:|---:|---:|---:|---|
| 1001 | 101 | 10 | 2 | 500 | 0 | FULFILLED |
| 1002 | 101 | 11 | 1 | 200 | 0 | FULFILLED |
| 1003 | 102 | 10 | 1 | 500 | 50 | FULFILLED |
| 1004 | 102 | 12 | 2 | 300 | 0 | FULFILLED |
| 1005 | 103 | 11 | 1 | 200 | 0 | CANCELLED |
| 1006 | 104 | 10 | 1 | 500 | 0 | FULFILLED |
| 1007 | 105 | 13 | 3 | 100 | 0 | FULFILLED |
| 1008 | 106 | 12 | 1 | 300 | 0 | FULFILLED |
| 1009 | 107 | 10 | 1 | 500 | 0 | PENDING |
| 1010 | 108 | 11 | 2 | 200 | 0 | FULFILLED |

### products

| product_id | name | category | brand | list_price |
|---:|---|---|---|---:|
| 10 | Keyboard | Accessories | KeyCo | 550 |
| 11 | Mouse | Accessories | KeyCo | 220 |
| 12 | Monitor | Displays | ViewMax | 300 |
| 13 | Cable | Accessories | LinkPro | 100 |

### payments

| payment_id | order_id | attempt | payment_ts | status | amount |
|---:|---:|---:|---|---|---:|
| 5001 | 101 | 1 | 2025-01-10 10:01 | SUCCESS | 1200 |
| 5002 | 102 | 1 | 2025-01-15 12:01 | FAILED | 950 |
| 5003 | 102 | 2 | 2025-01-15 12:05 | SUCCESS | 950 |
| 5004 | 103 | 1 | 2025-01-20 09:02 | REFUNDED | 200 |
| 5005 | 104 | 1 | 2025-02-05 15:01 | SUCCESS | 500 |
| 5006 | 105 | 1 | 2025-02-07 13:01 | SUCCESS | 300 |
| 5007 | 106 | 1 | 2025-03-01 17:01 | SUCCESS | 300 |
| 5008 | 108 | 1 | 2025-03-05 19:01 | SUCCESS | 400 |

### events

| event_id | customer_id | session_id | event_name | event_ts | product_id | order_id |
|---:|---:|---|---|---|---:|---:|
| 9001 | 1 | s1 | view_product | 2025-01-10 09:00 | 10 | NULL |
| 9002 | 1 | s1 | add_to_cart | 2025-01-10 09:05 | 10 | NULL |
| 9003 | 1 | s1 | purchase | 2025-01-10 10:00 | NULL | 101 |
| 9004 | 1 | s2 | view_product | 2025-01-15 11:00 | 12 | NULL |
| 9005 | 1 | s2 | purchase | 2025-01-15 12:00 | NULL | 102 |
| 9006 | 2 | s3 | view_product | 2025-02-05 14:00 | 10 | NULL |
| 9007 | 2 | s3 | purchase | 2025-02-05 15:00 | NULL | 104 |
| 9008 | 3 | s4 | view_product | 2025-02-07 12:00 | 13 | NULL |
| 9009 | 3 | s4 | purchase | 2025-02-07 13:00 | NULL | 105 |
| 9010 | 1 | s5 | view_product | 2025-03-01 16:00 | 12 | NULL |

## Metric definitions used here

- Completed order: `orders.order_status = 'COMPLETED'`.
- Gross item value: `quantity * unit_price`.
- Net item value: `quantity * unit_price - COALESCE(item_discount, 0)`.
- Net merchandise value: eligible fulfilled item values.
- Cash collected: successful payment amount; not automatically equal to revenue.
- Order count: distinct orders at order grain.
- Active customer: one or more qualifying events in the period.
- Taxes, shipping, refunds, FX and order-level discount allocation are excluded unless explicitly stated.

GMV, booked revenue, recognized revenue, cash collected, net sales, and contribution margin are not synonyms. Clarify the metric contract before coding.

# 2. Foundations and query semantics

## Q1. What is the grain of each table, and why does it matter?

**Answer:** customers is customer-grain; orders is order-grain; order_items is line-grain; payments is payment-attempt-grain; events is event-grain; status history is transition-grain.

An order with 3 lines and 2 payment attempts can create 6 rows in a raw join. Summing item values afterward doubles them.

**Best:** Declare output grain, profile join-key uniqueness, and aggregate one-to-many children to the desired grain before joining measures.

**Level signal:** Lead prevents the defect; Staff standardizes facts/tests; Principal establishes canonical metric contracts and ownership.

## Q2. Explain logical SQL processing order.

Conceptually: FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT. Window functions are evaluated after grouping/aggregation in the logical model; the optimizer may reorder physical execution. A WHERE clause generally cannot reference a window result: use a subquery/CTE or QUALIFY where supported.

## Q3. Find completed orders for customers in India.

```sql
SELECT o.order_id, o.customer_id, o.order_ts, o.currency_code
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_status = 'COMPLETED'
  AND c.country_code = 'IN';
```

**Alternative:** EXISTS if only membership matters:

```sql
SELECT o.order_id, o.customer_id, o.order_ts, o.currency_code
FROM orders o
WHERE o.order_status = 'COMPLETED'
  AND EXISTS (
    SELECT 1 FROM customers c
    WHERE c.customer_id = o.customer_id AND c.country_code = 'IN'
  );
```

**Best:** Both are valid under unique customer keys. EXISTS avoids multiplying output if the customer input is unexpectedly non-unique. Clarify deleted customers and historical country as-of order time.

## Q4. WHERE vs HAVING?

```sql
SELECT o.customer_id,
       SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount, 0)) AS net_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'COMPLETED'
  AND oi.item_status = 'FULFILLED'
GROUP BY o.customer_id
HAVING SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount, 0)) > 1000;
```

WHERE filters rows before aggregation; HAVING filters groups afterward. Put row eligibility in WHERE and aggregate thresholds in HAVING.

## Q5. COUNT(*) vs COUNT(column) vs COUNT(DISTINCT column)?

```sql
SELECT COUNT(*) AS row_count,
       COUNT(email) AS non_null_emails,
       COUNT(DISTINCT email) AS unique_non_null_emails
FROM customers;
```

COUNT(*) counts rows; COUNT(column) ignores NULL; COUNT(DISTINCT column) counts unique non-NULL values. Approximate distinct functions trade precision for compute; do not use for finance/contractual measures without an approved error bound.

## Q6. Why is NOT IN risky when the subquery can return NULL?

A NULL can make comparisons UNKNOWN under three-valued logic. Use a correlated anti-join:

```sql
SELECT c.customer_id
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```

LEFT JOIN ... IS NULL is also valid when checking a non-nullable match key. NOT IN can be safe if NULLs are excluded deliberately.

## Q7. Find customers with no completed orders.

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.customer_id
    AND o.order_status = 'COMPLETED'
);
```

A customer with only cancelled/pending orders qualifies. That differs from having no orders at all.

## Q8. UNION vs UNION ALL?

UNION removes duplicate result rows; UNION ALL preserves them. Prefer UNION ALL unless set semantics require deduplication. Duplicate removal can require sort/hash work and hide upstream defects.

## Q9. Explain CASE, COALESCE, NULLIF.

CASE is conditional logic; COALESCE returns first non-NULL; NULLIF(a,b) returns NULL when equal. Example safe division:

```sql
SELECT 100.0 / NULLIF(COUNT(*), 0)
FROM orders WHERE order_status = 'COMPLETED';
```

Do not convert every NULL to zero; unknown, missing, and zero may differ.

## Q10. Explain join types and semi/anti joins.

INNER returns matches; LEFT preserves left rows; FULL preserves both; CROSS produces a Cartesian product; SELF joins a table to itself. Semi join returns left rows when a match exists (EXISTS); anti join returns left rows when none exists (NOT EXISTS). State expected 1:1/1:many/many:1/many:many cardinality before joining.

# 3. Aggregation, revenue and product analytics

## Q11. Calculate net merchandise value per order.

```sql
SELECT o.order_id, o.currency_code,
       SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount, 0)) AS net_item_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'COMPLETED'
  AND oi.item_status = 'FULFILLED'
GROUP BY o.order_id, o.currency_code;
```

Aggregate from line grain to order grain. This excludes taxes, shipping, refunds, and order-level discounts; production metrics need a financial contract.

## Q12. Calculate customer value by currency.

```sql
WITH order_value AS (
  SELECT o.order_id, o.customer_id, o.currency_code,
         SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount, 0)) AS net_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_status = 'COMPLETED'
    AND oi.item_status = 'FULFILLED'
  GROUP BY o.order_id, o.customer_id, o.currency_code
)
SELECT customer_id, currency_code, SUM(net_value) AS customer_value
FROM order_value
GROUP BY customer_id, currency_code;
```

Keep currencies separate until a documented FX policy specifies source, rate date, and precision.

## Q13. Top 5 customers by spend per currency.

```sql
WITH customer_value AS (
  SELECT o.customer_id, o.currency_code,
         SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount, 0)) AS net_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_status = 'COMPLETED' AND oi.item_status = 'FULFILLED'
  GROUP BY o.customer_id, o.currency_code
),
ranked AS (
  SELECT *, DENSE_RANK() OVER (
    PARTITION BY currency_code ORDER BY net_value DESC
  ) AS rnk
  FROM customer_value
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY currency_code, rnk, customer_id;
```

DENSE_RANK includes ties; ROW_NUMBER gives at most five rows with deterministic secondary ordering. Clarify “five positions” vs “five ranks”.

## Q14. Top product by units sold in each category.

```sql
WITH product_units AS (
  SELECT p.category, p.product_id, p.product_name, SUM(oi.quantity) AS units_sold
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.order_status = 'COMPLETED' AND oi.item_status = 'FULFILLED'
  GROUP BY p.category, p.product_id, p.product_name
),
ranked AS (
  SELECT *, RANK() OVER (
    PARTITION BY category ORDER BY units_sold DESC
  ) AS rnk
  FROM product_units
)
SELECT * FROM ranked WHERE rnk = 1;
```

To include zero-sales products, start from products and LEFT JOIN aggregated sales.

## Q15. Include products with zero fulfilled sales.

```sql
WITH sales AS (
  SELECT product_id, SUM(quantity) AS units_sold
  FROM order_items WHERE item_status = 'FULFILLED'
  GROUP BY product_id
)
SELECT p.product_id, p.product_name, COALESCE(s.units_sold, 0) AS units_sold
FROM products p LEFT JOIN sales s ON s.product_id = p.product_id;
```

Aggregate first so sales has one row per product.

## Q16. Daily order count and merchandise value.

```sql
WITH order_value AS (
  SELECT o.order_id, o.order_ts::date AS order_date, o.currency_code,
         SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount,0)) AS net_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_status = 'COMPLETED' AND oi.item_status = 'FULFILLED'
  GROUP BY o.order_id, o.order_ts::date, o.currency_code
)
SELECT order_date, currency_code, COUNT(*) AS order_count, SUM(net_value) AS net_value
FROM order_value
GROUP BY order_date, currency_code
ORDER BY order_date, currency_code;
```

The intermediate CTE makes order grain explicit and avoids using COUNT(DISTINCT) as a patch for a multiplied join.

## Q17. Calculate average order value per currency.

Build the order_value CTE from Q16, then AVG(net_value) grouped by currency_code. This makes denominator one row per order. SUM(line value)/COUNT(DISTINCT order_id) can be correct with aligned filters, but the CTE is easier to review and extend.

## Q18. Monthly cancellation rate.

```sql
SELECT DATE_TRUNC('month', order_ts) AS month,
       COUNT(*) FILTER (WHERE order_status = 'CANCELLED') AS cancelled,
       COUNT(*) AS all_orders,
       100.0 * COUNT(*) FILTER (WHERE order_status = 'CANCELLED')
         / NULLIF(COUNT(*), 0) AS cancellation_pct
FROM orders
GROUP BY DATE_TRUNC('month', order_ts)
ORDER BY month;
```

Portable alternative: SUM(CASE WHEN order_status='CANCELLED' THEN 1 ELSE 0 END). Clarify whether month means order-created month or cancellation-event month; use status history for the latter.

## Q19. Payment attempt success rate by method.

```sql
SELECT payment_method, COUNT(*) AS attempts,
       SUM(CASE WHEN payment_status='SUCCESS' THEN 1 ELSE 0 END) AS successes,
       100.0 * SUM(CASE WHEN payment_status='SUCCESS' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS attempt_success_pct
FROM payments GROUP BY payment_method;
```

Attempts, orders, and customers are different denominators. Aggregate to order grain for an order-level metric.

## Q20. Customers whose cumulative net value exceeds 1,000 by currency.

Use the customer_value CTE in Q12 and filter `net_value > 1000`. Do not mix currencies.

# 4. Window functions and ranking

## Q21. ROW_NUMBER vs RANK vs DENSE_RANK?

For values 100, 90, 90, 80: ROW_NUMBER gives 1,2,3,4 (with deterministic tie ordering); RANK gives 1,2,2,4; DENSE_RANK gives 1,2,2,3. ROW_NUMBER is for exactly N rows; RANK/DENSE_RANK preserve business ties.

## Q22. Latest order per customer.

```sql
WITH ranked AS (
  SELECT o.*, ROW_NUMBER() OVER (
    PARTITION BY customer_id ORDER BY order_ts DESC, order_id DESC
  ) AS rn
  FROM orders o
)
SELECT * FROM ranked WHERE rn = 1;
```

PostgreSQL alternative is DISTINCT ON with matching ORDER BY. ROW_NUMBER is portable. Secondary key makes selection deterministic.

## Q23. First and second order per customer.

```sql
WITH ranked AS (
  SELECT o.*, ROW_NUMBER() OVER (
    PARTITION BY customer_id ORDER BY order_ts, order_id
  ) AS seq
  FROM orders o
)
SELECT * FROM ranked WHERE seq IN (1,2);
```

Filter to completed orders inside the CTE if first/second completed order is asked.

## Q24. Latest successful payment per order.

```sql
WITH ranked AS (
  SELECT p.*, ROW_NUMBER() OVER (
    PARTITION BY order_id ORDER BY payment_ts DESC, payment_id DESC
  ) AS rn
  FROM payments p WHERE payment_status = 'SUCCESS'
)
SELECT * FROM ranked WHERE rn = 1;
```

This means latest successful payment. To get latest attempt and then check status, rank all attempts first and filter outside. They are not equivalent.

## Q25. Running total per customer/currency.

After aggregating one row per order:

```sql
SUM(net_value) OVER (
  PARTITION BY customer_id, currency_code
  ORDER BY order_ts, order_id
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

Explicit ROWS makes row-by-row accumulation clear and avoids ambiguity with peer rows under default frames.

## Q26. Three-order rolling average per customer.

After order-grain aggregation:

```sql
AVG(net_value) OVER (
  PARTITION BY customer_id, currency_code
  ORDER BY order_ts, order_id
  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
)
```

Three rows are not three calendar days. Use a date spine or time-based RANGE frame for calendar windows.

## Q27. Compare each order with previous order.

```sql
WITH order_value AS (
  SELECT o.order_id, o.customer_id, o.currency_code, o.order_ts,
         SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount,0)) AS net_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_status = 'COMPLETED' AND oi.item_status = 'FULFILLED'
  GROUP BY o.order_id, o.customer_id, o.currency_code, o.order_ts
)
SELECT *, LAG(net_value) OVER (
  PARTITION BY customer_id, currency_code ORDER BY order_ts, order_id
) AS previous_order_value
FROM order_value;
```

Aggregate before LAG because the target grain is order, not item.

## Q28. Largest order-value increase per customer.

Build on Q27; calculate net_value - previous_order_value, rank descending per customer, exclude rows with no previous order. ROW_NUMBER gives one deterministic winner; clarify if only positive increases count.

## Q29. Customers with at least three completed orders.

```sql
SELECT customer_id, COUNT(*) AS completed_orders
FROM orders
WHERE order_status = 'COMPLETED'
GROUP BY customer_id
HAVING COUNT(*) >= 3;
```

Use a window COUNT only if individual order rows must remain visible.

## Q30. Median completed order value per currency.

Aggregate to one row per completed order first, then:

```sql
SELECT currency_code,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY net_value) AS median_value
FROM order_value
GROUP BY currency_code;
```

If unsupported, implement odd/even median with row numbers. Median and mean answer different questions.

# 5. Time series, cohort, gaps and islands

## Q31. Month-over-month order value.

```sql
WITH monthly AS (
  SELECT DATE_TRUNC('month', o.order_ts) AS month, o.currency_code,
         SUM(oi.quantity * oi.unit_price - COALESCE(oi.item_discount,0)) AS net_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.order_status = 'COMPLETED' AND oi.item_status = 'FULFILLED'
  GROUP BY DATE_TRUNC('month', o.order_ts), o.currency_code
),
compared AS (
  SELECT *, LAG(net_value) OVER (
    PARTITION BY currency_code ORDER BY month
  ) AS prior_month_value
  FROM monthly
)
SELECT *, 100.0 * (net_value-prior_month_value)
  / NULLIF(prior_month_value,0) AS mom_growth_pct
FROM compared;
```

LAG returns previous row, not necessarily previous calendar month. Fill missing months for calendar continuity.

## Q32. Month spine with zero-filled order counts (PostgreSQL).

```sql
WITH months AS (
  SELECT GENERATE_SERIES(
    DATE '2025-01-01', DATE '2025-12-01', INTERVAL '1 month'
  )::date AS month_start
),
monthly AS (
  SELECT DATE_TRUNC('month', order_ts)::date AS month_start,
         currency_code, COUNT(*) AS order_count
  FROM orders WHERE order_status = 'COMPLETED'
  GROUP BY DATE_TRUNC('month', order_ts)::date, currency_code
),
currencies AS (SELECT DISTINCT currency_code FROM orders)
SELECT m.month_start, c.currency_code, COALESCE(x.order_count,0) AS order_count
FROM months m CROSS JOIN currencies c
LEFT JOIN monthly x
  ON x.month_start=m.month_start AND x.currency_code=c.currency_code
ORDER BY m.month_start, c.currency_code;
```

Snowflake can use generator/calendar tables; BigQuery supports GENERATE_DATE_ARRAY. A calendar dimension is useful for fiscal periods/holidays.

## Q33. Month-N active users retained in N+1.

```sql
WITH activity AS (
  SELECT DISTINCT customer_id, DATE_TRUNC('month',event_ts)::date AS month
  FROM events WHERE customer_id IS NOT NULL
)
SELECT a.month, COUNT(*) AS active_customers,
       COUNT(b.customer_id) AS retained_customers,
       100.0*COUNT(b.customer_id)/NULLIF(COUNT(*),0) AS retention_pct
FROM activity a
LEFT JOIN activity b
  ON b.customer_id=a.customer_id
 AND b.month=(a.month+INTERVAL '1 month')::date
GROUP BY a.month ORDER BY a.month;
```

This rolling month-to-next-month retention is not signup-cohort retention.

## Q34. Signup-cohort month-1 retention.

```sql
WITH cohort AS (
  SELECT customer_id, DATE_TRUNC('month',signup_ts)::date AS cohort_month
  FROM customers WHERE signup_ts IS NOT NULL
),
activity AS (
  SELECT DISTINCT customer_id, DATE_TRUNC('month',event_ts)::date AS activity_month
  FROM events WHERE customer_id IS NOT NULL
),
sizes AS (
  SELECT cohort_month, COUNT(*) AS cohort_customers
  FROM cohort GROUP BY cohort_month
),
retained AS (
  SELECT c.cohort_month, COUNT(DISTINCT c.customer_id) AS retained_customers
  FROM cohort c JOIN activity a
    ON a.customer_id=c.customer_id
   AND a.activity_month=(c.cohort_month+INTERVAL '1 month')::date
  GROUP BY c.cohort_month
)
SELECT s.cohort_month, s.cohort_customers,
       COALESCE(r.retained_customers,0) AS retained_customers,
       100.0*COALESCE(r.retained_customers,0)/NULLIF(s.cohort_customers,0) AS month_1_retention
FROM sizes s LEFT JOIN retained r ON r.cohort_month=s.cohort_month;
```

Define qualifying activity. Signup month and first-purchase month are distinct cohort definitions.

## Q35. Customers active on three consecutive calendar days.

```sql
WITH days AS (
  SELECT DISTINCT customer_id, event_ts::date AS activity_date
  FROM events WHERE customer_id IS NOT NULL
),
x AS (
  SELECT *,
         LAG(activity_date,1) OVER (PARTITION BY customer_id ORDER BY activity_date) AS d1,
         LAG(activity_date,2) OVER (PARTITION BY customer_id ORDER BY activity_date) AS d2
  FROM days
)
SELECT DISTINCT customer_id
FROM x
WHERE activity_date=d1+1 AND d1=d2+1;
```

Deduplicate customer/day to prevent multiple same-day events creating false streaks.

## Q36. Longest consecutive activity streak (gaps-and-islands).

```sql
WITH days AS (
  SELECT DISTINCT customer_id, event_ts::date AS activity_date
  FROM events WHERE customer_id IS NOT NULL
),
numbered AS (
  SELECT *, activity_date - ROW_NUMBER() OVER (
    PARTITION BY customer_id ORDER BY activity_date
  )::int AS island_key
  FROM days
),
streaks AS (
  SELECT customer_id, MIN(activity_date) AS streak_start,
         MAX(activity_date) AS streak_end, COUNT(*) AS streak_days
  FROM numbered GROUP BY customer_id, island_key
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY customer_id ORDER BY streak_days DESC, streak_end DESC
  ) AS rn
  FROM streaks
)
SELECT * FROM ranked WHERE rn=1;
```

Date arithmetic varies by engine; preserve the invariant that consecutive dates map to the same grouping key.

## Q37. Sessionize events with 30-minute inactivity threshold.

```sql
WITH ordered AS (
  SELECT e.*, LAG(event_ts) OVER (
    PARTITION BY customer_id ORDER BY event_ts, event_id
  ) AS previous_ts
  FROM events e
),
flags AS (
  SELECT *, CASE
    WHEN previous_ts IS NULL OR event_ts-previous_ts>INTERVAL '30 minutes'
    THEN 1 ELSE 0 END AS new_session
  FROM ordered
),
numbered AS (
  SELECT *, SUM(new_session) OVER (
    PARTITION BY customer_id ORDER BY event_ts,event_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS derived_session
  FROM flags
)
SELECT customer_id, derived_session, MIN(event_ts) AS session_start,
       MAX(event_ts) AS session_end, COUNT(*) AS event_count
FROM numbered GROUP BY customer_id,derived_session;
```

If a trusted session_id already exists, validate it rather than blindly re-sessionizing. Clarify whether exactly 30 minutes creates a new session (`>` or `>=`).

## Q38. Gap between consecutive orders.

```sql
SELECT customer_id, order_id, order_ts,
       order_ts-LAG(order_ts) OVER (
         PARTITION BY customer_id ORDER BY order_ts,order_id
       ) AS gap_from_previous
FROM orders;
```

Clarify whether cancelled and pending orders count.

## Q39. Orders not completed within 24 hours.

```sql
SELECT order_id,customer_id,order_ts,order_status
FROM orders
WHERE order_status<>'COMPLETED'
  AND order_ts<CURRENT_TIMESTAMP-INTERVAL '24 hours';
```

This current-state alert is not historical SLA measurement. Use status history to calculate actual completion duration and parameterize an as-of timestamp for reproducibility.

## Q40. Show product/date combinations with zero sales.

Create a date spine, cross join products, left join daily product sales, and COALESCE absent units to zero. Fact-only SQL cannot show dates without fact rows.

# 6. Funnels and behavioral analytics

## Q41. Count distinct users at each funnel event.

```sql
SELECT
 COUNT(DISTINCT CASE WHEN event_name='view_product' THEN customer_id END) AS viewers,
 COUNT(DISTINCT CASE WHEN event_name='add_to_cart' THEN customer_id END) AS cart_users,
 COUNT(DISTINCT CASE WHEN event_name='purchase' THEN customer_id END) AS purchasers
FROM events;
```

This is event presence, not ordered conversion.

## Q42. Ordered view → cart → purchase within a session.

```sql
WITH steps AS (
  SELECT customer_id,session_id,
    MIN(CASE WHEN event_name='view_product' THEN event_ts END) AS view_ts,
    MIN(CASE WHEN event_name='add_to_cart' THEN event_ts END) AS cart_ts,
    MIN(CASE WHEN event_name='purchase' THEN event_ts END) AS purchase_ts
  FROM events GROUP BY customer_id,session_id
)
SELECT COUNT(*) FILTER(WHERE view_ts IS NOT NULL) AS viewed,
       COUNT(*) FILTER(WHERE view_ts IS NOT NULL AND cart_ts>=view_ts) AS cart_after_view,
       COUNT(*) FILTER(WHERE view_ts IS NOT NULL AND cart_ts>=view_ts
                                     AND purchase_ts>=cart_ts) AS purchase_after_cart
FROM steps;
```

This is a simplified session funnel. Product-level matching and repeated events require event sequencing and product ID matching. Define attribution window and allowed gaps.

## Q43. Funnel conversion percentages.

Using the same validated funnel base, calculate cart/view, purchase/cart, and purchase/view with `100.0 * numerator / NULLIF(denominator,0)`. Keep numerator and denominator populations aligned.

## Q44. Product view followed by purchase within seven days.

Join view events to purchase events on customer/product; require purchase time >= view time and < view time + 7 days. If purchase events carry only order_id, join orders and order_items to identify purchased product. Deduplicate at the chosen attribution grain.

Clarify first-touch vs last-touch vs multi-touch attribution when several views precede purchase.

## Q45. Customer/product viewed but never purchased later.

```sql
SELECT DISTINCT v.customer_id,v.product_id
FROM events v
WHERE v.event_name='view_product' AND v.product_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1
    FROM events p JOIN order_items oi
      ON oi.order_id=p.order_id AND oi.product_id=v.product_id
    WHERE p.customer_id=v.customer_id
      AND p.event_name='purchase'
      AND p.event_ts>=v.event_ts
  );
```

No attribution horizon is applied here. Add a window if required and decide whether any later session counts.

## Q46. Deduplicate raw event deliveries by event ID.

```sql
WITH ranked AS (
  SELECT r.*, ROW_NUMBER() OVER (
    PARTITION BY event_id
    ORDER BY source_updated_at DESC NULLS LAST, ingested_at DESC
  ) AS rn
  FROM raw_events r
)
SELECT * FROM ranked WHERE rn=1;
```

Keep immutable raw ingestion separate from curated canonical events. The curated teaching DDL assumes event_id uniqueness.

# 7. Deduplication, CDC, and SCD

## Q47. Keep latest customer version by source update.

```sql
WITH ranked AS (
 SELECT r.*,ROW_NUMBER() OVER(
   PARTITION BY customer_id
   ORDER BY source_updated_at DESC NULLS LAST,ingested_at DESC
 ) AS rn
 FROM raw_customers r
)
SELECT * FROM ranked WHERE rn=1;
```

Use deterministic tie-breakers. Do not remove tombstones before ranking, or old active rows may be resurrected.

## Q48. Duplicate emails after normalization.

```sql
SELECT LOWER(TRIM(email)) AS normalized_email,COUNT(*) AS customer_count
FROM customers
WHERE email IS NOT NULL
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*)>1;
```

Email may not be a unique identity key. Shared/recycled addresses and normalization rules require an identity policy.

## Q49. Detect changed attributes with LAG.

```sql
WITH x AS (
 SELECT customer_id,country_code,email,source_updated_at,
        LAG(country_code) OVER(PARTITION BY customer_id ORDER BY source_updated_at,ingested_at) AS old_country,
        LAG(email) OVER(PARTITION BY customer_id ORDER BY source_updated_at,ingested_at) AS old_email
 FROM raw_customer_changes
)
SELECT * FROM x
WHERE country_code IS DISTINCT FROM old_country
   OR email IS DISTINCT FROM old_email;
```

IS DISTINCT FROM is PostgreSQL NULL-safe syntax; use equivalent syntax in other dialects.

## Q50. Build SCD Type 2 from daily snapshots.

```sql
WITH ordered AS (
 SELECT s.*,
        LAG(country_code) OVER(PARTITION BY customer_id ORDER BY snapshot_date) AS old_country,
        LAG(email) OVER(PARTITION BY customer_id ORDER BY snapshot_date) AS old_email
 FROM customer_snapshot s
),
changes AS (
 SELECT * FROM ordered
 WHERE old_country IS NULL
    OR country_code IS DISTINCT FROM old_country
    OR email IS DISTINCT FROM old_email
),
versions AS (
 SELECT customer_id,customer_name,email,country_code,
        snapshot_date AS effective_from,
        LEAD(snapshot_date) OVER(PARTITION BY customer_id ORDER BY snapshot_date) AS next_from
 FROM changes
)
SELECT customer_id,customer_name,email,country_code,effective_from,
       COALESCE(next_from-1,DATE '9999-12-31') AS effective_to,
       (next_from IS NULL) AS is_current
FROM versions;
```

This example uses inclusive date ends. Half-open `[effective_from,effective_to)` intervals are usually safer for timestamps. Daily snapshots miss multiple within-day changes; late history requires interval correction; define tracked attributes, deletes, source precedence, and surrogate keys.

## Q51. SCD Type 1 vs 2 vs 3?

Type 1 overwrites; Type 2 inserts effective-dated versions; Type 3 keeps limited prior values in columns. Choose based on analytical history, privacy, correction, and query requirements.

## Q52. Idempotent latest-state upsert in PostgreSQL.

```sql
INSERT INTO customers (
 customer_id,customer_name,email,country_code,signup_ts,created_at,updated_at,
 is_deleted,source_updated_at,ingested_at
)
SELECT customer_id,customer_name,email,country_code,signup_ts,created_at,updated_at,
       is_deleted,source_updated_at,ingested_at
FROM staged_customers
ON CONFLICT(customer_id) DO UPDATE SET
 customer_name=EXCLUDED.customer_name,
 email=EXCLUDED.email,
 country_code=EXCLUDED.country_code,
 updated_at=EXCLUDED.updated_at,
 is_deleted=EXCLUDED.is_deleted,
 source_updated_at=EXCLUDED.source_updated_at,
 ingested_at=EXCLUDED.ingested_at
WHERE EXCLUDED.source_updated_at>customers.source_updated_at;
```

Older replays cannot overwrite newer state. Define NULL source timestamp ordering, tombstones, source sequence, and concurrency behavior.

## Q53. Process CDC inserts, updates, deletes.

Preserve raw source event identity, business key, operation, source sequence/LSN, commit time, ingestion time. Deduplicate retransmissions by event identity; order changes by source sequence; apply tombstones per policy; make writes idempotent; checkpoint after durable target commit or build recovery for partial commit; reconcile source offsets to target state.

## Q54. Late-arriving facts/dimensions?
