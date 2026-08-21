"""
PRODUCTION TROUBLESHOOTING FOR DATA ENGINEERS
Real Production Issues + Debugging + Root Cause Analysis

Interview Weight: ⭐⭐⭐⭐⭐ at senior levels (2+ years experience)
Target: Demonstrate production maturity and debugging skills

This handbook covers:
1. Common production failures
2. Debugging methodologies
3. Root cause analysis (5 Whys)
4. Incident response templates
5. Preventive patterns
"""

# ============================================================================
# CASE STUDY 1: SPARK JOB HANGING (STUCK FOR HOURS)
# ============================================================================

"""
INCIDENT REPORT:
Date: 2024-07-15 02:30 AM
Duration: 3.5 hours before manual kill
Pipeline: Customer Revenue Aggregation (daily)
Impact: Dashboard stale, 12 hour delay

INITIAL SYMPTOMS:
- Spark job status: RUNNING
- Logs: Stopped after stage 500, waiting for reducer task 12345
- Cluster: 32 nodes, all have load <10%
- Storage: S3 accessible, no network errors

INVESTIGATION STEPS:

Step 1: Check Spark UI
- Go to http://spark-driver:4040
- Look at "Stages" tab → Find stuck stage
- Stage 500: 5000 tasks, 4999 completed, 1 stuck
- Stuck task: Partition 1234, on executor 25

Step 2: Check Task Distribution
- Stage 500 is a shuffle (SortByKey operation)
- Partition 1234: 8.5 GB data (others: 100-200 MB)
- ROOT CAUSE: Severe data skew!

Step 3: Identify Skew
- Partition key: user_id = "anonymous_user" (default for logged-out users)
- 50% of events have this key
- Solution: Add random salt

RESOLUTION:
Before:
  df = events.groupBy("user_id").agg(sum("amount"))

After (with salt):
  from pyspark.sql import functions as F
  
  salt = F.when(df.user_id == "anonymous_user", 
                 F.rand() % 100).otherwise(0)
  
  salted_key = F.concat(F.col("user_id"), F.lit("_"), salt)
  
  df_salted = events.groupBy(salted_key).agg(sum("amount"))
  df_final = df_salted.groupBy("user_id").agg(sum("amount"))
  
  # Time: 3 hours → 8 minutes (22x improvement!)

ROOT CAUSE ANALYSIS (5 Whys):
1. Why did stage hang? → One partition took 10x longer than others
2. Why was partition 1234 so large? → Data skew on user_id
3. Why is there skew? → Anonymous users grouped under same ID
4. Why not caught earlier? → No data profile checks before aggregation
5. Why no alerts? → No job duration monitoring per stage

PREVENTION:
1. Add data profiling:
   df.groupBy("user_id").count().orderBy("count", ascending=False).show(20)
   
2. Add stage duration monitoring:
   Stage threshold: Alert if >30 min
   
3. Add pre-processing:
   - Count distinct values of groupBy key
   - If <100 for DataFrame with 1M+ rows → likely skew
   - Add sampling check

SIMILAR ISSUES:
- Spark collecting too much to driver (collect() on large RDD)
- Cartesian product accidentally created
- Broadcast variable too large (>2GB)
"""

# ============================================================================
# CASE STUDY 2: DATA QUALITY DEGRADATION (SILENT FAILURE)
# ============================================================================

