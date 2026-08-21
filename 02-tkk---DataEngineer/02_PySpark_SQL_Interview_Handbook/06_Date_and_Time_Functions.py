# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 06: DATE & TIME FUNCTIONS
# ================================================================================
# Topics: current_date, current_timestamp, to_date, date_format, date_add,
#         date_sub, datediff, months_between, last_day, next_day,
#         year, month, day, weekofyear, quarter, unix_timestamp, from_unixtime
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ Databricks uses Spark 3.x date semantics by default.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col

DATASETS = "/FileStore/tables/interview_handbook"
DF_CSV   = f"{DATASETS}/df.csv"

# Parse the string date column to a proper DateType at read time.
df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df = df.withColumn("adate", F.to_date("activity_date", "yyyy-MM-dd"))
df.createOrReplaceTempView("df")

# ==============================================================================
# current_date / current_timestamp
# ==============================================================================
# INTERVIEW Q: "What is the difference between current_date and current_timestamp?"
#   current_date()      → date only (no time component), type DATE
#   current_timestamp() → date + time, type TIMESTAMP; timezone-aware in Spark 3.x
spark.sql("SELECT CURRENT_DATE() AS today, CURRENT_TIMESTAMP() AS now").show(1, truncate=False)
df.select(F.current_date().alias("today"), F.current_timestamp().alias("now")).limit(1).show(1, truncate=False)

# ==============================================================================
# to_date — parse a string into a DateType with a format pattern
# ==============================================================================
# INTERVIEW Q: "What happens if the format doesn't match?"
#   → Returns NULL silently in lenient mode (default). Use try_to_date() in SQL
#     (Spark 3.4+) to return NULL instead of error on bad formats.
spark.sql("SELECT activity_date, TO_DATE(activity_date, 'yyyy-MM-dd') AS d FROM df").show(5)
df.select("activity_date", F.to_date("activity_date", "yyyy-MM-dd").alias("d")).show(5)

# ==============================================================================
# date_format — format a DateType back to a string
# ==============================================================================
# Common format patterns:
#   'yyyy-MM-dd'  → 2024-03-15
#   'dd/MM/yyyy'  → 15/03/2024
#   'yyyy-MM'     → 2024-03    (monthly bucket — great for groupBy)
#   'EEEE'        → Monday     (full weekday name)
#   'MMM'         → Mar        (short month name)
spark.sql("SELECT adate, DATE_FORMAT(adate, 'dd/MM/yyyy') AS fmt FROM df").show(5)
df.select("adate", F.date_format("adate", "dd/MM/yyyy").alias("fmt")).show(5)
df.select("adate", F.date_format("adate", "EEEE").alias("weekday")).show(5)

# ==============================================================================
# date_add / date_sub — shift a date by N days
# ==============================================================================
spark.sql("""
    SELECT adate,
           DATE_ADD(adate, 7)  AS plus7,
           DATE_SUB(adate, 3)  AS minus3
    FROM df
""").show(5)

df.select(
    "adate",
    F.date_add("adate", 7).alias("plus7"),
    F.date_sub("adate", 3).alias("minus3"),
).show(5)

# ==============================================================================
# datediff — difference in DAYS (end_date, start_date)
# ==============================================================================
# INTERVIEW TRAP: Argument order is (end, start) — positive if end is after start.
spark.sql("SELECT adate, DATEDIFF(CURRENT_DATE(), adate) AS days_ago FROM df").show(5)
df.select("adate", F.datediff(F.current_date(), col("adate")).alias("days_ago")).show(5)

# ==============================================================================
# months_between — fractional months between two dates
# ==============================================================================
# Returns a decimal — 1.5 means 1 month and 15 days.
# round() if you need whole months.
spark.sql("SELECT adate, MONTHS_BETWEEN(CURRENT_DATE(), adate) AS months FROM df").show(5)
df.select("adate", F.months_between(F.current_date(), col("adate")).alias("months")).show(5)

# ==============================================================================
# last_day / next_day
# ==============================================================================
# INTERVIEW Q: "How do you find the end-of-month date?"
#   → LAST_DAY(date) — works for any month length (28/29/30/31).
spark.sql("SELECT adate, LAST_DAY(adate) AS month_end FROM df").show(5)
df.select("adate", F.last_day("adate").alias("month_end")).show(5)

spark.sql("SELECT adate, NEXT_DAY(adate, 'Monday') AS next_mon FROM df").show(5)
df.select("adate", F.next_day("adate", "Mon").alias("next_mon")).show(5)

# ==============================================================================
# Date parts: year / month / day / dayofweek / weekofyear / quarter
# ==============================================================================
# INTERVIEW Q: "How do you extract the year and month for a monthly trend report?"
#   → DATE_FORMAT(date, 'yyyy-MM') or YEAR(date)/MONTH(date) separately.
spark.sql("""
    SELECT adate,
           YEAR(adate)       AS y,
           MONTH(adate)      AS m,
           DAY(adate)        AS d,
           DAYOFWEEK(adate)  AS dow,
           WEEKOFYEAR(adate) AS woy,
           QUARTER(adate)    AS q
    FROM df
""").show(5)

df.select(
    "adate",
    F.year("adate").alias("y"),
    F.month("adate").alias("m"),
    F.dayofmonth("adate").alias("d"),     # Note: dayofmonth() in DataFrame API (not day())
    F.dayofweek("adate").alias("dow"),    # 1=Sunday, 7=Saturday (SQL standard)
    F.weekofyear("adate").alias("woy"),
    F.quarter("adate").alias("q"),
).show(5)

# ==============================================================================
# unix_timestamp / from_unixtime — convert between dates and epoch seconds
# ==============================================================================
# INTERVIEW Q: "Why store timestamps as epoch integers?"
#   → Timezone-neutral, simple arithmetic (subtract to get duration),
#     commonly used in event logs and streaming systems.
spark.sql("""
    SELECT adate,
           UNIX_TIMESTAMP(adate) AS epoch,
           FROM_UNIXTIME(UNIX_TIMESTAMP(adate), 'yyyy-MM-dd HH:mm:ss') AS back
    FROM df
""").show(5, truncate=False)

df.select(
    "adate",
    F.unix_timestamp("adate").alias("epoch"),
    F.from_unixtime(F.unix_timestamp("adate"), "yyyy-MM-dd HH:mm:ss").alias("back"),
).show(5, truncate=False)

# ==============================================================================
# Interview pattern: monthly bucketing — count records per month
# ==============================================================================
# INTERVIEW Q: "How do you build a monthly trend report in Spark?"
#   → DATE_FORMAT(date, 'yyyy-MM') as the group key, then COUNT/SUM.
spark.sql("""
    SELECT DATE_FORMAT(adate, 'yyyy-MM') AS ym, COUNT(*) AS n
    FROM df
    GROUP BY DATE_FORMAT(adate, 'yyyy-MM')
    ORDER BY ym
""").show()

df.groupBy(F.date_format("adate", "yyyy-MM").alias("ym")).count().orderBy("ym").show()
