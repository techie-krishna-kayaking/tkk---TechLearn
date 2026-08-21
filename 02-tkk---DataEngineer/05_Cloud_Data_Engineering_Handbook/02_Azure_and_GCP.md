# Chapter 2: Azure & GCP for Data Engineering

---

## ☁️ Azure Data Engineering Stack

```
INGEST           →   STORE           →   PROCESS          →   SERVE
──────────────────────────────────────────────────────────────────────
Event Hubs           ADLS Gen2            Azure Databricks     Synapse SQL
IoT Hub              Azure Blob           Azure Data Factory   Power BI
Data Factory         Azure SQL DB         HDInsight (Hadoop)   Synapse Analytics
```

### ADLS Gen2 (Azure Data Lake Storage Gen2)

The Azure equivalent of S3. Built on top of Azure Blob Storage with:
- Hierarchical namespace (true folder structure, not just key prefixes)
- POSIX-compatible ACLs (fine-grained permission per file/folder)
- Protocol: `abfss://container@account.dfs.core.windows.net/path`

**Interview Q:** *"ADLS Gen1 vs Gen2 — what changed?"*
Gen2 = Gen1 features (hierarchical namespace, POSIX ACL) + Blob Storage (unlimited scale, lifecycle management). Gen2 is the current standard.

---

### Azure Data Factory (ADF)

The managed ETL/orchestration service. Think: GUI-based Airflow + Glue combined.

**Key components:**
```
Pipeline     → workflow of activities
Activity     → single step (Copy Data, Databricks Notebook, Stored Procedure)
Dataset      → pointer to data (what to read/write)
Linked Service → connection to a data source (like a connection string)
Trigger      → when to run (schedule, tumbling window, event-based)
```

**Interview Q:** *"When would you use ADF over Databricks for ETL?"*
- ADF: drag-and-drop, no-code/low-code ETL, works well for simple data copies and orchestration
- Databricks: complex transformations, large-scale Spark, ML integration

---

### Azure Synapse Analytics

Microsoft's integrated analytics platform (SQL + Spark in one workspace).

```
Synapse SQL Pool      → dedicated SQL data warehouse (like Redshift)
                        MPP, columnar, great for BI workloads
Synapse Serverless SQL→ query ADLS directly with SQL (like Athena)
                        pay per TB scanned
Synapse Spark Pool    → managed Spark cluster (like Databricks, but simpler)
Synapse Pipelines     → ADF embedded in Synapse (same code, same UI)
```

**Interview Q:** *"Synapse vs Databricks — when to use each?"*
| Factor | Synapse | Databricks |
|---|---|---|
| SQL Warehouse | Native, MPP | Via Delta + SQL |
| ML/MLflow | Limited | Best-in-class |
| Spark | Adequate | Best-in-class |
| Integration | Azure-native | Multi-cloud |

---

### Azure Event Hubs

Managed event streaming (like Kinesis / Kafka-compatible).

- **Partitions** → units of parallelism (like Kafka partitions, Kinesis shards)
- **Consumer groups** → independent readers of the same partition
- **Capture** → automatically archive to ADLS/Blob (like Kinesis Firehose)
- **Kafka protocol** → Event Hubs is Kafka-compatible (can use Kafka clients)

---

## 🌐 GCP Data Engineering Stack

```
INGEST          →   STORE       →   PROCESS        →   SERVE
────────────────────────────────────────────────────────────────
Pub/Sub              GCS              Dataflow           BigQuery
Datastream           BigQuery         Dataproc           Looker
Cloud Composer       Cloud SQL        Cloud Functions    Data Studio
```

### BigQuery (BQ)

**Interview Q:** *"What makes BigQuery different from traditional warehouses?"*

BigQuery is a fully managed, serverless data warehouse:
- **Columnar storage** on Google's Capacitor format (proprietary Parquet-like)
- **Dremel engine**: massively parallel SQL execution
- **Serverless**: no cluster to provision — query in seconds
- **Separation of storage and compute**: storage in Colossus, compute on demand
- **Auto-scaling**: scales to petabytes without manual tuning
- **Pay per query**: $5 per TB scanned (or flat rate)

