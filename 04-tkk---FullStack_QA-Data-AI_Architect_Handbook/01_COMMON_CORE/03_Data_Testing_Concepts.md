# Data Testing Concepts

## Executive Summary

Data testing goes beyond traditional software testing—it validates **data correctness, completeness, consistency, and fitness for purpose** across the data lifecycle. This document covers data validation techniques, data quality dimensions, reconciliation patterns, and data observability practices.

**Target Audience**: QA engineers (5+ years) specializing in data pipelines, analytics platforms, and data-driven applications.

---

## Why This Matters in Enterprise

### Business Impact
- **Poor data quality costs organizations $12.9M annually** (Gartner)
- **33% of business leaders don't trust their data** (KPMG 2025)
- **Data-driven decisions**: 87% of organizations consider data critical to strategy

### Technical Imperative
- **Data pipelines fail silently**: Schema changes, missing data often undetected
- **Cascading failures**: Bad data in upstream systems propagates downstream
- **Compliance risks**: GDPR, HIPAA violations due to data quality issues

### Career Value
- **Specialized skillset**: Data testing requires SQL, Python, data profiling expertise
- **High demand**: 68% of organizations lack data quality expertise (DataKitchen)
- **Cross-functional**: Bridges data engineering, analytics, and business domains

---

## Scope and Boundaries

### In Scope
- Data quality dimensions (accuracy, completeness, consistency, validity, timeliness, uniqueness)
- Data validation techniques (schema, format, range, referential integrity)
- Data reconciliation patterns (row count, checksum, data profiling)
- Data observability and monitoring
- Test data generation strategies

### Out of Scope
- ETL logic testing (covered in [04_ETL_Concepts.md](./04_ETL_Concepts.md))
- Big data platform specifics (covered in [05_Big_Data_Concepts.md](./05_Big_Data_Concepts.md))
- ML data validation (covered in [07_ML_Concepts_QA_Perspective.md](./07_ML_Concepts_QA_Perspective.md))

---

## Data Quality Dimensions

### 1. Accuracy
**Definition**: Data correctly represents real-world values.

**Example**: Customer email = `john@example.com` (correct) vs. `john@exmple.com` (typo)

**Tests**:
    ```sql
    -- Validate email format
    SELECT email FROM customers
    WHERE email NOT LIKE '%@%.%'
      OR email LIKE '%@%@%'; -- Catches double @
    
    -- Cross-reference with source system
    SELECT COUNT(*) AS mismatches
    FROM dwh.customers d
    LEFT JOIN source.customers s ON d.customer_id = s.customer_id
    WHERE d.email != s.email;
    ```

### 2. Completeness
**Definition**: All expected data is present.

**Example**: Customer table should have 1M records, but only 950K loaded (5% missing)

**Tests**:
    ```sql
    -- Row count comparison
    SELECT 
        (SELECT COUNT(*) FROM source.customers) AS source_count,
        (SELECT COUNT(*) FROM dwh.customers) AS dwh_count,
        ABS((SELECT COUNT(*) FROM source.customers) - 
            (SELECT COUNT(*) FROM dwh.customers)) AS difference;
    
    -- Null checks on mandatory fields
    SELECT 
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(email) AS email_nulls,
        COUNT(*) - COUNT(phone) AS phone_nulls
    FROM dwh.customers;
    ```

### 3. Consistency
**Definition**: Data is uniform across systems and datasets.

**Example**: Customer `C123` has birthdate `1990-01-15` in CRM but `1990-01-16` in DWH

