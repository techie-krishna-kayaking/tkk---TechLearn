-- ============================================================
-- CHAPTER 5: DATA MODELING
-- Practice in: Databricks SQL / any SQL engine
-- Topics: Star Schema, Snowflake Schema, SCD Type 1/2,
--         Fact vs Dimension tables, normalization
-- ============================================================

-- ============================================================
-- SECTION 1: STAR SCHEMA — E-Commerce Example
-- ============================================================
-- Star schema: 1 Fact table + multiple Dimension tables
-- Used in: Redshift, Snowflake, BigQuery, Databricks Lakehouse

-- DIMENSION TABLES (descriptive, slowly changing)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key   BIGINT PRIMARY KEY,   -- surrogate key
    customer_id    STRING,               -- natural/business key
    full_name      STRING,
    email          STRING,
    city           STRING,
    state          STRING,
    country        STRING,
    customer_since DATE,
    tier           STRING                -- Bronze/Silver/Gold/Platinum
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key    BIGINT PRIMARY KEY,
    product_id     STRING,
    product_name   STRING,
    category       STRING,
    sub_category   STRING,
    brand          STRING,
    unit_cost      DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key       INT PRIMARY KEY,      -- format: YYYYMMDD e.g. 20240115
    full_date      DATE,
    day_of_week    STRING,
    day_of_month   INT,
    week_of_year   INT,
    month_num      INT,
    month_name     STRING,
    quarter        INT,
    year           INT,
    is_weekend     BOOLEAN,
    is_holiday     BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_key     BIGINT PRIMARY KEY,
    region_name    STRING,
    country        STRING,
    timezone       STRING
);

-- FACT TABLE (transactional, numeric metrics, FK to dims)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id       BIGINT PRIMARY KEY,
    order_date_key INT,                  -- FK → dim_date
    customer_key   BIGINT,              -- FK → dim_customer
    product_key    BIGINT,              -- FK → dim_product
    region_key     BIGINT,              -- FK → dim_region
    -- Measures (additive facts)
    quantity       INT,
    unit_price     DECIMAL(10,2),
    discount_pct   DECIMAL(5,2),
    gross_amount   DECIMAL(12,2),
    discount_amount DECIMAL(12,2),
    net_amount     DECIMAL(12,2),
    cost_amount    DECIMAL(12,2),
    profit         DECIMAL(12,2),
    is_returned    BOOLEAN
);

-- ============================================================
-- SECTION 2: Star Schema Queries (Business Intelligence style)
-- ============================================================

-- Q: Monthly revenue by product category and region (YTD)
SELECT
    d.year,
    d.month_name,
    p.category,
    r.region_name,
    SUM(f.net_amount)  AS revenue,
    SUM(f.profit)      AS profit,
    SUM(f.quantity)    AS units_sold,
    AVG(f.unit_price)  AS avg_price
FROM fact_orders f
JOIN dim_date     d ON f.order_date_key = d.date_key
JOIN dim_product  p ON f.product_key    = p.product_key
JOIN dim_region   r ON f.region_key     = r.region_key
WHERE d.year = 2024
GROUP BY d.year, d.month_name, d.month_num, p.category, r.region_name
ORDER BY d.month_num, revenue DESC;

-- Q: Top 10 customers by lifetime value (LTV)
SELECT
    c.full_name,
    c.tier,
    c.city,
    COUNT(DISTINCT f.order_id)  AS total_orders,
    SUM(f.net_amount)           AS lifetime_value,
    AVG(f.net_amount)           AS avg_order_value,
    MAX(d.full_date)            AS last_order_date
FROM fact_orders f
JOIN dim_customer c ON f.customer_key   = c.customer_key
JOIN dim_date     d ON f.order_date_key = d.date_key
GROUP BY c.customer_key, c.full_name, c.tier, c.city
ORDER BY lifetime_value DESC
LIMIT 10;

-- ============================================================
-- SECTION 3: SNOWFLAKE SCHEMA
-- ============================================================
-- Difference: Dimension tables are normalized (split further)
-- dim_product → sub-dimension: dim_category

CREATE TABLE IF NOT EXISTS dim_category (
    category_key   BIGINT PRIMARY KEY,
    category_name  STRING,
    department     STRING
);

CREATE TABLE IF NOT EXISTS dim_product_snow (
    product_key    BIGINT PRIMARY KEY,
    product_id     STRING,
    product_name   STRING,
    category_key   BIGINT,   -- FK → dim_category (normalized!)
    brand          STRING,
    unit_cost      DECIMAL(10,2)
);
-- Pro: Less redundancy, smaller storage
-- Con: More joins, slower queries — Star schema preferred for analytics

-- ============================================================
-- SECTION 4: SCD (Slowly Changing Dimensions)
-- ============================================================

-- SCD Type 1: Overwrite (no history kept)
-- Use when: history doesn't matter (e.g., phone number)
UPDATE dim_customer
SET city = 'Mumbai', state = 'MH'
WHERE customer_id = 'CUST001';

-- SCD Type 2: Add new row (full history kept) — MOST COMMON
-- Extra columns needed: effective_date, expiry_date, is_current
CREATE TABLE IF NOT EXISTS dim_customer_scd2 (
    customer_key   BIGINT PRIMARY KEY,   -- new surrogate key per version
    customer_id    STRING,               -- natural key (same across versions)
    full_name      STRING,
    email          STRING,
    city           STRING,
    tier           STRING,
    effective_date DATE,
    expiry_date    DATE,                 -- NULL or '9999-12-31' = current
    is_current     BOOLEAN
);

-- Insert SCD2 change (city changed from Pune to Mumbai)
-- Step 1: Expire old record
UPDATE dim_customer_scd2
SET expiry_date = CURRENT_DATE() - INTERVAL 1 DAY,
    is_current  = FALSE
WHERE customer_id = 'CUST001' AND is_current = TRUE;

-- Step 2: Insert new record
INSERT INTO dim_customer_scd2 VALUES
(9999, 'CUST001', 'Alice', 'alice@co.com', 'Mumbai', 'Gold',
 CURRENT_DATE(), '9999-12-31', TRUE);

-- Query: Current state of all customers
SELECT * FROM dim_customer_scd2 WHERE is_current = TRUE;

-- Query: Historical state as of 2023-06-01
SELECT * FROM dim_customer_scd2
WHERE customer_id = 'CUST001'
  AND effective_date <= '2023-06-01'
  AND expiry_date    >= '2023-06-01';

-- ============================================================
-- SECTION 5: Normalization — 1NF, 2NF, 3NF
-- ============================================================
/*
  1NF: Atomic values, no repeating groups
       BAD: orders table with "product1,product2" in one column

  2NF: 1NF + No partial dependencies (every non-key col depends on full PK)
       BAD: order_items(order_id, product_id, product_name)
            product_name depends only on product_id, not full PK

  3NF: 2NF + No transitive dependencies
       BAD: employees(emp_id, dept_id, dept_name)
            dept_name depends on dept_id, not emp_id
       GOOD: Separate dept table

  BCNF (Boyce-Codd): Stronger version of 3NF — every determinant is a key
*/

-- ============================================================
-- SECTION 6: Data Vault (Advanced — asked at senior level)
-- ============================================================
/*
  Data Vault 2.0: Flexible, audit-friendly, handles change well
  Components:
    - HUB: Business keys (customer_id, product_id)
    - LINK: Relationships between hubs (order links customer to product)
    - SATELLITE: Descriptive attributes (name, address — versioned like SCD2)

  When to mention Data Vault:
  → Large enterprises with multiple source systems
  → Need full audit trail
  → Schema changes frequently
*/
