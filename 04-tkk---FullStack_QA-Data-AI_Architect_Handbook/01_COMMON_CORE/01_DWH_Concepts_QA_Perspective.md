# Data Warehouse Concepts - QA Perspective

## Executive Summary

Data warehousing forms the analytical backbone of enterprise data architecture. From a **QA perspective**, validating DWH implementations requires mastery of dimensional modeling, slowly changing dimensions (SCD), schema patterns, and analytical workload failure modes.

**Target Audience**: Senior/Principal QA engineers (8+ years) testing data pipelines and analytical systems.

---

## Why This Matters in Enterprise

### Business Impact
- **Data quality incidents cost $12.9M annually** (Gartner 2025)
- **DWH powers revenue intelligence**: Sales forecasting, customer analytics ($50M-$500M impact)
- **Regulatory compliance**: Financial reporting (SOX), healthcare (HIPAA), privacy (GDPR)

### Technical Imperative
- **Single source of truth**: Errors cascade to all downstream BI/ML consumers
- **Historical accuracy**: SCD Type 2 enables trend analysis but is complex to validate
- **Query performance**: Poor schemas cause 10-100x degradation at scale

---

## Scope and Boundaries

### In Scope
- Dimensional modeling (star/snowflake schemas, fact/dimension tables)
- SCD patterns (Type 0/1/2/3/4/6)
- Fact table patterns (transactional, periodic snapshot, accumulating snapshot)
- Dimension patterns (conformed, junk, role-playing, degenerate)
- Data Vault 2.0 (Hub/Link/Satellite)
- QA strategies for DWH validation

### Out of Scope
- Platform-specific syntax (covered in stack files)
- ETL orchestration (see [04_ETL_Concepts.md](./04_ETL_Concepts.md))
- Real-time streaming (see [05_Big_Data_Concepts.md](./05_Big_Data_Concepts.md))

---

## Architecture Patterns

### Star Schema (Kimball)

    ```mermaid
    graph TD
        FT[Fact: Sales] -->|date_key| D1[Dim: Date]
        FT -->|product_key| D2[Dim: Product]
        FT -->|customer_key| D3[Dim: Customer]
        FT -->|store_key| D4[Dim: Store]
        style FT fill:#fcc
        style D1 fill:#cfc
        style D2 fill:#cfc
        style D3 fill:#cfc
        style D4 fill:#cfc
    ```

**Characteristics**: Denormalized dimensions, fast queries (minimal joins), easy for business users

**QA Focus**:
- Validate grain (one row per transaction)
- Check FK relationships (no orphaned facts)
- Verify measure additivity (can SUM across all dimensions?)

### Snowflake Schema

**Characteristics**: Normalized dimensions (hierarchies split), reduced storage, complex queries

**QA Focus**: Test referential integrity across dimension hierarchies, validate join performance

---

## Slowly Changing Dimensions (SCD)

### SCD Type 1: Overwrite
    ```sql
    -- Before
    product_key | product_id | category
    1           | P001       | Electronics
    
    -- After update
    product_key | product_id | category
    1           | P001       | Home Goods  -- Old value lost
    ```

**QA Tests**: Verify old value truly overwritten, no history retained

### SCD Type 2: Add New Row (Most Common)
    ```sql
    -- Before
    product_key | product_id | category    | valid_from | valid_to   | is_current
    1           | P001       | Electronics | 2024-01-01 | 9999-12-31 | Y
    
    -- After update
    product_key | product_id | category    | valid_from | valid_to   | is_current
    1           | P001       | Electronics | 2024-01-01 | 2024-06-14 | N
    2           | P001       | Home Goods  | 2024-06-15 | 9999-12-31 | Y
    ```

**QA Tests**:
- **Temporal validity**: No overlapping valid_from/valid_to ranges
- **Current flag accuracy**: Only one row per natural key has is_current = 'Y'
- **Historical integrity**: Old facts join to correct historical dimension row
- **End-dating logic**: Previous valid_to = new valid_from - 1 day

### SCD Type 3: Add Column
    ```sql
    product_key | product_id | current_category | previous_category
    1           | P001       | Home Goods       | Electronics
    ```

**QA Tests**: Validate column shift logic, check data loss when history depth exceeded

---

## Fact Table Patterns

