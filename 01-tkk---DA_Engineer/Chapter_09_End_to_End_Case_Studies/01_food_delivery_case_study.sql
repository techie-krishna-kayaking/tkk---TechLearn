-- ============================================================
-- CHAPTER 9: END-TO-END CASE STUDY
-- "Food Delivery App" — Swiggy/Zomato/Uber Eats style
-- Practice in: Databricks SQL
-- This simulates a real senior DA take-home / round
-- ============================================================

-- SCHEMA:
-- users(user_id, signup_date, city, device)
-- restaurants(rest_id, name, city, cuisine, avg_rating)
-- orders(order_id, user_id, rest_id, order_date, status, delivery_mins, amount, discount)
-- sessions(session_id, user_id, session_date, screens_viewed, app_crashes)

-- ============================================================
-- BUSINESS QUESTION 1:
-- "GMV is down 15% week-over-week. Debug it."
-- ============================================================

-- Step 1: Confirm the drop
WITH weekly_gmv AS (
    SELECT
        DATE_TRUNC('week', order_date)    AS week_start,
        SUM(amount)                        AS gmv,
        COUNT(DISTINCT order_id)           AS orders,
        COUNT(DISTINCT user_id)            AS buyers,
        SUM(amount) / COUNT(DISTINCT order_id) AS aov
    FROM orders
    WHERE status = 'delivered'
    GROUP BY DATE_TRUNC('week', order_date)
)
SELECT
    week_start,
    gmv,
    orders,
    buyers,
    aov,
    LAG(gmv)    OVER (ORDER BY week_start)                                  AS prev_week_gmv,
    ROUND((gmv - LAG(gmv) OVER (ORDER BY week_start)) * 100.0
          / NULLIF(LAG(gmv) OVER (ORDER BY week_start), 0), 2)              AS wow_gmv_pct
FROM weekly_gmv
ORDER BY week_start;

-- Step 2: Decompose — is it fewer users OR lower order rate OR lower AOV?
WITH this_week AS (
    SELECT user_id, order_id, amount
    FROM orders
    WHERE order_date >= CURRENT_DATE - 7 AND status = 'delivered'
),
last_week AS (
    SELECT user_id, order_id, amount
    FROM orders
    WHERE order_date >= CURRENT_DATE - 14 AND order_date < CURRENT_DATE - 7 AND status = 'delivered'
)
SELECT
    'This Week' AS period,
    COUNT(DISTINCT user_id)                      AS buyers,
    COUNT(DISTINCT order_id)                     AS orders,
    SUM(amount)                                  AS gmv,
    ROUND(SUM(amount) / COUNT(DISTINCT user_id), 2) AS gmv_per_user,
    ROUND(COUNT(DISTINCT order_id) / COUNT(DISTINCT user_id), 2) AS orders_per_user,
    ROUND(SUM(amount) / COUNT(DISTINCT order_id), 2) AS aov
FROM this_week
UNION ALL
SELECT 'Last Week', COUNT(DISTINCT user_id), COUNT(DISTINCT order_id),
       SUM(amount), ROUND(SUM(amount)/COUNT(DISTINCT user_id),2),
       ROUND(COUNT(DISTINCT order_id)/COUNT(DISTINCT user_id),2),
       ROUND(SUM(amount)/COUNT(DISTINCT order_id),2)
FROM last_week;

-- Step 3: Segment drill — which city / cuisine dropped?
SELECT
    r.city,
    r.cuisine,
    SUM(CASE WHEN o.order_date >= CURRENT_DATE - 7  THEN o.amount END) AS gmv_this_week,
    SUM(CASE WHEN o.order_date >= CURRENT_DATE - 14
             AND o.order_date < CURRENT_DATE - 7    THEN o.amount END) AS gmv_last_week,
    ROUND(
        (SUM(CASE WHEN o.order_date >= CURRENT_DATE - 7  THEN o.amount END)
       - SUM(CASE WHEN o.order_date >= CURRENT_DATE - 14
                  AND o.order_date < CURRENT_DATE - 7 THEN o.amount END)) * 100.0
        / NULLIF(SUM(CASE WHEN o.order_date >= CURRENT_DATE - 14
                          AND o.order_date < CURRENT_DATE - 7 THEN o.amount END), 0),
    2) AS wow_pct
FROM orders o
JOIN restaurants r ON o.rest_id = r.rest_id
WHERE o.status = 'delivered'
GROUP BY r.city, r.cuisine
ORDER BY wow_pct ASC
LIMIT 20;

-- ============================================================
-- BUSINESS QUESTION 2:
-- "We launched a new checkout flow. Was it successful?"
-- ============================================================
-- Assume: treatment_users table has user_id, group (control/treatment)

