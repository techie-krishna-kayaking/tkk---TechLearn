# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 01: BASICS
# ================================================================================
# Topics: Reading (CSV/JSON/Parquet/ORC/Delta), Schema, select, filter,
#         cast, alias, lit, expr, col, distinct, sort, CASE WHEN, NULL handling.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — never create or stop a SparkSession here.
#   ✓ Use display(df) for a rich table view; show() also works in notebooks.
#   ✓ Upload the datasets folder to DBFS (Data → Add Data → DBFS) first.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col, lit, expr
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

# ── Set these to where you uploaded the CSVs in DBFS ─────────────────────────
DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"
OUTPUT   = "/FileStore/tables/interview_handbook_output/01_basics"

# ==============================================================================
# READING — CSV with inferred schema
# ==============================================================================
# INTERVIEW Q: "Why is inferSchema risky in production?"
#   → Triggers a full extra scan to guess types. A leading-zero string "01" may
#     silently become int 1. Always define an explicit schema for prod pipelines.
#
# header=True      → first row becomes column names
# inferSchema=True → Spark reads ALL data to guess types (extra job!)
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(DF_CSV)
)

# createOrReplaceTempView → registers the DF as a SQL-queryable temp table.
# INTERVIEW Q: "How do you run SQL against a DataFrame?"
#   → createOrReplaceTempView("name"), then spark.sql("SELECT ... FROM name")
#     The view lives until the SparkSession ends (or you drop it).
df.createOrReplaceTempView("df")
display(df)

# ==============================================================================
# READING — explicit schema (production best practice)
# ==============================================================================
# INTERVIEW Q: "StructType vs inferSchema — pros/cons?"
#   StructType  → no extra scan, type-safe, deterministic → use in production.
#   inferSchema → convenient for quick exploration on small data.
#
# StructType  → ordered list of columns
# StructField → (columnName, dataType, nullable)
schema = StructType([
    StructField("id",            IntegerType(), True),
    StructField("name",          StringType(),  True),
    StructField("category",      StringType(),  True),
    StructField("activity",      StringType(),  True),
    StructField("calories",      IntegerType(), True),
    StructField("duration_min",  IntegerType(), True),
    StructField("activity_date", StringType(),  True),
    StructField("city",          StringType(),  True),
    StructField("tags",          StringType(),  True),
])
df_explicit = spark.read.option("header", True).schema(schema).csv(DF_CSV)
display(df_explicit)

# ==============================================================================
# READING — JSON / Parquet / ORC / Delta
# ==============================================================================
# INTERVIEW Q: "Which file format do you prefer and why?"
#   CSV / JSON  → row-based, human-readable, slow for analytics, no pushdown.
#   Parquet     → columnar, splittable, compressed, schema embedded.
#                 THE standard for analytics on Spark / cloud lakehouses.
#   ORC         → columnar like Parquet; dominant in Hive/Hadoop ecosystem.
#   Delta       → Parquet + ACID + time travel + schema enforcement.
#                 The native Databricks format; always prefer Delta in production.

df.write.mode("overwrite").json(f"{OUTPUT}/json")
df.write.mode("overwrite").parquet(f"{OUTPUT}/parquet")
df.write.mode("overwrite").orc(f"{OUTPUT}/orc")

display(spark.read.json(f"{OUTPUT}/json").limit(3))
display(spark.read.parquet(f"{OUTPUT}/parquet").limit(3))
display(spark.read.orc(f"{OUTPUT}/orc").limit(3))

# Delta is natively supported in Databricks — no extra library needed.
df.write.format("delta").mode("overwrite").save(f"{OUTPUT}/delta")
display(spark.read.format("delta").load(f"{OUTPUT}/delta").limit(3))

# ==============================================================================
# SCHEMA INSPECTION
# ==============================================================================
# INTERVIEW Q: "How do you inspect a DataFrame's structure?"
#   printSchema() → human-readable column tree
#   .schema       → StructType Python object (useful for programmatic checks)
#   .columns      → list[str]
#   .dtypes       → list[(columnName, typeString)]
df.printSchema()
print("columns:", df.columns)
print("dtypes :", df.dtypes)

# ==============================================================================
# SELECT — specific columns (4 equivalent DataFrame styles)
# ==============================================================================
# INTERVIEW Q: "What is the difference between col(), df['col'], and string names?"
#   All resolve to the same column; col() / df['col'] return a Column *object*
#   which supports method chaining (.alias, .cast, .asc, .desc, etc.).
spark.sql("SELECT id, name, calories FROM df").show(3)
df.select("id", "name", "calories").show(3)                    # string names
df.select(col("id"), col("name"), col("calories")).show(3)     # col() objects
df.select(df["id"], df["name"], df["calories"]).show(3)        # bracket syntax

# ==============================================================================
# selectExpr — SQL expression strings inside the DataFrame API
# ==============================================================================
# INTERVIEW Q: "When do you use selectExpr over select?"
#   selectExpr accepts raw SQL strings → great for quick expressions without imports.
spark.sql("SELECT id, calories * 2 AS calories_x2 FROM df").show(3)
df.selectExpr("id", "calories * 2 AS calories_x2").show(3)

# ==============================================================================
# ALIAS — rename a column
# ==============================================================================
spark.sql("SELECT name AS person FROM df").show(3)
df.select(col("name").alias("person")).show(3)

