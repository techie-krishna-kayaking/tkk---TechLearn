# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 08: DATAFRAME OPERATIONS (execution & partitioning control)
# ================================================================================
# Topics: cache, persist, checkpoint, repartition, coalesce, partitionBy (write),
#         sortWithinPartitions, foreachPartition, foreach, DataFrame.transform
#
# These concepts separate junior engineers from senior ones in interviews.
# They are about HOW Spark executes and physically lays out data.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ DBFS is the default storage layer on Databricks.
#   ✓ Checkpoint dir is set to /tmp which maps to the cluster's local DBFS temp area.
#
# Golden rule: SQL analogue first → then the DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col
from pyspark.storagelevel import StorageLevel

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"
OUTPUT   = "/FileStore/tables/interview_handbook_output/08_ops"

# Set checkpoint dir in DBFS (required before calling checkpoint())
spark.sparkContext.setCheckpointDir("/tmp/spark_checkpoints")

df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df.createOrReplaceTempView("df")

# ==============================================================================
# cache — materialize a DataFrame in memory (lazy until first action)
# ==============================================================================
# INTERVIEW Q: "cache() vs persist()?"
#   cache()           → shorthand for persist(MEMORY_AND_DISK) in Spark 3.x.
#   persist(level)    → you choose the exact StorageLevel (memory only, disk, etc.).
#   Both are LAZY — the data isn't actually stored until an action triggers it.
#   Always unpersist() when done to free executor memory.

spark.sql("CACHE TABLE df")   # SQL analogue: eager cache of a temp view
print("cached count:", spark.sql("SELECT COUNT(*) FROM df").collect()[0][0])
spark.sql("UNCACHE TABLE df")

df.cache()
df.count()     # triggers the cache materialization
print("is cached →", df.is_cached)
df.unpersist()

# ==============================================================================
# persist — explicit storage level
# ==============================================================================
# INTERVIEW Q: "When would you use DISK_ONLY over MEMORY_AND_DISK?"
#   → When memory is constrained and GC pressure is a concern.
#     Recomputing from DISK_ONLY is cheaper than GC pauses.
#   StorageLevels: MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY,
#                  MEMORY_AND_DISK_2 (replicated), OFF_HEAP (Tungsten off-heap)
df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
print("persisted with MEMORY_AND_DISK")
df.unpersist()

# ==============================================================================
# checkpoint — truncate lineage by writing to reliable storage
# ==============================================================================
# INTERVIEW Q: "Why do you need checkpoint in iterative algorithms?"
#   → Long chains of transformations create a long lineage / DAG. If a task
#     fails, Spark must recompute the entire chain. Checkpoint cuts the DAG by
#     materializing the result to DBFS/S3, so recovery only goes back to that point.
#   → Unlike cache (memory), checkpoint survives executor failures.
chk = df.checkpoint(eager=True)
print("checkpointed rows:", chk.count())

# ==============================================================================
# repartition — full shuffle to N partitions (can increase OR decrease)
# ==============================================================================
# INTERVIEW Q: "repartition vs coalesce?"
#   repartition(n)        → full shuffle → evenly-sized partitions; can increase count.
#   coalesce(n)           → narrow (no shuffle) → only DECREASES partitions; may
#                           leave uneven sizes. Prefer coalesce when shrinking.
#   repartition(n, col)   → hash-partition by column → co-locates same-key rows
#                           (beneficial before joins or window functions on that key).
print("initial partitions:", df.rdd.getNumPartitions())
print("after repartition(8):", df.repartition(8).rdd.getNumPartitions())
print("after coalesce(2):", df.repartition(8).coalesce(2).rdd.getNumPartitions())
print("after repartition by category:", df.repartition(4, col("category")).rdd.getNumPartitions())

# ==============================================================================
# partitionBy — physically partition data on WRITE (directory layout)
# ==============================================================================
# INTERVIEW Q: "What is partition pruning?"
#   → When a query filters on a partition column, Spark reads ONLY the matching
#     directory (e.g. category=Exercise/) — skipping all other partitions entirely.
#     This dramatically reduces I/O on large datasets.
(
    df.write.mode("overwrite")
    .partitionBy("category")
    .parquet(f"{OUTPUT}/by_category")
)
print("written partitioned parquet by category")

# ==============================================================================
# sortWithinPartitions — sort each partition WITHOUT a global shuffle
# ==============================================================================
# INTERVIEW Q: "orderBy vs sortWithinPartitions?"
#   orderBy → full global sort (shuffle + merge); guarantees total order across DF.
#   sortWithinPartitions → sorts each partition independently; NO shuffle; no global order.
#   Use sortWithinPartitions when writing to files and local sort is sufficient.
spark.sql("SELECT id, calories FROM df SORT BY calories DESC").show(5)   # SQL: SORT BY
df.sortWithinPartitions(col("calories").desc()).select("id", "calories").show(5)

# ==============================================================================
# DataFrame.transform — chain custom transformation functions fluently
# ==============================================================================
# INTERVIEW Q: "What is DataFrame.transform()?"
#   → Applies a function (DataFrame → DataFrame) to the current DataFrame.
#     Enables clean functional pipelines without intermediate variable assignment.
def add_effort(input_df):
    """effort = calories per minute."""
    return input_df.withColumn("effort", F.round(col("calories") / col("duration_min"), 2))

def only_exercise(input_df):
    return input_df.filter(col("category") == "Exercise")

df.transform(add_effort).transform(only_exercise).select("id", "effort").show()

# ==============================================================================
# foreach / foreachPartition — run side effects on executors
# ==============================================================================
# INTERVIEW Q: "foreach vs foreachPartition?"
#   foreach(fn)          → fn called once per ROW; one call per record.
#   foreachPartition(fn) → fn called once per PARTITION (iterator of rows).
#                          PREFERRED for I/O: open one DB connection per partition,
#                          process all rows, then close it — far fewer connections.
#
# TRAP: These run on EXECUTORS (not the driver). You CANNOT mutate driver-side
#       variables inside them. Use Accumulators for driver-side metrics instead.
def print_row(row):
    _ = f"id={row['id']} cal={row['calories']}"   # in practice: write to DB/queue

df.foreach(print_row)

def process_partition(rows):
    count = 0
    for _ in rows:
        count += 1
    # In practice: open DB connection, batch-insert, close connection

df.foreachPartition(process_partition)
print("foreach / foreachPartition executed")