WITH experiment AS (
    SELECT
        t.group,
        COUNT(DISTINCT t.user_id)                                       AS exposed_users,
        COUNT(DISTINCT o.user_id)                                       AS converted_users,
        COUNT(DISTINCT o.order_id)                                      AS orders,
        SUM(o.amount)                                                   AS gmv,
        ROUND(COUNT(DISTINCT o.user_id) * 100.0
              / COUNT(DISTINCT t.user_id), 2)                           AS conversion_pct,
        ROUND(SUM(o.amount) / NULLIF(COUNT(DISTINCT t.user_id), 0), 2) AS gmv_per_user
    FROM treatment_users t
    LEFT JOIN orders o
        ON  t.user_id = o.user_id
        AND o.order_date BETWEEN '2024-03-01' AND '2024-03-31'
    GROUP BY t.group
)
SELECT * FROM experiment;

-- ============================================================
-- BUSINESS QUESTION 3:
-- "Identify power users vs at-risk users"
-- ============================================================

WITH user_stats AS (
    SELECT
        user_id,
        COUNT(DISTINCT order_id)                            AS total_orders,
        SUM(amount)                                         AS total_spend,
        DATEDIFF(CURRENT_DATE(), MAX(order_date))           AS days_since_last_order,
        DATEDIFF(MAX(order_date), MIN(order_date))          AS active_span_days,
        AVG(amount)                                         AS avg_order_value,
        AVG(delivery_mins)                                  AS avg_delivery_mins
    FROM orders
    WHERE status = 'delivered'
    GROUP BY user_id
),
segmented AS (
    SELECT *,
        CASE
            WHEN total_orders >= 10 AND days_since_last_order <= 14 THEN 'Power User'
            WHEN total_orders >= 5  AND days_since_last_order <= 30 THEN 'Regular'
            WHEN total_orders >= 1  AND days_since_last_order <= 60 THEN 'Occasional'
            WHEN days_since_last_order > 60                         THEN 'At Risk'
            ELSE 'New'
        END AS user_segment
    FROM user_stats
)
SELECT
    user_segment,
    COUNT(*)                        AS user_count,
    ROUND(AVG(total_orders), 1)     AS avg_orders,
    ROUND(AVG(total_spend), 2)      AS avg_ltv,
    ROUND(AVG(days_since_last_order), 0) AS avg_recency
FROM segmented
GROUP BY user_segment
ORDER BY avg_ltv DESC;

-- ============================================================
-- BUSINESS QUESTION 4:
-- "Which restaurants should we feature on homepage?"
-- ============================================================
-- Score = weighted combination of orders, rating, delivery time, revenue

WITH rest_stats AS (
    SELECT
        r.rest_id,
        r.name,
        r.cuisine,
        r.city,
        r.avg_rating,
        COUNT(DISTINCT o.order_id)                         AS total_orders,
        SUM(o.amount)                                      AS total_gmv,
        AVG(o.delivery_mins)                               AS avg_delivery_mins,
        COUNT(DISTINCT CASE WHEN o.status = 'cancelled'
                            THEN o.order_id END) * 1.0
        / COUNT(DISTINCT o.order_id)                       AS cancel_rate
    FROM restaurants r
    LEFT JOIN orders o ON r.rest_id = o.rest_id
    WHERE o.order_date >= DATE_SUB(CURRENT_DATE(), 30)
    GROUP BY r.rest_id, r.name, r.cuisine, r.city, r.avg_rating
),
normalized AS (
    SELECT *,
        -- Normalize each metric 0-1 using min-max
        (total_orders   - MIN(total_orders)   OVER()) / NULLIF(MAX(total_orders)   OVER() - MIN(total_orders)   OVER(), 0) AS orders_norm,
        (avg_rating     - MIN(avg_rating)     OVER()) / NULLIF(MAX(avg_rating)     OVER() - MIN(avg_rating)     OVER(), 0) AS rating_norm,
        1 - (avg_delivery_mins - MIN(avg_delivery_mins) OVER()) /
            NULLIF(MAX(avg_delivery_mins) OVER() - MIN(avg_delivery_mins) OVER(), 0)                                       AS speed_norm,
        1 - cancel_rate                                                                                                    AS reliability_norm
    FROM rest_stats
)
SELECT
    rest_id,
    name,
    cuisine,
    city,
    avg_rating,
    total_orders,
    ROUND(0.30 * orders_norm + 0.30 * rating_norm +
          0.25 * speed_norm  + 0.15 * reliability_norm, 4) AS homepage_score
FROM normalized
ORDER BY homepage_score DESC
LIMIT 20;
