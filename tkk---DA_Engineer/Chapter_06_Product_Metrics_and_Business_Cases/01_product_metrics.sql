-- ============================================================
-- CHAPTER 6: PRODUCT METRICS & BUSINESS CASES
-- Practice in: Databricks SQL
-- Topics asked at: Google, Meta, Uber, Swiggy, Zomato, Flipkart
-- "How would you measure success of feature X?"
-- ============================================================

-- ============================================================
-- SECTION 1: The North Star Metric Framework
-- ============================================================
/*
  North Star Metric = the ONE metric that best captures product value
  Examples:
    - Uber:      Weekly Rides Completed
    - Airbnb:    Nights Booked
    - Spotify:   Time Listening per Day
    - LinkedIn:  Monthly Active Users (MAU)
    - Zomato:    Orders Delivered per Month

  Supporting metrics (guardrails):
    - Revenue, Retention, NPS, Latency, Error Rate

  In interviews: Always state the North Star FIRST, then supporting metrics
*/

-- ============================================================
-- SECTION 2: DAU / MAU / WAU and Engagement Ratio
-- ============================================================

-- Table: user_activity(user_id, activity_date, event_type)

-- DAU: Daily Active Users
SELECT
    activity_date,
    COUNT(DISTINCT user_id) AS DAU
FROM user_activity
WHERE activity_date >= DATE_SUB(CURRENT_DATE(), 30)
GROUP BY activity_date
ORDER BY activity_date;

-- MAU: Monthly Active Users
SELECT
    DATE_FORMAT(activity_date, 'yyyy-MM') AS month,
    COUNT(DISTINCT user_id)               AS MAU
FROM user_activity
GROUP BY DATE_FORMAT(activity_date, 'yyyy-MM')
ORDER BY month;

-- Stickiness Ratio = DAU / MAU (higher = more sticky)
-- Target: > 20% is considered good (Facebook ~66%!)
WITH dau AS (
    SELECT
        activity_date,
        COUNT(DISTINCT user_id) AS daily_users
    FROM user_activity
    WHERE activity_date >= '2024-03-01' AND activity_date < '2024-04-01'
    GROUP BY activity_date
),
mau AS (
    SELECT COUNT(DISTINCT user_id) AS monthly_users
    FROM user_activity
    WHERE activity_date >= '2024-03-01' AND activity_date < '2024-04-01'
)
SELECT
    AVG(d.daily_users)                                   AS avg_dau,
    m.monthly_users                                      AS mau,
    ROUND(AVG(d.daily_users) * 100.0 / m.monthly_users, 2) AS stickiness_pct
FROM dau d
CROSS JOIN mau m;

-- ============================================================
-- SECTION 3: Retention Analysis
-- ============================================================

-- D1 / D7 / D30 Retention (classic mobile app metric)
-- D7 retention = % of Day 0 users still active on Day 7

WITH new_users AS (
    SELECT user_id, MIN(activity_date) AS first_active_date
    FROM user_activity
    GROUP BY user_id
),
cohort AS (
    SELECT
        n.user_id,
        n.first_active_date,
        a.activity_date,
        DATEDIFF(a.activity_date, n.first_active_date) AS day_num
    FROM new_users n
    LEFT JOIN user_activity a ON n.user_id = a.user_id
)
SELECT
    first_active_date                                      AS cohort_date,
    COUNT(DISTINCT user_id)                                AS cohort_size,
    COUNT(DISTINCT CASE WHEN day_num = 1  THEN user_id END) AS d1_retained,
    COUNT(DISTINCT CASE WHEN day_num = 7  THEN user_id END) AS d7_retained,
    COUNT(DISTINCT CASE WHEN day_num = 30 THEN user_id END) AS d30_retained,
    ROUND(COUNT(DISTINCT CASE WHEN day_num = 1  THEN user_id END) * 100.0
          / COUNT(DISTINCT user_id), 2)                    AS d1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN day_num = 7  THEN user_id END) * 100.0
          / COUNT(DISTINCT user_id), 2)                    AS d7_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN day_num = 30 THEN user_id END) * 100.0
          / COUNT(DISTINCT user_id), 2)                    AS d30_retention_pct
FROM cohort
GROUP BY first_active_date
ORDER BY first_active_date;

