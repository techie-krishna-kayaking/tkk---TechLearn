# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 11: ADVANCED PYSPARK
# ================================================================================
# Topics: Python UDF, Pandas UDF (vectorized), mapPartitions, RDD conversion,
#         Broadcast variables, Accumulators, Higher-order functions, Lambda on RDDs
#
# Key interview message:
#   Prefer: built-in functions > higher-order functions > Pandas UDF > Python UDF
#
#   Python UDFs  → black boxes to Catalyst (no optimization); row-by-row Python
#                  serialization cost. Avoid unless no built-in alternative exists.
#   Pandas UDFs  → vectorized via Apache Arrow; process a whole column batch at once;
#                  much faster than plain Python UDFs.
#   Higher-order → stay inside Catalyst; no serialization overhead. Always prefer.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ pandas and pyarrow are pre-installed on Databricks clusters.
#   ✓ Arrow-based Pandas UDFs work out-of-the-box; no extra config needed.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType, StringType

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"

sc = spark.sparkContext

df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df.createOrReplaceTempView("df")

# ==============================================================================
# 1. PYTHON UDF (user-defined function)
# ==============================================================================
# INTERVIEW Q: "Why are Python UDFs slow?"
#   → Each row is serialized from JVM → Python (pickle), processed in Python,
#     then serialized back to JVM. This happens PER ROW and prevents Catalyst
#     from optimizing the expression (it's a black box).
#   → Prefer built-in functions whenever possible. If you MUST use a UDF, use
#     a Pandas UDF (vectorized, Arrow-based) for 10–100× better performance.
def intensity(cal):
    if cal is None: return "unknown"
    if cal >= 500:  return "high"
    if cal >= 300:  return "medium"
    return "low"

intensity_udf = udf(intensity, StringType())
df.select("id", "calories", intensity_udf(col("calories")).alias("intensity")).show(5)

# Register for use in Spark SQL
spark.udf.register("intensity_sql", intensity, StringType())
spark.sql("SELECT id, calories, intensity_sql(calories) AS intensity FROM df").show(5)

# Decorator style — clean for module-level UDFs
@udf(returnType=IntegerType())
def add_ten(x):
    return None if x is None else int(x) + 10

df.select("id", add_ten(col("calories")).alias("cal_plus_10")).show(5)

# ==============================================================================
# 2. PANDAS UDF (vectorized / Arrow-backed)
# ==============================================================================
# INTERVIEW Q: "How does a Pandas UDF differ from a Python UDF?"
#   → Pandas UDFs receive an entire column as a pandas.Series (a batch),
#     process it with vectorized pandas/numpy operations, and return a Series.
#     Arrow transfers the batch between JVM and Python WITHOUT row-by-row pickling.
#     Result: 10–100× faster than a plain Python UDF for numeric/string operations.
import pandas as pd
from pyspark.sql.functions import pandas_udf

@pandas_udf(IntegerType())
def calories_kj(cal: pd.Series) -> pd.Series:
    # 1 kcal ≈ 4.184 kJ; vectorized operation over the whole batch
    return (cal.fillna(0) * 4.184).astype("int")

df.select("id", "calories", calories_kj(col("calories")).alias("kj")).show(5)

spark.udf.register("calories_kj_sql", calories_kj)
spark.sql("SELECT id, calories_kj_sql(calories) AS kj FROM df").show(5)

# ==============================================================================
# 3. mapPartitions — transform an entire partition at the RDD level
# ==============================================================================
# INTERVIEW Q: "When do you use mapPartitions over map?"
#   → When you need to open a resource (DB connection, model file) ONCE per
#     partition rather than once per row. Much cheaper for I/O-bound operations.
def partition_lengths(rows):
    for r in rows:
        yield (r["id"], len(r["name"]))

rdd_out = df.rdd.mapPartitions(partition_lengths)
print("mapPartitions sample:", rdd_out.take(5))