**Tests**:
    ```sql
    -- Cross-system consistency
    SELECT c1.customer_id, c1.birthdate AS crm_birthdate, c2.birthdate AS dwh_birthdate
    FROM crm.customers c1
    JOIN dwh.customers c2 ON c1.customer_id = c2.customer_id
    WHERE c1.birthdate != c2.birthdate;
    
    -- Aggregate consistency (monthly totals should match daily sum)
    SELECT month, SUM(daily_sales) AS sum_of_daily, monthly_total
    FROM (
        SELECT DATE_TRUNC('month', sale_date) AS month,
               SUM(amount) AS daily_sales
        FROM fact_sales
        GROUP BY DATE_TRUNC('month', sale_date)
    ) daily
    JOIN fact_monthly_sales monthly ON daily.month = monthly.month
    WHERE ABS(daily_sales - monthly_total) > 0.01; -- Allow for rounding
    ```

### 4. Validity
**Definition**: Data conforms to business rules and constraints.

**Example**: Age must be 0-120, order_date must be <= today

**Tests**:
    ```sql
    -- Range validation
    SELECT customer_id, age FROM customers
    WHERE age < 0 OR age > 120;
    
    -- Business rule validation
    SELECT order_id, order_date, ship_date
    FROM orders
    WHERE ship_date < order_date; -- Ship date should be >= order date
    
    -- Enum validation
    SELECT product_id, category FROM products
    WHERE category NOT IN ('Electronics', 'Clothing', 'Food', 'Books');
    ```

### 5. Timeliness
**Definition**: Data is available when needed.

**Example**: Daily sales report must be ready by 7 AM; data loaded at 9 AM = SLA breach

**Tests**:
    ```sql
    -- Data freshness check
    SELECT 
        MAX(last_updated) AS latest_data_timestamp,
        CURRENT_TIMESTAMP AS current_time,
        TIMESTAMPDIFF(HOUR, MAX(last_updated), CURRENT_TIMESTAMP) AS hours_stale
    FROM fact_sales
    HAVING hours_stale > 2; -- Alert if data is >2 hours old
    ```

### 6. Uniqueness
**Definition**: No duplicate records (unless intentional, like SCD Type 2).

**Example**: Customer table should have one row per customer_id (PK)

**Tests**:
    ```sql
    -- Duplicate detection
    SELECT customer_id, COUNT(*) AS duplicate_count
    FROM customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1;
    
    -- Composite key uniqueness
    SELECT order_id, line_number, COUNT(*) AS duplicate_count
    FROM order_lines
    GROUP BY order_id, line_number
    HAVING COUNT(*) > 1;
    ```

---

## Data Validation Techniques

### Schema Validation

**Purpose**: Ensure data structure matches expected schema (columns, data types, constraints).

**Tests**:
    ```sql
    -- Column existence check
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'customers'
      AND column_name IN ('customer_id', 'email', 'birthdate')
    ORDER BY column_name;
    
    -- Expected: 3 rows returned
    -- Actual: If < 3, columns are missing
    
    -- Data type validation
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'orders'
      AND column_name = 'order_date'
      AND data_type != 'DATE';
    -- Returns rows if data type is wrong
    ```

**Automated Schema Diff**:
    ```python
    # Compare schema between environments
    import pandas as pd
    
    def schema_diff(db1_schema, db2_schema):
        df1 = pd.DataFrame(db1_schema)  # [(col_name, data_type), ...]
        df2 = pd.DataFrame(db2_schema)
        
        # Columns in db1 not in db2
        missing_in_db2 = df1[~df1['column_name'].isin(df2['column_name'])]
        
        # Columns in db2 not in db1
        extra_in_db2 = df2[~df2['column_name'].isin(df1['column_name'])]
        
        # Data type mismatches
        merged = df1.merge(df2, on='column_name', suffixes=('_db1', '_db2'))
        type_mismatches = merged[merged['data_type_db1'] != merged['data_type_db2']]
        
        return {
            'missing': missing_in_db2,
            'extra': extra_in_db2,
            'type_mismatches': type_mismatches
        }
    ```

### Referential Integrity Validation

**Purpose**: Ensure foreign key relationships are valid (no orphaned records).

