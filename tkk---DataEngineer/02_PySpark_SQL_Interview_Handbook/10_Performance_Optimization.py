# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 10: PERFORMANCE OPTIMIZATION
# ================================================================================
# Topics: Partition pruning, Predicate pushdown, Broadcast join, Caching/Persist,
#         Checkpoint, AQE (Adaptive Query Execution), Explain plans,
#         Shuffle optimization, Small file problem, Skew + Salting,
#         Bucketing, Dynamic partition pruning
#
# This chapter is what separates senior data engineers in interviews.
# Each section explains WHAT the optimization is, WHY it helps, and HOW to trigger it.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ AQE is enabled by default on Databricks — you usually DON'T need to set it.
#   ✓ Auto-optimize (OPTIMIZE + ZORDER) is available for Delta tables on Databricks.
#   ✓ Photon engine (Databricks runtime) further accelerates vectorized execution.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col, broadcast
from pyspark.storagelevel import StorageLevel

DATASETS = "/FileStore/tables/interview_handbook"
OUTPUT   = "/FileStore/tables/interview_handbook_output/10_perf"

spark.sparkContext.setCheckpointDir("/tmp/spark_checkpoints")

df   = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/df.csv")
cust = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/cust.csv")
prod = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/prod.csv")
df.createOrReplaceTempView("df")

# ==============================================================================
# 1. PARTITION PRUNING — skip partition folders entirely at the scan level
# ==============================================================================
# INTERVIEW Q: "What is partition pruning?"
#   → When you write data with partitionBy("col") and then filter on that column,
#     Spark reads ONLY the matching subdirectory — all others are skipped without
#     any I/O. For a table with 1000 partitions, filtering on one partition reads
#     only 1/1000th of the data.
part_path = f"{OUTPUT}/partitioned"
df.write.mode("overwrite").partitionBy("category").parquet(part_path)
pruned = spark.read.parquet(part_path).filter(col("category") == "Exercise")
print("=== Partition pruning plan (only category=Exercise scanned) ===")
pruned.explain()    # look for: PartitionFilters: [isnotnull(category#...), (category#... = Exercise)]

# ==============================================================================
# 2. PREDICATE PUSHDOWN — push row filters INTO the file scan
# ==============================================================================
# INTERVIEW Q: "What is predicate pushdown?"
#   → Parquet/ORC store column statistics (min/max) per row group. Spark pushes
#     WHERE filters into the reader so entire row groups that can't satisfy the
#     predicate are skipped WITHOUT reading those bytes from disk/object store.
pq = f"{OUTPUT}/pushdown"
df.write.mode("overwrite").parquet(pq)
pushed = spark.read.parquet(pq).filter(col("calories") > 400)
print("=== Predicate pushdown plan (PushedFilters shown) ===")
pushed.explain()    # look for: PushedFilters: [IsNotNull(calories), GreaterThan(calories,400)]

# ==============================================================================
# 3. BROADCAST JOIN — avoid shuffling the large side
# ==============================================================================
# INTERVIEW Q: "What is a broadcast/map-side join and when should you use it?"
#   → The small table is copied to every executor; the large table is streamed locally.
#     The large table never shuffles → huge network savings.
#   → Auto-triggered when a table is below spark.sql.autoBroadcastJoinThreshold (10MB).
#   → Use broadcast() hint to force it even above the threshold.
#   → TRAP: Broadcasting a large table causes driver OOM (it must fit in driver + executor memory).
print("=== Broadcast join plan ===")
bj = prod.join(broadcast(cust), "cust_id")
bj.explain()        # look for: BroadcastHashJoin

# ==============================================================================
# 4. CACHING & 5. PERSIST — reuse a DataFrame across multiple actions
# ==============================================================================
# INTERVIEW Q: "Why do you cache a DataFrame?"
#   → If you perform multiple actions on the same DF (e.g., count + groupBy + write),
#     each action recomputes the entire lineage from scratch. Caching materializes
#     the result once and reuses it for subsequent actions.
df.cache()
df.count()
_ = df.groupBy("category").count().collect()   # reuses the cache
df.unpersist()

df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
df.unpersist()

# ==============================================================================
# 6. CHECKPOINT — cut a long lineage / add fault tolerance
# ==============================================================================
# INTERVIEW Q: "cache() vs checkpoint()?"
#   cache()      → stores in executor memory (or disk); lineage is preserved.
#   checkpoint() → writes to reliable storage (DBFS/S3); lineage is TRUNCATED.
#     Use checkpoint for iterative ML (MLlib) or very deep transformation chains
#     where lineage recomputation on failure is too expensive.
chk = df.checkpoint(eager=True)
print("checkpoint rows:", chk.count())

