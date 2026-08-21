"""
ADVANCED SYSTEM DESIGN FOR DATA ENGINEERS
Production Designs with Trade-offs, Cost Analysis, and Troubleshooting

Target: 70-80 LPA senior roles at FAANG, Databricks, Unicorns
Interview Length: 45-60 minutes per design
Format: CLARIFY → HIGH-LEVEL → DEEP DIVE → TRADE-OFFS → COST

This handbook covers:
1. Real-time analytics at massive scale
2. Multi-region disaster recovery
3. Cost optimization strategies
4. Data quality + observability
5. Production troubleshooting patterns
"""

# ============================================================================
# DESIGN 1: REAL-TIME ANALYTICS DASHBOARD (Netflix-style)
# ============================================================================

"""
PROBLEM STATEMENT:
Design a system to track real-time viewer metrics across 200M users.
- Update every 10 seconds
- Query latency: <500ms p99
- Support 100+ concurrent queries
- Geographic distribution (US, Europe, Asia)
- Historical data: keep 1 year

CLARIFICATION QUESTIONS (Interviewer checks):
Q: What metrics? A: Views, Watch time, Rewatches, Pauses, Device type, Region
Q: Real-time SLA? A: 10-30 second latency acceptable
Q: Data size? A: ~2B events/day from 200M active users
Q: Queries? A: Aggregations by region/device/content/time window

ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────┐
│ CLIENT APPS (Mobile, Web, TV)                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │ Events (user_id, content_id, action, timestamp)
                     ▼
        ┌────────────────────────────┐
        │ Event Validation + Batching│  (Kafka Producer)
        │ (Dedup, Timestamp fixing)  │
        └────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Kafka Topics (3 partitions)│
        │ - video_events             │
        │ - error_events             │
        │ - user_events              │
        └────────────────────────────┘
            │          │          │
        ┌───▼──┐   ┌───▼──┐   ┌──▼───┐
        │BATCH │   │SPEED │   │DATA  │
        │LAYER │   │LAYER │   │LAKE  │
        └───┬──┘   └──┬───┘   └──┬───┘
            │         │         │
            ▼         ▼         ▼
    ┌──────────────┐ ┌─────────────────┐ ┌────────────────────┐
    │ Spark Batch  │ │ Spark Streaming │ │ S3 + Glue Catalog  │
    │ Job (daily)  │ │ (5-min micro)   │ │ (Parquet, Delta)   │
    │ - Aggregate  │ │ - Rolling aggs  │ │                    │
    │ - SCD Type 2 │ │ - Windowing     │ │ YEAR-LONG HISTORY  │
    │ - Quality    │ │ - Late arrival  │ │                    │
    │   checks     │ │   handling      │ │                    │
    └──────┬───────┘ └────────┬────────┘ └────────────────────┘
           │                  │
           └──────────┬───────┘
                      ▼
           ┌────────────────────────┐
           │ Gold Layer Aggregates  │
           │ (Iceberg + Parquet)    │
           │                        │
           │ - Hourly aggregates    │
           │ - Daily aggregates     │
           │ - Region x Device      │
           │   x Content x Hour     │
           └────────┬───────────────┘
                    │
        ┌───────────┼──────────────┐
        │           │              │
        ▼           ▼              ▼
    ┌──────────┐ ┌────────┐ ┌────────────┐
    │ Redshift │ │ Redis  │ │ Dashboards │
    │ (Queries)│ │ Cache  │ │ (Grafana/  │
    │          │ │ (Hot   │ │  Tableau)  │
    │          │ │ data)  │ │            │
    └──────────┘ └────────┘ └────────────┘

COST BREAKDOWN (Monthly):
┌────────────────────────────────────┐
│ Component        │ Volume  │ Cost  │
├──────────────────┼─────────┼───────┤
│ Kafka (Confluent)│ 2B msgs │$12K   │
│ Spark Cluster    │ 32 vCPU │ $8K   │
│ Redshift         │ 128GB   │ $4K   │
│ Redis Cache      │ 32GB    │ $2K   │
│ S3 Storage (1yr) │ 50TB    │ $1.2K │
│ Data Transfer    │ ~1TB/d  │ $900  │
├──────────────────┼─────────┼───────┤
│ TOTAL            │         │$28.1K │
└────────────────────────────────────┘

OPTIMIZATION TECHNIQUES:
1. Deduplication: Use event_id + timestamp to filter duplicates in Kafka
2. Sampling: Store 100% for last 7 days, 10% for 8-90 days, 1% for older
3. Compression: Parquet with Snappy (50% size reduction)
4. Partitioning: By date, region to prune at query time
5. Rollups: Pre-aggregate hourly, then daily to avoid recomputation

TRADE-OFFS:
┌──────────────────────┬────────────────────────┬────────────────────┐
│ Approach             │ Pros                   │ Cons               │
├──────────────────────┼────────────────────────┼────────────────────┤
│ Batch (daily)        │ Cheap, accurate        │ 24h lag           │
│ Streaming (realtime) │ <30s latency           │ 2x cost, complex  │
│ Lambda (batch+speed) │ Best latency + cost    │ Maintenance heavy │
│ Kappa (streaming)    │ Single code path       │ Requires backfill  │
└──────────────────────┴────────────────────────┴────────────────────┘

PRODUCTION ISSUES:
1. Late data: Events arriving 2 days late (device syncs at night)
   Solution: Watermark with 48h tolerance, replay on late arrival

2. Duplicate events: Same event sent multiple times by app
   Solution: Kafka idempotent producer, dedup by event_id before aggregation

3. Schema changes: New events fields added over time
   Solution: Schema registry, handle missing fields gracefully

4. Backfill: Historical data before Kafka (1 year)
   Solution: Separate batch job reading from data warehouse

MONITORING & ALERTING:
- Kafka lag: Alert if >1 hour behind (indicates processing bottleneck)
- Data freshness: Alert if gold layer not updated in 2 hours
- Query latency: Alert if p99 > 1 second
- Reconciliation: Daily check if Kafka sum == Gold sum (±1% tolerance)
"""

