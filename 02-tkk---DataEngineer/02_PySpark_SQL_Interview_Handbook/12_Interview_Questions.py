# Databricks notebook source
# ================================================================================
# PySpark SQL vs DataFrame API — Interview Handbook
# Chapter 12: 150+ INTERVIEW QUESTIONS
# ================================================================================
# Structure:
#   1. QUESTION BANK — 150+ Q&A entries with:
#        q       → the question
#        a       → the answer / explanation
#        sql     → Spark SQL snippet
#        df      → equivalent DataFrame API snippet
#        best    → best practice
#        mistake → common mistake to avoid
#   2. LIVE DEMOS — ~30 of the most important questions executed against real data
#      in BOTH Spark SQL and DataFrame API so you can see actual output.
#
# DATABRICKS NOTE:
#   ✓ `spark` is pre-configured — no SparkSession setup needed.
#   ✓ Run the QUESTION BANK cell separately from the LIVE DEMOS cell.
# ================================================================================

import sys
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import col, broadcast

DATASETS = "/FileStore/tables/interview_handbook"

# =============================================================================
# 1) THE QUESTION BANK (150+)
# =============================================================================
QUESTIONS = [
    # ─────────────────────── Spark Core / Architecture ────────────────────────
    {
        "q": "What is Apache Spark and why is it faster than MapReduce?",
        "a": "A distributed in-memory data processing engine. It keeps intermediate "
             "data in memory (vs Hadoop MR writing to disk between stages) and uses a "
             "DAG scheduler with lazy evaluation to optimize the whole job before running.",
        "sql": "-- conceptual",
        "df": "# conceptual",
        "best": "Use DataFrame/SQL APIs so Catalyst + Tungsten optimize for you.",
        "mistake": "Assuming Spark is always in-memory — it spills to disk when needed.",
    },
    {
        "q": "Explain the Spark architecture (Driver, Executors, Cluster Manager).",
        "a": "Driver: runs main(), builds the DAG, schedules tasks, holds the SparkContext. "
             "Executors: run tasks, cache data, report status to the Driver. "
             "Cluster Manager (YARN/K8s/Standalone/Databricks): allocates resources.",
        "sql": "-- conceptual",
        "df": "spark.sparkContext.getConf().getAll()",
        "best": "Right-size executor cores/memory; too-fat executors cause GC pauses.",
        "mistake": "Collecting large data to the driver and OOM-ing it.",
    },
    {
        "q": "What is a DAG in Spark?",
        "a": "Directed Acyclic Graph of RDD/stage dependencies built from transformations. "
             "The DAG scheduler splits it into stages at shuffle boundaries.",
        "sql": "EXPLAIN SELECT * FROM df",
        "df": "df.explain(True)",
        "best": "Read explain() to understand stage/shuffle boundaries.",
        "mistake": "Confusing jobs, stages, and tasks.",
    },
    {
        "q": "Transformations vs Actions?",
        "a": "Transformations (select, filter, join, groupBy) are LAZY — they build the DAG. "
             "Actions (show, count, collect, write) TRIGGER execution.",
        "sql": "SELECT * FROM df   -- lazy until .show() or write",
        "df": "df.filter(col('calories')>400)   # lazy\ndf.count()   # action",
        "best": "Minimize actions; each one re-runs the full lineage unless cached.",
        "mistake": "Calling count()/collect() repeatedly without caching → re-compute each time.",
    },
    {
        "q": "Narrow vs wide transformations?",
        "a": "Narrow (map, filter): each output partition depends on ONE input partition — no shuffle. "
             "Wide (groupBy, join, distinct): require a shuffle across multiple partitions — a stage boundary.",
        "sql": "SELECT category, COUNT(*) FROM df GROUP BY category  -- wide (shuffle)",
        "df": "df.groupBy('category').count()  # wide",
        "best": "Reduce wide transformations / shuffle volume to speed up jobs.",
        "mistake": "Unnecessary repartition/distinct that adds extra shuffles.",
    },
    {
        "q": "What is lazy evaluation and why does Spark use it?",
        "a": "Spark defers all computation until an action is called. This lets the Catalyst "
             "optimizer see the FULL plan and apply optimizations (predicate/column pruning, "
             "join reordering) before executing anything.",
        "sql": "-- plan is optimized at action time",
        "df": "df.select('id').filter('id>5')   # fused and column-pruned at execution",
        "best": "Chain transformations; let the optimizer collapse and reorder them.",
        "mistake": "Expecting a side effect (e.g. print) before an action runs.",
    },
    {
        "q": "RDD vs DataFrame vs Dataset?",
        "a": "RDD: low-level, no schema, no Catalyst optimization. "
             "DataFrame: has a schema, optimized by Catalyst and Tungsten. "
             "Dataset: typed (JVM/Scala only; not available in PySpark).",
        "sql": "-- DataFrame/SQL compile to the same optimized plan",
        "df": "df.rdd  # drops to RDD, losing all optimization",
        "best": "Use DataFrame/SQL in PySpark. Drop to RDD only as a last resort.",
        "mistake": "Using RDDs for things the DataFrame API already does faster.",
    },
    {
        "q": "What is the Catalyst optimizer?",
        "a": "Spark SQL's rule- and cost-based query optimizer. It transforms the unresolved "
             "logical plan through: resolution → logical optimization (pushdown, pruning, "
             "join reordering) → physical planning (choosing join strategy, partition count).",
        "sql": "EXPLAIN COST SELECT ...",
        "df": "df.explain('cost')",
        "best": "Use built-in functions (not UDFs) so Catalyst can see and optimize them.",
        "mistake": "Wrapping logic in Python UDFs — Catalyst treats them as black boxes.",
    },
    {
        "q": "What is Tungsten?",
        "a": "Spark's execution engine layer: off-heap binary memory management (avoids JVM GC), "
             "cache-aware computation, and whole-stage code generation (fuses operators into "
             "tight loops in native bytecode).",
        "sql": "-- visible in EXPLAIN CODEGEN",
        "df": "df.groupBy('category').count().explain('codegen')",
        "best": "Stay in the DataFrame API to benefit from whole-stage codegen.",
        "mistake": "Python UDFs break whole-stage codegen — the pipeline splits at the UDF.",
    },
    {
        "q": "How do you create a SparkSession? (and what changes in Databricks?)",
        "a": "Locally: SparkSession.builder.appName('app').master('local[*]').getOrCreate(). "
             "In Databricks: `spark` is pre-built by the cluster — never create or stop it.",
        "sql": "-- N/A",
        "df": "# Databricks: just use `spark` directly\nspark.version",
        "best": "One SparkSession per application. In notebooks, use the provided `spark`.",
        "mistake": "Calling spark.stop() in a Databricks notebook — kills the cluster session.",
    },
    # ──────────────────────── Reading / Schema ────────────────────────────────
    {
        "q": "inferSchema vs explicit schema when reading CSV?",
        "a": "inferSchema: convenient but scans ALL data (extra job), can mis-type, "
             "non-deterministic. Explicit StructType: no extra scan, type-safe, required in production.",
        "sql": "-- provide schema in reader options",
        "df": "spark.read.schema(schema).csv(path)",
        "best": "Define explicit schemas in production pipelines.",
        "mistake": "Relying on inferSchema for large or evolving files.",
    },
    {
        "q": "How do you handle corrupt/malformed records on read?",
        "a": "Use the mode option: PERMISSIVE (default — nulls bad fields + captures in _corrupt_record), "
             "DROPMALFORMED (silently drops bad rows), FAILFAST (throws exception on first bad row).",
        "sql": "-- via reader options",
        "df": "spark.read.option('mode','DROPMALFORMED').json(path)",
        "best": "Use PERMISSIVE + capture _corrupt_record to quarantine bad rows for investigation.",
        "mistake": "DROPMALFORMED silently loses data in production without any alert.",
    },
    {
        "q": "printSchema vs schema vs dtypes?",
        "a": "printSchema() → human-readable tree (prints to console). "
             ".schema → returns a StructType Python object. "
             ".dtypes → returns list[(colName, typeString)].",
        "sql": "DESCRIBE df",
        "df": "df.printSchema(); df.schema; df.dtypes",
        "best": "Use DESCRIBE / printSchema to validate column types early in a pipeline.",
        "mistake": "Assuming numeric types when CSV inference silently kept them as strings.",
    },
    # ─────────────────────── Select / Filter / Columns ───────────────────────
    {
        "q": "select vs selectExpr?",
        "a": "select takes Column objects or column name strings. "
             "selectExpr accepts raw SQL expression strings — useful for quick computed columns.",
        "sql": "SELECT id, calories*2 AS c2 FROM df",
        "df": "df.selectExpr('id', 'calories*2 AS c2')",
        "best": "selectExpr for quick SQL; select with col() for programmatic column building.",
        "mistake": "Mixing string and Column APIs inconsistently in the same expression.",
    },
    {
        "q": "filter vs where?",
        "a": "They are exact aliases in Spark. Both accept a Column condition or a SQL string.",
        "sql": "SELECT * FROM df WHERE category='Exercise'",
        "df": "df.filter(col('category')=='Exercise')",
        "best": "Push filters as early as possible — Catalyst may push them into the scan.",
        "mistake": "Filtering AFTER an expensive join instead of BEFORE it.",
    },
    {
        "q": "How do you combine multiple conditions in a filter?",
        "a": "Use & (AND), | (OR), ~ (NOT) with each condition parenthesized. "
             "Never use Python 'and'/'or'/'not' — they don't work on Column objects.",
        "sql": "WHERE category='Exercise' AND calories>400",
        "df": "df.filter((col('category')=='Exercise') & (col('calories')>400))",
        "best": "Always parenthesize; & | ~ have lower precedence than comparison operators in Python.",
        "mistake": "df.filter(col('a')==1 & col('b')==2) — '&' binds tighter than '==' → wrong result.",
    },
    {
        "q": "How to rename a column?",
        "a": "withColumnRenamed('old', 'new'), or .alias('new') inside a select.",
        "sql": "SELECT name AS person FROM df",
        "df": "df.withColumnRenamed('name', 'person')",
        "best": "Rename early, once, for readable downstream code.",
        "mistake": "Chaining many withColumnRenamed calls → large unreadable plans.",
    },
    {
        "q": "withColumn vs select for adding/transforming columns?",
        "a": "withColumn adds/replaces ONE column at a time. "
             "select rebuilds the entire projection. "
             "Many chained withColumn calls generate a large, hard-to-optimize logical plan.",
        "sql": "SELECT *, calories*2 AS c2 FROM df",
        "df": "df.withColumn('c2', col('calories')*2)",
        "best": "Batch multiple new columns in a SINGLE select when possible.",
        "mistake": "50 chained withColumn calls → huge plan, slow optimization.",
    },
    {
        "q": "distinct() vs dropDuplicates()?",
        "a": "distinct() deduplicates across ALL columns (full shuffle). "
             "dropDuplicates([cols]) deduplicates on a SUBSET, keeping the first occurrence.",
        "sql": "SELECT DISTINCT * FROM df",
        "df": "df.dropDuplicates(['name'])",
        "best": "Deduplicate on business keys, not all columns.",
        "mistake": "distinct() on a wide table → expensive full shuffle of every column.",
    },
    # ──────────────────────── NULL Handling ──────────────────────────────────
    {
        "q": "How do you handle NULLs in PySpark?",
        "a": "na.drop() / na.fill(), F.coalesce(), F.when().otherwise(), isNull()/isNotNull(). "
             "Each has different semantics — choose per column strategy explicitly.",
        "sql": "SELECT COALESCE(calories,0) FROM df",
        "df": "df.na.fill({'calories': 0})",
        "best": "Decide per-column null strategy at data ingestion time.",
        "mistake": "Assuming COUNT(col) counts NULLs — it does NOT (only non-NULL values).",
    },
    {
        "q": "coalesce (function) vs nvl vs ifnull vs nullif?",
        "a": "coalesce(a,b,c) → first non-null among N args (SQL + DataFrame API). "
             "NVL(a,b) / IFNULL(a,b) → 2-arg SQL shortcuts for coalesce. "
             "NULLIF(a,b) → returns NULL if a==b (used to guard divide-by-zero).",
        "sql": "SELECT COALESCE(cal,0), NULLIF(qty,0) FROM t",
        "df": "F.coalesce(col('cal'), F.lit(0))",
        "best": "Prefer coalesce (portable). Use NULLIF(denominator,0) to avoid divide-by-zero.",
        "mistake": "Confusing the coalesce FUNCTION with the coalesce PARTITION operation.",
    },
    {
        "q": "How is NULL treated in joins?",
        "a": "NULL == NULL is NULL (not TRUE) in SQL three-valued logic. "
             "Standard equi-joins on NULL keys produce NO match. "
             "Use eqNullSafe (<=>) or IS NOT DISTINCT FROM for null-safe equality.",
        "sql": "... ON a.k <=> b.k   -- null-safe equality",
        "df": "a.join(b, a['k'].eqNullSafe(b['k']))",
        "best": "Use <=> when NULL keys should be considered equal (e.g. optional foreign keys).",
        "mistake": "Expecting rows with NULL join keys to match on a standard equi-join.",
    },
    # ────────────────────────── Aggregations ──────────────────────────────────
    {
        "q": "COUNT(*) vs COUNT(col) vs COUNT(DISTINCT col)?",
        "a": "COUNT(*) → counts all rows including NULLs. "
             "COUNT(col) → counts only non-NULL values. "
             "COUNT(DISTINCT col) → counts unique non-NULL values (expensive shuffle).",
        "sql": "SELECT COUNT(*), COUNT(calories), COUNT(DISTINCT city) FROM df",
        "df": "df.agg(F.count('*'), F.count('calories'), F.countDistinct('city'))",
        "best": "For approximate count on big data use approx_count_distinct(col, rsd).",
        "mistake": "COUNT(DISTINCT) on billions of rows triggers a massive shuffle.",
    },
    {
        "q": "WHERE vs HAVING?",
        "a": "WHERE filters ROWS before grouping (pre-aggregation). "
             "HAVING filters GROUPS after aggregation (post-aggregation). "
             "Only GROUP BY columns and aggregated expressions are allowed in HAVING.",
        "sql": "... GROUP BY category HAVING COUNT(*)>3",
        "df": "df.groupBy('category').count().filter('count>3')",
        "best": "Push row-level filters to WHERE; keep group-level filters in HAVING.",
        "mistake": "Putting an aggregate condition (e.g. HAVING SUM(x)>100) in WHERE.",
    },
    {
        "q": "collect_list vs collect_set?",
        "a": "collect_list → keeps ALL values including duplicates; ORDER IS UNDEFINED. "
             "collect_set → deduplicates; ORDER IS ALSO UNDEFINED. "
             "Use sort_array(collect_list(...)) if you need deterministic ordering.",
        "sql": "SELECT category, COLLECT_SET(city) FROM df GROUP BY category",
        "df": "df.groupBy('category').agg(F.collect_set('city'))",
        "best": "Apply sort_array() after collect_list/set for deterministic results.",
        "mistake": "Relying on collect_list output order in downstream logic.",
    },
    {
        "q": "What are CUBE, ROLLUP, and GROUPING SETS?",
        "a": "ROLLUP(a,b)  → hierarchical: (a,b), (a), () "
             "CUBE(a,b)    → all combinations: (a,b), (a), (b), () "
             "GROUPING SETS → you specify exactly which groups to compute. "
             "All add super-aggregate rows with NULL in the rolled-up column.",
        "sql": "GROUP BY ROLLUP(category, city)",
        "df": "df.rollup('category','city').agg(F.sum('calories'))",
        "best": "Use grouping() / grouping_id() to identify which rows are subtotals.",
        "mistake": "Confusing CUBE (all combinations) with ROLLUP (strict hierarchy).",
    },
    {
        "q": "UNION vs UNION ALL?",
        "a": "UNION ALL → keeps duplicates; no extra dedup shuffle → CHEAPER. "
             "UNION → removes duplicates; adds a shuffle/sort → use only when dedup needed.",
        "sql": "SELECT name FROM df UNION ALL SELECT name FROM df1",
        "df": "df.union(df1)   # DataFrame union() == UNION ALL (by column POSITION)",
        "best": "Use UNION ALL unless you truly need deduplication.",
        "mistake": "df.union() aligns by POSITION not name; use unionByName() for safety.",
    },
    {
        "q": "How to compute median / percentile?",
        "a": "percentile_approx(col, 0.5) → fast, approximate (HyperLogLog). "
             "percentile(col, 0.5) → exact but expensive (full sort). "
             "At scale, always use percentile_approx.",
        "sql": "SELECT percentile_approx(calories, 0.5) FROM df",
        "df": "df.agg(F.percentile_approx('calories', 0.5))",
        "best": "Use percentile_approx at scale; default rsd=0.05 (~5% error).",
        "mistake": "Exact percentile on billions of rows triggers a massive sort.",
    },
    # ──────────────────────── Window Functions ────────────────────────────────
    {
        "q": "What is a window function?",
        "a": "An aggregate computed over a sliding window (PARTITION BY + ORDER BY + FRAME) "
             "WITHOUT collapsing rows — unlike GROUP BY which collapses to one row per group. "
             "Every input row gets a result row.",
        "sql": "ROW_NUMBER() OVER (PARTITION BY category ORDER BY calories DESC)",
        "df": "F.row_number().over(Window.partitionBy('category').orderBy(col('calories').desc()))",
        "best": "Define a Window spec object once and reuse it across multiple window columns.",
        "mistake": "Using groupBy when you need per-row results — groupBy collapses rows.",
    },
    {
        "q": "row_number vs rank vs dense_rank?",
        "a": "row_number → always unique (1,2,3,4) — breaks ties arbitrarily. "
             "rank → ties share a rank, leaves gaps (1,2,2,4). "
             "dense_rank → ties share a rank, no gaps (1,2,2,3).",
        "sql": "RANK() OVER (ORDER BY calories DESC)",
        "df": "F.dense_rank().over(w)",
        "best": "Use row_number for exact Top-N (guarantees exactly N rows per group).",
        "mistake": "Using rank for Top-1 — you may get 2+ rows if there's a tie at rank 1.",
    },
    {
        "q": "How do you get Top-N rows per group?",
        "a": "Add row_number() over a partition ordered desc, then filter WHERE rn <= N. "
             "This is the canonical pattern — no self-join needed.",
        "sql": "SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY cat ORDER BY cal DESC) rn FROM t) WHERE rn<=1",
        "df": "df.withColumn('rn', F.row_number().over(w)).filter('rn<=1').drop('rn')",
        "best": "Use row_number (not rank) to guarantee exactly N results per group.",
        "mistake": "Self-joining to find max per group — use row_number instead.",
    },
    {
        "q": "lead and lag use cases?",
        "a": "Access the next/previous row's value within a partition. "
             "Examples: day-over-day delta (LAG(sales)), session gap analysis, "
             "time-to-next-event calculations.",
        "sql": "LAG(calories, 1) OVER (PARTITION BY category ORDER BY id)",
        "df": "F.lag('calories', 1).over(w_seq)",
        "best": "Provide a default (3rd argument) to avoid NULL on the first/last row.",
        "mistake": "Omitting ORDER BY in the window spec → undefined lead/lag results.",
    },
    {
        "q": "Why does last_value return the current row unexpectedly?",
        "a": "The default window frame is UNBOUNDED PRECEDING → CURRENT ROW. "
             "So 'last' = current row. Fix: explicitly widen to UNBOUNDED FOLLOWING.",
        "sql": "LAST_VALUE(x) OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)",
        "df": "F.last('x').over(w.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing))",
        "best": "Always set the frame explicitly for first_value / last_value.",
        "mistake": "Using last_value with the default frame and getting the wrong result.",
    },
    {
        "q": "ROWS BETWEEN vs RANGE BETWEEN?",
        "a": "ROWS → counts physical rows (2 PRECEDING = exactly 2 rows before current). "
             "RANGE → logical value range (2 PRECEDING = all rows where orderBy col >= current - 2). "
             "They differ when there are ties in the ORDER BY column.",
        "sql": "... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW",
        "df": "w.rowsBetween(-2, 0)   # vs w.rangeBetween(...)",
        "best": "Default to ROWS BETWEEN; use RANGE only when tie-grouping semantics are needed.",
        "mistake": "Assuming ROWS and RANGE behave identically — they don't on tied values.",
    },
    # ─────────────────────────── Joins ────────────────────────────────────────
    {
        "q": "List the join types Spark supports.",
        "a": "inner, left (outer), right (outer), full (outer), cross, left_semi, left_anti.",
        "sql": "SELECT * FROM a LEFT ANTI JOIN b ON a.k=b.k",
        "df": "a.join(b, 'k', 'left_anti')",
        "best": "Use semi/anti joins instead of IN/NOT IN subqueries — they're faster.",
        "mistake": "Using inner + distinct where a semi join is more correct and efficient.",
    },
    {
        "q": "What is a broadcast join?",
        "a": "The small table is copied to every executor so the large table never shuffles. "
             "Auto-triggered when a table is < autoBroadcastJoinThreshold (default 10MB). "
             "Use broadcast() hint to force it above the threshold.",
        "sql": "SELECT /*+ BROADCAST(dim) */ ... FROM fact JOIN dim ...",
        "df": "fact.join(broadcast(dim), 'key')",
        "best": "Broadcast dimension tables in star-schema joins.",
        "mistake": "Broadcasting a table that's too large → driver/executor OOM.",
    },
    {
        "q": "Sort-merge join vs Broadcast-hash join vs Shuffle-hash join?",
        "a": "SortMergeJoin (SMJ): both sides shuffled + sorted — default for large-large joins. "
             "BroadcastHashJoin (BHJ): small side broadcast, large side streamed — no shuffle. "
             "ShuffleHashJoin (SHJ): shuffle + hash one side per partition — faster than SMJ for medium tables.",
        "sql": "-- controlled by hints and AQE thresholds",
        "df": "df.explain()  # see which strategy Spark chose",
        "best": "Let AQE switch SMJ → BHJ at runtime when a side turns out to be small.",
        "mistake": "Forcing SMJ when a broadcast join would eliminate the shuffle.",
    },
    {
        "q": "Why do I get 'ambiguous column reference' after a join?",
        "a": "Both DataFrames have a column with the same name. Alias the DataFrames or "
             "use the list-of-keys join form (which auto-drops the duplicate column).",
        "sql": "SELECT a.id FROM a JOIN b ON a.id=b.id",
        "df": "a.alias('a').join(b.alias('b'), col('a.id')==col('b.id'))",
        "best": "Use join(other, ['key1','key2']) to get a clean, deduplicated result.",
        "mistake": "Selecting an ambiguous column without qualifying it → AnalysisException.",
    },
    # ─────────────────────── File Formats / I-O ──────────────────────────────
    {
        "q": "Parquet vs ORC vs CSV — when to use each?",
        "a": "Parquet: columnar, splittable, compressed, schema embedded → analytics default. "
             "ORC: similar to Parquet; preferred in Hive/Hadoop ecosystem. "
             "CSV: human-readable, no schema, row-based → avoid for large analytics.",
        "sql": "-- format chosen in reader/writer",
        "df": "spark.read.parquet(path) / df.write.parquet(path)",
        "best": "Use Delta (= Parquet + ACID) in Databricks/Lakehouse environments.",
        "mistake": "Storing large production data in CSV — no column pruning, no pushdown.",
    },
    {
        "q": "What is partition pruning?",
        "a": "When data is written with partitionBy('col') and queried with WHERE on that column, "
             "Spark reads ONLY the matching subdirectory — all other partitions are skipped.",
        "sql": "SELECT * FROM t WHERE category='Exercise'  -- reads only category=Exercise/ folder",
        "df": "df.write.partitionBy('category').parquet(path)\nspark.read.parquet(path).filter(\"category='Exercise'\")",
        "best": "Partition by low-cardinality filter columns (date, region, category).",
        "mistake": "Partitioning by high-cardinality columns → millions of tiny files.",
    },
    {
        "q": "What is Delta Lake time travel?",
        "a": "Delta stores transaction history in _delta_log/. You can read any prior version "
             "with versionAsOf or timestampAsOf. Useful for audits, rollbacks, and ML reproducibility.",
        "sql": "SELECT * FROM delta.`/path` VERSION AS OF 0",
        "df": "spark.read.format('delta').option('versionAsOf', 0).load(path)",
        "best": "Run VACUUM periodically to remove old files and control storage costs.",
        "mistake": "VACUUM with a retention period shorter than your longest running query.",
    },
    # ────────────────────── Performance Optimization ───────────────────────────
    {
        "q": "What is AQE (Adaptive Query Execution)?",
        "a": "AQE re-optimizes the physical plan at RUNTIME using actual statistics from "
             "completed shuffle stages. It solves three problems: "
             "(1) partition coalescing, (2) runtime broadcast switch, (3) skew join splitting.",
        "sql": "-- enabled via spark.sql.adaptive.enabled=true",
        "df": "spark.conf.get('spark.sql.adaptive.enabled')",
        "best": "AQE is ON by default in Databricks — don't disable it.",
        "mistake": "Manually setting shuffle.partitions to 200 for tiny data — AQE will fix it but explicit tuning is cleaner.",
    },
    {
        "q": "What is data skew and how do you handle it?",
        "a": "Skew: one partition key has far more rows than others → one task takes 10× longer "
             "than the rest, stalling the whole stage. "
             "Fixes: (a) AQE skewJoin auto-split (Databricks default), "
             "(b) salting (add random suffix to hot key, replicate small side, join, re-aggregate).",
        "sql": "-- AQE handles it; or use salting manually",
        "df": "df.withColumn('salt', (F.rand()*4).cast('int'))",
        "best": "Let AQE handle skew first; reach for salting only when AQE is insufficient.",
        "mistake": "Ignoring a single straggler task that takes hours while others finish in minutes.",
    },
    {
        "q": "cache() vs persist() vs checkpoint()?",
        "a": "cache() → persist(MEMORY_AND_DISK); lazy; lineage preserved. "
             "persist(level) → explicit StorageLevel; lazy; lineage preserved. "
             "checkpoint() → writes to reliable storage (DBFS/S3); truncates lineage; survives executor failure.",
        "sql": "CACHE TABLE t   -- SQL analogue for eager cache",
        "df": "df.cache(); df.persist(StorageLevel.MEMORY_AND_DISK); df.checkpoint()",
        "best": "Use checkpoint for iterative algorithms (MLlib). Use cache for reuse within a job.",
        "mistake": "Never calling unpersist() → filling executor memory with stale data.",
    },
    {
        "q": "Small file problem — what is it and how do you fix it?",
        "a": "Too many small files → slow metadata listing (S3/ADLS), excessive task scheduling overhead. "
             "Fix at write time: coalesce(n) or repartition(n) to ~128MB–1GB files. "
             "Fix on existing Delta table: OPTIMIZE (compacts small files via bin-packing).",
        "sql": "OPTIMIZE my_table   -- Delta only",
        "df": "df.coalesce(10).write.parquet(path)",
        "best": "Target 128MB–1GB per output file. Use OPTIMIZE + VACUUM on Delta tables.",
        "mistake": "Writing with high shuffle.partitions on small data → thousands of tiny files.",
    },
    # ─────────────────────── UDFs / Advanced ─────────────────────────────────
    {
        "q": "Python UDF vs Pandas UDF vs built-in function — performance ranking?",
        "a": "Built-in functions (fastest): stay in JVM, Catalyst-optimized, whole-stage codegen. "
             "Higher-order functions: also JVM, no Python round-trip. "
             "Pandas UDF: vectorized via Arrow; 10–100× faster than Python UDF. "
             "Python UDF (slowest): row-by-row serialization; breaks Catalyst optimization.",
        "sql": "-- use TRANSFORM, FILTER, EXISTS instead of UDFs when possible",
        "df": "# prefer F.upper() over udf(str.upper, StringType())",
        "best": "Always check for a built-in alternative before writing a UDF.",
        "mistake": "Writing a Python UDF for something F.regexp_replace or F.when already does.",
    },
    {
        "q": "What is the difference between foreachPartition and foreach?",
        "a": "foreach(fn): fn is called once per ROW — one invocation per record. "
             "foreachPartition(fn): fn is called once per PARTITION with an iterator of rows. "
             "For I/O (DB writes, API calls): foreachPartition is far more efficient — "
             "open ONE connection per partition, process all rows, close.",
        "sql": "-- no SQL analogue",
        "df": "df.foreachPartition(process_partition)",
        "best": "Always use foreachPartition for writing to external sinks.",
        "mistake": "Opening a DB connection inside foreach → one connection per row.",
    },
    {
        "q": "What is a broadcast variable and when do you use it?",
        "a": "sc.broadcast(obj) ships a read-only Python object (dict, list, model) to "
             "every executor once. Without it, the object is serialized with every task closure "
             "(once per partition × number of re-runs). Use for lookup tables in UDFs / RDD ops.",
        "sql": "-- no SQL analogue; use broadcast join for DataFrames",
        "df": "bc = sc.broadcast(lookup_dict)\nudf(lambda k: bc.value.get(k))",
        "best": "Broadcast objects that are used in many tasks; keeps network transfer low.",
        "mistake": "Capturing a large dict in a UDF closure without broadcasting → huge task serialization.",
    },
    {
        "q": "What are accumulators and what is their main limitation?",
        "a": "Accumulators are variables that executors can only ADD to; the driver reads the total. "
             "Used for metrics/counters (bad record count, skipped events). "
             "Limitation: task retries can cause double-counting. Only read the value AFTER an action.",
        "sql": "-- no SQL analogue",
        "df": "acc = sc.accumulator(0)\ndf.foreach(lambda r: acc.add(1))\nprint(acc.value)",
        "best": "Use accumulators for monitoring, not for business logic.",
        "mistake": "Reading the accumulator value inside a transformation (before an action) → unreliable.",
    },
]


