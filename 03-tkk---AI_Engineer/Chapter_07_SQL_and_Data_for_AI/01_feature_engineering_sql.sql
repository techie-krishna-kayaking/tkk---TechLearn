-- ============================================================
-- CHAPTER 7: SQL & DATA FOR AI ENGINEERS
-- Practice in: Databricks SQL
-- Topics: Feature engineering in SQL, training data prep,
--         time-series features, data quality for ML
-- ============================================================

-- ============================================================
-- SECTION 1: Feature Engineering in SQL
-- (How to build ML features without Python)
-- ============================================================

-- Scenario: Build user features for a churn prediction model
-- Tables: users(user_id, signup_date, city, plan_type)
--         events(user_id, event_date, event_type, session_id)
--         orders(user_id, order_date, amount, status)

-- Q: Build a feature table as of a reference date (point-in-time correct)
-- CRITICAL: Always use a cutoff date to prevent data leakage!

WITH reference_date AS (
    SELECT DATE('2024-03-31') AS cutoff     -- training cutoff
),

-- Recency features
recency_features AS (
    SELECT
        o.user_id,
        DATEDIFF((SELECT cutoff FROM reference_date), MAX(o.order_date)) AS days_since_last_order,
        DATEDIFF((SELECT cutoff FROM reference_date), MIN(o.order_date)) AS days_since_first_order
    FROM orders o
    WHERE o.order_date < (SELECT cutoff FROM reference_date)
      AND o.status = 'completed'
    GROUP BY o.user_id
),

-- Frequency features (30d, 90d, 365d windows)
frequency_features AS (
    SELECT
        o.user_id,
        COUNT(DISTINCT CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), o.order_date) <= 30
                            THEN o.order_id END)  AS orders_last_30d,
        COUNT(DISTINCT CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), o.order_date) <= 90
                            THEN o.order_id END)  AS orders_last_90d,
        COUNT(DISTINCT o.order_id)                 AS total_orders
    FROM orders o
    WHERE o.order_date < (SELECT cutoff FROM reference_date)
      AND o.status = 'completed'
    GROUP BY o.user_id
),

-- Monetary features
monetary_features AS (
    SELECT
        o.user_id,
        SUM(CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), o.order_date) <= 30
                 THEN o.amount END)                AS gmv_30d,
        SUM(CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), o.order_date) <= 90
                 THEN o.amount END)                AS gmv_90d,
        AVG(o.amount)                              AS avg_order_value,
        MAX(o.amount)                              AS max_order_value,
        STDDEV(o.amount)                           AS std_order_value       -- variability signal
    FROM orders o
    WHERE o.order_date < (SELECT cutoff FROM reference_date)
      AND o.status = 'completed'
    GROUP BY o.user_id
),

-- Behavioral features (session engagement)
behavioral_features AS (
    SELECT
        e.user_id,
        COUNT(DISTINCT CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), e.event_date) <= 7
                            THEN DATE(e.event_date) END)  AS active_days_last_7d,
        COUNT(DISTINCT CASE WHEN DATEDIFF((SELECT cutoff FROM reference_date), e.event_date) <= 30
                            THEN e.session_id END)        AS sessions_last_30d,
        COUNT(CASE WHEN e.event_type = 'search'
                    AND DATEDIFF((SELECT cutoff FROM reference_date), e.event_date) <= 30
                   THEN 1 END)                            AS searches_last_30d,
        COUNT(CASE WHEN e.event_type = 'app_crash'
                    AND DATEDIFF((SELECT cutoff FROM reference_date), e.event_date) <= 30
                   THEN 1 END)                            AS crashes_last_30d  -- quality signal
    FROM events e
    WHERE e.event_date < (SELECT cutoff FROM reference_date)
    GROUP BY e.user_id
),

-- Trend features — is engagement going up or down?
trend_features AS (
    SELECT
        user_id,
        SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), order_date) BETWEEN 0  AND 29  THEN amount END) AS gmv_0_30,
        SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), order_date) BETWEEN 30 AND 59  THEN amount END) AS gmv_30_60,
        SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), order_date) BETWEEN 60 AND 89  THEN amount END) AS gmv_60_90
    FROM orders
    WHERE status = 'completed'
    GROUP BY user_id
)