# ==============================================================================
# 7. ADAPTIVE QUERY EXECUTION (AQE)
# ==============================================================================
# INTERVIEW Q: "What is AQE and what three problems does it solve?"
#   1. Partition coalescing  → after a shuffle, merges tiny partitions into larger
#                              ones (fixes the small-file / many-task problem).
#   2. Runtime broadcast     → if Spark discovers at runtime that a join side is
#                              small enough, it switches SMJ → BroadcastHashJoin.
#   3. Skew join splitting   → detects skewed partitions and auto-splits them so
#                              one straggler task doesn't hold up the whole stage.
# AQE is ON by default in Databricks Runtime. Check / verify:
print("AQE enabled?", spark.conf.get("spark.sql.adaptive.enabled"))

# ==============================================================================
# 8. EXPLAIN PLANS — understand the physical execution strategy
# ==============================================================================
# INTERVIEW Q: "How do you read a Spark explain plan?"
#   explain()         → physical plan only (most useful for interviews)
#   explain(True)     → parsed → analyzed → optimized → physical (all 4 plans)
#   explain('cost')   → cost-based stats
#   explain('formatted') → pretty columnar output (easiest to read)
#   Look for: Exchange (shuffle), BroadcastHashJoin, SortMergeJoin, Filter (pushdown)
print("=== explain() — physical plan ===")
df.groupBy("category").agg(F.sum("calories")).explain()
df.groupBy("category").count().explain("formatted")

# ==============================================================================
# 9. SHUFFLE OPTIMIZATION — control partition count
# ==============================================================================
# INTERVIEW Q: "Why does spark.sql.shuffle.partitions matter?"
#   Default = 200. Too many → tiny partitions, excessive task overhead, small files.
#   Too few → large partitions, OOM, slow tasks. AQE auto-coalesces, but for
#   manual tuning: target ~128MB–1GB per partition.
print("shuffle.partitions:", spark.conf.get("spark.sql.shuffle.partitions"))
spark.conf.set("spark.sql.shuffle.partitions", "8")  # tune for your workload

# ==============================================================================
# 10. SMALL FILE PROBLEM — compact many tiny files at write time
# ==============================================================================
# INTERVIEW Q: "What is the small file problem and how do you fix it?"
#   → Too many small files → slow metadata listing, excessive task scheduling.
#   → Fix before writing: coalesce(n) or repartition(n) to target ~128MB files.
#   → Fix after writing on Delta: OPTIMIZE table (compacts small files automatically).
compact_path = f"{OUTPUT}/compacted"
df.coalesce(1).write.mode("overwrite").parquet(compact_path)
print("compacted to 1 file (demo — for production target 128MB–1GB per file)")

# ==============================================================================
# 11. DATA SKEW & 12. SALTING
# ==============================================================================
# INTERVIEW Q: "What is data skew and how do you handle it?"
#   → Skew: one partition key has far more rows than others → one straggler task
#     takes 10× longer than the rest, blocking the whole stage.
#
# Solutions:
#   a) AQE skewJoin (automatic): enabled by default on Databricks.
#   b) Salting (manual): add a random suffix (0..N-1) to the hot key,
#      replicate the small-side lookup for each salt, join, then aggregate back.
salted = (
    df.withColumn("salt", (F.rand() * 4).cast("int"))
      .withColumn("salted_key", F.concat_ws("_", col("category"), col("salt")))
)
print("=== Salted key sample — spreads a hot category across 4 buckets ===")
salted.select("category", "salt", "salted_key").show(8)

# ==============================================================================
# 13. BUCKETING — pre-shuffle by join key at write time to skip future shuffles
# ==============================================================================
# INTERVIEW Q: "How does bucketing eliminate join shuffles?"
#   → Both tables are written with bucketBy(N, key). On a join with the same key
#     and same bucket count, Spark knows each bucket N on the left maps to bucket N
#     on the right → no shuffle needed at join time.
#   → Requires saveAsTable; effective only when both join sides are bucketed identically.
print("Bucketing: pre-partition by join key at write time → shuffle-free future joins")

# ==============================================================================
# 14. DYNAMIC PARTITION PRUNING (DPP)
# ==============================================================================
# INTERVIEW Q: "What is dynamic partition pruning?"
#   → When joining a partitioned fact table to a filtered dimension, Spark can
#     inject the dimension's filter INTO the fact table scan AT RUNTIME.
#     This means even though the fact table is huge, only the matching partitions
#     (e.g. category=Exercise) are read — even inside a join.
spark.conf.set("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
fact = spark.read.parquet(part_path)         # written earlier, partitioned by category
dim  = df.select("category").distinct().filter(col("category") == "Exercise")
dpp  = fact.join(dim, "category")
print("=== Dynamic Partition Pruning plan ===")
dpp.explain()   # look for: dynamicpruning or PartitionFilters with runtime subquery