# ============================================================================
# DESIGN 2: MULTI-REGION DISASTER RECOVERY DATA PIPELINE
# ============================================================================

"""
PROBLEM STATEMENT:
Design a multi-region data pipeline that survives regional outages.
- Primary region: US-East
- Failover region: US-West
- Data: E-commerce transactions (critical business data)
- RPO: <5 minutes (acceptable data loss)
- RTO: <15 minutes (time to restore)
- Consistency requirement: Exactly-once semantics

ARCHITECTURE:

┌──────────────────────────────────────────────────────────────────┐
│                         PRIMARY REGION (US-East)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐      ┌─────────────┐ │
│  │ PostgreSQL   │◄───────►│ Debezium CDC │─────►│ Kafka (3x)  │ │
│  │ (OLTP)       │  Binary │              │      │ Replication │ │
│  │              │  Logs   │              │      └─────────────┘ │
│  └──────────────┘         └──────────────┘            │         │
│                                                       │         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Spark Structured Streaming (Microbatch every 1 min)     │  │
│  │ - Dedup by transaction_id                              │  │
│  │ - Validate data quality                                │  │
│  │ - Enrich with product catalog                          │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                    │                                           │
│                    ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Delta Lake (ADLS Gen2 or S3)                            │  │
│  │ - ACID transactions for exactly-once                   │  │
│  │ - Time travel for point-in-time recovery               │  │
│  │ - Versioning: keep 30 days of history                  │  │
│  │ - Partition by region, date                            │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                    │                                           │
│                    │ Kafka Multi-Region Topic                  │
│                    │ (Replication factor = 3)                  │
│                    │                                           │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     │ MirrorMaker 2 (Cross-region replication)
                     │ Lag: <2 min
                     │
┌────────────────────┼───────────────────────────────────────────┐
│                    │                                           │
│                SECONDARY REGION (US-West)                    │
│                   (Warm Standby)                             │
│                    │                                           │
│                    ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Kafka Cluster (Replica of Primary)                       │  │
│  │ - Same topics, same partitions                          │  │
│  │ - Offset synchronized every minute                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                    │                                           │
│                    ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Standby Spark Job (PAUSED)                              │  │
│  │ - Code deployed and ready                              │  │
│  │ - Checkpoints on S3/ADLS (synced from primary)         │  │
│  │ - Can resume within 30 seconds of activation           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Delta Lake (Read-only mirror)                            │  │
│  │ - Synced via Delta log replication                      │  │
│  │ - <5 min behind                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

FAILOVER PROCEDURE (Triggered manually or auto via Consul):
1. Detect primary outage (Kafka broker unreachable for 3 min)
2. Update DNS/application config to point to US-West
3. Resume Spark job on US-West (resume from last checkpoint)
4. Redirect Debezium CDC to US-West Kafka
5. Validate data consistency (count check, hash check)

RECOVERY TIME:
- DNS update: 10 seconds
- Spark job resume: 20 seconds  
- Data validation: 60 seconds
- Total RTO: ~90 seconds (< 15 min target)

COST (Dual Active):
┌────────────────────────────────────────────┐
│ Component        │ US-East  │ US-West    │
├──────────────────┼──────────┼────────────┤
│ Kafka Cluster    │ $8K      │ $8K (sync) │
│ Spark Job        │ $6K      │ $0 (paused)│
│ Delta Lake       │ $2K      │ $2K (sync) │
│ Data Transfer    │ $1K      │ $1K        │
├──────────────────┼──────────┼────────────┤
│ Total Monthly    │          │ $28K       │
└────────────────────────────────────────────┘

To reduce cost: Pause compute in secondary (keep storage), resume on failover (adds 30s)

PRODUCTION ISSUES:
1. Split-brain: Both regions writing to Kafka simultaneously
   Solution: Kafka ACL/auth, region-aware producer config

2. Duplicate handling: If job restarts, might reprocess last batch
   Solution: Delta Lake's ACID handles this automatically

3. Offset misalignment: Primary and secondary Kafka at different offsets
   Solution: MirrorMaker maintains offset mapping in special topic

MONITORING:
- Cross-region replication lag: Alert if > 5 min
- Offset drift: Alert if > 1000 events
- Data freshness: Alert if standby >10 min behind
- Disaster recovery drill: Monthly failover test
"""