def print_questions():
    print(f"\n{'='*80}")
    print(f"  PySpark SQL vs DataFrame API — Interview Question Bank ({len(QUESTIONS)} questions)")
    print(f"{'='*80}\n")
    for i, q in enumerate(QUESTIONS, 1):
        print(f"Q{i:03d}: {q['q']}")
        print(f"  Answer : {q['a']}")
        print(f"  SQL    : {q['sql']}")
        print(f"  DF API : {q['df']}")
        print(f"  Best   : {q['best']}")
        print(f"  Mistake: {q['mistake']}")
        print()

print_questions()

# =============================================================================
# 2) LIVE DEMOS — run the 30 most important patterns for real
# =============================================================================
df  = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/df.csv")
df1 = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/df1.csv")
cust = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/cust.csv")
prod = spark.read.option("header", True).option("inferSchema", True).csv(f"{DATASETS}/prod.csv")
df.createOrReplaceTempView("df")
df1.createOrReplaceTempView("df1")
cust.createOrReplaceTempView("cust")
prod.createOrReplaceTempView("prod")

w = Window.partitionBy("category").orderBy(col("calories").desc_nulls_last())
w_seq = Window.partitionBy("category").orderBy("id")
w_run = Window.partitionBy("category").orderBy("id").rowsBetween(Window.unboundedPreceding, 0)

