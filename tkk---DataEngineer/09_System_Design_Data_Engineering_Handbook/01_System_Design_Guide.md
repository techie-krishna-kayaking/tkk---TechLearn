# 09 — System Design for Data Engineering

> System design interviews for data engineers are different from SWE system design.
> You're designing DATA PIPELINES, not web services. Know the trade-offs between
> batch vs streaming, Lambda vs Kappa architecture, and how to handle scale.

---

## 🏗️ Framework for Data System Design Interviews

Use this structure every time:

```
1. CLARIFY REQUIREMENTS (5 min)
   → What is the data source? (DB, events, files, API?)
   → What is the scale? (GB/day, TB/day, PB/day? Events/sec?)
   → What is the latency requirement? (Real-time <1s, near-real-time <1min, batch)
   → What are the consumers? (BI tools, ML models, APIs, dashboards?)
   → Consistency vs availability trade-off? (Can we show stale data?)
   → SLA? (99.9% uptime? Data freshness SLA?)

2. HIGH-LEVEL DESIGN (10 min)
   → Draw the pipeline stages: Ingest → Store → Process → Serve
   → Choose batch vs streaming vs lambda architecture
   → Choose storage format and layer (raw, processed, serving)

3. DEEP DIVE (15 min)
   → Zoom into the hardest component
   → Discuss partitioning strategy, schema design, fault tolerance

4. TRADE-OFFS (5 min)
   → What did you give up? What would you do differently at 10x scale?
   → Cost vs performance vs consistency
```

---

## 📐 Architecture Patterns

### Batch Architecture (Traditional)

```
Data Source → Nightly ETL (Spark/Glue) → Warehouse (Redshift/BigQuery) → BI
```

When: Data freshness of 1 day is acceptable. Simpler, cheaper.

### Lambda Architecture

```
                  → Batch Layer (Spark, daily/hourly) ─────────────┐
Data Source                                                          → Serving Layer → Query
                  → Speed Layer (Spark Streaming/Flink, ms/sec) ──┘
```

When: Need both historical accuracy AND low-latency results.
Downside: Two codebases (batch + stream) to maintain. Complex.

### Kappa Architecture

```
Data Source → Stream Processing (Kafka + Spark Streaming) → Serving Layer → Query
            → Store raw events in Kafka/S3 for reprocessing
```

When: Streaming-first, reprocess by replaying raw events.
Simpler than Lambda — one codebase.

### Modern Lakehouse (Most Common Answer)

```
Sources → Kafka/Event Streaming → Bronze (raw Delta) → Silver (cleaned) → Gold (aggregated) → BI
                               → Airflow (orchestration)
```

---

## 🎯 Design Problem 1: Build a Real-Time Analytics Dashboard

**"Design a system that shows product metrics (page views, purchases, revenue) updated every 5 minutes."**

```
Step 1 — Clarify:
  Scale: 10M events/day, 120 events/sec peak
  Latency: 5-minute freshness
  Consumers: Grafana / internal BI dashboard
  Retention: 90 days warm, 3 years cold

Step 2 — Design:
  Producers (web/app) → Kafka (events topic) → Spark Structured Streaming
                                                    ↓
                                             5-min micro-batch
                                                    ↓
                                         Delta Lake (Silver table)
                                                    ↓
                                         Materialized aggregations (Gold)
                                                    ↓
                                       Grafana / Tableau / API

Step 3 — Components:
  Kafka topic: "product_events"
    Partitions: 12 (10 consumers + headroom)
    Retention: 7 days
    Key: product_id (event ordering per product)

  Spark Streaming:
    trigger(processingTime="5 minutes")
    withWatermark("event_time", "10 minutes")
    outputMode: update
    sink: Delta Lake with checkpointing

  Delta Lake:
    Bronze: raw events as-is (append only)
    Silver: cleaned, parsed, deduped (merge with unique_key)
    Gold: pre-aggregated by product/5-min window (for dashboard speed)

Step 4 — Trade-offs:
  Chose 5-min micro-batch over true streaming:
    → Simpler, cheaper, Delta Lake ACID guarantees
    → If needed, switch to 30-sec trigger (Databricks supports it)
  Delta over Parquet:
    → Schema enforcement, time travel for debugging, ACID
  Gold aggregations:
    → Pre-aggregate to avoid dashboard doing GROUP BY on billions of rows
```