-- ============================================================
-- SECTION 4: Funnel Analysis
-- ============================================================
-- Conversion funnel: Impression → Click → Cart → Purchase
-- Table: funnel_events(user_id, event_type, event_time)
-- event_type: 'impression', 'click', 'add_to_cart', 'purchase'

WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'impression'   THEN user_id END) AS impressions,
        COUNT(DISTINCT CASE WHEN event_type = 'click'        THEN user_id END) AS clicks,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart'  THEN user_id END) AS cart_adds,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase'     THEN user_id END) AS purchases
    FROM funnel_events
    WHERE event_time >= '2024-01-01'
)
SELECT
    impressions,
    clicks,
    cart_adds,
    purchases,
    ROUND(clicks      * 100.0 / impressions, 2) AS impression_to_click_pct,
    ROUND(cart_adds   * 100.0 / clicks, 2)      AS click_to_cart_pct,
    ROUND(purchases   * 100.0 / cart_adds, 2)   AS cart_to_purchase_pct,
    ROUND(purchases   * 100.0 / impressions, 2) AS overall_conversion_pct
FROM funnel;

-- ============================================================
-- SECTION 5: Cohort Analysis (classic interview ask)
-- ============================================================
-- "Build a retention cohort table by signup month"

WITH cohorts AS (
    SELECT
        user_id,
        DATE_FORMAT(MIN(order_date), 'yyyy-MM') AS cohort_month
    FROM orders
    GROUP BY user_id
),
order_months AS (
    SELECT
        o.user_id,
        c.cohort_month,
        DATE_FORMAT(o.order_date, 'yyyy-MM') AS order_month,
        MONTHS_BETWEEN(
            DATE_FORMAT(o.order_date, 'yyyy-MM-01'),
            DATE_FORMAT(c.cohort_month || '-01', 'yyyy-MM-01')
        ) AS months_since_signup
    FROM orders o
    JOIN cohorts c ON o.user_id = c.user_id
)
SELECT
    cohort_month,
    COUNT(DISTINCT CASE WHEN months_since_signup = 0 THEN user_id END) AS m0,
    COUNT(DISTINCT CASE WHEN months_since_signup = 1 THEN user_id END) AS m1,
    COUNT(DISTINCT CASE WHEN months_since_signup = 2 THEN user_id END) AS m2,
    COUNT(DISTINCT CASE WHEN months_since_signup = 3 THEN user_id END) AS m3,
    COUNT(DISTINCT CASE WHEN months_since_signup = 6 THEN user_id END) AS m6
FROM order_months
GROUP BY cohort_month
ORDER BY cohort_month;

-- ============================================================
-- SECTION 6: KPI Decomposition (Interview Framework)
-- ============================================================
/*
  Q: "Revenue dropped 20% this month — how do you debug it?"

  Decompose Revenue = Volume × Price
  Volume     = Users × Conversion Rate × Orders per User
  Price      = Avg Order Value

  Check each component:
  1. Total users   ↓?  → Acquisition problem (marketing, channel)
  2. Conversion    ↓?  → Product/UX issue, competitor
  3. AOV           ↓?  → Product mix shift, promotions, discounts
  4. Segment drill: category, region, device, user cohort
  5. External factors: seasonality, market events, supply issues

  ALWAYS ask clarifying questions first:
  - Is this a data/reporting issue?
  - Which segments? New vs returning users?
  - Any product changes deployed recently?
  - Competitor activity?
*/

-- Metric decomposition query template
SELECT
    DATE_FORMAT(order_date, 'yyyy-MM')   AS month,
    COUNT(DISTINCT customer_id)          AS unique_buyers,
    COUNT(DISTINCT order_id)             AS total_orders,
    SUM(net_amount)                      AS revenue,
    ROUND(SUM(net_amount) /
          COUNT(DISTINCT customer_id), 2) AS rev_per_user,
    ROUND(COUNT(DISTINCT order_id) /
          COUNT(DISTINCT customer_id), 2) AS orders_per_user,
    ROUND(SUM(net_amount) /
          COUNT(DISTINCT order_id), 2)   AS avg_order_value
FROM orders
GROUP BY DATE_FORMAT(order_date, 'yyyy-MM')
ORDER BY month;
