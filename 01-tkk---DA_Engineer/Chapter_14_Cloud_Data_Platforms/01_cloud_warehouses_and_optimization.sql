-- ============================================================
-- CHAPTER 14: CLOUD DATA PLATFORMS & WAREHOUSE INTERNALS
-- Practice in: BigQuery / Snowflake / Redshift / Databricks
-- Senior DAs are expected to write COST-AWARE, PERFORMANT SQL on
-- cloud warehouses and reason about internals. "It ran" is junior;
-- "it ran, scanning 2 GB not 2 TB, for $0.01" is senior.
-- ============================================================


-- ============================================================
-- SECTION 1: MPP MENTAL MODEL (say this to sound senior)
-- ------------------------------------------------------------
-- Cloud warehouses are Massively Parallel Processing (MPP):
--   - Storage is columnar + compressed (scan only needed columns).
--   - Compute is distributed across nodes/slots; data is
--     partitioned/distributed so nodes work in parallel.
--   - The killers of performance are: SCANNING too much data and
--     SHUFFLING/redistributing data across nodes (joins, GROUP BY).
-- Every optimization below reduces SCAN or SHUFFLE. That's it.
-- ============================================================


-- ============================================================
-- SECTION 2: PARTITIONING & CLUSTERING (prune the scan)
-- ------------------------------------------------------------
-- Partition on the column you FILTER by (usually a date).
-- Cluster/sort on high-cardinality columns you filter/join by.
-- ============================================================

-- BigQuery: billed by BYTES SCANNED — partition + cluster is $$$.
-- CREATE TABLE mart.fct_events
--   PARTITION BY DATE(event_ts)
--   CLUSTER BY user_id, event_name AS
-- SELECT ... ;
-- Good (prunes partitions): scans ONE day, not the whole table
SELECT COUNT(*)
FROM mart.fct_events
WHERE DATE(event_ts) = '2024-06-01'      -- partition filter
  AND event_name = 'checkout';           -- cluster filter
-- Bad: WHERE CAST(event_ts AS STRING) LIKE '2024-06-01%'  -- no pruning!

-- Snowflake: micro-partitions are automatic; add a CLUSTER KEY only
-- on very large tables with a dominant filter column.
-- ALTER TABLE fct_events CLUSTER BY (event_date);

-- Redshift: choose DISTKEY (join key -> co-locates rows, avoids
-- shuffle) and SORTKEY (range-filter column -> zone-map pruning).
-- CREATE TABLE fct_events (...)
--   DISTKEY(user_id) SORTKEY(event_date);

-- Databricks/Delta: OPTIMIZE + ZORDER (or liquid clustering).
-- OPTIMIZE fct_events ZORDER BY (user_id, event_date);


-- ============================================================
-- SECTION 3: COST-AWARE SQL HABITS (BigQuery-style, applies broadly)
-- ------------------------------------------------------------
-- 1. NEVER SELECT * on wide tables — name the columns you need
--    (columnar storage means unused columns cost nothing to skip).
-- 2. Filter the PARTITION column with a literal/deterministic expr.
-- 3. Aggregate/approx early:  APPROX_COUNT_DISTINCT() for big cardinalities.
-- 4. Materialize repeated heavy CTEs into a table; don't recompute.
-- 5. Preview with LIMIT does NOT reduce bytes scanned in BQ — use a
--    partition filter or TABLESAMPLE instead.
-- ------------------------------------------------------------
-- Approx distinct: 100x cheaper on billions of rows, ~2% error
SELECT
    event_date,
    APPROX_COUNT_DISTINCT(user_id) AS approx_dau
FROM mart.fct_events
WHERE event_date BETWEEN '2024-06-01' AND '2024-06-30'
GROUP BY event_date;


-- ============================================================
-- SECTION 4: JOIN STRATEGY (minimize shuffle)
-- ------------------------------------------------------------
-- Broadcast join: small table copied to every node — no shuffle of
--   the big table. Ideal when one side is small (< ~10-100 MB).
-- Shuffle/hash join: both sides repartitioned on the join key —
--   expensive; reduce rows/columns BEFORE the join.
-- ------------------------------------------------------------
-- Databricks hint:
-- SELECT /*+ BROADCAST(d) */ f.*, d.segment
-- FROM fct_events f JOIN dim_users d USING (user_id);
-- Senior habit: filter + project each side to the minimum, THEN join.


-- ============================================================
-- SECTION 5: PLATFORM CHEAT-SHEET (be conversant in all three)
-- ------------------------------------------------------------
-- BigQuery (GCP)
--   * Serverless, pay per BYTES SCANNED (on-demand) or slots.
--   * Partition + cluster + no SELECT *; check "bytes processed"
--     estimate before running. Nested/repeated (ARRAY/STRUCT) data.
-- Snowflake
--   * Separated storage/compute; virtual WAREHOUSES you size (XS..4XL)
--     and auto-suspend to save cost. Result cache, zero-copy CLONE,
--     TIME TRAVEL (undrop / query history), Streams+Tasks for CDC.
-- Redshift (AWS)
--   * Provisioned or serverless; DISTKEY/SORTKEY tuning matters,
--     VACUUM/ANALYZE housekeeping, Spectrum to query S3 (lake).
-- Databricks (Lakehouse)
--   * Delta Lake (ACID on files), Photon engine, Unity Catalog
--     governance, OPTIMIZE/ZORDER, MERGE upserts, medallion
--     (bronze/silver/gold) architecture.
-- Azure Synapse / Fabric
--   * Dedicated SQL pools (distributions/replicated tables) +
--     serverless over ADLS; similar distribution concepts to Redshift.


-- ============================================================
-- SECTION 6: LAKEHOUSE & FILE FORMATS (senior vocabulary)
-- ------------------------------------------------------------
-- Parquet/ORC : columnar, compressed, predicate pushdown.
-- Delta/Iceberg/Hudi : ACID transactions, schema evolution, time
--   travel, and MERGE on top of a data lake (S3/GCS/ADLS).
-- Medallion architecture: bronze (raw) -> silver (cleaned/conformed)
--   -> gold (business marts). Maps cleanly to dbt staging->marts.
-- INTERVIEW LINE: "A lakehouse gives warehouse-grade ACID + BI on
-- cheap object storage, so I get one governed copy for BI and ML."


-- ============================================================
-- SECTION 7: DEBUGGING A SLOW/EXPENSIVE QUERY (walk this live)
-- ------------------------------------------------------------
-- 1. Read the QUERY PLAN / EXPLAIN — find the biggest scan & the
--    shuffle/exchange steps.
-- 2. Is a partition filter being applied? (partition pruning)
-- 3. Data SKEW? one key/value dominates a partition -> salt the key.
-- 4. Spilling to disk? -> reduce columns, pre-aggregate, size up warehouse.
-- 5. Is a big join broadcastable? -> hint or pre-filter small side.
-- 6. Repeated subquery? -> materialize once.
-- Report the WIN in numbers: "scan 1.8 TB -> 40 GB, 9 min -> 25 s."


-- ============================================================
-- 30-SECOND SUMMARY FOR INTERVIEWS
-- ------------------------------------------------------------
-- "On cloud warehouses I optimize for two things: scan less
--  (partition + cluster + column pruning + approx) and shuffle
--  less (broadcast small joins, filter before joining, avoid skew).
--  I quantify wins in bytes scanned and dollars, not just seconds."
-- ============================================================