# ==============================================================================
# CAST — change a column's data type
# ==============================================================================
# INTERVIEW TRAP: Casting an invalid string to IntegerType returns NULL silently.
#   Always validate row counts before and after cast in production.
spark.sql("SELECT CAST(calories AS DOUBLE) AS calories_d FROM df").show(3)
df.select(col("calories").cast("double").alias("calories_d")).show(3)

# ==============================================================================
# lit / expr / col
# ==============================================================================
# INTERVIEW Q: "What is lit() for?"
#   lit() wraps a Python scalar into a Spark Column constant.
#   F.concat(col("name"), lit(" Jr.")) — without lit(), the string " Jr." fails.
df.select(
    col("id"),
    lit("fitness").alias("domain"),              # constant column
    expr("calories + duration_min AS effort"),   # SQL string → Column
).show(3)

# ==============================================================================
# DROP / DISTINCT / dropDuplicates / LIMIT / SAMPLE
# ==============================================================================
# INTERVIEW Q: "distinct() vs dropDuplicates()?"
#   distinct()          → dedup across ALL columns; triggers a full shuffle.
#   dropDuplicates([c]) → dedup on a SUBSET of columns; keeps the first occurrence.
df.drop("tags", "activity_date").show(3)
df.select("category").distinct().show()
df.dropDuplicates(["name"]).select("name").show()
df.limit(3).show()
train, test = df.randomSplit([0.7, 0.3], seed=42)
print("train:", train.count(), "test:", test.count())

# ==============================================================================
# ACTIONS — show / head / take / first / collect / count
# ==============================================================================
# INTERVIEW Q: "Transformations vs Actions?"
#   Transformations (select, filter, join, groupBy) → LAZY, build the DAG only.
#   Actions (show, count, collect, write)           → TRIGGER execution.
#
# TRAP: collect() pulls EVERY row to the driver → OOM on large data!
#       Cache the DF if you need to call multiple actions on it.
print("head(2) :", df.head(2))
print("first() :", df.first())
print("count() :", df.count())

# ==============================================================================
# describe / summary
# ==============================================================================
# INTERVIEW Q: "describe() vs summary()?"
#   describe() → count, mean, stddev, min, max
#   summary()  → same but you choose which statistics (supports percentiles)
df.describe("calories", "duration_min").show()
df.summary("count", "min", "25%", "50%", "75%", "max").show()

# ==============================================================================
# SORTING — sort / orderBy / asc / desc
# ==============================================================================
# INTERVIEW Q: "sort() vs orderBy() vs sortWithinPartitions()?"
#   sort() and orderBy() are ALIASES — both trigger a global sort (full shuffle).
#   sortWithinPartitions() sorts each partition independently — cheaper, no shuffle.
spark.sql("SELECT id, calories FROM df ORDER BY calories DESC").show(5)
df.orderBy(col("calories").desc()).select("id", "calories").show(5)
df.sort(F.desc("calories")).select("id", "calories").show(5)
# Multi-key sort with explicit null placement
df.orderBy(col("category").asc(), col("calories").desc_nulls_last()).select("category","calories").show(5)

# ==============================================================================
# FILTERING — WHERE / filter (aliases)
# ==============================================================================
# INTERVIEW Q: "filter() vs where()?"
#   Exact aliases. Both accept a Column condition OR a SQL string predicate.
#
# TRAP: Use & | ~ for AND/OR/NOT on Column objects — NOT Python and/or/not.
#       Always parenthesize each condition: & | ~ have low precedence in Python.
spark.sql("SELECT * FROM df WHERE category = 'Exercise'").show()
df.filter(col("category") == "Exercise").show()
df.where("category = 'Exercise'").show()

df.filter((col("category") == "Exercise") & (col("calories") > 400)).show()
df.filter((col("category") == "Sleep")    | (col("calories") > 500)).show()
df.filter(~(col("category") == "Exercise")).show()   # NOT

# ==============================================================================
# LIKE / IN / BETWEEN / IS NULL / CASE WHEN
# ==============================================================================
# TRAP (NOT IN): Returns no rows if any value in the list is NULL (3-valued logic).
#                Prefer NOT EXISTS subquery or left_anti join instead.
spark.sql("SELECT * FROM df WHERE name LIKE 'A%'").show()
df.filter(col("name").like("A%")).show()

spark.sql("SELECT * FROM df WHERE city IN ('Boston', 'Seattle')").show()
df.filter(col("city").isin("Boston", "Seattle")).show()
df.filter(~col("city").isin("Boston", "Seattle")).show()

spark.sql("SELECT * FROM df WHERE duration_min BETWEEN 30 AND 60").show()
df.filter(col("duration_min").between(30, 60)).show()

# TRAP (NULL): col == None uses Python equality, not SQL IS NULL → always wrong.
spark.sql("SELECT * FROM df WHERE calories IS NULL").show()
df.filter(col("calories").isNull()).show()
df.filter(col("calories").isNotNull()).show()

# INTERVIEW Q: "How do you write CASE WHEN in the DataFrame API?"
#   F.when(cond, val).when(cond, val).otherwise(default)
#   Each .when() is an ELIF branch; .otherwise() is the final ELSE.
spark.sql("""
    SELECT id, calories,
        CASE
            WHEN calories IS NULL THEN 'unknown'
            WHEN calories >= 500  THEN 'high'
            WHEN calories >= 300  THEN 'medium'
            ELSE 'low'
        END AS intensity
    FROM df
""").show()

df.select(
    "id", "calories",
    F.when(col("calories").isNull(), "unknown")
     .when(col("calories") >= 500, "high")
     .when(col("calories") >= 300, "medium")
     .otherwise("low")
     .alias("intensity"),
).show()