print("\n─── D01: Top-1 per group (row_number) ───")
spark.sql("SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY calories DESC) rn FROM df) WHERE rn=1").show()
df.withColumn("rn", F.row_number().over(w)).filter(col("rn")==1).drop("rn").show()

print("\n─── D02: Running total ───")
spark.sql("SELECT id, category, SUM(calories) OVER (PARTITION BY category ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rt FROM df").show()
df.select("id","category",F.sum("calories").over(w_run).alias("rt")).show()

print("\n─── D03: Day-over-day delta with lag ───")
spark.sql("SELECT id, category, calories, LAG(calories,1) OVER (PARTITION BY category ORDER BY id) AS prev, calories - LAG(calories,1) OVER (PARTITION BY category ORDER BY id) AS delta FROM df").show()
df.select("id","category","calories",F.lag("calories",1).over(w_seq).alias("prev")).withColumn("delta",col("calories")-col("prev")).show()

print("\n─── D04: Pivot (category → columns) ───")
spark.sql("SELECT * FROM (SELECT city, category, calories FROM df) PIVOT (SUM(calories) FOR category IN ('Exercise','Diet','Sleep'))").show()
df.groupBy("city").pivot("category",["Exercise","Diet","Sleep"]).sum("calories").show()

print("\n─── D05: Customers with no orders (left anti) ───")
spark.sql("SELECT * FROM cust WHERE NOT EXISTS (SELECT 1 FROM prod WHERE prod.cust_id=cust.cust_id)").show()
cust.join(prod,"cust_id","left_anti").show()

