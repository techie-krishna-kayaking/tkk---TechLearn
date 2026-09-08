# ETL Concepts - Extract, Transform, Load

## Executive Summary

ETL (Extract, Transform, Load) forms the backbone of data integration, moving data from source systems to analytical platforms. From a **QA perspective**, validating ETL pipelines requires understanding data extraction patterns, transformation logic, error handling, incremental processing, and orchestration workflows.

**Target Audience**: Senior QA engineers (6+ years) testing batch and real-time data pipelines across enterprise systems.

---

## Why This Matters in Enterprise

### Business Impact
- **ETL failures cost $1.7M per hour** in data downtime (Gartner)
- **70% of data project time** spent on ETL development and troubleshooting
- **Critical business processes depend on ETL**: Financial reporting, customer analytics, regulatory compliance

### Technical Imperative
- **Silent failures**: ETL jobs can succeed but load incorrect/incomplete data
- **Complex dependencies**: Upstream failures cascade to downstream systems
- **Performance at scale**: Processing billions of rows within batch windows

### Career Value
- **Foundational skillset**: ETL knowledge applies to all data platforms (cloud, on-prem, hybrid)
- **Cross-domain expertise**: Requires SQL, Python, orchestration, data modeling knowledge
- **High-impact role**: ETL defects directly affect business decisions

---

## Scope and Boundaries

### In Scope
- ETL vs. ELT paradigms
- Extraction patterns (full, incremental, CDC)
- Transformation types (data cleansing, business rules, aggregation)
- Load strategies (insert, upsert, merge, SCD)
- Error handling and data quality gates
- Orchestration and scheduling
- Performance optimization

### Out of Scope
- Platform-specific tools (Informatica, Talend, SSIS covered in stack files)
- Real-time streaming (covered in [05_Big_Data_Concepts.md](./05_Big_Data_Concepts.md))
- DWH schema design (covered in [01_DWH_Concepts_QA_Perspective.md](./01_DWH_Concepts_QA_Perspective.md))

---

## ETL vs. ELT

### ETL (Traditional)

