-- ============================================================
-- CHAPTER 12: BI & SEMANTIC MODELING (Looker / Tableau / Power BI)
-- Practice in: Looker (LookML), Tableau, Power BI
-- Senior DAs don't just BUILD dashboards — they design the
-- self-serve analytics LAYER the whole company trusts. That
-- governance + design skill is what 70-80 LPA roles pay for.
-- ============================================================
-- This file mixes LookML (a real language) with design principles
-- and Power BI DAX so you can speak to any BI stack in a loop.
-- ============================================================


-- ============================================================
-- SECTION 1: BI MATURITY — POSITION YOURSELF AS SENIOR
-- ------------------------------------------------------------
-- L1  Someone asks -> you pull a chart          (junior)
-- L2  You build dashboards on request           (mid)
-- L3  You design a governed semantic model +
--     self-serve so stakeholders answer their
--     own questions correctly                    (SENIOR / target)
-- L4  You set metric strategy, own the North
--     Star tree, define data contracts           (staff)
-- Interview goal: prove you operate at L3-L4.
-- ============================================================


-- ============================================================
-- SECTION 2: LookML — MODEL METRICS ONCE, GOVERN CENTRALLY
-- ------------------------------------------------------------
-- LookML separates the DATA MODEL from the chart. Define a
-- measure once; every explore/dashboard reuses it. No metric drift.
-- ============================================================

-- ------------------------------------------------------------
-- FILE: views/orders.view.lkml
-- ------------------------------------------------------------
-- view: orders {
--   sql_table_name: marts.fct_orders ;;
--
--   dimension: order_id {
--     primary_key: yes
--     type: string
--     sql: ${TABLE}.order_id ;;
--   }
--
--   dimension_group: created {
--     type: time
--     timeframes: [date, week, month, quarter, year]
--     sql: ${TABLE}.created_at ;;
--   }
--
--   dimension: customer_segment {
--     type: string
--     sql: ${TABLE}.customer_segment ;;
--   }
--
--   measure: total_revenue {
--     type: sum
--     sql: ${TABLE}.gross_amount ;;
--     value_format_name: usd
--   }
--
--   measure: order_count {
--     type: count
--   }
--
--   measure: aov {                       # composed / ratio metric
--     type: number
--     sql: 1.0 * ${total_revenue} / NULLIF(${order_count},0) ;;
--     value_format_name: usd
--   }
--
--   measure: unique_customers {
--     type: count_distinct
--     sql: ${TABLE}.customer_id ;;
--   }
-- }
-- INTERVIEW LINE: "One measure definition => the same 'revenue'
-- everywhere. That single governance decision saves a senior
-- analyst hours of 'why don't these two dashboards match?'."


-- ------------------------------------------------------------
-- FILE: models/ecommerce.model.lkml  (define the Explore = join graph)
-- ------------------------------------------------------------
-- explore: orders {
--   join: customers {
--     type: left_outer
--     sql_on: ${orders.customer_id} = ${customers.customer_id} ;;
--     relationship: many_to_one
--   }
-- }
-- 'relationship' is CRITICAL: wrong relationship => fan-out =>
-- double-counted revenue. Senior candidates call this out.


-- ============================================================
-- SECTION 3: THE FAN-OUT / DOUBLE-COUNTING TRAP (classic BI bug)
-- ------------------------------------------------------------
-- Joining orders (1) to order_items (many) then SUM(order.amount)
-- multiplies revenue by #items. Fixes:
--   - keep additive measures on their native grain view, OR
--   - use symmetric aggregates (Looker does this automatically), OR
--   - pre-aggregate in dbt to the reporting grain.
-- Being able to explain fan-out instantly = strong senior signal.
-- ============================================================


-- ============================================================
-- SECTION 4: POWER BI / DAX (know the equivalents)
-- ------------------------------------------------------------
-- Star schema in Power BI: one fact + dimensions, single-direction
-- relationships. Avoid bi-directional filters (ambiguity + perf).
--
-- -- Base measure
-- Total Revenue = SUM( fct_orders[gross_amount] )
--
-- -- Time intelligence
-- Revenue MTD = TOTALMTD( [Total Revenue], dim_date[date] )
-- Revenue YoY % =
--   VAR cur = [Total Revenue]
--   VAR ly  = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[date]))
--   RETURN DIVIDE(cur - ly, ly)
--
-- -- Context transition awareness (the #1 DAX interview topic):
-- -- CALCULATE changes filter context; a measure inside an iterator
-- -- triggers context transition. Explain row vs filter context.
-- ============================================================


-- ============================================================
-- SECTION 5: DASHBOARD DESIGN PRINCIPLES (get asked in portfolio review)
-- ------------------------------------------------------------
-- 1. Start with the DECISION, not the data. "What action does this
--    drive?" If none, cut the chart.
-- 2. Inverted pyramid: KPI headline -> trend -> breakdown -> detail.
-- 3. One primary metric per view; context (target, YoY) beside it.
-- 4. Pre-attentive attributes: position/length encode value better
--    than color/area. Avoid pie charts >3 slices, dual axes, 3D.
-- 5. Every number needs a comparison (vs target, vs last period,
--    vs segment) — a bare number is not insight.
-- 6. Performance: aggregate in the warehouse/dbt, extract/cache,
--    limit high-cardinality slicers. A slow dashboard is unused.
-- 7. Accessibility: colorblind-safe palette, labels not color-only.
-- ============================================================


-- ============================================================
-- SECTION 6: METRIC GOVERNANCE & SELF-SERVE (L4 talking points)
-- ------------------------------------------------------------
-- - Certified vs ad-hoc content: badge "official" dashboards.
-- - Metric dictionary: name, definition, owner, SQL, grain, caveats.
-- - Row-level security (RLS): a manager sees only their region.
-- - Deprecation policy: kill zombie dashboards; track usage.
-- - Data literacy: teach stakeholders to self-serve on a governed
--   model instead of queuing every question to the analyst.
-- INTERVIEW LINE: "I measure BI success by decisions enabled and
-- ticket volume REDUCED, not dashboards produced."
-- ============================================================


-- ============================================================
-- SECTION 7: PORTFOLIO-REVIEW STORY TEMPLATE (rehearse one)
-- ------------------------------------------------------------
-- "Stakeholders pinged me daily for the same cuts. I built a
--  governed Looker model with certified revenue/retention measures
--  + a self-serve explore. Ad-hoc requests dropped ~60%, and every
--  team reported the SAME numbers in the QBR for the first time."
-- Quantify: requests down X%, decision latency down from days->mins.
-- ============================================================