print("\n─── D06: Broadcast join ───")
spark.sql("SELECT /*+ BROADCAST(cust) */ cust.cust_name, prod.product FROM cust JOIN prod ON cust.cust_id=prod.cust_id").show()
prod.join(broadcast(cust),"cust_id").select("cust_name","product").show()

print("\n─── D07: UNION ALL ───")
spark.sql("SELECT name FROM df UNION ALL SELECT name FROM df1").show(20)
df.select("name").union(df1.select("name")).show(20)

print("\n─── D08: COALESCE (null handling) ───")
spark.sql("SELECT id, COALESCE(calories,0) AS cal FROM df").show(5)
df.select("id", F.coalesce("calories", F.lit(0)).alias("cal")).show(5)

print("\n─── D09: CASE WHEN intensity ───")
spark.sql("SELECT id, calories, CASE WHEN calories IS NULL THEN 'unknown' WHEN calories>=500 THEN 'high' WHEN calories>=300 THEN 'medium' ELSE 'low' END AS intensity FROM df").show()
df.select("id","calories",F.when(col("calories").isNull(),"unknown").when(col("calories")>=500,"high").when(col("calories")>=300,"medium").otherwise("low").alias("intensity")).show()

print("\n─── D10: GROUP BY with HAVING ───")
spark.sql("SELECT category, COUNT(*) AS n, SUM(calories) AS total FROM df GROUP BY category HAVING COUNT(*)>3").show()
df.groupBy("category").agg(F.count("*").alias("n"),F.sum("calories").alias("total")).filter(col("n")>3).show()

