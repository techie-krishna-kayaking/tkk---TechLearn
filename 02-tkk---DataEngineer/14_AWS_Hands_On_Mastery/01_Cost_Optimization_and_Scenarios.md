"""
AWS HANDS-ON MASTERY FOR DATA ENGINEERS
Cost Optimization + Real Scenarios + Architecture Decisions

Target: Deep AWS knowledge for 70-80 LPA roles
Format: Concept → Decision point → Cost comparison → Real example

This handbook covers:
1. S3 strategy (storage classes, lifecycle, costs)
2. Glue ETL (serverless transformation)
3. Redshift (data warehouse at scale)
4. Athena (serverless SQL on S3)
5. Cost optimization techniques
6. Production troubleshooting
"""

# ============================================================================
# SECTION 1: S3 STRATEGY & COST OPTIMIZATION
# ============================================================================

"""
SCENARIO: Store 1 PB (1000 TB) of historical data, 100 TB/month growing

DECISION POINT 1: Which storage class?
┌────────────────┬────────────┬──────────────┬─────────────────┐
│ Class          │ Cost/GB/mo │ Retrieval    │ Minimum Duration│
├────────────────┼────────────┼──────────────┼─────────────────┤
│ S3 Standard    │ $0.023     │ Immediate    │ None            │
│ S3-IA          │ $0.0125    │ 3+ seconds   │ 30 days         │
│ S3 Glacier Flex│ $0.004     │ 3-12 hours   │ 90 days         │
│ S3 Glacier Deep│ $0.00099   │ 12+ hours    │ 180 days        │
└────────────────┴────────────┴──────────────┴─────────────────┘

COST CALCULATION for 1 PB:
- Current (all Standard): 1000 TB × $0.023 = $23,000/month
- With tiering (below): ~$8,000/month (65% savings!)

OPTIMAL STRATEGY (Intelligent Tiering):
- Last 30 days: S3 Standard (frequent queries)
  └─ 100 TB × $0.023 = $2,300/month
  
- 31-90 days: S3-IA (occasional queries)
  └─ 200 TB × $0.0125 = $2,500/month
  
- 91+ days: S3 Glacier Flex (rare queries, backups)
  └─ 700 TB × $0.004 = $2,800/month
  
- TOTAL: $7,600/month (instead of $23,000)

IMPLEMENTATION (Lifecycle Policy):
```json
{
  "Rules": [
    {
      "Id": "Archive old data",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 2555  // Delete after 7 years
      }
    }
  ]
}
```

PARTITION STRATEGY for Analytics:
S3://data-lake/table_name/
  ├── year=2024/
  │   ├── month=01/
  │   │   ├── day=01/
  │   │   │   ├── part-00001.parquet
  │   │   │   ├── part-00002.parquet
  │   │   └── day=02/
  │   ├── month=02/
  └── year=2023/

Benefits:
- Prune at query time (Athena: "SELECT * WHERE year=2024 AND month=08")
- Parallel reads (1000+ files read simultaneously)
- Better compression (homogeneous data per partition)

COST IMPACT:
- Query cost: $5/TB scanned (Athena pricing)
- With partitioning: Scan 10 GB instead of 1 TB (100x reduction)
- Monthly query cost: $5 (instead of $500)

REAL EXAMPLE: Netflix-style setup
- Kafka → Kinesis Firehose → S3 (raw layer, 5 min batches)
- Lambda → Transform → S3 (silver layer, 1 hour)
- Athena/Glue → Redshift (gold layer, daily)
- Cost: $5K/month (vs $50K with single layer all Standard)

COMMON MISTAKES:
1. Using S3 Standard for everything ("it's cheaper than I thought")
   Problem: Archive data old 2+ years still costs $0.023/GB
   Solution: Apply lifecycle policies

2. Not partitioning data
   Problem: Every query scans entire dataset (billions of files)
   Solution: Partition by date at minimum

3. Storing too many small files (millions of objects)
   Problem: S3 LIST operations slow, more API calls
   Solution: Use Hadoop small files consolidation or EMRFS

4. Versioning enabled unnecessarily
   Problem: All old versions stored indefinitely
   Solution: Only enable for production tables
"""

# ============================================================================
# SECTION 2: GLUE ETL - WHEN & HOW
# ============================================================================

