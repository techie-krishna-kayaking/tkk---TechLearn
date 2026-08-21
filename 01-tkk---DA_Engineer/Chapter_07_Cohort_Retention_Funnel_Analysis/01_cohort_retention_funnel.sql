-- ============================================================
-- CHAPTER 7: COHORT, RETENTION & FUNNEL ANALYSIS
-- Practice in: Databricks SQL + Python
-- These are the most commonly asked case study problems
-- at Swiggy, Zomato, Uber, Flipkart, Myntra, Google, Meta
-- ============================================================

-- ============================================================
-- SECTION 1: Monthly Cohort Retention Heatmap (SQL)
-- ============================================================
-- Canonical cohort table: who signed up in month X,
-- and what % came back in subsequent months?

-- Step 1: Assign cohort month to each user
WITH user_cohorts AS (
    SELECT
        user_id,
        DATE_FORMAT(MIN(event_date), 'yyyy-MM') AS cohort_month
    FROM user_events
    WHERE event_type = 'signup'
    GROUP BY user_id
),

-- Step 2: For each activity, compute months since signup
user_activity_enriched AS (
    SELECT
        e.user_id,
        c.cohort_month,
        DATE_FORMAT(e.event_date, 'yyyy-MM')                        AS activity_month,
        CAST(
            MONTHS_BETWEEN(
                DATE_FORMAT(e.event_date, 'yyyy-MM-dd'),
                DATE_FORMAT(c.cohort_month || '-01', 'yyyy-MM-dd')
            ) AS INT
        )                                                           AS month_number
    FROM user_events e
    JOIN user_cohorts c ON e.user_id = c.user_id
),

-- Step 3: Pivot — cohort size and retained users per month_number
cohort_pivot AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id)                                             AS cohort_size,
        COUNT(DISTINCT CASE WHEN month_number = 0  THEN user_id END)       AS m0,
        COUNT(DISTINCT CASE WHEN month_number = 1  THEN user_id END)       AS m1,
        COUNT(DISTINCT CASE WHEN month_number = 2  THEN user_id END)       AS m2,
        COUNT(DISTINCT CASE WHEN month_number = 3  THEN user_id END)       AS m3,
        COUNT(DISTINCT CASE WHEN month_number = 6  THEN user_id END)       AS m6,
        COUNT(DISTINCT CASE WHEN month_number = 12 THEN user_id END)       AS m12
    FROM user_activity_enriched
    GROUP BY cohort_month
)

-- Step 4: Convert to retention percentages
SELECT
    cohort_month,
    cohort_size,
    ROUND(m0  * 100.0 / cohort_size, 1) AS r_m0,
    ROUND(m1  * 100.0 / cohort_size, 1) AS r_m1,
    ROUND(m2  * 100.0 / cohort_size, 1) AS r_m2,
    ROUND(m3  * 100.0 / cohort_size, 1) AS r_m3,
    ROUND(m6  * 100.0 / cohort_size, 1) AS r_m6,
    ROUND(m12 * 100.0 / cohort_size, 1) AS r_m12
FROM cohort_pivot
ORDER BY cohort_month;

-- ============================================================
-- SECTION 2: Funnel Drop-off Analysis
-- ============================================================
-- Find WHERE in the funnel users are dropping off most