# ==============================================================================
# 4. RDD CONVERSION — DataFrame ↔ RDD
# ==============================================================================
# INTERVIEW Q: "When do you drop to RDD from a DataFrame?"
#   → When you need operations that don't exist in the DataFrame API:
#     custom partitioners, zip with index, complex stateful transformations.
#   → ALWAYS try the DataFrame API first; dropping to RDD loses Catalyst optimization.
rdd = df.rdd
print("rdd first row:", rdd.first())

# RDD → DataFrame (back)
df_back = rdd.map(lambda r: (r["id"], r["name"].upper())).toDF(["id", "name_upper"])
df_back.show(5)

# ==============================================================================
# 5. BROADCAST VARIABLES — ship a read-only lookup to every executor once
# ==============================================================================
# INTERVIEW Q: "Broadcast variable vs broadcast join?"
#   Broadcast variable → ships a Python object (dict, list) to every executor.
#                        Accessed inside UDFs or RDD operations. Use for lookup tables.
#   Broadcast join     → Spark's join optimization (broadcasts a small DataFrame).
#     Without broadcast(), the same lookup dict would be serialized with EVERY TASK
#     closure — broadcast() sends it once per executor, saving significant I/O.
city_region = {
    "New York": "East", "Boston": "East", "Chicago": "Central",
    "Seattle": "West",  "Denver": "West"
}
bc = sc.broadcast(city_region)

region_udf = udf(lambda c: bc.value.get(c, "Unknown"), StringType())
df.select("id", "city", region_udf(col("city")).alias("region")).show(5)

# ==============================================================================
# 6. ACCUMULATORS — driver-side counters updated by executor tasks
# ==============================================================================
# INTERVIEW Q: "What are accumulators used for?"
#   → Counting bad records, tracking metrics from tasks running on executors.
#     Only the DRIVER should read the value (after an action). Reading inside
#     a transformation gives unreliable results (task retries double-count).
null_calories = sc.accumulator(0)

def count_nulls(row):
    if row["calories"] is None:
        null_calories.add(1)

df.foreach(count_nulls)
print("null calories (accumulator):", null_calories.value)

# ==============================================================================
# 7. HIGHER-ORDER FUNCTIONS — operate on arrays without UDFs (stay in Catalyst)
# ==============================================================================
# INTERVIEW Q: "Why prefer higher-order functions over UDFs for array operations?"
#   → They compile to JVM bytecode inside Catalyst; no Python round-trip.
#     Always use these (transform, filter, exists, aggregate) before reaching for a UDF.
arr = df.withColumn("tag_arr", F.split("tags", r"\|"))

arr.select(
    "id",
    F.transform("tag_arr", lambda x: F.upper(x)).alias("upper_tags"),
    F.filter("tag_arr", lambda x: x != "outdoor").alias("no_outdoor"),
    F.exists("tag_arr", lambda x: x == "cardio").alias("has_cardio"),
    F.aggregate("tag_arr", F.lit(0), lambda acc, x: acc + F.length(x)).alias("total_len"),
).show(5, False)

arr.createOrReplaceTempView("arr")
spark.sql(r"""
    SELECT id,
           TRANSFORM(tag_arr, x -> UPPER(x))     AS upper_tags,
           EXISTS(tag_arr, x -> x = 'cardio')    AS has_cardio
    FROM arr
""").show(5, False)

# ==============================================================================
# 8. LAMBDA EXPRESSIONS on RDDs
# ==============================================================================
# INTERVIEW Q: "map vs flatMap vs filter on RDDs?"
#   map(fn)     → one-to-one transformation per element
#   flatMap(fn) → one-to-many (fn returns an iterable; results are flattened)
#   filter(fn)  → keep only elements where fn returns True
total_calories = (
    df.rdd
    .map(lambda r: r["calories"] or 0)    # None → 0
    .reduce(lambda a, b: a + b)           # sum via reduce
)
print("total calories via RDD lambda reduce:", total_calories)
