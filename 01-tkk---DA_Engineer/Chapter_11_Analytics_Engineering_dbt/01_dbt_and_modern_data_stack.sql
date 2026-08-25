-- ============================================================
-- CHAPTER 11: ANALYTICS ENGINEERING with dbt (Modern Data Stack)
-- Practice in: dbt + Snowflake / BigQuery / Databricks
-- The Analytics Engineer skillset is what pushes DA comp from
-- 40-50 LPA into the 70-90 LPA band. Owning the transformation
-- layer + semantic layer = staff-level leverage.
-- ============================================================
-- This file is a WALKTHROUGH: SQL models + the dbt YAML/config
-- that wraps them. Read top-to-bottom like a real dbt project.
-- ============================================================


-- ============================================================
-- SECTION 1: WHY ANALYTICS ENGINEERING
-- ------------------------------------------------------------
-- Analyst (SQL in a BI tool)         -> answers one question
-- Analytics Engineer (dbt + tests)   -> owns TRUSTED metrics for
--                                       the whole org, versioned,
--                                       tested, documented in git.
-- Interview signal: you think in LAYERS, not one-off queries:
--   sources -> staging -> intermediate -> marts -> semantic layer
-- ============================================================


-- ============================================================
-- SECTION 2: PROJECT STRUCTURE (say this in the interview)
-- ------------------------------------------------------------
-- models/
--   staging/      1:1 with source, rename+cast+clean ONLY
--   intermediate/ reusable business logic, joins, fan-out fixes
--   marts/        final star-schema tables BI/stakeholders use
--     core/       dim_users, dim_dates, fct_orders
--     finance/    fct_revenue, fct_refunds
-- Naming: stg_<source>__<entity>, int_<verb>, dim_/fct_<entity>
-- ============================================================


-- ------------------------------------------------------------
-- FILE: models/staging/stg_orders.sql
-- Staging = clean, cast, rename. NO business logic, NO joins.
-- ------------------------------------------------------------
-- {{ config(materialized='view') }}
WITH source AS (
    SELECT * FROM {{ source('shop', 'raw_orders') }}
),
renamed AS (
    SELECT
        order_id::STRING              AS order_id,
        customer_id::STRING           AS customer_id,
        LOWER(status)                 AS order_status,
        CAST(amount AS DECIMAL(12,2)) AS gross_amount,
        CAST(created_at AS TIMESTAMP) AS created_at
    FROM source
    WHERE order_id IS NOT NULL          -- drop corrupt rows early
)
SELECT * FROM renamed;


-- ------------------------------------------------------------
-- FILE: models/marts/core/fct_orders.sql
-- Fact table: grain = ONE ROW PER ORDER. State the grain always.
-- Shows: ref() lineage, incremental materialization, surrogate key
-- ------------------------------------------------------------
-- {{ config(
--       materialized='incremental',
--       unique_key='order_id',
--       incremental_strategy='merge',
--       on_schema_change='append_new_columns'
--    ) }}
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['o.order_id']) }} AS order_key,
        o.order_id,
        o.customer_id,
        c.customer_segment,
        o.order_status,
        o.gross_amount,
        o.created_at,
        DATE(o.created_at) AS order_date
    FROM orders o
    LEFT JOIN customers c USING (customer_id)

    {% if is_incremental() %}
      -- Only process new/updated rows since last run (cost saver)
      WHERE o.created_at > (SELECT MAX(created_at) FROM {{ this }})
    {% endif %}
)
SELECT * FROM final;
-- INTERVIEW LINE: "Incremental + merge means we reprocess only new
-- partitions, cutting warehouse cost 10-100x on large fact tables."


-- ------------------------------------------------------------
-- FILE: models/marts/core/schema.yml
-- TESTS + DOCS live next to the model. This is the trust layer.
-- ------------------------------------------------------------
-- version: 2
-- models:
--   - name: fct_orders
--     description: "One row per order. Grain: order_id."
--     columns:
--       - name: order_key
--         description: "Surrogate PK."
--         tests: [unique, not_null]
--       - name: customer_id
--         tests:
--           - not_null
--           - relationships:
--               to: ref('dim_customers')
--               field: customer_id
--       - name: order_status
--         tests:
--           - accepted_values:
--               values: ['placed','shipped','delivered','cancelled']
--       - name: gross_amount
--         tests:
--           - dbt_utils.accepted_range:
--               min_value: 0
-- INTERVIEW LINE: "unique+not_null+relationships+accepted_values are
-- my four workhorse tests. They catch 90% of pipeline breakages
-- BEFORE stakeholders see a wrong number."


