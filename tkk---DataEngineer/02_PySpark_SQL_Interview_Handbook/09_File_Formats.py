# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 09: FILE FORMATS & I/O
# ================================================================================
# Topics: CSV, JSON, Parquet, ORC, Delta, Partitioned writes, Bucketing,
#         Compression codecs, Schema evolution (mergeSchema)
#
# Key interview themes:
#   • Columnar (Parquet/ORC) vs row (CSV/JSON) — why columnar wins for analytics
#   • Splittable + compressed (snappy) vs non-splittable (gzip csv)
#   • Delta / ACID / time travel — the Databricks/lakehouse native format
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ Delta Lake is natively supported — no extra library required.
#   ✓ Bucketing (saveAsTable) works with Databricks' built-in Hive metastore.
#   ✓ Unity Catalog users: adjust database/table names as needed.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"
OUTPUT   = "/FileStore/tables/interview_handbook_output/09_formats"

df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df.createOrReplaceTempView("df")

# ==============================================================================
# CSV — row-based, human-readable, NO schema embedded in the file
# ==============================================================================
# INTERVIEW Q: "What are the downsides of CSV for analytics?"
#   → Row-based: must read every column even if you only need two.
#   → No schema: types must be inferred or supplied on every read.
#   → Large files compressed with gzip are NOT splittable → one task handles the
#     whole file (bottleneck). Snappy CSV is splittable but rarely used.
csv_out = f"{OUTPUT}/csv"
df.write.mode("overwrite").option("header", True).csv(csv_out)
spark.read.option("header", True).option("inferSchema", True).csv(csv_out).show(3)
spark.sql(f"SELECT * FROM csv.`{csv_out}` LIMIT 3").show()

# ==============================================================================
# JSON — row-based, schema-on-read, natively nested
# ==============================================================================
# INTERVIEW Q: "When is JSON preferred over Parquet?"
#   → Human-readable debugging, API payloads, and when the schema is highly
#     dynamic / evolving. For storage-efficient analytics, always prefer Parquet.
json_out = f"{OUTPUT}/json"
df.write.mode("overwrite").json(json_out)
spark.read.json(json_out).show(3)
spark.sql(f"SELECT * FROM json.`{json_out}` LIMIT 3").show()

# ==============================================================================
# PARQUET — columnar, compressed, splittable (the analytics default)
# ==============================================================================
# INTERVIEW Q: "Why is Parquet the de-facto standard for big-data analytics?"
#   1. Columnar storage → only read the columns you SELECT (column pruning).
#   2. Schema embedded → no need to specify types at read time.
#   3. Splittable (snappy/uncompressed row groups) → parallelism at scale.
#   4. Efficient compression: repeated values in a column compress much better
#      than row-interleaved data.
pq_out = f"{OUTPUT}/parquet"
df.write.mode("overwrite").parquet(pq_out)
spark.read.parquet(pq_out).show(3)
spark.sql(f"SELECT id, calories FROM parquet.`{pq_out}` LIMIT 3").show()

# ==============================================================================
# ORC — columnar, common in the Hive/Hadoop ecosystem
# ==============================================================================
# INTERVIEW Q: "Parquet vs ORC?"
#   Both are columnar + compressed. Parquet is the Spark/cloud default.
#   ORC has better predicate pushdown in older Hive; Parquet is the clear winner
#   in the modern Spark / Databricks / cloud lakehouse ecosystem.
orc_out = f"{OUTPUT}/orc"
df.write.mode("overwrite").orc(orc_out)
spark.read.orc(orc_out).show(3)
spark.sql(f"SELECT * FROM orc.`{orc_out}` LIMIT 3").show()

