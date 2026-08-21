# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 05: JOINS
# ================================================================================
# Topics: Inner, Left/Right/Full Outer, Cross, Left Semi, Left Anti,
#         Self join, Broadcast join, Multi-column join, Complex (non-equi) join
#
# Datasets: cust.csv JOIN prod.csv on cust_id
#   cust_id 106-108 → have NO orders (shows up in left/full outer)
#   order cust_id 109 → has NO customer (shows up in right/full outer)
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ broadcast() hint is available from pyspark.sql.functions.
#
# Golden rule: SQL first → then the equivalent DataFrame API.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.functions import col, broadcast

DATASETS = "/FileStore/tables/interview_handbook"

cust = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/cust.csv")
prod = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/prod.csv")
cust.createOrReplaceTempView("cust")
prod.createOrReplaceTempView("prod")

# ==============================================================================
# INNER JOIN — only rows that match on both sides
# ==============================================================================
# INTERVIEW Q: "What is an inner join?"
#   → Returns rows where the join condition is met in BOTH tables.
#     Non-matching rows from either side are dropped.
spark.sql("""
    SELECT c.cust_id, c.cust_name, p.product, p.amount
    FROM cust c JOIN prod p ON c.cust_id = p.cust_id
""").show()

cust.join(prod, cust.cust_id == prod.cust_id, "inner") \
    .select(cust.cust_id, "cust_name", "product", "amount").show()

# ==============================================================================
# LEFT (OUTER) JOIN — all left rows; NULLs where no match on the right
# ==============================================================================
# INTERVIEW Q: "When would you use a left join?"
#   → "Give me all customers WITH OR WITHOUT orders." NULLs in order columns
#     indicate a customer with no purchase — use this to find inactive customers.
spark.sql("""
    SELECT c.cust_id, c.cust_name, p.product, p.amount
    FROM cust c LEFT JOIN prod p ON c.cust_id = p.cust_id
""").show()

# Pass key as a string list to avoid duplicate cust_id column in result
cust.join(prod, "cust_id", "left").select("cust_id", "cust_name", "product", "amount").show()

# ==============================================================================
# RIGHT (OUTER) JOIN — all right rows; NULLs where no match on the left
# ==============================================================================
spark.sql("""
    SELECT c.cust_id, c.cust_name, p.product
    FROM cust c RIGHT JOIN prod p ON c.cust_id = p.cust_id
""").show()
cust.join(prod, "cust_id", "right").select("cust_id", "cust_name", "product").show()

# ==============================================================================
# FULL (OUTER) JOIN — everything from both sides; NULLs where no match
# ==============================================================================
spark.sql("""
    SELECT c.cust_id AS c_id, p.cust_id AS p_id, c.cust_name, p.product
    FROM cust c FULL OUTER JOIN prod p ON c.cust_id = p.cust_id
""").show()
cust.join(prod, "cust_id", "full").select("cust_id", "cust_name", "product").show()

# ==============================================================================
# CROSS JOIN — cartesian product (all combinations of left × right)
# ==============================================================================
# INTERVIEW TRAP: Cross join produces N×M rows. Dangerous on large datasets.
#   Spark requires either crossJoin() or enableCrossJoin config to allow it.
#   Use it only when you genuinely need every combination (e.g. date × product grid).
small_c = cust.limit(2)
small_p = prod.limit(2)
small_c.createOrReplaceTempView("small_c")
small_p.createOrReplaceTempView("small_p")
spark.sql("SELECT small_c.cust_name, small_p.product FROM small_c CROSS JOIN small_p").show()
small_c.crossJoin(small_p).select("cust_name", "product").show()

# ==============================================================================
# LEFT SEMI JOIN — left rows that HAVE a match (no right columns returned)
# ==============================================================================
# INTERVIEW Q: "Semi join vs inner join?"
#   → Semi join returns only LEFT columns; inner join returns columns from both sides.
#     Semi join is equivalent to WHERE EXISTS and is more efficient than
#     inner join + distinct when you only need left-side columns.
spark.sql("""
    SELECT * FROM cust c
    WHERE EXISTS (SELECT 1 FROM prod p WHERE p.cust_id = c.cust_id)
""").show()
cust.join(prod, "cust_id", "left_semi").show()