"""
INCIDENT REPORT:
Date: 2024-07-20 03:15 PM
Duration: 8 hours undetected
Pipeline: Customer Payment Processing
Impact: 15% missing transactions in reports

ALERT RECEIVED:
- dbt test failure: Null check failed on payment_method
- 5% of transactions have NULL payment_method (normally 0%)

INVESTIGATION:

Step 1: Timeline
  15:15 - Alert received
  15:30 - Last successful run was 07:00 AM
  15:45 - Check data

Step 2: Data Analysis
  SELECT COUNT(*), COUNT(DISTINCT payment_method)
  FROM payments
  WHERE DATE(created_at) = '2024-07-20'
  
  Result: 100,000 transactions, 10,000 have NULL payment_method
  
  SELECT payment_method, COUNT(*)
  FROM payments
  WHERE DATE(created_at) = '2024-07-20'
  AND payment_method IS NULL
  
  Result: All NULL entries have transaction_source = "mobile_web_v3"

Step 3: Root Cause
  Mobile Web v3 app deployed at 07:05 AM
  NEW CODE: Forgot to pass payment_method to backend API
  Payment table INSERT: No default value for payment_method
  Result: NULL inserted into DB

Step 4: Timeline of Issues
  07:05 - Code deployed
  07:10 - App starts making requests (1000/min)
  07:15 - NULLs start appearing in database
  15:15 - dbt test runs (8 hours later), catches it

RESOLUTION:

Immediate (Manual Fix):
  UPDATE payments
  SET payment_method = 'unknown'
  WHERE payment_method IS NULL
  AND DATE(created_at) = '2024-07-20'
  AND transaction_source = 'mobile_web_v3'
  
  -- Notify analytics: report has 10K transactions marked "unknown"

Root Fix:
  1. Hotfix code: Default payment_method = 'unknown' if missing
  2. Add NOT NULL constraint in schema (catch at insert time)
  3. Add stronger dbt tests with alert severity

ROOT CAUSE ANALYSIS (5 Whys):
1. Why NULL values? → Code didn't pass payment_method
2. Why did code break? → No unit test for API response
3. Why wasn't caught at deployment? → No integration test before production
4. Why 8-hour delay? → dbt tests run on schedule, not real-time
5. Why no real-time alerts? → Alert only on daily aggregation, not source table

PREVENTION:
1. Add real-time schema validation:
   ┌────────────────────────────────────┐
   │ Kafka → Schema Registry            │
   │ - Validates every message          │
   │ - Blocks incompatible schema       │
   │ - Dev: Test before deploy          │
   └────────────────────────────────────┘

2. Add pre-insert validation (PySpark):
   def validate_payment(row):
       assert row.payment_method is not None, "payment_method required"
       assert row.amount > 0, "amount must be positive"
       return row
   
   df = spark.read.kafka(...)
   df_validated = df.map(validate_payment)

3. Add continuous dbt tests:
   - Run every 30 minutes (not daily)
   - Alert on first test failure (not after 8 hours)
   - Integrate with Slack webhook

4. Add canary deployments:
   - Route 1% of traffic to new code
   - If error rate increases >5%, rollback automatically
   - Monitor for 15 minutes before full rollout

MONITORING:
  - Freshness: Alert if data not updated in 5 min
  - Completeness: Alert if NULL count > threshold
  - Accuracy: Compare aggregates with yesterday ±10%
  - Timeliness: dbt tests run every 30 min, not once daily
"""

# ============================================================================
# CASE STUDY 3: MEMORY LEAK IN SPARK STREAMING JOB
# ============================================================================

