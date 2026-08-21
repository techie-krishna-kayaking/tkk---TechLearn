# 05 — Cloud Data Engineering Handbook
# Chapter 1: AWS for Data Engineering

> Cloud is non-negotiable at 60 LPA+. You don't need to be a cloud architect —
> you need to know the data-relevant services, when to use each, and how they
> connect into a pipeline. This chapter covers AWS (most common in Indian interviews).

---

## 🏗️ The AWS Data Engineering Stack

```
INGEST          →    STORE          →    PROCESS        →    SERVE
────────────────────────────────────────────────────────────────────
Kinesis Streams      S3 (raw)            Glue ETL          Athena (SQL)
Kafka (MSK)          S3 (processed)      EMR (Spark)       Redshift
DMS (DB migration)   RDS / Aurora        Lambda            QuickSight
AppFlow              DynamoDB            Step Functions    API Gateway
```

---

## 🪣 Amazon S3 (Simple Storage Service)

**Interview Q:** *"What is S3 and why is it the backbone of a data lakehouse?"*

S3 is object storage — you store files (objects) in containers (buckets). It's not a file system.

**Key concepts:**
```
bucket          → top-level container (globally unique name)
object          → a file + metadata (no hierarchy, just key-value)
key             → object's path (e.g. "data/year=2024/month=01/file.parquet")
prefix          → simulated folder (everything before the last '/')
```

**Why it's used for data lakes:**
- Virtually unlimited storage, low cost (~$0.023/GB/month)
- Durability: 99.999999999% (11 nines)
- Decouples storage from compute (Glue, EMR, Athena all read from same S3)
- Supports Parquet, Delta, Iceberg, Hudi natively

**Storage Classes (cost optimization):**
| Class | Use Case | Cost |
|---|---|---|
| Standard | Frequently accessed data | $$$ |
| Standard-IA | Infrequent access (monthly) | $$ |
| Glacier | Archive (accessed rarely) | $ |
| Glacier Deep Archive | Long-term compliance archive | ¢ |

**Best practices:**
```
- Partition data by date: s3://bucket/table/year=2024/month=01/
- Use Parquet/ORC (columnar, compressed)
- Enable versioning for critical data
- Use lifecycle policies to move old data to Glacier automatically
```

**Interview Q:** *"How do you handle large file uploads to S3?"*

Use **multipart upload** for files > 100 MB. Split file into parts, upload in parallel, merge.
AWS CLI and SDK do this automatically above a threshold.

---

## 🔄 AWS Glue (Serverless ETL)

**Interview Q:** *"What is AWS Glue and when would you choose it over EMR?"*

Glue is serverless — no cluster management. You write a Spark/Python script, Glue runs it.

**Components:**
```
Glue Data Catalog  → Metadata store (tables, schemas, partitions). Like a Hive metastore.
                     Athena, EMR, Redshift Spectrum all query from here.

Glue Crawler       → Auto-discovers schema from S3/RDS and registers in the Catalog.
                     Runs on schedule or on-demand.

Glue ETL Jobs      → PySpark or Python Shell scripts. Serverless execution.
                     No cluster to manage — pay per DPU-hour.

Glue Workflow      → Chain multiple Glue jobs + crawlers with dependencies.

DynamicFrame       → Glue's version of a Spark DataFrame.
                     Tolerates schema inconsistencies ("flexible schema").
```

**When to use Glue vs EMR:**
| Factor | Glue | EMR |
|---|---|---|
| Management | Serverless (zero setup) | Self-managed cluster |
| Cost | Pay per job | Pay for idle cluster too |
| Customization | Limited | Full Spark/Hadoop control |
| Use case | Simple ETL, ad-hoc | Complex pipelines, cost at scale |

**Sample Glue ETL job:**
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read from catalog
dyf = glueContext.create_dynamic_frame.from_catalog(
    database="my_db",
    table_name="raw_sales"
)

# Convert to DataFrame for transformations
df = dyf.toDF()
df_clean = df.dropna().filter("amount > 0")