# ==============================================================================
# LEFT ANTI JOIN — left rows with NO match (WHERE NOT EXISTS)
# ==============================================================================
# INTERVIEW Q: "How do you find customers who have never placed an order?"
#   → Left anti join: keep only left rows where the join key has NO match on the right.
#
# TRAP: NOT IN with nullable right-side column returns 0 rows if any value is NULL.
#       Anti join handles NULLs correctly — always prefer it over NOT IN.
spark.sql("""
    SELECT * FROM cust c
    WHERE NOT EXISTS (SELECT 1 FROM prod p WHERE p.cust_id = c.cust_id)
""").show()
cust.join(prod, "cust_id", "left_anti").show()

# ==============================================================================
# SELF JOIN — join a table to itself
# ==============================================================================
# INTERVIEW Q: "When do you use a self join?"
#   → Find pairs within the same group, compare a row to others in the same table,
#     or traverse hierarchies (employee → manager in the same employees table).
spark.sql("""
    SELECT a.cust_name AS name_a, b.cust_name AS name_b, a.city
    FROM cust a JOIN cust b
      ON a.city = b.city AND a.cust_id < b.cust_id
""").show()

a = cust.alias("a")
b = cust.alias("b")
a.join(b, (col("a.city") == col("b.city")) & (col("a.cust_id") < col("b.cust_id"))) \
 .select(col("a.cust_name").alias("name_a"), col("b.cust_name").alias("name_b"), col("a.city")).show()

# ==============================================================================
# BROADCAST JOIN — replicate the small table to every executor (shuffle-free)
# ==============================================================================
# INTERVIEW Q: "What is a broadcast join and when does Spark use it automatically?"
#   → Spark copies the small table to every executor so the large table is NEVER shuffled.
#   → Auto-triggered when a table is smaller than spark.sql.autoBroadcastJoinThreshold (10MB).
#   → Use the broadcast() hint to force it even when above the threshold.
#   → TRAP: Broadcasting a table that is too large → driver/executor OOM.
spark.sql("""
    SELECT /*+ BROADCAST(c) */ c.cust_name, p.product
    FROM cust c JOIN prod p ON c.cust_id = p.cust_id
""").show()
prod.join(broadcast(cust), "cust_id").select("cust_name", "product").show()

# ==============================================================================
# MULTI-COLUMN JOIN — join on more than one key
# ==============================================================================
# Passing a list deduplicates the join columns in the result (no ambiguous names).
prod2 = prod.withColumn("city", F.lit("New York"))
prod2.createOrReplaceTempView("prod2")
spark.sql("""
    SELECT c.cust_name, p.product
    FROM cust c JOIN prod2 p
      ON c.cust_id = p.cust_id AND c.city = p.city
""").show()
cust.join(prod2, ["cust_id", "city"], "inner").select("cust_name", "product").show()

# ==============================================================================
# COMPLEX (NON-EQUI) JOIN — join with a range or inequality condition
# ==============================================================================
# INTERVIEW Q: "What is a non-equi join? Give an example."
#   → A join whose condition includes <, >, BETWEEN, or other non-equality operators.
#   → Example: match orders where the amount falls in a customer's allowed budget range.
#   → Non-equi joins cannot use a hash join; Spark falls back to sort-merge or broadcast.
spark.sql("""
    SELECT c.cust_name, p.product, p.amount
    FROM cust c JOIN prod p
      ON c.cust_id = p.cust_id AND p.amount BETWEEN 20 AND 130
""").show()
cond = (cust.cust_id == prod.cust_id) & (prod.amount.between(20, 130))
cust.join(prod, cond, "inner").select("cust_name", "product", "amount").show()