"""
SCENARIO: Ingest data from 50 source databases daily

OPTIONS:
1. AWS Glue: Serverless, scales automatically
2. Self-managed Spark on EC2: Cheaper, more control
3. Lambda: Good for small transforms (<15 min)
4. EMR: Good for heavy compute (ML, complex aggregations)

COMPARISON:
┌────────────────┬────────────────┬────────────────┬──────────────────┐
│ Tool           │ Cost Model     │ Scaling        │ Best For         │
├────────────────┼────────────────┼────────────────┼──────────────────┤
│ Glue           │ DPU-hours      │ Auto           │ Variable workload │
│ EC2 Spark      │ Instance/hour  │ Manual         │ Steady workload   │
│ Lambda         │ GB-seconds     │ Auto           │ <15min jobs       │
│ EMR            │ Node/hour      │ Manual/Auto    │ Heavy compute     │
└────────────────┴────────────────┴────────────────┴──────────────────┘

GLUE COST CALCULATION:
- DPU (Data Processing Unit) = 4 vCPU + 16 GB RAM
- Cost: $0.44 per DPU-hour
- Job: 50 databases × 10 GB each = 500 GB data
- Processing time: 30 minutes with 10 DPUs
- Cost: 10 DPU × 0.5 hours × $0.44 = $2.20 per day = $66/month

When Glue makes sense:
- Variable workload (some days 1 hour, others 5 hours)
- Don't want to manage infrastructure
- Need integration with Glue Catalog (metadata)

GLUE JOB EXAMPLE (PySpark):
```python
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read from S3
dyf = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={"paths": ["s3://my-bucket/input/"]},
    transformation_ctx="dyf"
)

# Transform
df = dyf.toDF()
df_transformed = df.filter(col("age") > 18).withColumn("year", year(col("date")))

# Write to S3
glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(df_transformed, glueContext, "output"),
    connection_type="s3",
    format="parquet",
    connection_options={"path": "s3://my-bucket/output/"},
    transformation_ctx="output"
)

job.commit()
```

GLUE CATALOG BENEFITS:
- Metadata repository for all tables
- Schema versioning
- Partition indexes (faster queries)
- Integration with Athena/Redshift/Spark

Cost: $1 per 100,000 metadata objects (usually negligible)
"""

# ============================================================================
# SECTION 3: REDSHIFT - DATA WAREHOUSE AT SCALE
# ============================================================================

"""
SCENARIO: Query 500 GB daily aggregated data for dashboards

REDSHIFT SIZING:
┌──────────────┬────────────┬────────────────┬─────────────────┐
│ Node Type    │ vCPU/Mem   │ Storage        │ Cost/month      │
├──────────────┼────────────┼────────────────┼─────────────────┤
│ dc2.large    │ 2/16GB     │ 160 GB SSD     │ $500 (1 node)   │
│ dc2.xlarge   │ 4/32GB     │ 2 TB SSD       │ $1000 (1 node)  │
│ ra3.xlplus   │ 4/32GB     │ 32 TB managed  │ $1200 (1 node)  │
│ ra3.4xlarge  │ 16/128GB   │ 128 TB managed │ $3500 (1 node)  │
└──────────────┴────────────┴────────────────┴─────────────────┘

STRATEGY: Start small, scale as needed
- 500 GB data initially: 1x ra3.xlplus ($1,200/month)
- With 3x replication reserve: Need 1.5 TB usable space
- Redshift provides: 32 TB per node (plenty of headroom)

COST BREAKDOWN (1 node):
- Compute: $1,200/month
- Backups (automated, 1 day retention): Free
- Data transfer: 
  * To S3 (same region): Free
  * To EC2 (same region): Free
  * Cross-region: $0.02/GB (minimize!)
- TOTAL: $1,200/month

SORT KEY STRATEGY:
```sql
CREATE TABLE orders (
    order_id BIGINT,
    order_date DATE,
    customer_id INT,
    amount DECIMAL(10, 2),
    region VARCHAR(10)
)
SORTKEY (order_date, region);
-- Optimized for queries filtering by date range + region
```

DISTRIBUTION STRATEGY:
```sql
CREATE TABLE orders (
    order_id BIGINT,
    customer_id INT,
    amount DECIMAL(10, 2)
)
DISTKEY (customer_id);
-- Distribute by join key for efficient joins

CREATE TABLE customers (
    customer_id INT,
    name VARCHAR(100),
    region VARCHAR(10)
)
DISTSTYLE ALL;  -- Small table, replicate to all nodes
-- Join is local (no network transfer)
```

QUERY PERFORMANCE OPTIMIZATION:
1. Use EXPLAIN to check distribution
   EXPLAIN SELECT * FROM orders o JOIN customers c ON o.customer_id = c.customer_id;
   
2. Check for skew
   SELECT slice, count(*) FROM svv_diskusage GROUP BY slice ORDER BY count DESC;
   
3. Vacuum to reclaim space
   VACUUM orders;  -- Rebuild after deletes

UNLOAD FOR COST SAVINGS:
```sql
UNLOAD (SELECT * FROM orders WHERE order_date >= CURRENT_DATE - 30)
TO 's3://my-bucket/orders/recent/'
WITH (FORMAT PARQUET, COMPRESSION SNAPPY);
-- Move stale data to S3 (cheaper storage)
-- Keep only recent hot data in Redshift
```

WHEN TO USE REDSHIFT vs ALTERNATIVES:
┌────────────────┬────────────┬────────────────────┐
│ Redshift       │ Athena     │ BigQuery           │
├────────────────┼────────────┼────────────────────┤
│ Hot data: 1yr  │ Archive: 5yr│ Anything           │
│ Complex joins  │ Simple SQL │ Nested data (JSON) │
│ High throughput│ Cheap      │ Real-time         │
│ Consistency    │ Eventual   │ Strong             │
└────────────────┴────────────┴────────────────────┘
"""