-- Assemble final feature table
SELECT
    u.user_id,
    u.plan_type,
    u.city,
    DATEDIFF(CURRENT_DATE(), u.signup_date)       AS account_age_days,

    -- Recency
    COALESCE(r.days_since_last_order, 999)         AS days_since_last_order,
    COALESCE(r.days_since_first_order, 0)          AS days_since_first_order,

    -- Frequency
    COALESCE(f.orders_last_30d, 0)                 AS orders_last_30d,
    COALESCE(f.orders_last_90d, 0)                 AS orders_last_90d,
    COALESCE(f.total_orders, 0)                    AS total_orders,

    -- Monetary
    COALESCE(m.gmv_30d, 0)                         AS gmv_30d,
    COALESCE(m.gmv_90d, 0)                         AS gmv_90d,
    COALESCE(m.avg_order_value, 0)                 AS avg_order_value,
    COALESCE(m.std_order_value, 0)                 AS std_order_value,

    -- Behavioral
    COALESCE(b.active_days_last_7d, 0)             AS active_days_last_7d,
    COALESCE(b.sessions_last_30d, 0)               AS sessions_last_30d,
    COALESCE(b.crashes_last_30d, 0)                AS crashes_last_30d,

    -- Trend (is spend accelerating or decelerating?)
    COALESCE(t.gmv_0_30, 0) - COALESCE(t.gmv_30_60, 0)  AS spend_trend_mom,

    -- Derived ratio features
    CASE WHEN f.total_orders > 0
         THEN COALESCE(f.orders_last_30d, 0) * 1.0 / f.total_orders
         ELSE 0 END                                AS recent_order_share

FROM users u
LEFT JOIN recency_features    r ON u.user_id = r.user_id
LEFT JOIN frequency_features  f ON u.user_id = f.user_id
LEFT JOIN monetary_features   m ON u.user_id = m.user_id
LEFT JOIN behavioral_features b ON u.user_id = b.user_id
LEFT JOIN trend_features      t ON u.user_id = t.user_id;

-- ============================================================
-- SECTION 2: Point-in-Time Correct Training Data
-- ============================================================
-- NEVER JOIN training labels with features computed after the label date.
-- This is the #1 data leakage source in production ML.

-- WRONG approach (data leakage):
-- SELECT u.*, avg(o.amount) AS avg_order_value
-- FROM users u JOIN orders o ON u.user_id = o.user_id
-- -- ^ includes orders AFTER the label date!

-- CORRECT approach:
WITH label_dates AS (
    -- Define the label for each user-date pair
    SELECT
        user_id,
        label_date,           -- date we make prediction as of
        churned_next_30d      -- label: did user churn in next 30 days?
    FROM churn_labels
),
point_in_time_features AS (
    SELECT
        l.user_id,
        l.label_date,
        l.churned_next_30d,
        -- Feature: only look at data BEFORE label_date
        AVG(CASE WHEN o.order_date < l.label_date THEN o.amount END) AS avg_order_value,
        COUNT(CASE WHEN o.order_date >= DATE_SUB(l.label_date, 30)
                    AND o.order_date < l.label_date THEN 1 END)        AS orders_last_30d
    FROM label_dates l
    LEFT JOIN orders o ON l.user_id = o.user_id
    GROUP BY l.user_id, l.label_date, l.churned_next_30d
)
SELECT * FROM point_in_time_features;

-- ============================================================
-- SECTION 3: Data Quality Checks for ML Pipelines
-- ============================================================

-- Run these checks BEFORE feeding data to training

-- Check 1: Null rates per feature
SELECT
    'user_id'           AS feature, SUM(CASE WHEN user_id           IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS null_pct FROM users
UNION ALL
SELECT 'email',                      SUM(CASE WHEN email              IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) FROM users
UNION ALL
SELECT 'signup_date',                SUM(CASE WHEN signup_date        IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) FROM users;

-- Check 2: Outlier detection — values beyond 5 standard deviations
WITH stats AS (
    SELECT AVG(amount) AS mu, STDDEV(amount) AS sigma FROM orders
)
SELECT COUNT(*) AS outlier_count,
       MIN(amount) AS min_outlier,
       MAX(amount) AS max_outlier
FROM orders, stats
WHERE ABS(amount - mu) > 5 * sigma;

-- Check 3: Class balance for classification target
SELECT
    churned_next_30d,
    COUNT(*)                          AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM churn_labels
GROUP BY churned_next_30d;

-- Check 4: Temporal ordering — no future data leakage
SELECT COUNT(*) AS leakage_rows
FROM churn_labels cl
JOIN orders o ON cl.user_id = o.user_id
WHERE o.order_date >= cl.label_date;  -- should be 0

-- Check 5: Feature distribution stability (compare training vs serving)
-- Compare with PSI in SQL (binned):
WITH baseline AS (
    SELECT
        FLOOR(avg_order_value / 50) * 50 AS bucket,
        COUNT(*) AS n
    FROM training_features
    GROUP BY bucket
),
current AS (
    SELECT
        FLOOR(avg_order_value / 50) * 50 AS bucket,
        COUNT(*) AS n
    FROM serving_features_today
    GROUP BY bucket
)
SELECT
    b.bucket,
    b.n / SUM(b.n) OVER ()             AS baseline_pct,
    c.n / SUM(c.n) OVER ()             AS current_pct,
    (b.n / SUM(b.n) OVER () - c.n / SUM(c.n) OVER ())
    * LN((b.n / SUM(b.n) OVER ()) / NULLIF(c.n / SUM(c.n) OVER (), 0)) AS psi_contribution
FROM baseline b
JOIN current  c ON b.bucket = c.bucket;