### Transactional Fact
**Grain**: One row per transaction (order line, payment)  
**Measures**: Additive (can SUM sales_amount across all dimensions)  
**QA**: Row count reconciliation, measure totals vs. source

### Periodic Snapshot Fact
**Grain**: One row per time period (daily account balance)  
**Measures**: Semi-additive (can SUM across products, AVG across time)  
**QA**: Snapshot completeness (every date has data), semi-additive validation

### Accumulating Snapshot Fact
**Grain**: One row per process lifecycle (order: placement → shipment → delivery)  
**Measures**: Multiple date keys, lag measures (days_to_ship)  
**QA**: Logical date sequence (ship_date >= order_date), lag calculation accuracy

---

## QA Strategy and Operating Model

### RACI Matrix

| Activity | QA | Data Engineer | Business Analyst | DBA |
|----------|-----|---------------|------------------|-----|
| Schema Design Review | C | R | A | C |
| SCD Testing | R | A | C | I |
| Data Reconciliation | R | C | A | I |
| Performance Testing | R | C | I | A |

**Legend**: R=Responsible, A=Accountable, C=Consulted, I=Informed

### Test Coverage Model

| Layer | Target | Test Types |
|-------|--------|------------|
| Schema | 100% | Metadata validation, naming conventions |
| Referential Integrity | 100% | Orphan detection, FK checks |
| SCD Logic | 100% | Temporal validity, current flag |
| Business Rules | 100% | Derivations, aggregations |
| Data Quality | 95%+ completeness, 99%+ accuracy | Null checks, format validation |

---

## Test Design Techniques

### Equivalence Partitioning for SCD
1. **New dimension record**: INSERT with is_current='Y'
2. **Update non-tracked attribute**: UPDATE existing row
3. **Update tracked attribute**: End-date old row, INSERT new row
4. **No change**: Idempotent (no action)

### Boundary Value Analysis for Date Dimensions
- Leap year: Feb 29, 2024 (exists) vs. 2025 (missing)
- Fiscal year boundary: Last day Q4 vs. first day Q1
- Daylight saving: Spring forward (23-hour day) vs. fall back (25-hour day)

---

## Risk/Failure Modes (FMEA)

| Failure Mode | Severity | Occurrence | Detection | RPN | Mitigation |
|--------------|----------|-----------|-----------|-----|------------|
| SCD overlapping validity | 9 | 5 | 6 | 270 | PK+valid_from uniqueness constraint |
| Missing dimension records | 8 | 6 | 4 | 192 | Default dimension row, orphan detection |
| Incorrect fact grain | 10 | 3 | 5 | 150 | Document grain, row count reconciliation |
| Non-additive measures | 7 | 7 | 8 | 392 | Metadata tags (additive/semi/non) |

### Anti-Patterns
❌ **Smart keys**: product_key='ELEC-2024-001' (embeds meaning)  
✅ **Dumb keys**: product_key=123456 (surrogate)

❌ **NULL FKs in facts**: customer_key=NULL  
✅ **Unknown dimension**: customer_key=-1 ('Unknown Customer' row)

❌ **Updating facts**: UPDATE fact_sales SET amount=X  
✅ **Insert reversal**: INSERT negative + corrected row

---

## Controls and Evidence

### SOX Compliance
**Control**: Segregation of duties (QA approves schema, separate from DE)  
**Evidence**: Change tickets with QA sign-off, Git reviewer ≠ committer

**Control**: Data reconciliation (fact totals match source GL)  
**Evidence**: Daily reconciliation reports, exception logs

### GDPR Compliance
**Control**: Right to erasure (customer dimension supports delete)  
**Evidence**: Deletion scripts with audit logs, annual data inventory

---

## SLI/SLO/SLA Framework

### SLIs
- **Data freshness**: Time since last ETL (<2hr good, >4hr bad)
- **Data completeness**: % expected rows loaded (>99.5% good)
- **Data accuracy**: % reconciliation matches (>99.9% good)
- **Query performance**: P95 latency (<5sec good, >30sec bad)

### SLO Example
99.5% of daily ETL runs complete within 2-hour SLA  
**Error budget**: 0.5% = ~1.8 failures/year

---

## Performance/Cost/Reliability