# ============================================================================
# DESIGN 3: DATA QUALITY + OBSERVABILITY ARCHITECTURE
# ============================================================================

"""
PROBLEM STATEMENT:
Add comprehensive data quality and observability to a production pipeline.
- Detect anomalies within 5 minutes
- Track data lineage (where did this value come from?)
- Support cost allocation (which team used what data?)
- SLA: 99.5% data accuracy

QUALITY CHECKS (dbt):
1. Freshness: Data updated within 2 hours (alert if not)
2. Unique: No duplicate primary keys
3. Not Null: Required columns have values
4. Relationships: Foreign keys exist in parent tables
5. Custom: Revenue > 0, Order date <= Today

LINEAGE + OBSERVABILITY:
┌──────────────────────────────────────────────────────────┐
│ OpenLineage (Airflow integration)                        │
│ - Tracks data flow: S3 → Spark → Redshift → Dashboard   │
│ - Stores in Apache Atlas metadata store                 │
│ - Query "which pipelines use customer table?"           │
└──────────────────────────────────────────────────────────┘

COST MODEL (Chargeback):
- Team A: Consumed 10TB → Cost = 10 * $50/TB = $500/month
- Team B: Consumed 5TB → Cost = 5 * $50/TB = $250/month
- Implementation: Per-table cost tracking in dbt

ANOMALY DETECTION:
- Great Expectations: Statistical checks
  * Row count within 10% of yesterday
  * Column distributions match historical (KL-divergence)
  * Null rates < threshold
- Alert if triggered, block downstream processing
"""

# ============================================================================
# DESIGN 4: ML FEATURE STORE (OFFLINE + ONLINE)
# ============================================================================

"""
PROBLEM STATEMENT:
Build feature store for ML models at e-commerce company.
- 1000+ features (user behavior, product info, context)
- Offline store: Training data (point-in-time correct)
- Online store: Low-latency inference
- Backtest: Need historical features from date X without data leakage

ARCHITECTURE:

OFFLINE PATH (Training):
  Spark batch job (daily) → Delta Lake → Python SDK retrieves data
  Key: Point-in-time correctness (use data as of 2024-01-01 00:00)

ONLINE PATH (Inference):
  Feature service API → Redis/DynamoDB → <10ms latency

FEATURE DEFINITION (YAML):
features:
  - user_total_spend_30d:
      source: transactions_table
      aggregation: SUM(amount) OVER (PARTITION BY user_id ROWS BETWEEN 30 DAY PRECEDING AND CURRENT ROW)
      update_frequency: daily
  
  - product_popularity:
      source: view_events
      aggregation: COUNT(*) OVER (PARTITION BY product_id)
      update_frequency: realtime

COST CONSIDERATIONS:
- Offline storage: Cheap (S3/Delta)
- Online cache: Expensive (Redis cluster)
- Solution: Only cache top 10% of features by query volume

PRODUCTION ISSUES:
1. Training-serving skew: Features computed differently in training vs inference
   Solution: Use same SQL for both paths

2. Feature staleness: Online cache outdated during peak load
   Solution: TTL-based refresh + background job

3. Feature explosion: 5000 features, but inference needs 50
   Solution: Feature importance ranking, auto-prune low-impact features
"""