**Tests**:
    ```sql
    -- Orphaned facts (FK not in dimension)
    SELECT COUNT(*) AS orphaned_orders
    FROM fact_sales f
    LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
    WHERE c.customer_key IS NULL;
    
    -- Expected: 0 orphaned records
    
    -- Circular references (parent-child hierarchy)
    WITH RECURSIVE manager_hierarchy AS (
        SELECT employee_id, manager_id, 1 AS level
        FROM employees
        WHERE manager_id IS NOT NULL
        
        UNION ALL
        
        SELECT e.employee_id, e.manager_id, h.level + 1
        FROM employees e
        JOIN manager_hierarchy h ON e.manager_id = h.employee_id
        WHERE h.level < 100 -- Prevent infinite loop
    )
    SELECT * FROM manager_hierarchy
    WHERE level = 100; -- Circular reference detected if any rows returned
    ```

### Data Profiling

**Purpose**: Analyze data characteristics (distributions, patterns, anomalies).

**Key Metrics**:
    ```sql
    -- Column profiling
    SELECT 
        'customer_age' AS column_name,
        COUNT(*) AS total_rows,
        COUNT(age) AS non_null_count,
        COUNT(*) - COUNT(age) AS null_count,
        ROUND(100.0 * (COUNT(*) - COUNT(age)) / COUNT(*), 2) AS null_percentage,
        MIN(age) AS min_value,
        MAX(age) AS max_value,
        AVG(age) AS avg_value,
        STDDEV(age) AS std_deviation,
        COUNT(DISTINCT age) AS distinct_values
    FROM customers;
    
    -- Output example:
    -- column_name   | total_rows | non_null | null_count | null_% | min | max | avg  | stddev | distinct
    -- customer_age  | 1000000    | 995000   | 5000       | 0.50   | 18  | 95  | 42.3 | 15.2   | 78
    ```

**Anomaly Detection**:
    ```sql
    -- Detect outliers using IQR method
    WITH stats AS (
        SELECT 
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY order_amount) AS q1,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY order_amount) AS q3
        FROM orders
    ),
    iqr AS (
        SELECT q1, q3, (q3 - q1) AS iqr_value FROM stats
    )
    SELECT order_id, order_amount
    FROM orders, iqr
    WHERE order_amount < (q1 - 1.5 * iqr_value)  -- Lower outliers
       OR order_amount > (q3 + 1.5 * iqr_value); -- Upper outliers
    ```

---

## Data Reconciliation Patterns

### Row Count Reconciliation

**Use Case**: Verify same number of records in source and target.

    ```sql
    -- Simple count
    SELECT 
        'source' AS system, COUNT(*) AS row_count FROM source.orders
    UNION ALL
    SELECT 
        'target' AS system, COUNT(*) AS row_count FROM target.orders;
    
    -- With tolerance (allow 0.1% variance)
    WITH counts AS (
        SELECT 
            (SELECT COUNT(*) FROM source.orders) AS source_count,
            (SELECT COUNT(*) FROM target.orders) AS target_count
    )
    SELECT 
        source_count, 
        target_count,
        ABS(source_count - target_count) AS difference,
        CASE 
            WHEN ABS(source_count - target_count) <= 0.001 * source_count 
            THEN 'PASS' 
            ELSE 'FAIL' 
        END AS status
    FROM counts;
    ```

### Checksum Reconciliation

**Use Case**: Verify data content matches (not just counts).

    ```sql
    -- Aggregate checksum
    SELECT 
        'source' AS system,
        SUM(order_amount) AS total_amount,
        COUNT(*) AS row_count,
        SUM(CAST(MD5(CONCAT(order_id, customer_id, order_amount)) AS UNSIGNED)) AS checksum
    FROM source.orders
    UNION ALL
    SELECT 
        'target' AS system,
        SUM(order_amount) AS total_amount,
        COUNT(*) AS row_count,
        SUM(CAST(MD5(CONCAT(order_id, customer_id, order_amount)) AS UNSIGNED)) AS checksum
    FROM target.orders;
    
    -- If checksums differ, data content mismatch exists
    ```

