# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 04: WINDOW FUNCTIONS
# ================================================================================
# Topics: Window spec, row_number, rank, dense_rank, lead, lag, ntile,
#         cume_dist, percent_rank, first_value, last_value,
#         running total, moving average, running count, Top-N per group
#
# Window functions are THE most common advanced SQL/Spark interview topic.
# Master these three concepts:
#   PARTITION BY → "group by" equivalent (reset counter per group)
#   ORDER BY     → defines the row sequence within each partition
#   FRAME        → ROWS/RANGE BETWEEN ... (which rows to include in the window)
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"

df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df.createOrReplaceTempView("df")

# ==============================================================================
# Window Specification — the blueprint for all window functions
# ==============================================================================
# INTERVIEW Q: "What are the three parts of a window specification?"
#   1. PARTITION BY → resets the window for each distinct value (like GROUP BY,
#                     but keeps all rows).
#   2. ORDER BY     → determines the sequence within each partition.
#   3. FRAME        → how many rows to include (ROWS BETWEEN / RANGE BETWEEN).
#                     Default frame: UNBOUNDED PRECEDING → CURRENT ROW (for ordered),
#                     or whole partition (for unordered). Know this default!

w = Window.partitionBy("category").orderBy(col("calories").desc_nulls_last())

w_running = (
    Window.partitionBy("category")
    .orderBy("id")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

# ==============================================================================
# row_number — unique sequential number per partition (no ties)
# ==============================================================================
# INTERVIEW Q: "row_number vs rank vs dense_rank?"
#   row_number → always unique (1,2,3,4)  — breaks ties arbitrarily
#   rank       → ties share a rank, leaves gaps (1,2,2,4)
#   dense_rank → ties share a rank, no gaps (1,2,2,3)
#
#   Use row_number for exact Top-N (guarantees exactly N rows per group).
spark.sql("""
    SELECT id, category, calories,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY calories DESC) AS rn
    FROM df
""").show()

df.select("id", "category", "calories", F.row_number().over(w).alias("rn")).show()

# ==============================================================================
# rank vs dense_rank — tie handling
# ==============================================================================
spark.sql("""
    SELECT id, category, calories,
           RANK()       OVER (PARTITION BY category ORDER BY calories DESC) AS rnk,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY calories DESC) AS drnk
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.rank().over(w).alias("rnk"),
    F.dense_rank().over(w).alias("drnk"),
).show()

# ==============================================================================
# lead / lag — access following / preceding rows
# ==============================================================================
# INTERVIEW Q: "What are lead and lag used for in practice?"
#   → Day-over-day / month-over-month deltas: LAG(sales) gives yesterday's sales.
#   → Session analysis: time gap between events.
#   → Always provide a default value (3rd arg) for the first/last row; otherwise NULL.
w_seq = Window.partitionBy("category").orderBy("id")

spark.sql("""
    SELECT id, category, calories,
           LAG(calories, 1)  OVER (PARTITION BY category ORDER BY id) AS prev_cal,
           LEAD(calories, 1) OVER (PARTITION BY category ORDER BY id) AS next_cal
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.lag("calories",  1).over(w_seq).alias("prev_cal"),
    F.lead("calories", 1).over(w_seq).alias("next_cal"),
).show()

# ==============================================================================
# ntile — split a partition into N equally-sized buckets
# ==============================================================================
# INTERVIEW Q: "What is ntile(4) used for?"
#   → Quartile analysis. NTILE(4) → 1=bottom 25%, 4=top 25%.
spark.sql("""
    SELECT id, category, calories,
           NTILE(3) OVER (PARTITION BY category ORDER BY calories DESC) AS bucket
    FROM df
""").show()

df.select("id", "category", "calories", F.ntile(3).over(w).alias("bucket")).show()

# ==============================================================================
# cume_dist / percent_rank — distribution metrics
# ==============================================================================
# cume_dist   → fraction of rows ≤ current row within partition (0 < x ≤ 1)
# percent_rank → (rank - 1) / (total rows - 1) (0 ≤ x ≤ 1)
w_asc = Window.partitionBy("category").orderBy("calories")

spark.sql("""
    SELECT id, category, calories,
           CUME_DIST()    OVER (PARTITION BY category ORDER BY calories) AS cume,
           PERCENT_RANK() OVER (PARTITION BY category ORDER BY calories) AS pct_rank
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.cume_dist().over(w_asc).alias("cume"),
    F.percent_rank().over(w_asc).alias("pct_rank"),
).show()

# ==============================================================================
# first_value / last_value
# ==============================================================================
# INTERVIEW TRAP: last_value with default frame (UNBOUNDED PRECEDING → CURRENT ROW)
#   returns the CURRENT ROW'S value, not the partition's last!
#   Fix: explicitly extend the frame to UNBOUNDED FOLLOWING.
w_full = (
    Window.partitionBy("category")
    .orderBy("calories")
    .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
)

spark.sql("""
    SELECT id, category, calories,
           FIRST_VALUE(calories) OVER (
               PARTITION BY category ORDER BY calories
               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_cal,
           LAST_VALUE(calories)  OVER (
               PARTITION BY category ORDER BY calories
               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_cal
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.first("calories").over(w_full).alias("first_cal"),
    F.last("calories").over(w_full).alias("last_cal"),
).show()

# ==============================================================================
# Running total (cumulative sum)
# ==============================================================================
# Frame: ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
# This is the default frame when ORDER BY is present — state it explicitly for clarity.
spark.sql("""
    SELECT id, category, calories,
           SUM(calories) OVER (
               PARTITION BY category ORDER BY id
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.sum("calories").over(w_running).alias("running_total"),
).show()

# ==============================================================================
# Moving average (last 3 rows: 2 preceding + current row)
# ==============================================================================
# INTERVIEW Q: "ROWS BETWEEN vs RANGE BETWEEN?"
#   ROWS   → physical row count (2 PRECEDING = exactly 2 rows before current)
#   RANGE  → logical value range (2 PRECEDING = all rows where order_col >= current - 2)
#   Ties behave differently. Default to ROWS unless you specifically need RANGE.
w_moving = Window.partitionBy("category").orderBy("id").rowsBetween(-2, 0)

spark.sql("""
    SELECT id, category, calories,
           AVG(calories) OVER (
               PARTITION BY category ORDER BY id
               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
    FROM df
""").show()

df.select(
    "id", "category", "calories",
    F.avg("calories").over(w_moving).alias("moving_avg"),
).show()

# ==============================================================================
# Running count
# ==============================================================================
spark.sql("""
    SELECT id, category,
           COUNT(*) OVER (
               PARTITION BY category ORDER BY id
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_count
    FROM df
""").show()

df.select("id", "category", F.count("*").over(w_running).alias("running_count")).show()

# ==============================================================================
# Classic interview pattern: Top-N per group (Top 1 per category)
# ==============================================================================
# INTERVIEW Q: "How do you find the highest-calorie activity per category?"
#   → row_number() OVER (PARTITION BY category ORDER BY calories DESC), then filter rn=1.
#   → Use row_number (not rank) to guarantee exactly one row per group even on ties.
spark.sql("""
    SELECT * FROM (
        SELECT id, category, calories,
               ROW_NUMBER() OVER (PARTITION BY category ORDER BY calories DESC) AS rn
        FROM df
    ) WHERE rn = 1
""").show()

df.withColumn("rn", F.row_number().over(w)).filter(col("rn") == 1).drop("rn").show()