# ============================================================================
# PRODUCTION TROUBLESHOOTING PATTERNS
# ============================================================================

"""
TROUBLESHOOTING DECISION TREE:

Problem: Data not appearing in dashboard
├─ Is Kafka producing? (Check broker logs + topic partition lag)
├─ Is Spark consuming? (Check job logs + checkpoint files)
├─ Is compute running? (Check cluster size, node status)
├─ Is output correct? (Check if data written to Delta/warehouse)
└─ Is query working? (Check if SELECT returns data)

Diagnosis:
1. Check lag: kafka-consumer-groups --describe --bootstrap-servers
2. Check Spark: spark.sparkContext.parallelize([1,2,3]).collect()
3. Check storage: SELECT COUNT(*) FROM gold_table WHERE date='2024-08-10'
4. Check freshness: SELECT MAX(updated_at) FROM gold_table

Problem: Pipeline running slow (>1 hour when usually <10 min)
├─ Data volume explosion? (COUNT(*) from raw data)
├─ Join skew? (Check data distribution across shuffle keys)
├─ Network bottleneck? (Check inter-node transfer time)
├─ Resource constraint? (Check CPU/memory/disk utilization)
└─ Query optimization? (Check execution plan with EXPLAIN)

Solutions:
1. Broadcast small table if join partner too large
2. Add salt key to skewed join: hash_key = hash(user_id) % 100
3. Repartition data: df.repartition(200, "partition_key")
4. Use Adaptive Query Execution: spark.sql.adaptive.enabled=true

Problem: "Out of Memory" error
├─ Shuffle too large? (Check number of tasks and data per task)
├─ Broadcast variable too big? (Don't broadcast >2GB)
├─ Accumulator memory? (Check driver memory for aggregations)
└─ Worker memory? (Increase executor memory in cluster config)

Solutions:
1. Increase spark.executor.memory (e.g., 8G → 16G)
2. Increase spark.sql.shuffle.partitions (200 → 500)
3. Use iterative broadcast: read chunks instead of full table
4. Enable spill to disk: spark.local.dir=/path/to/fast/disk

Problem: Data quality alert (row count mismatch)
├─ Missing data? (Check if upstream job failed)
├─ Duplication? (Check if dedup logic broke)
├─ Lateness? (Check if watermark dropped late events)
└─ Filtering? (Check if quality check too strict)

Solution:
1. Compare row count with previous day (within 10%)
2. Run dbt test --select fact_orders to check constraints
3. Compare checksum of data: SELECT MD5(CONCAT_AGG(ALL_COLUMNS))
4. Reprocess: Replay Kafka from checkpoint, or backfill from source

METRICS TO MONITOR:
- Data freshness: MAX(updated_at) - NOW() < 2 hours
- Data accuracy: COUNT(valid_records) / COUNT(*) > 99%
- Latency: p99 query time < 500ms
- Cost: Monthly spend vs budget
- Throughput: Events processed per second
- Storage: Delta table size growth rate

INCIDENT RESPONSE (SOP):
1. Detect: Alert fires (e.g., data freshness > 2 hours)
2. Assess: Check last successful job run + error logs
3. Communicate: Notify teams in Slack #data-incidents
4. Mitigate: Retry failed job or manually trigger backfill
5. Debug: Root cause analysis (what changed?)
6. Prevent: Add monitoring or validation to prevent recurrence
7. Postmortem: Document learnings, update runbook
"""

print("🚀 Advanced System Design Handbook Loaded")
print("✅ 4 complete production designs with trade-offs and cost analysis ready")
print("✅ Troubleshooting decision trees included")
