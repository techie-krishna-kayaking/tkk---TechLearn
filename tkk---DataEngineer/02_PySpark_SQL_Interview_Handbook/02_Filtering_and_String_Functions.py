# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 02: FILTERING & STRING FUNCTIONS
# ================================================================================
# Topics: concat, concat_ws, substring/substr, trim, upper/lower/initcap, length,
#         split, regexp_replace, regexp_extract, translate, repeat, reverse,
#         soundex, levenshtein, coalesce/nvl/ifnull/nullif
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
DF_CSV   = f"{DATASETS}/df.csv"

df = spark.read.option("header", True).option("inferSchema", True).csv(DF_CSV)
df.createOrReplaceTempView("df")

# ==============================================================================
# concat — join columns/strings WITHOUT a separator
# ==============================================================================
# INTERVIEW Q: "concat vs concat_ws?"
#   concat(a, b, c)         → NULL if ANY argument is NULL
#   concat_ws(sep, a, b, c) → skips NULLs cleanly and uses a separator
spark.sql("SELECT id, CONCAT(name, '-', city) AS name_city FROM df").show(5)
df.select("id", F.concat(col("name"), F.lit("-"), col("city")).alias("name_city")).show(5)

# ==============================================================================
# concat_ws — concat WITH a separator (NULL-safe)
# ==============================================================================
spark.sql("SELECT id, CONCAT_WS(' | ', name, category, city) AS combo FROM df").show(5, False)
df.select("id", F.concat_ws(" | ", col("name"), col("category"), col("city")).alias("combo")).show(5, False)

# ==============================================================================
# substring / substr — extract part of a string (1-indexed, NOT 0-indexed!)
# ==============================================================================
# INTERVIEW TRAP: Spark string positions are 1-based (like SQL), NOT 0-based like Python.
spark.sql("SELECT name, SUBSTRING(name, 1, 3) AS first3 FROM df").show(5)
df.select("name", col("name").substr(1, 3).alias("first3")).show(5)
df.select("name", F.substring(col("name"), 1, 3).alias("first3b")).show(5)

# ==============================================================================
# trim / ltrim / rtrim — remove whitespace
# ==============================================================================
padded = df.select(F.lit("   spark   ").alias("s"))
padded.createOrReplaceTempView("padded")
spark.sql("SELECT s, TRIM(s) AS t, LTRIM(s) AS lt, RTRIM(s) AS rt FROM padded LIMIT 1").show(1, truncate=False)
padded.select("s", F.trim("s").alias("t"), F.ltrim("s").alias("lt"), F.rtrim("s").alias("rt")).show(1, truncate=False)

# ==============================================================================
# upper / lower / initcap — case functions
# ==============================================================================
# initcap → Title Case (first letter of EACH word capitalized)
spark.sql("SELECT name, UPPER(name) AS up, LOWER(name) AS lo, INITCAP(activity) AS ic FROM df").show(5)
df.select("name", F.upper("name").alias("up"), F.lower("name").alias("lo"), F.initcap("activity").alias("ic")).show(5)

# ==============================================================================
# length — number of characters in a string
# ==============================================================================
spark.sql("SELECT name, LENGTH(name) AS len FROM df").show(5)
df.select("name", F.length("name").alias("len")).show(5)

# ==============================================================================
# split — string → array by a regex pattern
# ==============================================================================
# INTERVIEW TRAP: split() takes a REGEX, not a plain string.
#   '|' in regex means alternation (match nothing or nothing). Escape it: '\\|'
spark.sql(r"SELECT tags, SPLIT(tags, '\\|') AS tag_arr FROM df").show(5, False)
df.select("tags", F.split("tags", r"\|").alias("tag_arr")).show(5, False)

# ==============================================================================
# regexp_replace — replace substrings by regex pattern
# ==============================================================================
spark.sql("SELECT city, REGEXP_REPLACE(city, ' ', '_') AS city2 FROM df").show(5)
df.select("city", F.regexp_replace("city", " ", "_").alias("city2")).show(5)