-- ============================================================
-- SECTION 3: SLOWLY CHANGING DIMENSIONS via dbt SNAPSHOTS
-- ------------------------------------------------------------
-- dbt automates SCD Type 2 with snapshots (no hand-written MERGE).
-- FILE: snapshots/customers_snapshot.sql
-- {% snapshot customers_snapshot %}
--   {{ config(
--        target_schema='snapshots',
--        unique_key='customer_id',
--        strategy='timestamp',
--        updated_at='updated_at'
--   ) }}
--   SELECT * FROM {{ source('shop', 'raw_customers') }}
-- {% endsnapshot %}
-- dbt auto-adds dbt_valid_from / dbt_valid_to => full history.
-- ============================================================


-- ============================================================
-- SECTION 4: REUSABLE MACRO (DRY business logic)
-- ------------------------------------------------------------
-- FILE: macros/net_revenue.sql
-- {% macro net_revenue(gross_col, refund_col) %}
--     ({{ gross_col }} - COALESCE({{ refund_col }}, 0))
-- {% endmacro %}
-- Usage in a model:  {{ net_revenue('gross_amount','refund_amount') }} AS net_rev
-- One definition of "net revenue" org-wide => no metric drift.
-- ============================================================


-- ============================================================
-- SECTION 5: THE SEMANTIC LAYER (Metrics-as-code) — SENIOR TOPIC
-- ------------------------------------------------------------
-- The #1 org pain: "every dashboard defines 'active user'
-- differently." The semantic layer defines a metric ONCE; every
-- tool (BI, notebooks, APIs) queries the same definition.
-- FILE: models/marts/core/metrics.yml  (dbt MetricFlow / Cube style)
-- ------------------------------------------------------------
-- semantic_models:
--   - name: orders
--     model: ref('fct_orders')
--     entities: [{name: order, type: primary, expr: order_id}]
--     dimensions:
--       - name: order_date
--         type: time
--         type_params: {time_granularity: day}
--       - name: customer_segment
--         type: categorical
--     measures:
--       - name: net_revenue
--         agg: sum
--         expr: gross_amount
--       - name: order_count
--         agg: count
--         expr: order_id
-- metrics:
--   - name: revenue
--     type: simple
--     type_params: {measure: net_revenue}
--   - name: aov                      # composed metric
--     type: ratio
--     type_params: {numerator: net_revenue, denominator: order_count}
-- INTERVIEW LINE: "A semantic layer is the single source of truth
-- for metrics. It kills the 'which number is right?' debate that
-- eats senior analyst time."


-- ============================================================
-- SECTION 6: WAREHOUSE-SPECIFIC PERFORMANCE (know at least one)
-- ------------------------------------------------------------
-- Snowflake : clustering keys, result cache, warehouse sizing,
--             zero-copy CLONE for dev, TIME TRAVEL for recovery.
-- BigQuery  : PARTITION BY date + CLUSTER BY high-card cols;
--             billed by BYTES SCANNED => never SELECT *, prune
--             partitions in WHERE, use approx functions.
-- Databricks: Delta Lake, OPTIMIZE + ZORDER, liquid clustering,
--             photon engine, MERGE for upserts.
-- ------------------------------------------------------------
-- Example: BigQuery cost-aware DDL
-- CREATE TABLE mart.fct_orders
--   PARTITION BY order_date
--   CLUSTER BY customer_segment AS
-- SELECT ... ;   -- queries filtering order_date scan far fewer bytes


-- ============================================================
-- SECTION 7: ORCHESTRATION & CI/CD (mention this — it's staff signal)
-- ------------------------------------------------------------
-- Airflow / Dagster / dbt Cloud schedules the DAG:
--   extract (Fivetran/Airbyte) -> dbt run -> dbt test -> BI refresh
-- CI on every PR:  dbt build --select state:modified+   (only
--   changed models + downstream), so bad SQL never hits prod.
-- Freshness:  dbt source freshness  -> alert if data is stale.
-- ============================================================

-- ============================================================
-- 30-SECOND SUMMARY TO SAY IN INTERVIEWS
-- ------------------------------------------------------------
-- "I model in layers (staging->marts), enforce trust with dbt
--  tests + freshness, version everything in git with CI, and
--  expose ONE metric definition through a semantic layer. That
--  turns me from someone who answers questions into someone who
--  owns the company's trusted metrics."
-- ============================================================
