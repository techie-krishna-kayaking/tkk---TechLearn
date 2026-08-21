# ============================================================
# CHAPTER 4: PYSPARK
# Practice in: Databricks
# Topics: RDD vs DataFrame, transformations, actions,
#         joins, aggregations, window functions, optimization
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import *

# In Databricks, 'spark' is already available — no need to create session
# spark = SparkSession.builder.appName("DA_Practice").getOrCreate()

# ============================================================
# SECTION 1: Create Sample DataFrames
# ============================================================

# employees
emp_data = [
    (1, "Alice",   "Eng",   90000, "2018-01-15"),
    (2, "Bob",     "Eng",   85000, "2019-03-10"),
    (3, "Charlie", "Sales", 70000, "2020-06-01"),
    (4, "Diana",   "Sales", 75000, "2017-11-20"),
    (5, "Eve",     "HR",    60000, "2021-02-28"),
    (6, "Frank",   "HR",    62000, "2022-08-15"),
]
emp_schema = ["emp_id", "name", "dept", "salary", "hire_date"]
emp_df = spark.createDataFrame(emp_data, emp_schema)

# orders
order_data = [
    (101, 1, "2024-01-10", 500,  "North"),
    (102, 2, "2024-01-15", 1200, "South"),
    (103, 1, "2024-02-05", 800,  "North"),
    (104, 3, "2024-02-20", 300,  "East"),
    (105, 2, "2024-03-01", 950,  "South"),
    (106, 4, "2024-03-15", 1500, "West"),
    (107, 1, "2024-04-02", 700,  "North"),
]
order_schema = ["order_id", "customer_id", "order_date", "amount", "region"]
order_df = spark.createDataFrame(order_data, order_schema)

emp_df.show()
order_df.show()

# ============================================================
# SECTION 2: Core Transformations (Lazy — no execution yet)
# ============================================================

# select, filter, withColumn, drop
high_earners = (emp_df
    .filter(F.col("salary") > 70000)
    .select("name", "dept", "salary")
    .withColumn("salary_lakhs", F.round(F.col("salary") / 100000, 2))
)
high_earners.show()

# Column expressions
emp_df2 = emp_df \
    .withColumn("hire_date", F.to_date("hire_date")) \
    .withColumn("years_exp", F.round(F.datediff(F.current_date(), F.col("hire_date")) / 365.25, 1)) \
    .withColumn("salary_tier",
                F.when(F.col("salary") >= 85000, "Senior")
                 .when(F.col("salary") >= 70000, "Mid")
                 .otherwise("Junior"))
emp_df2.show()

# ============================================================
# SECTION 3: groupBy & Aggregations
# ============================================================

dept_stats = emp_df.groupBy("dept").agg(
    F.count("emp_id").alias("headcount"),
    F.avg("salary").alias("avg_salary"),
    F.max("salary").alias("max_salary"),
    F.sum("salary").alias("total_payroll")
)
dept_stats.show()

# Orders: monthly revenue
order_df2 = order_df.withColumn("order_date", F.to_date("order_date")) \
                    .withColumn("month", F.date_format("order_date", "yyyy-MM"))

monthly_rev = order_df2.groupBy("month", "region") \
                        .agg(F.sum("amount").alias("total_revenue")) \
                        .orderBy("month", "region")
monthly_rev.show()

# ============================================================
# SECTION 4: Joins
# ============================================================

# Inner join: orders + (customer info from emp as proxy)
joined = order_df2.join(
    emp_df.select("emp_id", "name", "dept"),
    order_df2["customer_id"] == emp_df["emp_id"],
    how="left"
)
joined.show()

# Join types: inner, left, right, full, left_semi, left_anti
# left_semi  → like WHERE EXISTS
# left_anti  → like WHERE NOT EXISTS

# Find employees who NEVER placed an order (anti join)
no_orders = emp_df.join(order_df, emp_df["emp_id"] == order_df["customer_id"], "left_anti")
no_orders.show()

# ============================================================
# SECTION 5: Window Functions (CRITICAL)
# ============================================================

# RANK within department by salary
window_dept = Window.partitionBy("dept").orderBy(F.desc("salary"))

emp_ranked = emp_df.withColumn("rank",       F.rank().over(window_dept)) \
                   .withColumn("dense_rank", F.dense_rank().over(window_dept)) \
                   .withColumn("row_num",    F.row_number().over(window_dept))
emp_ranked.show()

# Top 1 per dept
top_per_dept = emp_ranked.filter(F.col("dense_rank") == 1)
top_per_dept.show()

# Running total of orders per customer
window_cust = Window.partitionBy("customer_id").orderBy("order_date") \
                    .rowsBetween(Window.unboundedPreceding, Window.currentRow)

order_running = order_df2.withColumn("running_total", F.sum("amount").over(window_cust))
order_running.show()

# LAG / LEAD: MoM revenue comparison
window_month = Window.orderBy("month")
monthly_total = order_df2.groupBy("month").agg(F.sum("amount").alias("revenue")) \
                          .orderBy("month")

monthly_lag = monthly_total \
    .withColumn("prev_revenue", F.lag("revenue", 1).over(window_month)) \
    .withColumn("mom_change",   F.col("revenue") - F.col("prev_revenue"))
monthly_lag.show()

# ============================================================
# SECTION 6: Performance Optimization Tips (Interview must-know)
# ============================================================

# 1. AVOID SHUFFLES where possible
#    Bad:  df.orderBy("col")          — global sort = shuffle
#    Good: df.sortWithinPartitions()  — local sort

# 2. BROADCAST JOIN — small table (< few hundred MB)
from pyspark.sql.functions import broadcast

small_lookup = spark.createDataFrame([("North", "N"), ("South", "S")], ["region", "code"])
joined_broadcast = order_df.join(broadcast(small_lookup), on="region", how="left")
# Avoids shuffle on the large table

# 3. CACHE / PERSIST — reused DataFrames
emp_df.cache()    # in memory
emp_df.persist()  # configurable storage level
# emp_df.unpersist()  # free memory after use

# 4. REPARTITION vs COALESCE
#    repartition(n) — full shuffle, can increase or decrease
#    coalesce(n)    — no full shuffle, only decrease
df_repartitioned = order_df.repartition(4, "region")  # partition by region for filter perf
df_coalesced     = order_df.coalesce(2)                # reduce partitions before write

# 5. PREDICATE PUSHDOWN — filter early, before joins
#    Push filters close to data source → less data shuffled

# 6. ADAPTIVE QUERY EXECUTION (AQE) — Databricks default ON
#    Auto-optimizes shuffle partitions, join strategies at runtime

# 7. PARTITIONING on write — for large tables
# order_df.write.partitionBy("region").parquet("/mnt/output/orders/")

# 8. DELTA LAKE — Z-ORDER for multi-column filtering
# OPTIMIZE orders ZORDER BY (customer_id, order_date)

# ============================================================
# SECTION 7: SQL on Spark (Databricks style)
# ============================================================

emp_df.createOrReplaceTempView("employees")
order_df.createOrReplaceTempView("orders")

result = spark.sql("""
    SELECT
        e.dept,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.amount)              AS total_revenue,
        AVG(o.amount)              AS avg_order_value
    FROM orders o
    LEFT JOIN employees e ON o.customer_id = e.emp_id
    GROUP BY e.dept
    ORDER BY total_revenue DESC
""")
result.show()

print("✅ Chapter 4: PySpark complete!")