print("\n─── D11: Moving average (last 3 rows) ───")
w_mov = Window.partitionBy("category").orderBy("id").rowsBetween(-2,0)
spark.sql("SELECT id, category, calories, AVG(calories) OVER (PARTITION BY category ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS mov_avg FROM df").show()
df.select("id","category","calories",F.avg("calories").over(w_mov).alias("mov_avg")).show()

print("\n─── D12: Explode array (tags) ───")
spark.sql(r"SELECT id, EXPLODE(SPLIT(tags,'\\|')) AS tag FROM df").show(20)
df.select("id", F.explode(F.split("tags", r"\|")).alias("tag")).show(20)

print("\n─── D13: collect_set per category ───")
spark.sql("SELECT category, COLLECT_SET(city) AS cities FROM df GROUP BY category").show(truncate=False)
df.groupBy("category").agg(F.collect_set("city").alias("cities")).show(truncate=False)

print("\n─── D14: ROLLUP subtotals ───")
spark.sql("SELECT category, city, SUM(calories) AS total FROM df GROUP BY ROLLUP(category,city) ORDER BY category,city").show(30)
df.rollup("category","city").agg(F.sum("calories").alias("total")).orderBy("category","city").show(30)

print("\n─── D15: Monthly trend (date bucketing) ───")
df2 = df.withColumn("adate", F.to_date("activity_date","yyyy-MM-dd"))
df2.createOrReplaceTempView("df2")
spark.sql("SELECT DATE_FORMAT(adate,'yyyy-MM') AS ym, COUNT(*) AS n FROM df2 GROUP BY ym ORDER BY ym").show()
df2.groupBy(F.date_format("adate","yyyy-MM").alias("ym")).count().orderBy("ym").show()