"""
INCIDENT REPORT:
Date: 2024-07-25
Duration: Gradual degradation over 5 days
Pipeline: Real-time Event Processing
Symptom: Job gets slower each hour, eventually crashes with OutOfMemory

METRICS BEFORE CRASH:
- Hour 1: Throughput = 100K events/sec, Latency = 2 sec
- Hour 12: Throughput = 50K events/sec, Latency = 60 sec (12x slower!)
- Hour 24: OutOfMemory error, job crashes

INVESTIGATION:

Step 1: Check Memory Usage
  - Driver memory: Stable at 2GB
  - Executor memory: Started at 4GB, now at 14GB (almost OOM at 16GB limit)
  - GC time: Increased from 5% to 45%

Step 2: Check Heap Dump
  jmap -dump:live,format=b,file=heap.bin <pid>
  
  Analysis shows:
  - HashMap with 50M entries
  - Entries not being garbage collected
  - Keys are UUID strings (should have expired)

Step 3: Find Code
  ```python
  # Spark Streaming job (runs every 5 minutes)
  
  CACHE = {}  # Global dictionary
  
  def process_batch(df):
      for row in df.collect():
          uuid = row.event_id
          CACHE[uuid] = row  # Adding to cache
          # NO REMOVAL!
          
      result = df.groupBy("user_id").count()
      return result
  
  streamingDF.foreachBatch(process_batch)
  ```

ROOT CAUSE:
- CACHE dictionary grows unbounded
- No TTL or eviction policy
- After 5 days: 50M entries × 1KB = 50GB attempted memory usage

RESOLUTION:

Fix 1: Add TTL to Cache
  import time
  from functools import lru_cache
  
  # Use LRU Cache with max size
  @lru_cache(maxsize=1_000_000)
  def get_cached(uuid):
      return CACHE.get(uuid)
  
  def process_batch(df):
      for row in df.collect():
          uuid = row.event_id
          # Only cache if not already cached
          if uuid not in CACHE and len(CACHE) < 100_000:
              CACHE[uuid] = row
      
      result = df.groupBy("user_id").count()
      return result

Fix 2: Use Redis instead of memory
  import redis
  
  r = redis.Redis(host='localhost', port=6379)
  
  def process_batch(df):
      for row in df.collect():
          uuid = row.event_id
          r.setex(uuid, 3600, row.to_json())  # 1-hour TTL
      
      result = df.groupBy("user_id").count()
      return result

ROOT CAUSE ANALYSIS:
1. Why OutOfMemory? → Cache grows without bounds
2. Why cache added? → Developer wanted to deduplicate events
3. Why not evicted? → No TTL or size limit implementation
4. Why not caught in testing? → Load test ran for 1 hour, not 5 days
5. Why no monitoring? → Memory not tracked per streaming batch

PREVENTION:
1. Streaming-specific monitoring:
   - Memory per partition/batch (not just cluster-wide)
   - Task count (if increasing, memory leak likely)
   - GC frequency (if increasing, heap pressure)

2. Code review patterns:
   - Flag global dictionaries/variables
   - Flag code without eviction policy
   - Flag .collect() in streaming (use aggregate instead)

3. Deployment checklist:
   - Run smoke test for 24 hours before production
   - Set memory monitoring alerts
   - Set maximum cache sizes

LESSONS:
- Streaming ≠ Batch: Long-running processes need cleanup
- Memory management critical for HA pipelines
- Always implement TTL for caches
- Monitor GC time, not just heap size
"""

# ============================================================================
# CASE STUDY 4: SCHEMA EVOLUTION BREAKS PIPELINE
# ============================================================================

"""
INCIDENT REPORT:
Date: 2024-08-05
Duration: 30 minutes
Pipeline: Customer Data Warehouse
Issue: New column added, but downstream code breaks

TIMELINE:
14:30 - DBA adds new column to source table: customer.credit_limit
14:32 - Spark ETL job processes data
14:35 - Parquet file written to Delta table
14:37 - Dashboard query fails: "credit_limit column not recognized"
14:50 - Issue escalated to data team
15:00 - Root cause found, fix deployed

ROOT CAUSE:
```python
# Spark job with hardcoded schema
schema = StructType([
    StructField("customer_id", IntegerType()),
    StructField("name", StringType()),
    StructField("email", StringType()),
    # NO credit_limit field!
])

df = spark.read.schema(schema).parquet("s3://data/customers")
# New credit_limit column DROPPED during read because not in schema!
```

SOLUTION 1: Schema-on-read (flexible)
```python
# Don't hardcode schema
df = spark.read.option("mergeSchema", "true").parquet("s3://data/customers")
# Automatically infers schema from data

# Or use Auto-schema evolution
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
df = spark.read.table("customers")
```

SOLUTION 2: Schema Registry (strict)
```python
# Use Confluent Schema Registry
client = SchemaRegistryClient(url="http://schema-registry:8081")

# Consumer validates against registered schema
reader = AvroReader(schema_registry_url=..., subject="customer-value")
df = spark.readStream.format("kafka").option(...).load()
```

SOLUTION 3: Backward Compatibility (defensive)
```python
# Add new columns to downstream references gradually
def safe_read(path):
    df = spark.read.parquet(path)
    
    # Add missing columns with default values
    expected_cols = ["customer_id", "name", "email", "credit_limit"]
    for col in expected_cols:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None))
    
    return df.select(expected_cols)
```

PREVENTION:
1. Centralized data dictionary:
   - Document all columns and expected types
   - Track when columns added/removed
   - Notify consumers of schema changes

2. Backward compatibility:
   - New columns should have default values
   - Don't remove columns (deprecate instead)
   - Version schemas explicitly

3. Testing:
   - Test with multiple schema versions
   - Integration tests before deploying schema changes
   - Canary: Deploy to 1% of consumers first

MONITORING:
- Alert if schema changes detected
- Track schema version usage
- Alert if consumers reading from old schema version
"""