### Performance Optimization
    ```sql
    -- Clustered index on fact table
    CREATE CLUSTERED INDEX idx_sales ON fact_sales(date_key, customer_key);
    
    -- Partitioning by year
    PARTITION BY RANGE (date_key) (
        PARTITION p2023 VALUES LESS THAN (20240101),
        PARTITION p2024 VALUES LESS THAN (20250101)
    );
    
    -- Materialized aggregates
    CREATE MATERIALIZED VIEW mv_monthly_sales AS
    SELECT year, month, product_category, SUM(sales_amount)
    FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key
    JOIN dim_product p ON f.product_key=p.product_key
    GROUP BY 1,2,3;
    ```

### Cost Optimization
- **Storage tiering**: Hot (current year, SSD) → Warm (2yr, HDD) → Cold (3+yr, object storage)
- **Compression**: Columnar formats (Parquet/ORC) achieve 10:1 compression

---

## Interview Questions

### Basic (0-3 years)
**Q1**: Difference between fact and dimension table?  
**A1**: Facts contain measures (sales_amount, quantity) and FKs. Dimensions contain descriptive attributes (customer_name, product_category). Facts are tall/narrow, dimensions are short/wide.

**Q2**: What is a surrogate key?  
**A2**: System-generated unique ID (auto-increment) with no business meaning. Enables SCD Type 2 (multiple rows for same natural key), faster joins (int vs varchar), handles source key collisions.

### Advanced (4-8 years)
**Q3**: How to validate SCD Type 2?  
**A3**: (1) No overlapping valid_from/to for same natural key, (2) Only one current row, (3) Historical facts join to correct version, (4) End-dating logic correct, (5) Surrogate keys unique.

**Q4**: What are conformed dimensions?  
**A4**: Dimensions shared across fact tables with identical structure (dim_date, dim_customer used by sales/support). Enables cross-mart queries, ensures consistent reporting.

### Scenario (8-12 years)
**Q5**: Sales fact shows $10M, source shows $10.2M. Troubleshoot?  
**A5**: (1) Row count check, (2) Date range match, (3) Orphaned facts (FK not in dimension), (4) Aggregation logic (NULL handling), (5) SCD impact (query joins wrong version), (6) Late-arriving transactions.

### Architect (12+ years)
**Q6**: Design DWH for global retailer: 500 stores, 1M SKUs, 100M trans/day?  
**A6**: Star schema, partition fact by month, SCD Type 2 for product/store, junk dimension for flags, clustered index (date_key, store_key), pre-aggregate rollups, columnar storage, Data Vault staging, UTC timestamps, locale-specific dimensions.

---

## Frequently Asked Questions

**Q1**: Use SCD Type 2 for all dimensions?  
**A1**: No. Only for attributes where history matters. Type 1 sufficient for corrections, irrelevant history, high-churn attributes.

**Q2**: Star vs. snowflake schema?  
**A2**: Star (denormalized) is default—faster queries, simpler. Snowflake (normalized) only when storage expensive, deep hierarchies, or regulatory normalization required.

**Q3**: Data warehouse vs. data lake?  
**A3**: DWH = structured, schema-on-write, SQL analytics. Lake = raw, schema-on-read, big data processing. Lakehouse = hybrid (Delta Lake, Iceberg).

**Q4**: Handle timezone in global DWH?  
**A4**: Store all timestamps in UTC. Add local_timezone column to dimension. Convert at query time. Date dimension includes UTC and local date keys.

**Q5**: Factless fact table use case?  
**A5**: Records events without measures (student enrollment, product promotions, facility usage). Queries: COUNT(*), coverage analysis.

**Q6**: Test incremental ETL (CDC)?  
**A6**: (1) Initial load row count, (2) Incremental insert (verify delta), (3) Update (check SCD), (4) Delete (soft delete flag), (5) Late arrivals (backdate handling).

**Q7**: OLTP vs. OLAP?  
**A7**: OLTP = row-store, normalized, write-heavy, sub-second, few queries. OLAP = column-store, denormalized, read-heavy, complex aggregations, many queries.

**Q8**: Handle slowly changing hierarchies?  
**A8**: (1) Bridge table (many-to-many), (2) SCD Type 2 on dimension, (3) Re-state history (breaks audit), (4) Dual hierarchies (both old/new).

**Q9**: Degenerate dimension when appropriate?  
**A9**: Operational IDs (invoice_number, order_id) with no descriptive attributes, high cardinality. Not appropriate if descriptive attributes exist.