---

## 🎯 Design Problem 2: Build a Data Ingestion Pipeline from 50 Source DBs

**"Design a pipeline that ingests data from 50 different transactional databases (MySQL, PostgreSQL, Oracle) into a central data lake, with low latency and no impact on the source systems."**

```
Step 1 — Clarify:
  Volume: 50 databases, ~10 tables each, ~10 GB/day total
  Latency: <15 min for most tables, hourly for large tables
  Impact: zero impact on production databases
  Schema: schemas change occasionally (ADD COLUMN is common)

Step 2 — Design:
  Debezium (CDC) → Kafka → Kafka Connect S3 Sink → Bronze (S3/ADLS)
                                                         ↓
                                                    Glue ETL (hourly)
                                                         ↓
                                              Silver (Parquet/Delta, partitioned)
                                                         ↓
                                              Athena / Redshift Spectrum

  For initial full load:
    AWS DMS full-load → S3 → then switch to CDC mode

Step 3 — Components:
  Debezium:
    Reads MySQL binlog / PostgreSQL WAL / Oracle redo logs
    Produces change events to Kafka (INSERT/UPDATE/DELETE as JSON)
    Zero impact on source (reads from logs, not tables)

  Kafka:
    One topic per table: "cdc.mydb.orders"
    Key = primary key value (ensures same-row updates go to same partition)
    Log compaction → keeps only latest state per key (useful for snapshots)

  S3 Sink Connector:
    Dumps Kafka to S3 in Parquet every 100MB or 15 minutes
    Path: s3://datalake/bronze/mydb/orders/year=2024/month=01/

  Schema Evolution:
    Confluent Schema Registry — tracks Avro schemas
    Bronze layer: store raw JSON (no schema enforcement)
    Silver layer: apply schema, handle new columns gracefully (mergeSchema=True)

Step 4 — Trade-offs:
  CDC vs polling:
    → CDC is more real-time, lower DB impact. Polling is simpler but slower.
  Debezium vs DMS:
    → Debezium: open-source, more Kafka-native. DMS: AWS managed, easier setup.
  Avro vs JSON in Kafka:
    → Avro: compact binary, schema enforced. JSON: human-readable, flexible.
    → Production: Avro + Schema Registry.
```

---

## 🎯 Design Problem 3: Design a Data Warehouse for an E-Commerce Platform

**"Design the warehouse schema and pipeline for an e-commerce company to answer: monthly revenue per category, top 10 products, customer lifetime value."**

```
Step 1 — Data Modeling (Star Schema):

Fact Tables:
  fct_orders:
    order_id (PK), customer_id (FK), product_id (FK), date_id (FK),
    quantity, unit_price, total_amount, discount_amount

Dimension Tables:
  dim_customers:   customer_id, name, email, country, customer_tier, joined_date
  dim_products:    product_id, name, category, subcategory, brand, cost
  dim_dates:       date_id, date, year, month, quarter, is_weekend, is_holiday

Step 2 — Query Examples:
  -- Monthly revenue per category
  SELECT d.year, d.month, p.category, SUM(o.total_amount) AS revenue
  FROM fct_orders o
  JOIN dim_dates d ON o.date_id = d.date_id
  JOIN dim_products p ON o.product_id = p.product_id
  GROUP BY d.year, d.month, p.category

  -- Customer Lifetime Value
  SELECT customer_id, SUM(total_amount) AS ltv,
         COUNT(DISTINCT order_id) AS order_count,
         AVG(total_amount) AS avg_order_value
  FROM fct_orders
  GROUP BY customer_id

Step 3 — Physical Design (Redshift/BigQuery):
  fct_orders:
    DIST KEY: customer_id (most joins are on customer)
    SORT KEY: order_date (range queries are common)

  dim_products: DISTSTYLE ALL (small dimension, replicate to all nodes)
  dim_customers: DISTSTYLE KEY(customer_id) (matches fct_orders dist key)
  dim_dates: DISTSTYLE ALL (small, < 36,500 rows for 100 years)

Step 4 — SCD Type 2 for dim_customers:
  When a customer's tier changes (Bronze → Gold), create a new row:
  customer_id=1, tier=Bronze, valid_from=2023-01-01, valid_to=2024-06-01
  customer_id=1, tier=Gold,   valid_from=2024-06-01, valid_to=9999-12-31
  (dbt Snapshots handles this automatically)
```