# ============================================================================
# TROUBLESHOOTING FRAMEWORKS
# ============================================================================

"""
INCIDENT RESPONSE CHECKLIST:

DETECTION (Alert received):
☐ What happened? (specific error message)
☐ When? (exact timestamp)
☐ Where? (which system/pipeline)
☐ Who? (on call engineer, team)

ASSESSMENT (Understand impact):
☐ Severity: Critical/High/Medium/Low
☐ Users affected: Number of users, services
☐ Data impact: Missing/incorrect/delayed data
☐ Revenue impact: Estimated loss

MITIGATION (Stop the bleeding):
☐ Kill the job / Stop the pipeline
☐ Revert recent changes if applicable
☐ Start manual workaround if available
☐ Notify stakeholders of ETA for fix

ROOT CAUSE ANALYSIS (5 Whys):
☐ What is the immediate cause?
☐ Why did that happen?
☐ Why wasn't it caught before?
☐ Why does prevention exist?
☐ What permanent fix?

RESOLUTION:
☐ Implement permanent fix
☐ Validate fix with tests
☐ Deploy to production
☐ Monitor for recurrence

POSTMORTEM:
☐ Timeline (what, when, by whom)
☐ Root cause (full analysis)
☐ Impact (users, revenue, data)
☐ Resolution (what was done)
☐ Prevention (how to avoid)
☐ Assigned action items

DEBUGGING DECISION TREE:
```
Is there data?
├─ YES → Is it correct?
│   ├─ YES → Is it fresh?
│   │   ├─ YES → Problem solved ✅
│   │   └─ NO → Check freshness monitoring
│   └─ NO → Check data quality / validation rules
└─ NO → Is pipeline running?
    ├─ YES → Check if stuck (Spark UI)
    │   ├─ YES → Check for data skew or resource limits
    │   └─ NO → Check network / storage
    └─ NO → Check for errors in logs
        ├─ Error message → Search KB / error docs
        └─ No error → Check monitoring dashboards
```

KEY METRICS TO MONITOR:
- Pipeline status (succeeded/failed)
- Data freshness (max(updated_at) - now())
- Data completeness (row count, not null rate)
- Data accuracy (reconciliation with source)
- Latency (p50, p95, p99)
- Throughput (events/sec, rows/sec)
- Resource utilization (CPU, memory, disk, network)
- Cost (compute cost, storage cost, transfer cost)
- Incidents (count per week)

ALERT THRESHOLDS:
- Data freshness: > 2 hours → Alert
- Row count change: > 20% day-over-day → Alert
- NULL rate: > 5% → Alert
- Query latency p99: > 1 second → Alert
- Job duration: > 2x historical average → Alert
- Kafka lag: > 100,000 events → Alert
"""

print("✅ Production Troubleshooting Handbook Loaded")
print("✅ 4 real case studies with resolution strategies ready")
print("✅ Incident response templates included")