**Q10**: Implement data lineage?  
**A10**: (1) Audit columns (insert_date, source_system_id), (2) Metadata repo (ETL logs), (3) Lineage tools (Informatica, Collibra), (4) Data Vault record_source.

**Q11**: Multi-currency in DWH?  
**A11**: Store source currency+code, exchange rate dimension, converted measures (sales_amount_usd), historical rates for temporal analysis.

**Q12**: Test data quality rules?  
**A12**: Completeness (NULL checks), validity (format/range), consistency (cross-field), uniqueness (PK), referential integrity (FK), timeliness (freshness).

**Q13**: Junk dimension trade-offs?  
**A13**: Pros: reduces fact width, easy to add flags. Cons: large size (cartesian product), requires lookup.

**Q14**: Data archival strategy?  
**A14**: Partition by date (fast drop), archive to cold storage (S3/ADLS), summarize before archive (keep aggregates), compliance checks (retention policies).

**Q15**: Staging area role?  
**A15**: Landing zone for raw source (ELT). Benefits: isolate source impact, restartability, audit trail, parallel loading. Trade-off: extra storage.

**Q16**: Mini-dimension for high cardinality?  
**A16**: Split demographics (age, income) into mini-dimension (100 rows vs. 10M customer rows). Avoids SCD Type 2 explosion on main dimension.

**Q17**: ETL vs. ELT?  
**A17**: ETL = transform in tool before load (expensive DWH). ELT = load raw, transform in DWH with SQL/Spark (modern cloud DWH).

**Q18**: Handle hierarchical data (org chart)?  
**A18**: (1) Bridge table (ancestor-descendant), (2) Path enumeration (/CEO/VP/Director), (3) Nested set (left/right nodes), (4) Recursive CTEs.

**Q19**: DWH QA effectiveness metrics?  
**A19**: Defect detection rate (>80%), escaped defects (<5/quarter), test coverage (>90%), reconciliation accuracy (>99.9%), MTTD (<24hr).

**Q20**: Test DWH performance?  
**A20**: Baseline queries, load testing (100 concurrent users), data volume (5 years), index effectiveness (EXPLAIN PLAN), partition pruning validation.

---

## Actionable Checklists

### Pre-Implementation (Schema Design Review)
- [ ] Grain definition documented
- [ ] Conformed dimensions identified
- [ ] SCD strategy per dimension
- [ ] Surrogate keys on all dimensions
- [ ] Temporal columns (valid_from, valid_to, is_current)
- [ ] Audit columns (insert_date, update_date, source_system_id)
- [ ] Naming conventions consistent
- [ ] Appropriate data types
- [ ] Constraints defined (PK, FK, NOT NULL)
- [ ] Index strategy documented

### Execution (Testing)
- [ ] Schema validation complete
- [ ] No orphaned facts
- [ ] SCD Type 2 temporal integrity
- [ ] Row count reconciliation
- [ ] Measure validation (SUM match)
- [ ] Dimension completeness
- [ ] Data quality checks pass
- [ ] Incremental load tested
- [ ] Performance SLA met
- [ ] Lineage columns populated

### Post-Production (Monitoring)
- [ ] Daily reconciliation automated
- [ ] Freshness check dashboard
- [ ] Exception monitoring alerts
- [ ] Query performance tracking
- [ ] Storage growth monitoring
- [ ] Access audit reviews
- [ ] Incident postmortems documented

---

## References

### Books
- **The Data Warehouse Toolkit** (Kimball, Ross): Dimensional modeling bible
- **The Data Warehouse Lifecycle Toolkit** (Kimball et al.): End-to-end implementation
- **Building the Data Warehouse** (Inmon): Normalized approach
- **Data Vault 2.0 Methodology** (Linstedt, Olschimke): Enterprise patterns

### Standards
- **ANSI/ISO/IEC 9075**: SQL Standard
- **DAMA-DMBOK**: Data Management Body of Knowledge
- **ISO/IEC 25012**: Data Quality Model

### Online Resources
- Kimball Group: https://www.kimballgroup.com
- Data Vault Alliance: https://datavaultalliance.com
- TDWI: Research, training, conferences

---

**Core References**: Platform-agnostic DWH concepts  
**Stack Deltas**: See Azure/AWS/GCP/Snowflake/Databricks stack files for platform-specific implementations

**Previous**: [00_README.md](./00_README.md)  
**Next**: [02_QA_Concepts.md](./02_QA_Concepts.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)