### Column-Level Reconciliation

**Use Case**: Compare specific columns for discrepancies.

    ```sql
    -- Identify mismatched rows
    SELECT s.order_id,
           s.order_amount AS source_amount,
           t.order_amount AS target_amount,
           ABS(s.order_amount - t.order_amount) AS difference
    FROM source.orders s
    JOIN target.orders t ON s.order_id = t.order_id
    WHERE ABS(s.order_amount - t.order_amount) > 0.01; -- Allow for rounding
    ```

---

## Data Observability

### Monitoring Framework

    ```mermaid
    graph LR
        A[Data Pipeline] --> B[Data Quality Checks]
        B --> C{Pass?}
        C -->|Yes| D[Update Metrics Dashboard]
        C -->|No| E[Trigger Alert]
        E --> F[On-Call Engineer]
        D --> G[Historical Trend Analysis]
        G --> H[Anomaly Detection ML]
        
        style B fill:#e1f5ff
        style E fill:#ffe1e1
    ```

### Key Observability Metrics

**Freshness**:
    ```sql
    -- Data staleness (hours since last update)
    SELECT 
        table_name,
        MAX(last_updated) AS latest_record,
        TIMESTAMPDIFF(HOUR, MAX(last_updated), CURRENT_TIMESTAMP) AS hours_stale
    FROM data_catalog.table_metadata
    GROUP BY table_name
    HAVING hours_stale > 24; -- Alert if data is >24 hours old
    ```

**Volume Anomalies**:
    ```sql
    -- Detect volume spikes/drops (>20% variance from 7-day average)
    WITH daily_counts AS (
        SELECT 
            DATE(order_date) AS date,
            COUNT(*) AS daily_count
        FROM orders
        WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAY
        GROUP BY DATE(order_date)
    ),
    avg_counts AS (
        SELECT 
            date,
            daily_count,
            AVG(daily_count) OVER (
                ORDER BY date 
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS avg_7day
        FROM daily_counts
    )
    SELECT date, daily_count, avg_7day,
           ROUND(100.0 * (daily_count - avg_7day) / avg_7day, 2) AS variance_pct
    FROM avg_counts
    WHERE ABS(daily_count - avg_7day) > 0.2 * avg_7day; -- >20% variance
    ```

**Schema Drift**:
    ```python
    # Monitor schema changes over time
    import json
    
    def detect_schema_drift(current_schema, baseline_schema_json):
        baseline = json.loads(baseline_schema_json)
        
        drift = {
            'added_columns': [],
            'removed_columns': [],
            'type_changes': []
        }
        
        current_cols = {col['name']: col['type'] for col in current_schema}
        baseline_cols = {col['name']: col['type'] for col in baseline}
        
        # Detect added columns
        for col in current_cols:
            if col not in baseline_cols:
                drift['added_columns'].append(col)
        
        # Detect removed columns
        for col in baseline_cols:
            if col not in current_cols:
                drift['removed_columns'].append(col)
        
        # Detect type changes
        for col in current_cols:
            if col in baseline_cols and current_cols[col] != baseline_cols[col]:
                drift['type_changes'].append({
                    'column': col,
                    'old_type': baseline_cols[col],
                    'new_type': current_cols[col]
                })
        
        return drift
    ```

---

## Test Data Generation

### Synthetic Data Generation

**Use Case**: Create realistic test data without using production data (GDPR/HIPAA compliant).

    ```python
    from faker import Faker
    import pandas as pd
    
    fake = Faker()
    
    def generate_customer_data(num_records=1000):
        data = {
            'customer_id': [fake.uuid4() for _ in range(num_records)],
            'first_name': [fake.first_name() for _ in range(num_records)],
            'last_name': [fake.last_name() for _ in range(num_records)],
            'email': [fake.email() for _ in range(num_records)],
            'phone': [fake.phone_number() for _ in range(num_records)],
            'address': [fake.address() for _ in range(num_records)],
            'birthdate': [fake.date_of_birth(minimum_age=18, maximum_age=90) 
                          for _ in range(num_records)],
            'registration_date': [fake.date_between(start_date='-5y', end_date='today') 
                                   for _ in range(num_records)]
        }
        return pd.DataFrame(data)
    
    # Generate 10,000 test customers
    test_customers = generate_customer_data(10000)
    test_customers.to_csv('test_customers.csv', index=False)
    ```