# ==============================================================================
# DELTA — ACID transactions, time travel, schema enforcement
# ==============================================================================
# INTERVIEW Q: "What advantages does Delta Lake add over plain Parquet?"
#   1. ACID transactions → concurrent reads/writes without corruption.
#   2. Time travel (versionAsOf, timestampAsOf) → audit trail, rollback.
#   3. Schema enforcement → reject writes that don't match the table schema.
#   4. Schema evolution → ALTER TABLE ADD COLUMN without rewriting all files.
#   5. Optimized writes: OPTIMIZE + Z-ORDER for data skipping.
#   6. VACUUM to remove old files and manage storage costs.
delta_out = f"{OUTPUT}/delta"
df.write.format("delta").mode("overwrite").save(delta_out)
spark.read.format("delta").load(delta_out).show(3)

# Time travel — read a previous version of the table
spark.read.format("delta").option("versionAsOf", 0).load(delta_out).show(3)

# ==============================================================================
# PARTITIONED WRITES — physical directory partitioning for partition pruning
# ==============================================================================
# INTERVIEW Q: "What is partition pruning and how do you enable it?"
#   → Write data with partitionBy("col") → creates subfolders like category=Exercise/.
#     A query with WHERE category='Exercise' scans ONLY that folder — all others skipped.
#     This dramatically reduces I/O on petabyte-scale datasets.
part_out = f"{OUTPUT}/partitioned"
df.write.mode("overwrite").partitionBy("category", "city").parquet(part_out)
print(f"partitioned by category/city → {part_out}")
spark.read.parquet(part_out).filter("category = 'Exercise'").show(3)

# ==============================================================================
# BUCKETING — hash-partition into N buckets to eliminate future join shuffles
# ==============================================================================
# INTERVIEW Q: "What is bucketing and when does it help?"
#   → Bucketing pre-shuffles data by the join/group-by key at write time.
#     When two bucketed tables with the same key + bucket count are joined,
#     Spark skips the shuffle entirely → massive speedup on repeated joins.
#   → Requires saveAsTable (persisted to the metastore); not available with write.parquet().
spark.sql("DROP TABLE IF EXISTS df_bucketed")
(
    df.write.mode("overwrite")
    .bucketBy(4, "city")
    .sortBy("city")
    .saveAsTable("df_bucketed")
)
print("bucketed table created:", spark.catalog.tableExists("df_bucketed"))
spark.sql("SELECT city, COUNT(*) FROM df_bucketed GROUP BY city").show()

# ==============================================================================
# COMPRESSION — codecs for Parquet and CSV
# ==============================================================================
# INTERVIEW Q: "Snappy vs Gzip for Parquet?"
#   Snappy → fast compress/decompress; moderate ratio; SPLITTABLE within Parquet row groups.
#   Gzip   → better ratio; slower; NOT splittable for plain CSV files.
#   Zstd   → best ratio at good speed; the new recommended default in Spark 3.2+.
#   For Parquet: use snappy (default) or zstd. For CSV: snappy if splittability matters.
snappy_out = f"{OUTPUT}/parquet_snappy"
df.write.mode("overwrite").option("compression", "snappy").parquet(snappy_out)
gzip_csv = f"{OUTPUT}/csv_gzip"
df.write.mode("overwrite").option("compression", "gzip").csv(gzip_csv)
print("wrote snappy parquet and gzip csv")

# ==============================================================================
# SCHEMA EVOLUTION / mergeSchema — read Parquet files with differing schemas
# ==============================================================================
# INTERVIEW Q: "How does Parquet handle schema changes over time?"
#   → Use mergeSchema=True at read time: Spark unions all schemas found across files.
#     Columns present in some files but not others are filled with NULL.
#   → Delta Lake handles this automatically; ALTER TABLE ADD COLUMN is always backward-compatible.
evo = f"{OUTPUT}/evolve"
df.select("id", "name").write.mode("overwrite").parquet(evo)
df.select("id", "name", F.lit("v2").alias("version")).write.mode("append").parquet(evo)
merged = spark.read.option("mergeSchema", True).parquet(evo)
print("merged schema columns:", merged.columns)
merged.show(5)
