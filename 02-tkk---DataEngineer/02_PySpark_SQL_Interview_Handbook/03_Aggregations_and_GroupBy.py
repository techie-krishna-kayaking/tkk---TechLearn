# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 03: AGGREGATIONS & GROUP BY
# ================================================================================
# Topics: sum, avg, count, countDistinct, min, max, variance, stddev,
#         collect_list, collect_set, groupBy, HAVING, PIVOT, CUBE, ROLLUP,
#         GROUPING SETS, UNION / UNION ALL / INTERSECT / EXCEPT
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ display(df) renders a richer table in the notebook UI.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col

DATASETS = "/FileStore/tables/interview_handbook"

df  = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/df.csv")
df1 = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/df1.csv")
df.createOrReplaceTempView("df")
df1.createOrReplaceTempView("df1")

# ==============================================================================
# Simple aggregates: sum, avg/mean, count, min, max
# ==============================================================================
# INTERVIEW TRAP: COUNT(*) counts rows including NULLs.
#                 COUNT(col) counts only non-NULL values for that column.
spark.sql("""
    SELECT
        SUM(calories)   AS total_cal,
        AVG(calories)   AS avg_cal,
        COUNT(*)        AS n_rows,
        COUNT(calories) AS n_non_null_cal,  -- ignores NULLs
        MIN(calories)   AS min_cal,
        MAX(calories)   AS max_cal
    FROM df
""").show()

df.agg(
    F.sum("calories").alias("total_cal"),
    F.avg("calories").alias("avg_cal"),       # avg == mean (aliases in Spark)
    F.mean("calories").alias("mean_cal"),
    F.count("*").alias("n_rows"),
    F.count("calories").alias("n_non_null_cal"),
    F.min("calories").alias("min_cal"),
    F.max("calories").alias("max_cal"),
).show()

# ==============================================================================
# countDistinct
# ==============================================================================
# INTERVIEW Q: "COUNT(DISTINCT col) on big data — what's the concern?"
#   → Exact COUNT(DISTINCT) requires a full shuffle + sort. On billions of rows,
#     use approx_count_distinct(col, rsd) (HyperLogLog, ~5% error) instead.
spark.sql("SELECT COUNT(DISTINCT city) AS distinct_cities FROM df").show()
df.agg(F.countDistinct("city").alias("distinct_cities")).show()

# ==============================================================================
# variance / stddev
# ==============================================================================
# variance() / stddev() → sample variance/stddev (ddof=1)
# var_pop() / stddev_pop() → population variance/stddev (ddof=0)
spark.sql("SELECT VARIANCE(calories) AS var_cal, STDDEV(calories) AS std_cal FROM df").show()
df.agg(F.variance("calories").alias("var_cal"), F.stddev("calories").alias("std_cal")).show()

# ==============================================================================
# collect_list / collect_set (array aggregation)
# ==============================================================================
# INTERVIEW Q: "collect_list vs collect_set?"
#   collect_list → keeps ALL values (including duplicates); ORDER IS UNDEFINED.
#   collect_set  → deduplicates values; ORDER IS ALSO UNDEFINED.
#   Use sort_array() afterwards if you need deterministic ordering.
spark.sql("""
    SELECT category,
           COLLECT_LIST(activity) AS activities,
           COLLECT_SET(city)      AS cities
    FROM df GROUP BY category
""").show(truncate=False)

df.groupBy("category").agg(
    F.collect_list("activity").alias("activities"),
    F.collect_set("city").alias("cities"),
).show(truncate=False)

# ==============================================================================
# groupBy + multiple aggregates
# ==============================================================================
spark.sql("""
    SELECT category,
           COUNT(*)          AS n,
           SUM(calories)     AS total_cal,
           AVG(duration_min) AS avg_dur
    FROM df
    GROUP BY category
    ORDER BY category
""").show()

df.groupBy("category").agg(
    F.count("*").alias("n"),
    F.sum("calories").alias("total_cal"),
    F.avg("duration_min").alias("avg_dur"),
).orderBy("category").show()