# ==============================================================================
# regexp_extract — extract a capture group from a string
# ==============================================================================
# Group 0 = entire match; group 1 = first capture group; etc.
spark.sql("SELECT tags, REGEXP_EXTRACT(tags, '^([a-z]+)', 1) AS first_tag FROM df").show(5)
df.select("tags", F.regexp_extract("tags", r"^([a-z]+)", 1).alias("first_tag")).show(5)

# ==============================================================================
# translate — character-by-character substitution (NOT substring replace)
# ==============================================================================
# INTERVIEW Q: "REPLACE vs TRANSLATE?"
#   REPLACE(str, 'from_str', 'to_str') → replaces a SUBSTRING
#   TRANSLATE(str, 'chars', 'chars')   → maps individual CHARACTERS
spark.sql("SELECT city, REPLACE(city, 'New', 'Old') AS c FROM df").show(5)
df.select("city", F.regexp_replace("city", "New", "Old").alias("c")).show(5)  # DataFrame uses regexp_replace for literal replace

spark.sql("SELECT name, TRANSLATE(name, 'aei', '431') AS leet FROM df").show(5)
df.select("name", F.translate("name", "aei", "431").alias("leet")).show(5)

# ==============================================================================
# repeat / reverse
# ==============================================================================
spark.sql("SELECT REPEAT('ab', 3) AS r, REVERSE(name) AS rev FROM df").show(5)
df.select(F.repeat(F.lit("ab"), 3).alias("r"), F.reverse("name").alias("rev")).show(5)

# ==============================================================================
# soundex — phonetic encoding ("sounds-alike" matching)
# ==============================================================================
# INTERVIEW Q: "When would you use soundex?"
#   → Fuzzy name matching when spellings vary (e.g. "Smith" vs "Smyth").
spark.sql("SELECT name, SOUNDEX(name) AS sx FROM df").show(5)
df.select("name", F.soundex("name").alias("sx")).show(5)

# ==============================================================================
# levenshtein — edit distance between two strings
# ==============================================================================
# INTERVIEW Q: "What is Levenshtein distance used for?"
#   → Fuzzy string matching / deduplication. Lower = more similar.
spark.sql("SELECT name, LEVENSHTEIN(name, 'Alice') AS dist FROM df").show(5)
df.select("name", F.levenshtein("name", F.lit("Alice")).alias("dist")).show(5)

# ==============================================================================
# NULL HANDLING: coalesce / nvl / ifnull / nullif
# ==============================================================================
# INTERVIEW Q: "coalesce vs nvl vs ifnull?"
#   All return the first non-null value. NVL/IFNULL are 2-arg SQL shortcuts.
#   COALESCE is N-arg and available in both SQL and DataFrame API. Prefer coalesce.
#
# INTERVIEW Q: "What does nullif(a, b) do?"
#   Returns NULL if a == b, else returns a. Classic guard for divide-by-zero:
#     amount / NULLIF(qty, 0)  → returns NULL instead of divide-by-zero error.

# coalesce
spark.sql("SELECT id, COALESCE(calories, 0) AS cal FROM df").show(5)
df.select("id", F.coalesce("calories", F.lit(0)).alias("cal")).show(5)

# nvl
spark.sql("SELECT id, NVL(calories, -1) AS cal FROM df").show(5)
df.select("id", F.coalesce("calories", F.lit(-1)).alias("cal")).show(5)   # coalesce = nvl in DF API

# ifnull
spark.sql("SELECT id, IFNULL(calories, -1) AS cal FROM df").show(5)
df.select("id", F.coalesce("calories", F.lit(-1)).alias("cal")).show(5)

# nullif
spark.sql("SELECT id, NULLIF(calories, 0) AS cal FROM df").show(5)
df.select(
    "id",
    F.when(col("calories") == 0, None).otherwise(col("calories")).alias("cal"),
).show(5)
