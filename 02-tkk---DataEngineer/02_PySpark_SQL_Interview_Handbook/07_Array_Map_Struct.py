# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 07: ARRAY, MAP & STRUCT (complex / nested types)
# ================================================================================
# Topics: array, array_contains, size, explode, posexplode, map, map_keys,
#         map_values, struct, named_struct, inline, flatten, arrays_zip,
#         higher-order functions (transform, filter, exists, aggregate)
#
# These semi-structured operations are heavily tested for JSON / nested-data
# pipelines — very common in FAANG / Databricks / lakehouse interviews.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ Delta tables and JSON files with nested schemas are native to Databricks.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"

# Build an array column from the pipe-delimited tags string for the demos below.
df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df = df.withColumn("tag_arr", F.split("tags", r"\|"))
df.createOrReplaceTempView("df")

# ==============================================================================
# array — build an array column from multiple column values or literals
# ==============================================================================
spark.sql("SELECT id, ARRAY(name, city) AS arr FROM df").show(5, False)
df.select("id", F.array("name", "city").alias("arr")).show(5, False)

# ==============================================================================
# array_contains — check membership in an array
# ==============================================================================
# INTERVIEW Q: "How do you filter rows where a tag array includes 'cardio'?"
#   → array_contains(array_col, value) → boolean Column
spark.sql(r"SELECT id, tags, ARRAY_CONTAINS(SPLIT(tags,'\\|'), 'cardio') AS has_cardio FROM df").show(5)
df.select("id", "tag_arr", F.array_contains("tag_arr", "cardio").alias("has_cardio")).show(5)

# ==============================================================================
# size — number of elements in an array (or map)
# ==============================================================================
spark.sql(r"SELECT id, SIZE(SPLIT(tags,'\\|')) AS n_tags FROM df").show(5)
df.select("id", F.size("tag_arr").alias("n_tags")).show(5)

# ==============================================================================
# explode — one row per array element
# ==============================================================================
# INTERVIEW Q: "explode vs explode_outer?"
#   explode       → drops rows where the array is NULL or empty.
#   explode_outer → keeps those rows, emitting NULL for the element value.
spark.sql(r"SELECT id, EXPLODE(SPLIT(tags,'\\|')) AS tag FROM df").show(20)
df.select("id", F.explode("tag_arr").alias("tag")).show(20)
df.select("id", F.explode_outer("tag_arr").alias("tag")).show(20)

# ==============================================================================
# posexplode — explode WITH the element's 0-based position/index
# ==============================================================================
# Useful when you need to know WHERE in the array the element appeared.
spark.sql(r"SELECT id, POSEXPLODE(SPLIT(tags,'\\|')) AS (pos, tag) FROM df").show(20)
df.select("id", F.posexplode("tag_arr").alias("pos", "tag")).show(20)

# ==============================================================================
# map / map_keys / map_values
# ==============================================================================
# INTERVIEW Q: "How do you create a map (key→value) column in Spark?"
#   → create_map(key_col, value_col, ...) alternates keys and values.
spark.sql("SELECT id, MAP(category, calories) AS m FROM df").show(5, False)
dmap = df.select("id", F.create_map(col("category"), col("calories")).alias("m"))
dmap.show(5, False)
dmap.createOrReplaceTempView("dmap")

spark.sql("SELECT id, MAP_KEYS(m) AS ks, MAP_VALUES(m) AS vs FROM dmap").show(5, False)
dmap.select("id", F.map_keys("m").alias("ks"), F.map_values("m").alias("vs")).show(5, False)

# ==============================================================================
# struct / named_struct — group columns into a nested record (row type)
# ==============================================================================
# INTERVIEW Q: "When do you use struct in Spark?"
#   → To nest related fields together (e.g. address.city, address.zip).
#     Common when writing Parquet/Delta with nested schemas or building APIs.
spark.sql("SELECT id, STRUCT(name, city) AS person FROM df").show(5, False)
df.select("id", F.struct("name", "city").alias("person")).show(5, False)

# named_struct → assign explicit field names in SQL
spark.sql("SELECT id, NAMED_STRUCT('who', name, 'where', city) AS person FROM df").show(5, False)
df.select(
    "id",
    F.struct(col("name").alias("who"), col("city").alias("where")).alias("person"),
).show(5, False)

# ==============================================================================
# inline — explode an array<struct> into multiple rows AND multiple columns
# ==============================================================================
arr_struct = df.select(
    "id",
    F.array(
        F.struct(col("activity").alias("act"), col("calories").alias("cal"))
    ).alias("events"),
)
arr_struct.createOrReplaceTempView("arr_struct")
spark.sql("SELECT id, INLINE(events) FROM arr_struct").show(10, False)
arr_struct.select("id", F.explode("events").alias("e")).select("id", "e.*").show(10, False)

# ==============================================================================
# flatten — array<array<T>> → array<T>
# ==============================================================================
spark.sql("SELECT FLATTEN(ARRAY(ARRAY(1,2), ARRAY(3,4))) AS flat").show(1, False)
df.select(
    F.flatten(F.array(F.array(F.lit(1), F.lit(2)), F.array(F.lit(3), F.lit(4)))).alias("flat")
).limit(1).show(False)

# ==============================================================================
# arrays_zip — merge multiple arrays element-wise into array<struct>
# ==============================================================================
zipped = df.select(
    "id",
    F.arrays_zip(F.split("tags", r"\|"), F.array("activity")).alias("zipped"),
)
zipped.show(5, False)

# ==============================================================================
# Higher-order functions — transform / filter / exists / aggregate
# ==============================================================================
# INTERVIEW Q: "Why prefer higher-order functions over UDFs for array operations?"
#   → Higher-order functions (transform, filter, exists, aggregate) stay inside
#     Catalyst's optimizer — no Python serialization overhead.
#   → Python UDFs are black boxes; they break Catalyst optimization and pay a
#     row-by-row serialization cost. Always use built-ins or higher-order first.

# transform — apply an expression to every element (uppercase each tag)
spark.sql(r"SELECT id, TRANSFORM(SPLIT(tags,'\\|'), x -> UPPER(x)) AS up FROM df").show(5, False)
df.select("id", F.transform("tag_arr", lambda x: F.upper(x)).alias("up")).show(5, False)

# filter — keep only elements matching a predicate
spark.sql(r"SELECT id, FILTER(SPLIT(tags,'\\|'), x -> x = 'cardio') AS only FROM df").show(5, False)
df.select("id", F.filter("tag_arr", lambda x: x == "cardio").alias("only")).show(5, False)

# exists — return True if any element matches
spark.sql(r"SELECT id, EXISTS(SPLIT(tags,'\\|'), x -> x = 'cardio') AS has_cardio FROM df").show(5, False)
df.select("id", F.exists("tag_arr", lambda x: x == "cardio").alias("has_cardio")).show(5, False)

# aggregate — reduce an array to a scalar
spark.sql(r"SELECT id, AGGREGATE(SPLIT(tags,'\\|'), 0, (acc, x) -> acc + LENGTH(x)) AS total_len FROM df").show(5, False)
df.select(
    "id",
    F.aggregate("tag_arr", F.lit(0), lambda acc, x: acc + F.length(x)).alias("total_len"),
).show(5, False)