# ============================================================================
# SECTION 4: ATHENA - SERVERLESS QUERIES
# ============================================================================

"""
SCENARIO: Run ad-hoc queries on data lake (S3)

COST MODEL: Pay only for data scanned
- $5 per TB scanned
- Minimum charge: 100 MB per query
- Example: Query scanning 50 GB = $0.25

ATHENA OPTIMIZATION:
1. Partition pruning (scan less data)
   SELECT COUNT(*) FROM events WHERE year=2024 AND month=08
   -- Without partitioning: Scan all 1 PB
   -- With partitioning: Scan only 10 GB
   -- Cost: $5000 vs $0.05

2. File format (compression ratio)
   - JSON: 1 MB uncompressed
   - Parquet: 100 KB (10x compression)
   - Cost: $5/TB vs $0.50/TB

3. Projection pushdown (only needed columns)
   SELECT customer_id, amount FROM orders WHERE year=2024
   -- Parquet only reads required columns
   -- Reduces I/O by 50%

QUERY EXAMPLE:
```sql
SELECT
    DATE_TRUNC('day', event_timestamp) as day,
    device_type,
    COUNT(*) as event_count,
    SUM(event_value) as total_value
FROM events
WHERE
    year = YEAR(CURRENT_DATE)
    AND month = MONTH(CURRENT_DATE)
    AND day >= CAST(DAY(CURRENT_DATE) - 30 AS VARCHAR)
GROUP BY 1, 2
ORDER BY day DESC, event_count DESC;
```

WORKGROUP CONFIGURATION:
```sql
CREATE WORKGROUP dev_queries AS (
    RESULT_CONFIGURATION 's3://my-bucket/athena-results/',
    ENFORCE_WORKGROUP_CONFIG true,
    PUBLISH_CLOUDWATCH_METRICS_ENABLED true,
    BYTES_SCANNED_CUTOFF_PER_QUERY 1000000000  -- 1 GB max per query
);
```

WHEN ATHENA SHINES:
- Ad-hoc queries (don't need dedicated cluster)
- Exploratory analysis (cheap to fail)
- Data lake queries (already in S3)
- Compliance queries (separate billing per workgroup)

WHEN TO AVOID ATHENA:
- Real-time (queries are slower)
- Complex joins (Redshift faster)
- Repeated queries (cache results in Redshift)
"""

# ============================================================================
# SECTION 5: END-TO-END AWS DATA PIPELINE
# ============================================================================

"""
ARCHITECTURE: Real-time e-commerce analytics

Flow:
1. Order placed in website
2. RDS update → Debezium CDC → Kinesis
3. Kinesis → Lambda (transform) → S3 (raw)
4. S3 (raw) → Glue Spark job → S3 (processed)
5. S3 (processed) → Glue Crawler (update catalog)
6. Athena / Redshift query → Dashboard

COST BREAKDOWN (Daily):
- Kinesis: 1000 events/sec = 86M events/day = $50
- Lambda: 86M invocations × $0.0000002 = $17
- S3 Storage: 50 GB = $1.15
- Glue: 1 hour processing × 10 DPU × $0.44 = $4.40
- Athena: 3 queries × 10 GB scanned = $0.15
- Redshift: 1 node/day (amortized) = $40
- Data transfer: 100 GB/day = $2
TOTAL/day: $114.70 (~$3,400/month)

For comparison: On-premise would cost $5-8K/month + $50K upfront

DEPLOYMENT CHECKLIST:
1. ☐ Create S3 buckets with lifecycle policies
2. ☐ Set up Kinesis stream with auto-scaling
3. ☐ Deploy Lambda function with IAM role
4. ☐ Configure Glue job with DPU size
5. ☐ Create Glue Crawler for catalog
6. ☐ Set up Redshift cluster with security group
7. ☐ Create Athena workgroups with result location
8. ☐ Set up CloudWatch alarms (lag, errors, costs)
9. ☐ Enable encryption at rest + in transit
10. ☐ Set up VPC endpoints (avoid internet gateway)

COST MONITORING:
- Set monthly budget alert: $5K
- Alert if any service > 50% of budget
- Review unused resources weekly
- Use AWS Cost Explorer to identify trends
"""

print("✅ AWS Hands-On Mastery Handbook Loaded")
print("✅ Cost optimization strategies included")
print("✅ Real scenarios and decision frameworks ready")