# ==============================================================================
# HAVING — filter AFTER aggregation
# ==============================================================================
# INTERVIEW Q: "WHERE vs HAVING?"
#   WHERE  → filters ROWS before grouping (pre-aggregation).
#   HAVING → filters GROUPS after aggregation. You can only reference aggregated
#            columns or GROUP BY columns in HAVING.
spark.sql("""
    SELECT category, COUNT(*) AS n
    FROM df
    GROUP BY category
    HAVING COUNT(*) > 3
""").show()

# DataFrame API: just filter the aggregated result
df.groupBy("category").agg(F.count("*").alias("n")).filter(col("n") > 3).show()

# ==============================================================================
# PIVOT — rows → columns
# ==============================================================================
# INTERVIEW Q: "How do you implement PIVOT in Spark?"
#   → In SQL: PIVOT (agg FOR col IN (val1, val2, ...))
#   → In DataFrame API: groupBy(...).pivot(col, [values]).agg(...)
#
# INTERVIEW TIP: Always provide the explicit value list in pivot() —
#   without it Spark runs an extra scan to discover unique values (slow).
spark.sql("""
    SELECT * FROM (
        SELECT city, category, calories FROM df
    )
    PIVOT (
        SUM(calories) FOR category IN ('Exercise', 'Diet', 'Sleep')
    )
""").show()

df.groupBy("city").pivot("category", ["Exercise", "Diet", "Sleep"]).sum("calories").show()

# ==============================================================================
# CUBE — all combinations of grouping columns (+ grand total)
# ==============================================================================
# INTERVIEW Q: "CUBE vs ROLLUP vs GROUPING SETS?"
#   ROLLUP(a, b)    → hierarchical subtotals: (a,b), (a), ()
#   CUBE(a, b)      → all combinations: (a,b), (a), (b), ()
#   GROUPING SETS   → you define EXACTLY which groups to compute
#   All produce NULL in the grouping column to represent the "all" level.
spark.sql("""
    SELECT category, city, SUM(calories) AS total
    FROM df
    GROUP BY CUBE(category, city)
    ORDER BY category, city
""").show(50)

df.cube("category", "city").agg(F.sum("calories").alias("total")).orderBy("category", "city").show(50)

# ==============================================================================
# ROLLUP — hierarchical subtotals
# ==============================================================================
spark.sql("""
    SELECT category, city, SUM(calories) AS total
    FROM df
    GROUP BY ROLLUP(category, city)
    ORDER BY category, city
""").show(50)

df.rollup("category", "city").agg(F.sum("calories").alias("total")).orderBy("category", "city").show(50)

# ==============================================================================
# GROUPING SETS — explicit list of groupings (SQL only)
# ==============================================================================
# DataFrame API equivalent: union separate groupBy results, or use cube/rollup
# with grouping() / grouping_id() to filter down to the desired groups.
spark.sql("""
    SELECT category, city, SUM(calories) AS total
    FROM df
    GROUP BY GROUPING SETS ((category), (city), ())
    ORDER BY category, city
""").show(50)

# ==============================================================================
# SET OPERATIONS: UNION ALL / UNION / INTERSECT / EXCEPT
# ==============================================================================
# INTERVIEW Q: "UNION vs UNION ALL?"
#   UNION ALL → keeps duplicates (no extra shuffle → cheaper). Prefer this unless
#               you specifically need deduplication.
#   UNION     → removes duplicates (adds a shuffle/sort to dedup).
#
# INTERVIEW TRAP: df.union(other) in the DataFrame API is UNION ALL (by POSITION),
#                 NOT by column name. Use unionByName to align by name.

# UNION ALL
spark.sql("SELECT name FROM df UNION ALL SELECT name FROM df1").show(50)
df.select("name").union(df1.select("name")).show(50)   # DataFrame union == UNION ALL

# UNION (distinct)
spark.sql("SELECT name FROM df UNION SELECT name FROM df1").show(50)
df.select("name").union(df1.select("name")).distinct().show(50)

# unionByName — align by column NAME (safer when schemas may differ in order)
df.unionByName(df1).show(50)

# INTERSECT — rows present in BOTH datasets
spark.sql("SELECT name FROM df INTERSECT SELECT name FROM df1").show()
df.select("name").intersect(df1.select("name")).show()

# EXCEPT / MINUS — rows in left but NOT in right
spark.sql("SELECT name FROM df EXCEPT SELECT name FROM df1").show()
df.select("name").exceptAll(df1.select("name")).show()  # exceptAll keeps duplicates