# Write back to S3
glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrameCollection(df_clean, glueContext),
    connection_type="s3",
    connection_options={"path": "s3://my-bucket/processed/sales/"},
    format="parquet"
)
```

---

## ⚡ Amazon Kinesis (Real-Time Streaming)

**Interview Q:** *"How does Kinesis work? Compare it to Kafka."*

Kinesis is AWS's managed streaming service. Three main services:

| Service | Purpose |
|---|---|
| **Kinesis Data Streams** | Real-time event ingestion (like Kafka topics) |
| **Kinesis Firehose** | Managed delivery to S3/Redshift/Elasticsearch (no code) |
| **Kinesis Analytics** | SQL or Apache Flink on streaming data |

**Core Kinesis Concepts:**
```
Stream      → named channel for records (like a Kafka topic)
Shard       → basic throughput unit (1 MB/s write, 2 MB/s read)
Producer    → sends records to the stream (apps, IoT, logs)
Consumer    → reads from the stream (Lambda, Kinesis Analytics, custom apps)
Partition key → determines which shard a record goes to (affects ordering)
Retention   → default 24h, max 7 days (vs Kafka's configurable unlimited)
```

**Kinesis vs Kafka:**
| Feature | Kinesis | Kafka (MSK) |
|---|---|---|
| Management | Fully managed | More setup needed |
| Retention | 24h–7 days | Configurable (forever) |
| Throughput | Per-shard limits | Highly scalable |
| Cost | Pay per shard-hour | Pay for brokers |
| Ecosystem | AWS-native | Broader (Spark, Flink, etc.) |

**Interview Q:** *"When would you use Kinesis Firehose?"*

When you want zero-code delivery to S3/Redshift with optional transformation (Lambda).
No consumers to manage — fire and forget.

```
Source → Kinesis Firehose → Buffer (size/time) → S3/Redshift/Elasticsearch
```

---

## 🏛️ Amazon Redshift (Cloud Data Warehouse)

**Interview Q:** *"What is Redshift? How is it different from a regular database?"*

Redshift is a **columnar, MPP (Massively Parallel Processing)** data warehouse.

**Architecture:**
```
Leader Node   → receives SQL queries, builds execution plan, coordinates workers
Compute Nodes → each stores a slice of data, executes plan in parallel
```

**Why columnar storage for analytics:**
```
Row store (RDBMS):  reads entire row → slower for SELECT col1, col2 FROM billion_row_table
Column store:       reads ONLY col1 + col2 bytes → massive I/O reduction
```

**Key Concepts:**
```
DIST KEY    → column used to distribute rows across nodes.
              Choose a column used in many JOINs to co-locate matching rows.

SORT KEY    → column used to sort data on disk.
              WHERE on sort key → zone map skips entire blocks (like pushdown).

VACUUM      → reclaims space from deleted rows.
ANALYZE     → updates statistics for the query optimizer.
```

**Interview Q:** *"What is a distribution style in Redshift and how do you choose one?"*

| Style | Description | Use When |
|---|---|---|
| `EVEN` | Rows distributed round-robin | No clear join key, small tables |
| `KEY(col)` | Rows with same col value on same node | Large tables joined on this col |
| `ALL` | Full copy on every node | Small dimension tables |
| `AUTO` | Redshift chooses | Default, let AWS decide |

---

## 🔍 Amazon Athena (Serverless SQL on S3)

**Interview Q:** *"What is Athena and when do you use it over Redshift?"*

Athena = serverless SQL engine. You write SQL, Athena reads data directly from S3. Pay per query (per TB scanned).

```sql
-- Query S3 data directly via Athena
SELECT year, month, SUM(amount) AS total
FROM "my_db"."raw_sales"
WHERE year = 2024
GROUP BY year, month
ORDER BY month;
```

| Feature | Athena | Redshift |
|---|---|---|
| Setup | Zero | Cluster needed |
| Cost | Per-TB scanned | Per-node-hour |
| Speed | Slower (S3 I/O) | Faster (in-memory) |
| Concurrency | High | Limited |
| Use Case | Ad-hoc queries on S3 | Regular BI, dashboards |

**Cost optimization tips:**
- Use Parquet/ORC (columnar) — 10-100x less data scanned
- Partition data (WHERE partition_col = '...' only scans that folder)
- Compress files (snappy/zstd)

---

## 🔷 AWS Lambda (Serverless Functions)

**Interview Q:** *"Where does Lambda fit in a data pipeline?"*

Lambda runs code without managing servers. In data pipelines:
- Trigger ETL job when file lands in S3
- Light transformations on Kinesis Firehose records
- Data quality checks on incoming records
- API endpoints that query data

**Limits to know:**
- Max execution time: 15 minutes
- Max memory: 10 GB
- Not for heavy Spark jobs (use Glue/EMR)

---

## 🔧 AWS Step Functions (Pipeline Orchestration)

**Interview Q:** *"How do you orchestrate multi-step data pipelines on AWS?"*

Step Functions coordinate multiple services into a workflow (like Airflow but AWS-native):
```
Start → Glue Crawler → Lambda (data quality check) → Glue ETL → Redshift Copy → End
```

Each step can have retry logic, error handling, and conditional branching.

---

## 🗂️ AWS DMS (Database Migration Service)

**Interview Q:** *"How do you migrate a production database to AWS with minimal downtime?"*

DMS supports **full load + CDC (Change Data Capture)**:
1. Full load: copies all existing data
2. CDC: continuously captures inserts/updates/deletes from transaction logs
3. Keeps source and target in sync during migration
4. Cutover when ready

Source support: Oracle, SQL Server, MySQL, PostgreSQL, MongoDB
Target support: Redshift, S3, RDS, Aurora

---

## ❓ Top 10 AWS Interview Questions

**Q1: Explain the architecture of a typical AWS data lakehouse.**
```
Raw Zone (S3)    → Glue Crawler → Glue Catalog (schema)
                                ↓
                   Glue ETL → Processed Zone (S3 Parquet)
                                ↓
                   Athena (ad-hoc) / Redshift Spectrum (BI)
```

**Q2: What is S3 Select?**
Retrieve only needed data from S3 objects using SQL expressions. Instead of downloading the whole file, filter at the S3 level. Reduces cost and transfer time.

**Q3: How do you handle schema evolution in a Glue catalog?**
Crawlers detect schema changes. For evolution (adding columns), use `mergeSchema=True` in Spark reads. For incompatible changes, version the table or create a new one.

**Q4: What is the difference between Kinesis Streams and Firehose?**
Streams: you write consumers, manage checkpointing, control processing. Firehose: fully managed delivery to destinations, no consumer code needed. Streams for custom processing, Firehose for simple delivery.

**Q5: How do you optimize cost in Athena?**
Partition data, use columnar formats (Parquet/ORC), compress files, limit SELECT columns.

**Q6: What is Redshift Spectrum?**
Query S3 data directly from Redshift SQL (without loading into Redshift). Useful for joining Redshift tables with cold data in S3.

**Q7: How does Glue handle schema mismatches (e.g., a CSV with inconsistent columns)?**
DynamicFrame's `resolveChoice()` handles type conflicts. Or use `errorsAsDynamicFrame()` to route bad records separately.

**Q8: What is an EMR cluster? When would you use EMR over Glue?**
EMR is a managed cluster running Hadoop/Spark/Hive. Use EMR for: complex Spark pipelines, custom configurations, large-scale processing where hourly cluster cost < Glue DPU cost.

**Q9: How do you trigger a Glue job when a file lands in S3?**
S3 Event Notification → Lambda → start Glue job via `boto3.client('glue').start_job_run()`. Or use S3 Event Notifications with EventBridge + Step Functions.

**Q10: What is the CAP theorem and how does it apply to choosing AWS data stores?**
Consistency, Availability, Partition Tolerance — you can only have two.
- DynamoDB: AP (available, partition tolerant) — eventual consistency by default
- RDS/Aurora: CP (consistent, partition tolerant) — sacrifices availability on partition
- Redshift: CA (consistent, available) — no partition tolerance (single AZ)