---

## 🎯 Design Problem 4: Batch ML Feature Pipeline

**"Design a pipeline that computes 50 user features for a recommendation model, updated daily."**

```
Sources:
  orders DB → CDC → Kafka → Raw S3
  clickstream → Kafka → Raw S3
  product catalog → DB snapshot → S3

Pipeline (Airflow DAG, runs at 2 AM daily):
  Task 1: dbt snapshot (SCD2 for users)
  Task 2: Spark on EMR (feature computation)
           → sliding window aggregations (last 7d, 30d, 90d purchase amounts)
           → user-item interaction matrix
           → categorical encoding
  Task 3: Write features to Feature Store (Feast/Tecton/SageMaker Feature Store)
  Task 4: Trigger model training if features changed >5%

Feature Store:
  Offline store: S3/Delta (historical features for training)
  Online store: DynamoDB/Redis (low-latency feature serving for inference)

Key design decisions:
  Point-in-time correctness: features for 2024-03-01 model training
    MUST use feature values as they existed on 2024-03-01 (not current values)
    → Feature store handles this via as_of_date parameter
  Backfilling: Compute features for the past 2 years for initial model training
    → Use Spark on S3 historical data, not live pipeline
```

---

## 📊 Key Concepts for System Design

### CAP Theorem
```
Consistency   → every read sees the most recent write (or an error)
Availability  → every request gets a (non-error) response
Partition Tol → system works even if nodes can't communicate

Choose 2:
  CP (Consistent + Partition): HBase, Zookeeper, MongoDB(default)
  AP (Available + Partition):  Cassandra, CouchDB, DynamoDB(default)
  CA: doesn't exist in distributed systems (network always partitions)
```

### Data Freshness Trade-offs
```
Real-time streaming   → 1-10 seconds. Cost: $$$$. Complexity: High.
Near-real-time        → 1-15 minutes. Cost: $$$.  Complexity: Medium.
Hourly batch          → 1 hour.       Cost: $$.   Complexity: Low.
Daily batch           → 24 hours.     Cost: $.    Complexity: Lowest.
```

**Interview Tip:** Always ask "what is the business need for freshness?" before designing.
Most dashboards that ask for "real-time" are fine with 15-minute freshness.

---

## ❓ Top 5 System Design Interview Questions

**Q1: Lambda vs Kappa architecture — explain the trade-offs.**
Lambda: separate batch and speed layers, complex to maintain, accurate historical + low-latency.
Kappa: streaming only, reprocess by replaying Kafka, single codebase, requires reliable event storage.
Modern answer: Lakehouse (Delta/Iceberg) with Spark Streaming often replaces both.

**Q2: How do you handle late data in a batch pipeline?**
Design with a delay buffer: instead of processing "yesterday's data" at midnight, process it at 2 AM. This gives a 2-hour window for late-arriving events. For critical pipelines, run a reconciliation job 24h later comparing processed vs expected counts.

**Q3: How do you ensure data pipeline idempotency?**
An idempotent pipeline produces the same result when run multiple times.
Strategies: partition overwrites (`replaceWhere` on date partition), upserts with unique keys (Delta merge), `CREATE OR REPLACE TABLE`, checking if output already exists before writing.

**Q4: How would you design for data observability?**
Four pillars: freshness (when was data last updated?), volume (did row count change unusually?), schema (did columns change?), distribution (did value ranges change, detecting data drift?).
Tools: Great Expectations, dbt tests, Monte Carlo, Bigeye, or custom checks in Airflow.

**Q5: How do you handle a pipeline that processes 100 TB/day?**
Partition strategy (by date, business entity), columnar format (Parquet/ORC), partition pruning and predicate pushdown, appropriate cluster sizing (more executors, higher memory), Z-ORDER on frequently filtered columns (Delta), avoid full shuffles (broadcast small tables, pre-partition by join key), AQE enabled.