```mermaid
graph LR
    A[Source DB] -->|Extract| B[ETL Tool]
    B -->|Transform| B
    B -->|Load| C[Data Warehouse]
    
    style B fill:#ffe1f5
Characteristics:

Transform data before loading to target
Processing happens in ETL tool (Informatica, SSIS)
Suitable for on-premise, limited DWH compute
Pros: Offload compute from DWH, data cleansed before landing
Cons: ETL tool bottleneck, expensive licensing, less flexibility

ELT (Modern Cloud)
Diagram: graph,LR


Extract

Load Raw

Transform SQL/Spark

Source DB

Data Lake

Data Warehouse

Diagram source code
Characteristics:

Load raw data then transform in target system
Processing leverages DWH/Data Lake compute (Snowflake, BigQuery, Databricks)
Suitable for cloud platforms with elastic compute
Pros: Scalable, faster initial load, raw data preserved
Cons: Requires strong DWH compute, data quality issues propagate

QA Considerations
Aspect	ETL	ELT
Test Environment	Requires ETL tool license	SQL-based, easier to replicate
Data Validation	Pre-load + post-load checks	Post-load checks critical
Performance Testing	Test ETL tool throughput	Test DWH query performance
Debugging	ETL tool logs + target data	SQL query logs + target data
Extraction Patterns
Full Extraction
Definition: Extract all data from source every run (complete refresh).

Use Cases:

Small tables (<100K rows)
Reference data (country codes, product categories)
Source system doesn't support incremental (no timestamps/flags)
QA Tests:

sql





-- Row count validation
SELECT 
    (SELECT COUNT(*) FROM source.customers) AS source_count,
    (SELECT COUNT(*) FROM stage.customers) AS stage_count,
    ABS(source_count - stage_count) AS difference;

-- Expected: difference = 0
Risks: Performance degradation as table grows, network bandwidth, source system impact.

Incremental Extraction (Timestamp-Based)
Definition: Extract only new/modified records since last run (delta).

Implementation:

sql





-- Extract records modified since last ETL run
SELECT * FROM source.orders
WHERE last_modified_date > (SELECT MAX(last_etl_timestamp) FROM stage.etl_watermark)
   OR last_modified_date IS NULL; -- Catch nulls (new records without timestamp)
QA Tests:

sql





-- Validate watermark update
SELECT table_name, last_etl_timestamp, CURRENT_TIMESTAMP
FROM stage.etl_watermark
WHERE table_name = 'orders'
  AND last_etl_timestamp < CURRENT_TIMESTAMP - INTERVAL 25 HOUR; -- Alert if not updated in 25hr

-- Validate no duplicates in incremental load
SELECT order_id, COUNT(*) AS load_count
FROM stage.orders
WHERE etl_batch_id = (SELECT MAX(etl_batch_id) FROM stage.orders)
GROUP BY order_id
HAVING COUNT(*) > 1;
Risks: Missing records if source timestamp not updated on changes, timezone issues, late-arriving data.

Change Data Capture (CDC)
Definition: Capture insert/update/delete operations from source transaction logs.

Mechanisms:

Log-based CDC: Read database transaction logs (Oracle LogMiner, SQL Server CT)
Trigger-based CDC: Database triggers write to change table
Query-based CDC: Compare snapshots to detect changes
CDC Record Example:

Code





operation | order_id | customer_id | amount | timestamp
---------|----------|-------------|--------|-------------------
INSERT   | O001     | C123        | 100.50 | 2024-09-08 10:15:00
UPDATE   | O001     | C123        | 105.00 | 2024-09-08 11:30:00
DELETE   | O001     | C123        | NULL   | 2024-09-08 14:00:00
QA Tests:

sql





-- Validate CDC operation types
SELECT operation, COUNT(*) AS count
FROM cdc.orders
WHERE cdc_timestamp >= CURRENT_DATE
GROUP BY operation;

-- Expected distribution (sanity check): INSERT > UPDATE > DELETE

-- Validate hard deletes propagated
SELECT COUNT(*) AS orphaned_records
FROM dwh.fact_orders f
LEFT JOIN source.orders s ON f.order_id = s.order_id
WHERE s.order_id IS NULL
  AND f.is_deleted = 0; -- Should be marked deleted
Risks: CDC lag (high transaction volume), log retention limits, complex delete handling.

Transformation Types
Data Cleansing
Purpose: Fix data quality issues before loading to DWH.

Examples:

sql





-- Trim whitespace
UPDATE stage.customers
SET customer_name = TRIM(customer_name);

-- Standardize phone numbers (remove formatting)
UPDATE stage.customers
SET phone = REGEXP_REPLACE(phone, '[^0-9]', ''); -- Keep only digits

-- Handle nulls in mandatory fields
UPDATE stage.orders
SET customer_id = -1 -- Default "Unknown Customer"
WHERE customer_id IS NULL;

-- Fix data type mismatches
UPDATE stage.products
SET price = TRY_CAST(price_text AS DECIMAL(10,2));
QA Tests:

sql





-- Validate cleansing applied
SELECT COUNT(*) AS uncleansed_records
FROM stage.customers
WHERE customer_name != TRIM(customer_name) -- Whitespace remains
   OR phone LIKE '%-%'; -- Phone formatting remains
Data Enrichment
Purpose: Add derived/calculated fields.

Examples:

sql





-- Add age from birthdate
UPDATE stage.customers
SET age = YEAR(CURRENT_DATE) - YEAR(birthdate);

-- Add fiscal year (company year ends in June)
UPDATE stage.orders
SET fiscal_year = CASE 
    WHEN MONTH(order_date) >= 7 THEN YEAR(order_date) + 1
    ELSE YEAR(order_date)
END;

-- Geocode addresses (call external API)
UPDATE stage.customers
SET latitude = geocode_api(address).lat,
    longitude = geocode_api(address).lng;
QA Tests:

sql





-- Validate age calculation
SELECT customer_id, birthdate, age
FROM stage.customers
WHERE age != YEAR(CURRENT_DATE) - YEAR(birthdate)
   OR age < 0 OR age > 120; -- Invalid age range
Aggregation
Purpose: Pre-calculate summary tables for performance.

Examples:

sql





-- Daily sales aggregation
INSERT INTO dwh.fact_daily_sales
SELECT 
    DATE(order_date) AS sale_date,
    product_id,
    store_id,
    SUM(quantity) AS total_quantity,
    SUM(amount) AS total_amount,
    COUNT(*) AS transaction_count
FROM stage.orders
GROUP BY DATE(order_date), product_id, store_id;
QA Tests:

sql





-- Validate aggregation accuracy (compare to source)
WITH source_agg AS (
    SELECT DATE(order_date) AS sale_date, SUM(amount) AS source_total
    FROM source.orders
    WHERE DATE(order_date) = '2024-09-08'
    GROUP BY DATE(order_date)
),
dwh_agg AS (
    SELECT sale_date, total_amount AS dwh_total
    FROM dwh.fact_daily_sales
    WHERE sale_date = '2024-09-08'
)
SELECT s.sale_date, s.source_total, d.dwh_total,
       ABS(s.source_total - d.dwh_total) AS difference
FROM source_agg s
JOIN dwh_agg d ON s.sale_date = d.sale_date
WHERE ABS(s.source_total - d.dwh_total) > 0.01; -- Allow rounding
Business Rule Implementation
Purpose: Apply domain-specific logic.

Examples:

sql





-- Discount calculation
UPDATE stage.orders
SET discount_amount = CASE
    WHEN customer_type = 'PREMIUM' AND order_amount > 1000 THEN order_amount * 0.15
    WHEN customer_type = 'PREMIUM' THEN order_amount * 0.10
    WHEN order_amount > 1000 THEN order_amount * 0.05
    ELSE 0
END;

-- Sales territory assignment
UPDATE stage.customers
SET sales_territory = CASE
    WHEN state IN ('CA', 'OR', 'WA') THEN 'West'
    WHEN state IN ('NY', 'NJ', 'CT') THEN 'East'
    WHEN state IN ('TX', 'AZ', 'NM') THEN 'South'
    ELSE 'Midwest'
END;
QA Tests:

sql





-- Validate business rule with decision table
SELECT 
    customer_type,
    CASE WHEN order_amount > 1000 THEN '>1000' ELSE '<=1000' END AS amount_bracket,
    COUNT(*) AS record_count,
    AVG(discount_amount / order_amount) AS avg_discount_pct
FROM stage.orders
GROUP BY customer_type, 
         CASE WHEN order_amount > 1000 THEN '>1000' ELSE '<=1000' END;

-- Expected discount percentages:
-- PREMIUM, >1000  : 15%
-- PREMIUM, <=1000 : 10%
-- REGULAR, >1000  : 5%
-- REGULAR, <=1000 : 0%
Load Strategies
Insert-Only (Append)
Use Case: Transactional facts (immutable history).

sql





INSERT INTO dwh.fact_sales
SELECT 
    order_id,
    customer_key,
    product_key,
    order_date,
    amount
FROM stage.orders
WHERE etl_batch_id = :current_batch;
QA Tests:

sql





-- Validate no duplicates
SELECT order_id, COUNT(*) AS duplicate_count
FROM dwh.fact_sales
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Validate batch loaded completely
SELECT 
    (SELECT COUNT(*) FROM stage.orders WHERE etl_batch_id = 123) AS stage_count,
    (SELECT COUNT(*) FROM dwh.fact_sales WHERE etl_batch_id = 123) AS dwh_count;
Upsert (Insert or Update)
Use Case: Dimension tables (latest state).

sql





MERGE INTO dwh.dim_customer AS target
USING stage.customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET 
        customer_name = source.customer_name,
        email = source.email,
        updated_date = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (customer_id, customer_name, email, created_date)
    VALUES (source.customer_id, source.customer_name, source.email, CURRENT_TIMESTAMP);
QA Tests:

sql





-- Validate merge statistics
SELECT 
    (SELECT COUNT(*) FROM stage.customers) AS source_count,
    @@ROWCOUNT AS rows_affected, -- SQL Server syntax (use equivalent for other DBs)
    (SELECT COUNT(*) FROM dwh.dim_customer) AS target_count;

-- Validate updates applied
SELECT s.customer_id, s.email AS source_email, d.email AS dwh_email
FROM stage.customers s
JOIN dwh.dim_customer d ON s.customer_id = d.customer_id
WHERE s.email != d.email; -- Should be 0 mismatches
Slowly Changing Dimension (SCD Type 2)
Use Case: Historical tracking (customer address changes, product price changes).

sql





-- End-date existing record
UPDATE dwh.dim_product
SET valid_to = CURRENT_DATE - 1,
    is_current = 0
WHERE product_id IN (SELECT product_id FROM stage.products_changed)
  AND is_current = 1;

-- Insert new version
INSERT INTO dwh.dim_product (product_id, product_name, price, valid_from, valid_to, is_current)
SELECT 
    product_id,
    product_name,
    price,
    CURRENT_DATE AS valid_from,
    '9999-12-31' AS valid_to,
    1 AS is_current
FROM stage.products_changed;
QA Tests (see 01_DWH_Concepts_QA_Perspective.md for comprehensive SCD testing).

Truncate-and-Load
Use Case: Small reference tables, full refresh required.

sql





TRUNCATE TABLE dwh.dim_country; -- Delete all rows

INSERT INTO dwh.dim_country
SELECT * FROM stage.countries;
QA Tests:

sql





-- Validate table reloaded
SELECT COUNT(*) AS row_count FROM dwh.dim_country;
-- Expected: Match source count

-- Validate no gaps (check for expected reference data)
SELECT country_code FROM dwh.dim_country
WHERE country_code IN ('US', 'UK', 'CA', 'AU'); -- Critical countries
-- Expected: 4 rows returned
Error Handling and Data Quality Gates
Error Handling Strategies
Diagram: graph,TD


Pass

Fail

Yes

No

Pass

Fail

Extract Data

Data Quality Check

Transform

Quarantine Table

Alert Data Team

Transform Success?

Load to DWH

Log Error & Rollback

Post-Load Validation

Commit

Diagram source code
Quarantine Pattern
Purpose: Isolate bad records without failing entire batch.

sql





-- Separate good and bad records
INSERT INTO stage.orders_valid
SELECT * FROM stage.orders_raw
WHERE order_amount > 0 
  AND customer_id IS NOT NULL
  AND order_date <= CURRENT_DATE;

INSERT INTO stage.orders_quarantine
SELECT *, CURRENT_TIMESTAMP AS quarantine_date, 'Invalid amount or customer' AS reason
FROM stage.orders_raw
WHERE order_amount <= 0 
   OR customer_id IS NULL
   OR order_date > CURRENT_DATE;

-- Process only valid records
INSERT INTO dwh.fact_orders
SELECT * FROM stage.orders_valid;
QA Tests:

sql





-- Validate quarantine criteria
SELECT reason, COUNT(*) AS quarantine_count
FROM stage.orders_quarantine
WHERE quarantine_date >= CURRENT_DATE
GROUP BY reason;

-- Alert if quarantine rate exceeds threshold (e.g., 5%)
SELECT 
    (SELECT COUNT(*) FROM stage.orders_quarantine WHERE quarantine_date >= CURRENT_DATE) AS quarantined,
    (SELECT COUNT(*) FROM stage.orders_raw WHERE load_date >= CURRENT_DATE) AS total,
    100.0 * quarantined / total AS quarantine_pct
HAVING quarantine_pct > 5.0; -- Alert
Checkpoint/Restart Logic
Purpose: Resume ETL from last successful point after failure.

sql





-- Save checkpoint
INSERT INTO stage.etl_checkpoint (table_name, batch_id, last_processed_id, checkpoint_time)
VALUES ('orders', :batch_id, :last_order_id, CURRENT_TIMESTAMP);

-- Resume from checkpoint
SELECT * FROM source.orders
WHERE order_id > (SELECT last_processed_id FROM stage.etl_checkpoint 
                  WHERE table_name = 'orders' ORDER BY checkpoint_time DESC LIMIT 1);
Orchestration and Scheduling
Orchestration Tools
Tool	Use Case	Strengths
Apache Airflow	Complex workflows, Python-based	Open-source, extensible, UI monitoring
Azure Data Factory	Cloud ETL, Azure-native	Serverless, visual designer, integrated
AWS Glue	AWS data lake, Spark-based	Serverless, auto-scaling, data catalog
dbt	SQL transformations (ELT)	Version control, testing, documentation
Prefect/Dagster	Modern data orchestration	Dynamic pipelines, observability
Dependency Management
Diagram: graph,TD


Extract Customers

Extract Orders

Transform Orders

Load Dim Customer

Load Fact Orders

Aggregate Daily Sales

Diagram source code
QA Tests:

python





# Airflow DAG validation (example)
from airflow.models import DagBag

def test_dag_dependencies():
    dagbag = DagBag()
    dag = dagbag.get_dag('sales_etl_dag')
    
    # Test task exists
    assert 'extract_customers' in dag.task_ids
    assert 'load_fact_orders' in dag.task_ids
    
    # Test dependency
    load_task = dag.get_task('load_fact_orders')
    upstream_ids = [t.task_id for t in load_task.upstream_list]
    
    assert 'transform_orders' in upstream_ids
    assert 'load_dim_customer' in upstream_ids
Scheduling Patterns
Time-Based (Cron):

Code





0 2 * * *   # Daily at 2 AM
0 */4 * * * # Every 4 hours
0 0 * * 0   # Weekly on Sunday midnight
Event-Based (Trigger):

File arrival in S3/ADLS
Database record insert
Upstream job completion
QA Tests:

sql





-- Validate ETL ran on schedule
SELECT 
    etl_date,
    start_time,
    end_time,
    TIMESTAMPDIFF(MINUTE, start_time, end_time) AS duration_minutes
FROM stage.etl_log
WHERE etl_date >= CURRENT_DATE - 7
  AND HOUR(start_time) != 2; -- Expected start hour = 2 AM

-- Should return 0 rows if schedule maintained
Performance Optimization
Parallel Processing
Strategy: Split large tables into chunks, process concurrently.

python





# Parallel extraction (Python example)
from concurrent.futures import ThreadPoolExecutor

def extract_chunk(start_id, end_id):
    query = f"SELECT * FROM orders WHERE order_id BETWEEN {start_id} AND {end_id}"
    # Execute query, write to stage
    
# Split 1M orders into 10 chunks
chunk_size = 100000
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(extract_chunk, i, i+chunk_size-1) 
               for i in range(1, 1000001, chunk_size)]
QA Tests:

sql





-- Validate no records missed in parallel processing
WITH expected AS (
    SELECT generate_series(1, 1000000) AS order_id -- PostgreSQL syntax
),
actual AS (
    SELECT order_id FROM stage.orders
)
SELECT e.order_id AS missing_order_id
FROM expected e
LEFT JOIN actual a ON e.order_id = a.order_id
WHERE a.order_id IS NULL;
Incremental Load Optimization
Strategy: Only process changed data.

sql





-- Before optimization (full scan every run)
DELETE FROM dwh.dim_customer;
INSERT INTO dwh.dim_customer SELECT * FROM source.customers; -- 10M rows, 5 min

-- After optimization (incremental)
MERGE INTO dwh.dim_customer AS target
USING (SELECT * FROM source.customers WHERE last_modified > :last_run_time) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
-- 10K changed rows, 10 sec
Indexing Strategy
sql





-- Add indexes on join/filter columns
CREATE INDEX idx_orders_customer ON stage.orders(customer_id);
CREATE INDEX idx_orders_date ON stage.orders(order_date);

-- Drop indexes before bulk load, recreate after
DROP INDEX idx_orders_customer;
-- Bulk insert
CREATE INDEX idx_orders_customer ON stage.orders(customer_id);
Interview Questions
Basic (0-3 years)
Q1: What's the difference between ETL and ELT?
A1: ETL transforms data before loading (traditional). ELT loads raw data then transforms in target system (modern cloud). ELT leverages DWH compute, faster initial load.

Q2: What is incremental extraction?
A2: Extract only new/changed records since last run (delta), typically using timestamp or CDC. More efficient than full extraction for large tables.

Advanced (4-8 years)
Q3: How do you handle late-arriving dimension records?
A3: (1) Default dimension row (customer_key=-1 'Unknown'), (2) Late-binding (fact stores natural key, resolve to surrogate key in view), (3) Re-process facts when dimension arrives, (4) Alert data steward for manual resolution.

Q4: Explain the quarantine pattern in ETL.
A4: Separate bad records into quarantine table instead of failing entire batch. Allows good data to proceed, bad data reviewed/fixed offline. Prevents blocking business-critical loads.

Scenario (8-12 years)
Q5: ETL job completes successfully but row count is 10% lower than source. Troubleshoot?
A5: (1) Check extraction filter (WHERE clause too restrictive), (2) Review quarantine table (records rejected), (3) Validate timestamp watermark (old watermark skips new data), (4) Check for duplicates (de-duplication logic too aggressive), (5) Review ETL logs (partial commit), (6) Compare source count at extraction time vs. current (source data deleted after extraction).

Architect (12+ years)
Q6: Design ETL architecture for 500 source systems loading to enterprise DWH (100TB)?
A6: (1) Landing zone: Raw extracts (Parquet on S3/ADLS), no transformation, (2) Staging: Light cleansing, schema standardization, (3) Core DWH: Dimensional model, SCD Type 2, (4) Orchestration: Airflow with DAG per domain, (5) Metadata-driven: Config tables define source-to-target mappings, (6) Error handling: Quarantine + alert + manual review queue, (7) Monitoring: Freshness, volume anomalies, data quality scores, (8) Performance: Parallel processing, incremental loads, partitioning by date, (9) Governance: Data lineage, audit logging, compliance controls.

Frequently Asked Questions
Q1: How to test ETL performance?
A1: (1) Baseline: Measure time/throughput on known data volume, (2) Load test: Scale to expected peak (2x-5x normal volume), (3) Identify bottlenecks (CPU, I/O, network), (4) Optimize (parallel processing, indexing, partitioning), (5) Re-test and validate SLA met.

Q2: How often should ETL jobs run?
A2: Depends on business need: Real-time (streaming), Micro-batch (5-15 min), Hourly, Daily (most common for batch DWH), Weekly/Monthly (aggregates, compliance reports). Balance freshness vs. system load.

Q3: What's the role of a staging area?
A3: Temporary storage between source and DWH. Benefits: (1) Isolate source system (minimize impact), (2) Restartability (checkpoint), (3) Data quality validation (quarantine), (4) Parallel loading (multiple sources), (5) Audit trail (source snapshot).

Q4: How to handle schema changes in source systems?
A4: (1) Schema versioning: Track DDL changes in metadata repo, (2) Backward compatibility: Test ETL with old+new schema, (3) Automated schema diff: Alert on breaking changes, (4) Late-binding: Use position-independent column mapping (by name, not ordinal), (5) Communication: Source team notifies consumers before changes.

Q5: Difference between hard delete and soft delete in ETL?
A5: Hard delete: Physically remove record (DELETE FROM table). Soft delete: Mark as deleted (UPDATE table SET is_deleted=1). Soft delete preferred for audit trail, SCD Type 2, bi-temporal modeling.

Q6: How to validate data lineage in ETL?
A6: (1) Trace single record source → staging → DWH → BI, (2) Validate transformation applied correctly at each stage, (3) Check audit columns (insert_date, source_system_id), (4) Use lineage tools (Collibra, Atlan) to visualize flow.

Q7: What's idempotency in ETL and why does it matter?
A7: Idempotent ETL produces same result when run multiple times on same input data. Critical for restartability (re-run failed jobs without duplicating data). Achieved via: MERGE vs. INSERT, TRUNCATE+INSERT, surrogate key generation with deterministic logic.

Q8: How to test slowly changing dimensions (SCD Type 2) in ETL?
A8: See comprehensive SCD testing in 01_DWH_Concepts_QA_Perspective.md. Key tests: temporal validity, current flag accuracy, historical integrity, end-dating logic.

Q9: Best practices for ETL error logging?
A9: (1) Structured logs: JSON format with severity, timestamp, job_id, table_name, error_code, (2) Levels: DEBUG, INFO, WARN, ERROR, FATAL, (3) Context: Capture query, row data (sample), stack trace, (4) Centralized: Send to log aggregator (Splunk, ELK), (5) Alerting: P1 errors page on-call engineer.

Q10: How to handle timezone differences in global ETL?
A10: (1) Standardize: Store all timestamps in UTC, (2) Convert: Apply timezone offset at query time (not in ETL), (3) Metadata: Store original timezone in separate column, (4) Testing: Validate DST transitions (spring forward, fall back), (5) Date dimension: Include both UTC and local date keys.

Q11: What's the difference between batch and streaming ETL?
A11: Batch: Process data in scheduled intervals (hourly, daily). Streaming: Process data in real-time (sub-second latency). Batch = simpler, cheaper, sufficient for most analytics. Streaming = complex, expensive, required for real-time dashboards/alerting.

Q12: How to optimize ETL for large tables (1B+ rows)?
A12: (1) Partitioning: Process by date/region chunks, (2) Parallelism: Split into parallel threads, (3) Incremental: Only process changed data (CDC), (4) Columnar storage: Parquet/ORC for compression, (5) Indexing: Create on join/filter columns, drop before bulk insert, (6) Denormalization: Pre-join dimensions to reduce runtime joins.

Q13: How to test ETL rollback/recovery?
A13: (1) Simulate failure: Kill job mid-run, (2) Verify rollback: Check no partial data committed, (3) Restart: Validate job resumes from checkpoint, (4) Data integrity: Confirm no duplicates, no data loss, (5) Idempotency: Re-run completed job, confirm no double-loading.

Q14: What's the role of data profiling in ETL testing?
A14: Profiling = analyze source data characteristics (null%, distinct values, min/max, distributions). Use in ETL: (1) Validate cleansing rules applied, (2) Detect anomalies (outliers, volume spikes), (3) Baseline for monitoring (compare daily to historical), (4) Test data generation (mimic prod distributions).

Q15: How to handle parent-child load order?
A15: Load parent (dimension) before child (fact) to maintain referential integrity. Use orchestration tool (Airflow) to enforce dependencies. If parent load fails, skip child load (avoid orphaned facts).

Q16: Difference between staging and landing zones?
A16: Landing: Raw source data, no transformation (exact copy). Staging: Light transformation (cleansing, schema standardization), prep for DWH load. Landing = replayable source of truth, Staging = work area.

Q17: How to test CDC-based ETL?
A17: (1) INSERT test: Create new source record, verify appears in target, (2) UPDATE test: Modify source, verify change propagates (SCD logic), (3) DELETE test: Delete source, verify soft/hard delete in target, (4) Lag test: Measure time from source commit to target availability, (5) Out-of-order test: Simulate late CDC records, validate handling.

Q18: What's the 80/20 rule in ETL optimization?
A18: 80% of ETL runtime spent on 20% of tables. Focus optimization efforts on those bottleneck tables (largest, most complex transformations). Use profiling to identify them.

Q19: How to validate ETL transformation logic without test data?
A19: (1) Review code: SQL/Python code review against business requirements, (2) Reverse engineer: Sample prod data, trace backwards through transformations, (3) Ask: Consult business analyst for expected behavior, (4) Generate synthetic: Create deterministic test data matching prod patterns.

Q20: Best practices for ETL versioning/deployment?
A20: (1) Git: Version control all ETL code (SQL, Python, YAML), (2) CI/CD: Automated testing on commit, deploy to dev→test→prod, (3) Blue-green: Deploy new version alongside old, switch traffic after validation, (4) Rollback plan: Maintain previous version for quick revert, (5) Schema migration: Automated DDL scripts with rollback.

Actionable Checklists
ETL Testing Checklist
 Row count reconciliation (source vs. target)
 Column-level data validation (checksums, sampling)
 Null handling verified (mandatory fields populated)
 Data type conversions correct (no truncation/overflow)
 Business rule transformations validated (decision tables)
 Referential integrity (no orphaned facts)
 SCD logic tested (Type 1/2/3 as applicable)
 Incremental load tested (delta correctly identified)
 Error handling verified (quarantine, alerts)
 Performance SLA met (batch window, throughput)
 Idempotency validated (re-run produces same result)
 Rollback/recovery tested
ETL Performance Testing Checklist
 Baseline metrics captured (time, throughput, resource utilization)
 Load testing at 2x expected volume
 Stress testing at 5x expected volume
 Bottleneck analysis (CPU, I/O, network, DB locks)
 Index effectiveness validated (query execution plans)
 Parallel processing tested (no data loss/duplication)
 Incremental vs. full load performance compared
 Batch window SLA validated
ETL Production Readiness Checklist
 Orchestration dependencies configured
 Error alerting enabled (email/Slack/PagerDuty)
 Monitoring dashboards created (freshness, volume, quality)
 Runbook documented (troubleshooting, recovery steps)
 Access controls configured (least privilege)
 Audit logging enabled (compliance)
 Backup/recovery tested
 On-call rotation assigned
References
Books
The Data Warehouse ETL Toolkit (Kimball, Caserta): Comprehensive ETL patterns
Data Pipelines Pocket Reference (Densmore): Modern data engineering practices
Fundamentals of Data Engineering (Reis, Housley): End-to-end data architecture
Standards
ANSI/ISO SQL: Standard SQL syntax for transformations
DAMA-DMBOK: Data integration chapter (ETL best practices)
Tools Documentation
Apache Airflow: https://airflow.apache.org
dbt: https://docs.getdbt.com
AWS Glue: https://docs.aws.amazon.com/glue
Azure Data Factory: https://docs.microsoft.com/azure/data-factory
Core References: Platform-agnostic ETL concepts
Stack Deltas: See Azure/AWS/GCP stack files for platform-specific ETL tools

Previous: 03_Data_Testing_Concepts.md
Next: 05_Big_Data_Concepts.md
Up: Master Index