### Data Masking (Production Data Anonymization)

**Use Case**: Use production data for testing while protecting PII/PHI.

    ```sql
    -- Masking strategies
    SELECT 
        customer_id,  -- Keep original (non-sensitive)
        MD5(email) AS email_hash,  -- One-way hash
        CONCAT(
            SUBSTRING(first_name, 1, 1), 
            REPEAT('*', LENGTH(first_name) - 1)
        ) AS masked_first_name,  -- Partial masking
        'REDACTED' AS ssn,  -- Full redaction
        DATE_FORMAT(birthdate, '%Y-01-01') AS masked_birthdate,  -- Year only
        ROUND(order_amount, -2) AS rounded_amount  -- Round to nearest 100
    FROM customers;
    
    -- Output:
    -- customer_id | email_hash              | masked_first_name | ssn      | masked_birthdate | rounded_amount
    -- C001        | 5d41402abc4b2a76b9719... | J***              | REDACTED | 1990-01-01       | 1200
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What are the 6 dimensions of data quality?  
**A1**: Accuracy, Completeness, Consistency, Validity, Timeliness, Uniqueness.

**Q2**: Difference between data validation and data verification?  
**A2**: Validation = is data fit for purpose? (business rules). Verification = does data match specification? (format, schema).

### Advanced (4-8 years)
**Q3**: How do you validate data accuracy when source system is unavailable?  
**A3**: (1) Use historical baseline (compare today's data to last week's pattern), (2) Cross-reference with alternate sources, (3) Business rule validation (implicit checks like order_amount > 0), (4) Outlier detection (statistical anomalies).

**Q4**: Explain the difference between data profiling and data quality testing.  
**A4**: Profiling = exploratory analysis to understand data characteristics (distribution, patterns). Testing = validation against known rules/expectations (pass/fail).

### Scenario (8-12 years)
**Q5**: 1M customer records in source, 950K in target. How do you identify missing 50K?  
**A5**: (1) **LEFT JOIN**: `SELECT s.customer_id FROM source s LEFT JOIN target t ON s.customer_id = t.customer_id WHERE t.customer_id IS NULL`, (2) **Date range analysis**: Check if missing records fall in specific date range, (3) **Pattern analysis**: Missing by region, product category, etc., (4) **ETL logs**: Review extraction logs for failures/timeouts.

### Architect (12+ years)
**Q6**: Design a data quality framework for a 100TB data lake with 500+ datasets.  
**A6**: (1) **Metadata-driven**: Define quality rules in catalog (completeness thresholds, valid ranges per dataset), (2) **Automated profiling**: Nightly jobs profile all datasets, detect anomalies, (3) **Tiered SLAs**: Critical datasets (100% accuracy) vs. exploratory (best effort), (4) **Self-service**: Data owners define/monitor their rules via UI, (5) **Observability**: Centralized dashboard (freshness, volume, quality score), (6) **Alerting**: Severity-based routing (P1 → page on-call, P3 → email data owner).

---

## Frequently Asked Questions

**Q1**: How much data reconciliation is enough?  
**A1**: Depends on criticality. Financial data: 100% reconciliation (row-level). Clickstream: Sample-based (1% random sample). Use risk-based approach.

**Q2**: Should data quality checks run in ETL pipeline or separately?  
**A2**: **Both**. In-pipeline: Fail-fast checks (schema validation, null checks). Post-load: Comprehensive checks (referential integrity, business rules). Prevents bad data from propagating.

**Q3**: How to handle late-arriving data in reconciliation?  
**A3**: (1) **Grace period**: Re-reconcile after 24-hour window to catch late arrivals, (2) **Watermarking**: Track high-water mark of processed data, (3) **Append-only**: Late data appends vs. overwrites (audit trail).

**Q4**: What's the difference between data quality and data governance?  
**A4**: **Quality** = technical correctness (accurate, complete, valid). **Governance** = organizational policies (who owns data, access controls, retention rules).

**Q5**: How to test real-time data pipelines for data quality?  
**A5**: (1) **Streaming assertions**: Validate each event (schema, ranges) before processing, (2) **Windowed aggregations**: Check hourly totals vs. expected baseline, (3) **Latency monitoring**: Alert if event-to-storage time >SLA, (4) **Replay testing**: Re-process historical events to validate idempotency.

**Q6**: Best tools for data profiling?  
**A6**: **Open-source**: Great Expectations (Python), deequ (Spark), dbt tests (SQL). **Commercial**: Informatica Data Quality, Talend, AWS Glue DataBrew, Google Cloud Data Quality.

**Q7**: How to prioritize data quality issues?  
**A7**: Use **data criticality matrix**: (1) Business impact (revenue, compliance, decision-making), (2) Affected users (exec dashboard vs. internal report), (3) Data volume (1% error on 1B records = 10M bad records), (4) Fix complexity. Prioritize high-impact, high-volume, low-complexity fixes.

**Q8**: What's data observability vs. data monitoring?  
**A8**: **Monitoring** = reactive (alert when threshold breached). **Observability** = proactive (understand system state from outputs, detect unknown-unknowns). Observability includes: freshness, volume, schema, lineage, quality trends.

**Q9**: How to measure data quality score?  
**A9**: Weighted average of dimension scores: `Quality Score = (w1×Accuracy + w2×Completeness + w3×Timeliness + ...) / Σweights`. Example: 40% accuracy, 30% completeness, 20% timeliness, 10% consistency. Score: 0-100.

**Q10**: How often to run data quality checks?  
**A10**: **Critical data**: Real-time (streaming pipelines). **Batch data**: After each load (daily ETL). **Historical data**: Weekly profiling to detect drift. **Ad-hoc**: Before major releases or migrations.

**Q11**: How to test data lineage?  
**A11**: (1) **Trace data flow**: Verify data propagates source → staging → DWH → BI, (2) **Impact analysis**: Change source record, confirm downstream updates, (3) **Automated lineage tools**: Validate metadata (Collibra, Atlan) matches actual data flow.

**Q12**: What's the difference between null and empty string?  
**A12**: **NULL** = value unknown/not applicable (database concept). **Empty string** = value is known to be "" (application concept). Test both: `WHERE column IS NULL OR column = ''`.

**Q13**: How to test data privacy controls (GDPR Right to Erasure)?  
**A13**: (1) **Functional test**: Submit erasure request, verify data deleted within SLA, (2) **Completeness**: Check deletion across all systems (prod DB, backups, logs, analytics), (3) **Audit trail**: Verify deletion logged for compliance, (4) **Negative test**: Confirm deleted data inaccessible via APIs/reports.

**Q14**: Best practices for test data refresh in lower environments?  
**A14**: (1) **Frequency**: Weekly refresh from prod (keeps data realistic), (2) **Masking**: Anonymize PII during copy, (3) **Subsetting**: Copy recent 6 months (reduce storage), (4) **Referential integrity**: Ensure FK relationships maintained during subset, (5) **Version control**: Track test data snapshots for reproducibility.

**Q15**: How to detect data duplication?  
**A15**: (1) **Exact duplicates**: `GROUP BY all_columns HAVING COUNT(*) > 1`, (2) **Fuzzy duplicates**: Use similarity algorithms (Levenshtein distance for names, email domains), (3) **Composite keys**: Check expected uniqueness constraints, (4) **Tools**: Dedupe libraries (Python Dedupe, OpenRefine).

**Q16**: What's the 80/20 rule in data quality?  
**A16**: 80% of data quality issues trace to 20% of data sources/processes. Focus QA efforts on high-risk sources (manual entry systems, external APIs, legacy systems).

**Q17**: How to validate data transformations without knowing business logic?  
**A17**: (1) **Input-output mapping**: Sample 100 source records, trace through transformations, (2) **Inverse transformations**: If transform is reversible, validate roundtrip, (3) **Statistical properties**: Mean, variance should change predictably, (4) **Ask**: Consult business analyst or data engineer for business context.

**Q18**: Difference between data reconciliation and data migration testing?  
**A18**: **Reconciliation** = ongoing validation (daily ETL loads). **Migration** = one-time validation (legacy → new system cutover). Migration includes: schema mapping, data type conversions, historical data accuracy.

**Q19**: How to test cascading deletes in data pipelines?  
**A19**: (1) **Setup**: Create parent record with child records, (2) **Action**: Delete parent, (3) **Verify**: Confirm children also deleted (or FK set to NULL, depending on cascade rule), (4) **Audit**: Check deletion logged correctly.

**Q20**: What's the role of data contracts in data quality?  
**A20**: **Data contract** = formal agreement between data producer and consumer (schema, SLAs, quality guarantees). QA validates: (1) Producer honors contract (schema stability), (2) Consumer handles contract violations gracefully, (3) Contract versioning works (backward compatibility).

---

## Actionable Checklists

### Data Quality Testing Checklist
- [ ] Schema validation (columns, data types, constraints)
- [ ] Completeness checks (row counts, null percentages)
- [ ] Accuracy validation (sample verification vs. source)
- [ ] Consistency checks (cross-system reconciliation)
- [ ] Validity testing (format, range, business rules)
- [ ] Uniqueness verification (primary key, composite keys)
- [ ] Referential integrity (FK relationships)
- [ ] Timeliness monitoring (data freshness SLAs)

### Data Reconciliation Checklist
- [ ] Row count match (source vs. target)
- [ ] Checksum/hash validation (aggregate data)
- [ ] Column-level comparison (key fields)
- [ ] Date range coverage (no gaps in time series)
- [ ] Volume trend analysis (historical baseline)
- [ ] Outlier detection (statistical anomalies)
- [ ] Exception reporting (discrepancies documented)
- [ ] Sign-off (stakeholder approval of reconciliation results)

### Data Observability Setup Checklist
- [ ] Freshness monitors (alert on stale data)
- [ ] Volume monitors (alert on anomalies)
- [ ] Schema change detection (drift alerts)
- [ ] Quality score dashboards (dimensions tracked)
- [ ] Lineage visualization (data flow mapping)
- [ ] Incident response runbook (escalation paths)
- [ ] Historical trending (quality over time)
- [ ] Automated profiling (weekly data summaries)

---

## References

### Books
- **Data Quality: The Accuracy Dimension** (Jack E. Olson): Comprehensive data quality guide
- **The Enterprise Data Catalog** (Ole Olesen-Bagneux): Metadata management
- **Designing Data-Intensive Applications** (Martin Kleppmann): Data systems architecture

### Standards
- **ISO 8000**: Data quality standard
- **DAMA-DMBOK**: Data quality chapter (frameworks, metrics)
- **TDWI Best Practices**: Data quality reports

### Tools
- **Great Expectations**: Python data validation framework
- **dbt tests**: SQL-based data testing
- **Apache Griffin**: Data quality platform
- **Monte Carlo**: Data observability platform

---

**Core References**: Platform-agnostic data testing concepts  
**Stack Deltas**: See stack files for platform-specific data quality tools

**Previous**: [02_QA_Concepts.md](./02_QA_Concepts.md)  
**Next**: [04_ETL_Concepts.md](./04_ETL_Concepts.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)