WITH funnel_counts AS (
    SELECT
        'step1_visit'     AS step, 1 AS step_order, COUNT(DISTINCT user_id) AS users FROM funnel_events WHERE event_type='page_view'
    UNION ALL
    SELECT 'step2_search',  2, COUNT(DISTINCT user_id) FROM funnel_events WHERE event_type='search'
    UNION ALL
    SELECT 'step3_product', 3, COUNT(DISTINCT user_id) FROM funnel_events WHERE event_type='product_view'
    UNION ALL
    SELECT 'step4_cart',    4, COUNT(DISTINCT user_id) FROM funnel_events WHERE event_type='add_to_cart'
    UNION ALL
    SELECT 'step5_checkout',5, COUNT(DISTINCT user_id) FROM funnel_events WHERE event_type='checkout_start'
    UNION ALL
    SELECT 'step6_purchase',6, COUNT(DISTINCT user_id) FROM funnel_events WHERE event_type='purchase'
)
SELECT
    step,
    step_order,
    users,
    LAG(users) OVER (ORDER BY step_order)                     AS prev_step_users,
    ROUND(users * 100.0
          / FIRST_VALUE(users) OVER (ORDER BY step_order), 2) AS pct_of_top,
    ROUND(
        (LAG(users) OVER (ORDER BY step_order) - users) * 100.0
        / NULLIF(LAG(users) OVER (ORDER BY step_order), 0), 2
    )                                                         AS drop_off_pct
FROM funnel_counts
ORDER BY step_order;

-- ============================================================
-- SECTION 3: Churn Analysis
-- ============================================================
-- Define churn: user who was active in Month-2 but NOT in Month-1

WITH month_activity AS (
    SELECT
        user_id,
        DATE_FORMAT(activity_date, 'yyyy-MM') AS activity_month
    FROM user_activity
    GROUP BY user_id, DATE_FORMAT(activity_date, 'yyyy-MM')
),
two_months AS (
    SELECT
        COALESCE(m2.user_id, m1.user_id)    AS user_id,
        m2.activity_month                    AS two_months_ago,
        m1.activity_month                    AS last_month
    FROM month_activity m2
    FULL OUTER JOIN month_activity m1
        ON  m2.user_id = m1.user_id
        AND ADD_MONTHS(m2.activity_month || '-01', 1)
            = m1.activity_month || '-01'
    WHERE m2.activity_month = DATE_FORMAT(ADD_MONTHS(CURRENT_DATE(), -2), 'yyyy-MM')
)
SELECT
    COUNT(*)                                                           AS active_2_months_ago,
    COUNT(CASE WHEN last_month IS NOT NULL THEN 1 END)                AS retained,
    COUNT(CASE WHEN last_month IS NULL     THEN 1 END)                AS churned,
    ROUND(COUNT(CASE WHEN last_month IS NULL THEN 1 END) * 100.0
          / COUNT(*), 2)                                              AS churn_rate_pct
FROM two_months;

-- ============================================================
-- SECTION 4: User Segmentation (RFM Analysis)
-- ============================================================
-- RFM = Recency, Frequency, Monetary — classic customer segmentation

WITH rfm_base AS (
    SELECT
        customer_id,
        DATEDIFF(CURRENT_DATE(), MAX(order_date))   AS recency_days,
        COUNT(DISTINCT order_id)                    AS frequency,
        SUM(net_amount)                             AS monetary
    FROM orders
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days ASC)  AS r_score,  -- lower days = better
        NTILE(5) OVER (ORDER BY frequency DESC)    AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC)     AS m_score
    FROM rfm_base
),
rfm_segments AS (
    SELECT *,
           (r_score + f_score + m_score) AS total_score,
           CASE
               WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
               WHEN r_score >= 3 AND f_score >= 3                   THEN 'Loyal Customers'
               WHEN r_score >= 4 AND f_score <= 2                   THEN 'New Customers'
               WHEN r_score <= 2 AND f_score >= 3                   THEN 'At Risk'
               WHEN r_score <= 2 AND f_score <= 2                   THEN 'Lost'
               ELSE 'Potential Loyalists'
           END AS segment
    FROM rfm_scored
)
SELECT
    segment,
    COUNT(*)                       AS customer_count,
    ROUND(AVG(recency_days), 0)    AS avg_recency_days,
    ROUND(AVG(frequency), 1)       AS avg_orders,
    ROUND(AVG(monetary), 2)        AS avg_ltv
FROM rfm_segments
GROUP BY segment
ORDER BY avg_ltv DESC;