**Key BigQuery features:**
```sql
-- Partitioning (like Hive/S3 partitions)
CREATE TABLE project.dataset.events
PARTITION BY DATE(event_date)
AS SELECT * FROM raw_events;

-- Clustering (sort within partitions for pruning)
CREATE TABLE project.dataset.events
PARTITION BY DATE(event_date)
CLUSTER BY user_id, event_type
AS SELECT * FROM raw_events;

-- Time travel (like Delta Lake)
SELECT * FROM project.dataset.events
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);

-- Streaming inserts
INSERT INTO project.dataset.events VALUES (...)  -- near real-time availability
```

**Interview Q:** *"What is the difference between partitioning and clustering in BigQuery?"*
- **Partitioning**: divides the table into separate physical segments by a column (date, integer range). Queries with a WHERE on that column scan fewer partitions.
- **Clustering**: within each partition (or in a non-partitioned table), sorts rows by 1-4 columns. Block pruning skips entire blocks that can't match the filter.
- Together: partition + cluster = maximum query efficiency.

---

### Google Cloud Storage (GCS)

The GCP equivalent of S3 / ADLS. Protocol: `gs://bucket-name/prefix/object`.

**Storage classes:**
```
Standard  → hot data, frequently accessed
Nearline  → accessed < once/month
Coldline  → accessed < once/quarter
Archive   → accessed < once/year (cheapest, retrieval fee)
```

---

### Pub/Sub (Event Streaming)

GCP's managed pub/sub messaging (like Kinesis/Kafka):
```
Publisher  → sends messages to a topic
Topic      → named channel
Subscription → named consumer group that pulls from a topic
Push/Pull  → delivery modes (push = HTTP endpoint, pull = consumer polls)
```

**Interview Q:** *"Pub/Sub vs Kafka?"*
Pub/Sub: fully managed, serverless, global. Kafka: more control, larger ecosystem, on-prem possible. Pub/Sub has no ordering guarantees within a partition (unlike Kafka).

---

### Cloud Dataflow (Apache Beam)

Managed Apache Beam runner for both batch AND stream processing:
- Same code works for batch and streaming (unified model)
- Auto-scaling, no cluster management
- Integrates with Pub/Sub, GCS, BigQuery natively

```python
import apache_beam as beam

with beam.Pipeline() as p:
    (p
     | 'Read' >> beam.io.ReadFromText('gs://bucket/input.csv')
     | 'Parse' >> beam.Map(lambda line: line.split(','))
     | 'Filter' >> beam.Filter(lambda row: int(row[2]) > 100)
     | 'Write' >> beam.io.WriteToBigQuery('project:dataset.table')
    )
```

---

### Cloud Dataproc (Managed Hadoop/Spark)

GCP's equivalent of EMR — managed Spark/Hadoop clusters.

---

### Cloud Composer (Managed Airflow)

Fully managed Apache Airflow on GCP. You write the same DAGs, GCP manages the infrastructure.

---

## ❓ Top Cloud Interview Questions (Cross-Cloud)

**Q1: What is the shared responsibility model in cloud?**
Cloud provider manages hardware, network, physical security, hypervisor.
Customer manages data, applications, access controls, encryption.

**Q2: What is a data lakehouse and how does it differ from a data lake and warehouse?**
- Data lake: raw storage (S3/ADLS/GCS), schema on read, cheap, flexible
- Data warehouse: processed, structured, optimized for BI (Redshift/Synapse/BigQuery)
- Data lakehouse: combines both — open format storage (Parquet/Delta) with warehouse-like transactions, schema enforcement, BI performance

**Q3: How do you handle PII data in a cloud data pipeline?**
- Encrypt at rest (S3-SSE, ADLS encryption) and in transit (TLS)
- Column-level encryption or tokenization for sensitive fields
- Role-based access control (IAM) — least privilege
- Data masking in downstream serving layers
- Audit logs for all access
- Compliance: GDPR, CCPA, PDPA (India)

**Q4: What is infrastructure as code and why does it matter for data engineers?**
Tools like Terraform, AWS CDK, Pulumi define cloud resources as code (version controlled, repeatable, reviewable). A data engineer should be able to provision S3 buckets, Glue jobs, IAM roles with Terraform.

**Q5: How do you monitor a cloud data pipeline?**
- CloudWatch (AWS) / Azure Monitor / GCP Cloud Monitoring for metrics + alerts
- Log aggregation (CloudWatch Logs / Log Analytics / Cloud Logging)
- Custom business metrics (data quality, row counts, SLA breach alerts)
- Pipeline-level: Airflow task status, Glue job metrics, Dataflow latency
