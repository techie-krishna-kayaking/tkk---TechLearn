# PySpark Interview Masterbook — Lead / Staff / Principal Data Engineer

> **Target roles:** Lead Data Engineer · Staff Data Engineer · Principal Data Engineer · Data Architect  
> **Target market:** Product-based companies in India; ₹70+ LPA preparation target.  
> **Dataset strategy:** Every coding example uses one consistent e-commerce domain and the same DataFrames.  
> **Code baseline:** PySpark DataFrame API, generally compatible with Spark 3.5+ and Spark 4.x unless marked otherwise. Verify engine/runtime and cloud-provider differences before deployment.
>
> This is a curated senior-level interview preparation set based on recurring distributed-processing, DataFrame, performance, streaming, and production-engineering problem patterns. It is not a claim that these exact questions were asked by a named company.

---

# How to use this chapter

For every coding problem:

1. State the input and output grain.
2. Clarify business semantics: status, currency, time zone, NULLs, duplicates, and late data.
3. Write the simplest correct DataFrame transformation.
4. Explain the physical work Spark may perform: scan, shuffle, sort, broadcast, spill, state, or write.
5. Compare alternatives and defend the choice.
6. Explain tests, retries, observability, and recovery at production scale.

## What interviewers expect by level

| Dimension | Lead | Staff | Principal |
|---|---|---|---|
| DataFrame coding | Correct, maintainable transformations | Reusable patterns and correctness contracts | Platform-wide standards and semantic consistency |
| Performance | Reads plans, tunes joins and partitions | Diagnoses skew, shuffle, concurrency, cost | Optimizes workloads and platform architecture |
| Reliability | Retry-safe jobs and tests | Replay, backfill, CDC, state recovery | SLOs, ownership, resilience and risk governance |
| Design | Designs pipelines | Aligns multiple domains and teams | Sets multi-year technical direction |
| Leadership | Mentors engineers | Influences without authority | Aligns engineering, product, security, finance |

A Principal answer is not a longer PySpark script. It connects implementation choices to business semantics, cost, reliability, security, and organizational ownership.

---

# Part 1 — One dataset for every question

## 1.1 Business scenario

A multi-region e-commerce product has customers, products, orders, order lines, and clickstream events. It supports revenue and order analytics, product/customer ranking, retention and funnel metrics, source-to-target reconciliation, incremental/CDC ingestion, SCD Type 2 dimensions, streaming event processing, and operational monitoring.

## 1.2 DataFrames and their grains

| DataFrame | Grain | Business key |
|---|---|---|
| customers | One current row per customer | customer_id |
| products | One current row per product | product_id |
| orders | One row per order | order_id |
| order_items | One row per order line | order_item_id |
| payments | One row per payment attempt | payment_id |
| events | One row per event | event_id |
| customer_snapshot | One customer per extract date | customer_id + snapshot_date |

**Critical:** `orders` is order-grain; `order_items` is line-grain; `payments` is payment-attempt-grain; `events` is event-grain. Joining an order with three item rows and two payment attempts can create six rows. Aggregate child facts to the intended grain before joining measures.

## 1.3 Complete DataFrame setup

```python
from datetime import datetime, date
from decimal import Decimal

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

spark = (
    SparkSession.builder
    .appName("SeniorPySparkInterview")
    .getOrCreate()
)

customer_schema = T.StructType([
    T.StructField("customer_id", T.LongType(), False),
    T.StructField("customer_name", T.StringType(), True),
    T.StructField("email", T.StringType(), True),
    T.StructField("country_code", T.StringType(), True),
    T.StructField("signup_ts", T.TimestampType(), True),
    T.StructField("updated_at", T.TimestampType(), True),
    T.StructField("is_deleted", T.BooleanType(), False),
])

order_schema = T.StructType([
    T.StructField("order_id", T.LongType(), False),
    T.StructField("customer_id", T.LongType(), False),
    T.StructField("order_ts", T.TimestampType(), False),
    T.StructField("order_status", T.StringType(), False),
    T.StructField("currency_code", T.StringType(), False),
    T.StructField("source_sequence", T.LongType(), True),
])

item_schema = T.StructType([
    T.StructField("order_item_id", T.LongType(), False),
    T.StructField("order_id", T.LongType(), False),
    T.StructField("product_id", T.LongType(), False),
    T.StructField("quantity", T.IntegerType(), False),
    T.StructField("unit_price", T.DecimalType(12, 2), False),
    T.StructField("item_discount", T.DecimalType(12, 2), True),
    T.StructField("item_status", T.StringType(), False),
])

product_schema = T.StructType([
    T.StructField("product_id", T.LongType(), False),
    T.StructField("product_name", T.StringType(), False),
    T.StructField("category", T.StringType(), True),
    T.StructField("brand", T.StringType(), True),
    T.StructField("is_active", T.BooleanType(), False),
])

payment_schema = T.StructType([
    T.StructField("payment_id", T.LongType(), False),
    T.StructField("order_id", T.LongType(), False),
    T.StructField("payment_attempt", T.IntegerType(), False),
    T.StructField("payment_ts", T.TimestampType(), False),
    T.StructField("payment_status", T.StringType(), False),
    T.StructField("amount", T.DecimalType(12, 2), False),
    T.StructField("payment_method", T.StringType(), True),
])

event_schema = T.StructType([
    T.StructField("event_id", T.LongType(), False),
    T.StructField("customer_id", T.LongType(), True),
    T.StructField("session_id", T.StringType(), True),
    T.StructField("event_name", T.StringType(), False),
    T.StructField("event_ts", T.TimestampType(), False),
    T.StructField("product_id", T.LongType(), True),
    T.StructField("order_id", T.LongType(), True),
])

customers = spark.createDataFrame([
    (1, "Asha", "asha@example.com", "IN", datetime(2025, 1, 2, 9), datetime(2025, 3, 1, 9), False),
    (2, "Ben", "ben@example.com", "US", datetime(2025, 1, 5, 10), datetime(2025, 2, 5, 9), False),
    (3, "Chen", "chen@example.com", "SG", datetime(2025, 2, 1, 8), datetime(2025, 2, 7, 9), False),
    (4, "Diya", "diya@example.com", "IN", datetime(2025, 2, 10, 12), datetime(2025, 2, 10, 12), False),
    (5, "Eli", None, "IN", datetime(2025, 3, 1, 11), datetime(2025, 3, 1, 11), False),
], customer_schema)

orders = spark.createDataFrame([
    (101, 1, datetime(2025, 1, 10, 10), "COMPLETED", "INR", 1),
    (102, 1, datetime(2025, 1, 15, 12), "COMPLETED", "INR", 2),
    (103, 2, datetime(2025, 1, 20, 9), "CANCELLED", "USD", 3),
    (104, 2, datetime(2025, 2, 5, 15), "COMPLETED", "USD", 4),
    (105, 3, datetime(2025, 2, 7, 13), "COMPLETED", "SGD", 5),
    (106, 1, datetime(2025, 3, 1, 17), "COMPLETED", "INR", 6),
    (107, 4, datetime(2025, 3, 3, 8), "PENDING", "INR", 7),
    (108, 5, datetime(2025, 3, 5, 19), "COMPLETED", "INR", 8),
], order_schema)

order_items = spark.createDataFrame([
    (1001, 101, 10, 2, Decimal("500.00"), Decimal("0.00"), "FULFILLED"),
    (1002, 101, 11, 1, Decimal("200.00"), Decimal("0.00"), "FULFILLED"),
    (1003, 102, 10, 1, Decimal("500.00"), Decimal("50.00"), "FULFILLED"),
    (1004, 102, 12, 2, Decimal("300.00"), Decimal("0.00"), "FULFILLED"),
    (1005, 103, 11, 1, Decimal("200.00"), Decimal("0.00"), "CANCELLED"),
    (1006, 104, 10, 1, Decimal("500.00"), Decimal("0.00"), "FULFILLED"),
    (1007, 105, 13, 3, Decimal("100.00"), Decimal("0.00"), "FULFILLED"),
    (1008, 106, 12, 1, Decimal("300.00"), Decimal("0.00"), "FULFILLED"),
    (1009, 107, 10, 1, Decimal("500.00"), Decimal("0.00"), "PENDING"),
    (1010, 108, 11, 2, Decimal("200.00"), Decimal("0.00"), "FULFILLED"),
], item_schema)

products = spark.createDataFrame([
    (10, "Keyboard", "Accessories", "KeyCo", True),
    (11, "Mouse", "Accessories", "KeyCo", True),
    (12, "Monitor", "Displays", "ViewMax", True),
    (13, "Cable", "Accessories", "LinkPro", True),
], product_schema)

payments = spark.createDataFrame([
    (5001, 101, 1, datetime(2025, 1, 10, 10, 1), "SUCCESS", Decimal("1200.00"), "CARD"),
    (5002, 102, 1, datetime(2025, 1, 15, 12, 1), "FAILED", Decimal("950.00"), "CARD"),
    (5003, 102, 2, datetime(2025, 1, 15, 12, 5), "SUCCESS", Decimal("950.00"), "CARD"),
    (5004, 103, 1, datetime(2025, 1, 20, 9, 2), "REFUNDED", Decimal("200.00"), "WALLET"),
    (5005, 104, 1, datetime(2025, 2, 5, 15, 1), "SUCCESS", Decimal("500.00"), "CARD"),
    (5006, 105, 1, datetime(2025, 2, 7, 13, 1), "SUCCESS", Decimal("300.00"), "UPI"),
    (5007, 106, 1, datetime(2025, 3, 1, 17, 1), "SUCCESS", Decimal("300.00"), "UPI"),
    (5008, 108, 1, datetime(2025, 3, 5, 19, 1), "SUCCESS", Decimal("400.00"), "CARD"),
], payment_schema)

events = spark.createDataFrame([
    (9001, 1, "s1", "view_product", datetime(2025, 1, 10, 9), 10, None),
    (9002, 1, "s1", "add_to_cart", datetime(2025, 1, 10, 9, 5), 10, None),
    (9003, 1, "s1", "purchase", datetime(2025, 1, 10, 10), None, 101),
    (9004, 1, "s2", "view_product", datetime(2025, 1, 15, 11), 12, None),
    (9005, 1, "s2", "purchase", datetime(2025, 1, 15, 12), None, 102),
    (9006, 2, "s3", "view_product", datetime(2025, 2, 5, 14), 10, None),
    (9007, 2, "s3", "purchase", datetime(2025, 2, 5, 15), None, 104),
    (9008, 3, "s4", "view_product", datetime(2025, 2, 7, 12), 13, None),
    (9009, 3, "s4", "purchase", datetime(2025, 2, 7, 13), None, 105),
    (9010, 1, "s5", "view_product", datetime(2025, 3, 1, 16), 12, None),
], event_schema)
```

### Metric rules for this chapter

- Completed order means `order_status == "COMPLETED"`.
- Gross item value is `quantity * unit_price`.
- Net item value is `quantity * unit_price - COALESCE(item_discount, 0)`.
- Net merchandise value includes fulfilled lines from completed orders.
- Successful payment amount is cash-collected-like data, not automatically recognized revenue.
- Keep currencies separate unless an FX table/rate date and conversion policy are provided.
- Event time, source update time, and ingestion time are different concepts.

---

# Part 2 — PySpark and Spark execution foundations

## Q1. What is PySpark, and how is it different from Python?

**Answer:** PySpark is the Python API for Apache Spark. Python code describes DataFrame/RDD transformations; Spark plans and executes distributed work across executors. The driver coordinates the application; it does not normally hold the entire dataset.

**Best approach:** Explain PySpark as a distributed query/programming interface, not “Python automatically parallelized.” The Python driver, JVM Spark engine, executors, and any Python worker processes have distinct responsibilities.

**Lead:** Explain the application components. **Staff:** Discuss Python/JVM boundaries and runtime costs. **Principal:** Select execution model and platform based on workload, ecosystem, and operational needs.

## Q2. Explain SparkSession, SparkContext, and SQLContext.

```python
spark = (
    SparkSession.builder
    .appName("OrdersPipeline")
    .getOrCreate()
)
sc = spark.sparkContext
```

- `SparkSession`: modern entry point for DataFrames, SQL, catalog, configuration, and I/O.
- `SparkContext`: lower-level Spark Core/RDD context.
- `SQLContext`: historical SQL entry point; ordinary modern applications use `SparkSession`.

**Best:** Use one managed SparkSession per application/session context. Avoid creating multiple contexts in the same process unless the environment explicitly supports it.

## Q3. RDD vs DataFrame vs Dataset: which do you choose?

- RDD: lower-level distributed collection API; useful for specialized low-level transformations.
- DataFrame: schema-aware distributed table; Catalyst and Spark SQL can optimize expressions.
- Dataset: typed JVM abstraction in Scala/Java; Python users work primarily with DataFrames.

**Best:** Default to DataFrames for structured ETL. Choose RDD only when its lower-level control is needed and measured. A Python DataFrame is not equivalent to the strongly typed Scala Dataset API.

## Q4. Explain lazy evaluation.

```python
completed = (
    orders
    .filter(F.col("order_status") == "COMPLETED")
    .select("order_id", "customer_id", "order_ts")
)
```

This constructs a query plan. An action such as `count()`, `show()`, or a write requires execution.

**Why useful:** Spark can optimize a larger expression tree before executing it.

**Trap:** Multiple actions may execute the lineage multiple times if the result is not persisted or otherwise reused by the engine.

## Q5. Transformation vs action?

Transformations include `select`, `filter`, `withColumn`, `join`, and `groupBy().agg()`. Actions include `count`, `collect`, `take`, `show`, and writes.

**Best:** Avoid running diagnostic actions repeatedly on production-scale data. Use Spark UI/plan inspection and targeted bounded samples where possible.

## Q6. Explain driver, executor, job, stage, task, and partition.

- Driver: constructs plans, coordinates scheduling, tracks application state.
- Executor: runs tasks and can cache data.
- Job: execution triggered by an action.
- Stage: tasks separated by shuffle boundaries or other stage boundaries.
- Task: attempt to process one partition for a stage.
- Partition: a logical chunk of distributed data processed by tasks.

One task normally processes one partition per stage attempt. Number of executors is not equal to number of tasks.

## Q7. Narrow vs wide transformations?

- Narrow: each output partition depends on a limited set of input partitions; `filter`/`select` are common examples.
- Wide: records must be redistributed; `groupBy`, `distinct`, many joins, and global ordering commonly shuffle.

**Caveat:** A join may avoid a large shuffle with broadcast or compatible partitioning. Do not label every join unconditionally as a shuffle.

## Q8. What exactly happens during a shuffle?

Spark partitions data by key/partitioning requirements, writes intermediate shuffle data, transfers blocks between executors, and reads them for downstream tasks. It can involve serialization, disk I/O, network I/O, sort/hash work, and spill.

**Best:** Reduce data before shuffle only when semantics allow: filter, project columns, pre-aggregate, or broadcast a genuinely small side. Confirm with the physical plan and Spark UI.

## Q9. What is a shuffle dependency and why does it create a stage boundary?

A downstream task needs records from multiple upstream partitions. Spark must complete the map-side shuffle output before reduce-side tasks can consume it. This usually produces separate stages.

**Staff follow-up:** Explain map-side combine, shuffle file/block fetch, retries, and why shuffle read/write metrics help identify bottlenecks.

## Q10. What is lineage and how does Spark recover lost partitions?

Transformations form lineage describing how a partition can be recomputed. If executor loss removes a non-persisted partition, Spark can recompute it from lineage and source data.

**Caveat:** Recomputing a long/expensive lineage can be costly; checkpointing can truncate lineage in appropriate workflows. External side effects inside transformations must be treated carefully because tasks can be retried.

## Q11. What is Catalyst?

Catalyst is Spark SQL's query optimizer. It analyzes and transforms logical plans, applies rule-based optimizations, uses statistics where available, and selects physical strategies.

**Best:** Write declarative DataFrame expressions so Spark can reason about them. Python control flow that hides logic inside UDFs limits optimizer visibility.

## Q12. What is whole-stage code generation?

For supported physical operators, Spark can generate JVM code for a pipeline of operators to reduce virtual calls/intermediate object overhead. It is not universal and does not make arbitrary Python code execute as generated JVM code.

**Interview point:** A Python UDF may introduce a boundary where whole-stage codegen cannot fuse through the custom Python function.

## Q13. Explain logical plan vs physical plan.

```python
result.explain("extended")
result.explain("formatted")
```

- Parsed/analyzed/optimized logical plans describe relational semantics and optimizer rewrites.
- Physical plan describes selected execution operators such as scans, exchanges, joins, sorts, and aggregates.

**Best:** Read plans alongside runtime metrics. An explain plan is not proof of actual runtime performance.

## Q14. What is predicate pushdown?

Filter predicates may be pushed toward the data source so fewer rows are read. Actual support depends on data source, file format, predicate, type, and connector.

**Best:** Filter early in the DataFrame expression and verify pushed filters / scan metrics in the plan. A filter being written early in Python source does not guarantee physical execution order.

## Q15. What is column pruning?

Spark reads only required columns when the source format/connector supports columnar projection. Avoid `select("*")` in wide tables when downstream logic needs only a few columns.

**Trade-off:** Preserve audit/lineage columns needed for debugging or downstream contracts; do not prune columns blindly.

## Q16. What is the difference between DataFrame transformations and Python loops?

A Python loop over a list of literal column names can build a query plan. A loop over `collect()`ed data performs row-by-row work in the driver and destroys distributed execution.

**Best:** Express row transformations as native Spark column expressions. Use Python loops for schema-driven plan construction, not for moving large data to the driver.

## Q17. What happens when an executor fails?

Tasks running on that executor may fail and be retried elsewhere. Cached blocks may need recomputation; shuffle data loss can trigger upstream stage recomputation depending on shuffle service/deployment configuration. Repeated failures can exhaust retry policy and fail the job.

**Principal discussion:** Consider source replayability, external sink idempotency, cluster manager behavior, decommissioning, and recovery objective.

## Q18. What happens when the driver fails?

A standard batch application normally fails; an external orchestrator may restart it. Structured Streaming recovery can restore query progress/state from checkpoint under supported source/sink semantics, but a checkpoint is not a generic replacement for application-level recovery design.

**Best:** Make batch jobs restartable from immutable inputs and stable batch IDs. For streaming, use durable checkpoints and test restart/upgrade behavior.

## Q19. What is speculative execution?

Spark can launch duplicate attempts for slow tasks and accept a successful result, useful for transient stragglers. It does not fix deterministic skew or slow external systems and can duplicate side effects if code writes externally.

**Best:** Enable only with understanding of workload and side-effect semantics; make external writes idempotent.

## Q20. How do you explain a Spark job's execution from code to tasks?

Trace: DataFrame expressions → analyzed logical plan → optimized logical plan → physical plan → jobs/stages → tasks per partition → executor work → shuffle/read/write → committed output. Explain where actions occur and which operators cause exchange/sort/state.

---

# Part 3 — Core DataFrame coding questions

## Q21. Read orders from Parquet with schema validation.

```python
orders_raw = spark.read.parquet("/lake/bronze/orders")
orders_raw.printSchema()

expected = {
    "order_id": "bigint",
    "customer_id": "bigint",
    "order_ts": "timestamp",
    "order_status": "string",
    "currency_code": "string",
}

actual = {f.name: f.dataType.simpleString() for f in orders_raw.schema.fields}
missing = set(expected) - set(actual)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")
```

**Best:** Prefer schema-bearing columnar formats for production curated data. Validate required fields and compatible types; do not rely on accidental inference for contracts.

## Q22. Read CSV using explicit schema and safe options.

```python
csv_schema = T.StructType([
    T.StructField("order_id", T.LongType(), True),
    T.StructField("customer_id", T.LongType(), True),
    T.StructField("order_ts", T.StringType(), True),
    T.StructField("order_status", T.StringType(), True),
    T.StructField("currency_code", T.StringType(), True),
])

raw = (
    spark.read
    .option("header", True)
    .option("mode", "PERMISSIVE")
    .option("columnNameOfCorruptRecord", "_corrupt_record")
    .schema(csv_schema)
    .csv("/landing/orders/*.csv")
)
```

**Why string timestamp first?** It allows explicit parsing and invalid-value quarantine. Use `from_csv`/corrupt-record handling where suitable. Exact malformed-row semantics depend on CSV options and runtime.

## Q23. Filter completed orders and select required columns.

```python
completed_orders = (
    orders
    .filter(F.col("order_status") == "COMPLETED")
    .select("order_id", "customer_id", "order_ts", "currency_code")
)
```

**Best:** Native column expressions, explicit projection, no row-wise Python function. This supports optimizer visibility and column pruning.

## Q24. Add gross and net item value.

```python
items_with_value = (
    order_items
    .withColumn("gross_value", F.col("quantity") * F.col("unit_price"))
    .withColumn(
        "net_value",
        F.col("quantity") * F.col("unit_price")
        - F.coalesce(F.col("item_discount"), F.lit(0).cast("decimal(12,2)"))
    )
)
```

**Caveat:** Preserve DecimalType for money. Avoid converting monetary values to Float/Double for accounting calculations unless precision/rounding policy explicitly permits it.

## Q25. Normalize email and country code.

```python
normalized_customers = customers.withColumns({
    "email_normalized": F.lower(F.trim("email")),
    "country_code_normalized": F.upper(F.trim("country_code")),
})
```

`withColumns` availability depends on Spark version (introduced in Spark 3.3). Portable alternative is one `select("*", expr.alias(...))` or chained `withColumn` for a small number of fields.

**Best:** Normalize according to a documented identity/domain rule; lowercase/trim alone is not a universal email identity algorithm.

## Q26. Use when/otherwise to classify order status.

```python
classified = orders.withColumn(
    "order_status_group",
    F.when(F.col("order_status") == "COMPLETED", "SUCCESS")
     .when(F.col("order_status") == "CANCELLED", "STOPPED")
     .otherwise("IN_PROGRESS")
)
```

**Best:** Use a reference mapping table when status mapping is shared, governed, or frequently changes. CASE/when is fine for small stable mappings.

## Q27. Calculate order value at order grain.

```python
eligible_items = (
    order_items
    .filter(F.col("item_status") == "FULFILLED")
    .withColumn(
        "net_value",
        F.col("quantity") * F.col("unit_price")
        - F.coalesce(F.col("item_discount"), F.lit(0).cast("decimal(12,2)"))
    )
)

order_value = (
    eligible_items
    .groupBy("order_id")
    .agg(F.sum("net_value").alias("net_merchandise_value"))
)

completed_order_value = (
    orders.filter(F.col("order_status") == "COMPLETED")
    .join(order_value, "order_id", "inner")
)
```

**Best:** Aggregate line facts to order grain before joining to other order-grain facts such as payment totals. This prevents many-to-many multiplication.

## Q28. Calculate daily order count and value per currency.

```python
daily = (
    completed_order_value
    .withColumn("order_date", F.to_date("order_ts"))
    .groupBy("order_date", "currency_code")
    .agg(
        F.countDistinct("order_id").alias("order_count"),
        F.sum("net_merchandise_value").alias("net_merchandise_value")
    )
)
```

If `completed_order_value` is guaranteed one row per order, `count("*")` is simpler than `countDistinct`. Prefer enforcing grain over using DISTINCT defensively.

## Q29. Find customers with no completed orders (anti join).

```python
customers_without_completed_orders = (
    customers.alias("c")
    .join(
        orders.filter(F.col("order_status") == "COMPLETED")
              .select("customer_id").distinct().alias("o"),
        F.col("c.customer_id") == F.col("o.customer_id"),
        "left_anti"
    )
)
```

**Alternative:** `left` join followed by `where(o.customer_id is null)`. `left_anti` directly communicates absence and avoids carrying right-side columns.

## Q30. Find customers with at least one completed order (semi join).

```python
customers_with_completed_orders = (
    customers.join(
        orders.filter(F.col("order_status") == "COMPLETED")
              .select("customer_id").distinct(),
        "customer_id",
        "left_semi"
    )
)
```

A semi join returns left rows for which a match exists without multiplying them by the number of right-side matches.

## Q31. Rename multiple columns safely.

```python
renamed = orders.withColumnsRenamed({
    "order_ts": "order_timestamp",
    "order_status": "status",
})
```

For older runtimes, use sequential `withColumnRenamed` or `select` aliases. Check for collisions and case-sensitivity rules.

## Q32. Drop exact duplicate rows vs duplicate business keys.

```python
exact_deduped = df.dropDuplicates()
key_deduped = df.dropDuplicates(["order_id"])
```

`dropDuplicates(["order_id"])` does not express which version wins. If columns differ and latest source version is required, use `row_number` over a deterministic order.

**Best:** Deduplication policy must define event identity, winner precedence, tie-break, tombstones, and replay.

## Q33. Keep the latest record per customer deterministically.

```python
w = Window.partitionBy("customer_id").orderBy(
    F.col("updated_at").desc_nulls_last(),
    F.col("ingested_at").desc(),
    F.col("source_sequence").desc()
)

latest_customers = (
    raw_customer_changes
    .withColumn("_rn", F.row_number().over(w))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)
```

**Best:** Use a source sequence/LSN where available. Timestamp alone can tie or be out of order. Keep the latest tombstone in canonical state; filtering deletes before ranking can resurrect stale rows.

## Q34. Find top 3 customers by spend in each currency.

```python
customer_spend = (
    completed_order_value
    .groupBy("customer_id", "currency_code")
    .agg(F.sum("net_merchandise_value").alias("spend"))
)

w = Window.partitionBy("currency_code").orderBy(F.col("spend").desc())
top_three_with_ties = (
    customer_spend
    .withColumn("spend_rank", F.dense_rank().over(w))
    .filter(F.col("spend_rank") <= 3)
)
```

Use `row_number` with customer_id tie-breaker for at most three rows; use dense_rank to preserve tied rank positions. Ask what “top three” means.

## Q35. Find customers spending above their currency-level average.

```python
w = Window.partitionBy("currency_code")
above_average = (
    customer_spend
    .withColumn("currency_avg", F.avg("spend").over(w))
    .filter(F.col("spend") > F.col("currency_avg"))
)
```

A grouped average joined back is another option. A window keeps customer rows without a separate join. Compare plan and readability.

## Q36. Calculate a running total per customer and currency.

```python
w = (
    Window.partitionBy("customer_id", "currency_code")
    .orderBy("order_ts", "order_id")
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

running = order_value_with_ts.withColumn(
    "running_value",
    F.sum("net_merchandise_value").over(w)
)
```

The input must be one row per order. Explicit row frame and tie-break key make semantics deterministic.

## Q37. Calculate previous order value using lag.

```python
w = Window.partitionBy("customer_id", "currency_code").orderBy("order_ts", "order_id")

with_previous = (
    order_value_with_ts
    .withColumn("previous_value", F.lag("net_merchandise_value").over(w))
    .withColumn("change", F.col("net_merchandise_value") - F.col("previous_value"))
)
```

Aggregate to order grain before LAG; otherwise it compares line items.

## Q38. Find customers whose order value increased vs previous order.

Build on Q37 and filter `change > 0`. Clarify whether only completed orders count, whether zero/negative adjustments are possible, and whether comparison is currency-specific.

## Q39. Calculate a rolling three-order average.

```python
w = (
    Window.partitionBy("customer_id", "currency_code")
    .orderBy("order_ts", "order_id")
    .rowsBetween(-2, Window.currentRow)
)
rolling = order_value_with_ts.withColumn(
    "avg_last_3_orders", F.avg("net_merchandise_value").over(w)
)
```

Three rows are not three calendar days. For a calendar-time window, build a date spine or use a supported time-range frame and validate exact semantics.

## Q40. Find customers active on three consecutive calendar days.

```python
customer_days = (
    events
    .select("customer_id", F.to_date("event_ts").alias("activity_date"))
    .filter(F.col("customer_id").isNotNull())
    .distinct()
)

w = Window.partitionBy("customer_id").orderBy("activity_date")
streak_candidates = (
    customer_days
    .withColumn("d1", F.lag("activity_date", 1).over(w))
    .withColumn("d2", F.lag("activity_date", 2).over(w))
    .filter(
        (F.datediff("activity_date", "d1") == 1)
        & (F.datediff("d1", "d2") == 1)
    )
)
```

Deduplicate customer/day first. Multiple events on one day must not create false consecutive-day sequences.

## Q41. Find longest consecutive active-day streak (gaps and islands).

```python
w = Window.partitionBy("customer_id").orderBy("activity_date")
numbered = customer_days.withColumn("_rn", F.row_number().over(w))

islands = numbered.withColumn(
    "_island_key",
    F.date_sub(F.col("activity_date"), F.col("_rn"))
)

streaks = (
    islands.groupBy("customer_id", "_island_key")
    .agg(
        F.min("activity_date").alias("streak_start"),
        F.max("activity_date").alias("streak_end"),
        F.count("*").alias("streak_days")
    )
)

w_longest = Window.partitionBy("customer_id").orderBy(
    F.col("streak_days").desc(), F.col("streak_end").desc()
)

longest = (
    streaks.withColumn("_rn", F.row_number().over(w_longest))
    .filter(F.col("_rn") == 1)
    .drop("_rn", "_island_key")
)
```

**Why:** Subtracting row number from date gives a constant group key for consecutive dates. This is a reusable gaps-and-islands pattern.

## Q42. Find monthly retention.

Create distinct customer/month activity, then self-join month N to N+1. Keep a calendar spine if missing months must show zero. Clearly distinguish rolling active-month retention from signup-cohort retention.

## Q43. Build an ordered view → cart → purchase funnel within session.

```python
session_steps = (
    events
    .groupBy("customer_id", "session_id")
    .agg(
        F.min(F.when(F.col("event_name") == "view_product", F.col("event_ts"))).alias("view_ts"),
        F.min(F.when(F.col("event_name") == "add_to_cart", F.col("event_ts"))).alias("cart_ts"),
        F.min(F.when(F.col("event_name") == "purchase", F.col("event_ts"))).alias("purchase_ts"),
    )
)

funnel = session_steps.select(
    "*",
    F.when(F.col("view_ts").isNotNull(), 1).otherwise(0).alias("viewed"),
    F.when(
        F.col("view_ts").isNotNull() & (F.col("cart_ts") >= F.col("view_ts")), 1
    ).otherwise(0).alias("cart_after_view"),
    F.when(
        F.col("view_ts").isNotNull()
        & (F.col("cart_ts") >= F.col("view_ts"))
        & (F.col("purchase_ts") >= F.col("cart_ts")), 1
    ).otherwise(0).alias("purchase_after_cart"),
)
```

This is simplified: product-specific funnels, repeated steps, and multiple purchases require event sequencing and product matching. Define attribution window and allowed gaps.

## Q44. Sessionize events using a 30-minute inactivity gap.

```python
w = Window.partitionBy("customer_id").orderBy("event_ts", "event_id")

ordered_events = events.withColumn("previous_ts", F.lag("event_ts").over(w))

flagged = ordered_events.withColumn(
    "new_session",
    F.when(
        F.col("previous_ts").isNull()
        | ((F.col("event_ts").cast("long") - F.col("previous_ts").cast("long")) > 1800),
        1
    ).otherwise(0)
)

w_running = w.rowsBetween(Window.unboundedPreceding, Window.currentRow)

sessionized = flagged.withColumn(
    "derived_session_number", F.sum("new_session").over(w_running)
)
```

Clarify whether exactly 30 minutes starts a new session (`>` vs `>=`) and whether an upstream session ID is trusted. If it is, validate rather than recreate it blindly.

## Q45. Explode product arrays.

```python
orders_with_products = spark.createDataFrame(
    [(1, ["keyboard", "mouse"]), (2, ["monitor"])],
    ["order_id", "product_names"]
)

exploded = orders_with_products.select(
    "order_id",
    F.explode("product_names").alias("product_name")
)
```

`explode` emits one output row per array element. `explode_outer` retains a row for NULL/empty input with NULL element (semantics should be checked for the runtime and input).

## Q46. Flatten nested JSON / struct fields.

```python
flattened = events.select(
    "event_id",
    "customer_id",
    "event_ts",
    F.col("event_properties.device.type").alias("device_type"),
    F.col("event_properties.geo.country").alias("event_country")
)
```

Prefer schema-aware struct access when reading structured JSON. Avoid converting the entire row to JSON strings just to extract known fields.

## Q47. Parse timestamps safely.

```python
parsed = raw_events.withColumn(
    "event_ts",
    F.to_timestamp("event_ts_raw", "yyyy-MM-dd HH:mm:ss")
)

spark.conf.set("spark.sql.session.timeZone", "UTC")
```

Quarantine invalid parse results (NULL) with original payload and reason. Timestamp-with-time-zone semantics differ among formats and connectors.

## Q48. Count NULLs in every column.

```python
null_counts = raw.select(*[
    F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
    for c in raw.columns
])
```

This produces one aggregate row but scans the dataset. For very wide/large inputs consider profiling selected columns, sampling for discovery, or metrics produced during ingestion.

## Q49. Find duplicate order IDs.

```python
duplicate_keys = (
    orders.groupBy("order_id")
    .count()
    .filter(F.col("count") > 1)
)
```

To inspect all duplicate rows, use a window count and filter `_count > 1`. Do not choose an arbitrary winner without a source-version policy.

## Q50. Find source-only and target-only order keys.

```python
source_only = source_orders.join(
    target_orders.select("order_id").distinct(),
    "order_id",
    "left_anti"
)

target_only = target_orders.join(
    source_orders.select("order_id").distinct(),
    "order_id",
    "left_anti"
)
```

**Best:** `left_anti` directly expresses the set difference. Compare duplicate-key counts separately; key presence does not prove row equality.

## Q51. Reconcile source and target aggregates.

```python
source_agg = source_orders.groupBy("order_date", "currency_code").agg(
    F.count("*").alias("row_count"),
    F.sum("order_value").alias("total_value")
)

target_agg = target_orders.groupBy("order_date", "currency_code").agg(
    F.count("*").alias("row_count"),
    F.sum("order_value").alias("total_value")
)

reconciliation = (
    source_agg.alias("s")
    .join(target_agg.alias("t"), ["order_date", "currency_code"], "full")
    .select(
        F.coalesce(F.col("s.order_date"), F.col("t.order_date")).alias("order_date"),
        F.coalesce(F.col("s.currency_code"), F.col("t.currency_code")).alias("currency_code"),
        F.col("s.row_count").alias("source_count"),
        F.col("t.row_count").alias("target_count"),
        F.col("s.total_value").alias("source_value"),
        F.col("t.total_value").alias("target_value"),
    )
)
```

Add null-safe difference flags and tolerance. Equal counts and sums can still hide swapped records; combine aggregates with key and row-level comparisons.

## Q52. Compare rows null-safely.

```python
s = source_orders.alias("s")
t = target_orders.alias("t")

mismatches = (
    s.join(t, "order_id", "inner")
    .filter(
        ~F.col("s.order_status").eqNullSafe(F.col("t.order_status"))
        | ~F.col("s.customer_id").eqNullSafe(F.col("t.customer_id"))
        | ~F.col("s.currency_code").eqNullSafe(F.col("t.currency_code"))
        | ~F.col("s.order_value").eqNullSafe(F.col("t.order_value"))
    )
)
```

For money, apply agreed decimal precision/rounding; do not use arbitrary floating-point tolerance without contract. Hashes can accelerate screening but require canonical serialization and should not replace mismatch diagnosis.

## Q53. Why should you avoid collect() and toPandas() on large DataFrames?

Both move data to the driver/Python process. The driver may OOM or spend excessive time serializing/transferring data.

**Safer:** `limit(n).collect()` only for a known small result; distributed writes/aggregations for large outputs; `toLocalIterator()` only when streaming driver-side consumption is explicitly bounded and safe.

**Principal:** Define driver memory limits and code review rules preventing unbounded materialization.

## Q54. Explain repartition() vs coalesce().

```python
balanced = df.repartition(400, "customer_id")  # redistribution / shuffle
fewer = df.coalesce(40)                        # narrow reduction in many cases
```

- `repartition`: redistributes rows and can increase/decrease partitions; normally causes shuffle.
- `coalesce`: primarily reduces partition count without a full shuffle; can preserve imbalance.

**Best:** Use repartition when balanced distribution or key partitioning is needed; coalesce when reducing output task/file count after filtering and imbalance is acceptable. Inspect actual plan.

## Q55. How do you choose partition count?

Consider input size, target task size, available cores, shuffle volume, operator memory, file count, and concurrency. There is no magic “200 partitions” rule.

**Method:** Baseline job → Spark UI task distribution → identify tiny/huge tasks → adjust source and shuffle partitioning separately → compare runtime, spill, and output files.

AQE can coalesce post-shuffle partitions when enabled; it does not solve every input partition or output-file problem.

---

# Part 4 — Joins, skew, and execution strategies

## Q56. Explain broadcast hash join and when to use it.

```python
result = facts.join(
    F.broadcast(products.select("product_id", "category")),
    "product_id",
    "left"
)
```

A small relation is distributed to executors so the large side need not be shuffled for the join.

**Use when:** The build side's actual in-memory size fits safely on each executor and the join type supports broadcast.

**Avoid when:** The “small” table is large after serialization, executor memory is tight, or many concurrent broadcasts compete.

Verify with `explain("formatted")` and Spark UI. Hints are guidance, not a guarantee for every join type.

## Q57. Sort-merge join vs broadcast hash join vs shuffled hash join?

- Broadcast hash: small build side; avoids shuffling streamed side.
- Sort-merge: large equi-join sides; shuffle and sort by keys then merge.
- Shuffled hash: shuffle both sides then build hash maps per partition; memory-sensitive.

**Best:** Let statistics/AQE choose unless you have evidence. A forced hint can make a plan worse.

## Q58. What is data skew?

A small number of keys own a disproportionate amount of data, creating oversized partitions and straggler tasks.

```python
key_distribution = (
    orders.groupBy("customer_id")
    .count()
    .orderBy(F.desc("count"))
)
```

Look at task duration, shuffle read, spill, and max-vs-median partition size in Spark UI.

## Q59. How do you fix skew without salting?

Try, in order:
1. Verify it is key skew, not slow input/external I/O.
2. Filter/project earlier.
3. Pre-aggregate if mathematically correct.
4. Broadcast the small side if feasible.
5. Enable/test AQE skew join handling.
6. Isolate heavy-hitter keys to a separate path.

Salting is not the default first fix.

## Q60. Explain salting for a skewed join with code.

```python
salt_buckets = 16

skewed_facts = facts.withColumn(
    "_salt",
    F.pmod(F.hash("order_id"), F.lit(salt_buckets))
)

# Replicate only dimension keys that are known heavy hitters.
salted_dim = (
    heavy_key_dimension
    .withColumn("_salt", F.explode(F.sequence(F.lit(0), F.lit(salt_buckets - 1))))
)

# Non-heavy keys take a separate unsalted join path.
salted_result = skewed_facts.join(
    salted_dim,
    ["customer_id", "_salt"],
    "inner"
)
```

This is an illustrative heavy-hitter path; real implementation must combine salted heavy keys with normal non-heavy-key joins and ensure no duplicates.

**Trade-off:** Dimension replication increases data and memory. Choose salt buckets from observed skew and validate aggregate equivalence.

## Q61. What is Adaptive Query Execution (AQE)?

AQE can re-optimize portions of a query using runtime statistics. Common capabilities include coalescing post-shuffle partitions, converting some sort-merge joins to broadcast joins, and handling skewed shuffle partitions.

**Best:** Treat AQE as a useful optimizer, not a substitute for correct grain, stats, data layout, or plan inspection.

## Q62. How do you prove a broadcast hint worked?

```python
joined = facts.join(F.broadcast(dim), "product_id")
joined.explain("formatted")
```

Inspect for `BroadcastHashJoin` and broadcast exchange. Confirm in SQL tab/runtime metrics that the broadcast completed and memory stayed safe. A hint in source code is not proof of physical plan.

## Q63. Why can broadcast make a job slower or fail?

- Actual build-side size is larger than expected.
- Every executor needs the broadcast relation in memory.
- Serialization/deserialization and broadcast transfer are expensive.
- Concurrent queries multiply memory pressure.
- Broadcast timeout or executor OOM occurs.
- Join type/condition may not permit the expected strategy.

Measure actual size and executor memory; do not decide from compressed file size alone.

## Q64. What causes spill to disk?

An operator's memory demand exceeds available execution memory or the in-memory data structure cannot remain resident. Sorts, hash aggregates, joins, and shuffle operations can spill.

**Best:** Reduce rows/columns, pre-aggregate, fix skew, right-size partitions, and validate memory/concurrency. Increasing executor memory alone may not fix an algorithmic skew issue.

## Q65. What is spark.sql.shuffle.partitions?

It controls the default number of shuffle partitions for many SQL/DataFrame shuffle operations (default varies by Spark release/configuration; historically 200). It is not the number of input partitions or output files.

Tune with data size/task metrics and AQE. Never set a fixed number without considering workload variability.

---

# Part 5 — Performance engineering

## Q66. A 3 TB DataFrame job runs 5× slower after a data-volume increase. How do you investigate?

1. Compare input rows/bytes and file count.
2. Compare physical plans and scan pruning.
3. Compare shuffle bytes, partition distribution, and skew.
4. Inspect sort/hash spill, executor GC, CPU, and memory.
5. Check statistics, broadcast decisions, and AQE.
6. Inspect cluster utilization, queueing, and concurrent workloads.
7. Check source throttling and object-store latency.
8. Reproduce with representative partitions and measure one change at a time.

**Best:** Use Spark UI + event logs + query plan + data-quality metrics. Do not reflexively scale the cluster.

## Q67. Explain cache() vs persist() vs checkpoint().

- `cache()`: persist with the API's default storage level.
- `persist(level)`: choose storage level.
- `checkpoint()`: materialize to checkpoint storage and truncate lineage when configured.

```python
from pyspark import StorageLevel

reused = expensive_transform(raw).persist(StorageLevel.MEMORY_AND_DISK)
reused.count()        # materialize persistence
# multiple downstream consumers use reused
reused.unpersist()
```

Checkpointing is not merely another cache. It has storage/reliability implications and is useful for long lineage or iterative/stateful recovery patterns.

## Q68. Why can caching make performance worse?

Caching consumes executor memory, can evict useful blocks, increase GC, compete with shuffle memory, and may never be reused enough to repay materialization cost.

**Best:** Cache only expensive reused intermediates; materialize once; unpersist when done. Compare runtime and storage metrics.

## Q69. How do repeated actions affect a pipeline?

```python
df.count()
df.show()
df.write.parquet(path)
```

Each action may trigger a separate job and recompute the lineage. If multiple actions reuse an expensive result, consider a carefully placed persist/cache; for a one-off diagnostic, avoid scanning a huge dataset repeatedly.

## Q70. How does partition pruning work?

A partition filter allows Spark/data source to skip irrelevant physical partitions.

```python
daily = spark.read.parquet("/lake/orders")
one_day = daily.filter(F.col("order_date") == F.lit(date(2025, 3, 1)))
```

Verify `PartitionFilters`/scan metrics in plan. Physical partitioning should align with common selective predicates and lifecycle needs, not high-cardinality keys by default.

## Q71. What is predicate pushdown vs partition pruning?

- Partition pruning skips whole physical partitions.
- Predicate pushdown pushes supported filters toward the data source/reader to avoid reading/filtering unnecessary records.
- File statistics/data skipping can further skip row groups/files depending on format/table implementation.

They are different layers and not every predicate is pushable.

## Q72. Why is SELECT * expensive?

It can prevent column pruning and increase I/O, network, memory, and serialization. Select only required fields, especially from wide Parquet/Delta/Iceberg tables.

## Q73. Explain small-file problem and its symptoms.

Too many tiny files increase listing/open/metadata/task scheduling overhead and can reduce scan throughput. Symptoms include huge task counts, low bytes per task, slow planning, and slow table maintenance.

**Best:** Control write parallelism and partition cardinality; compact files using table-format/provider-supported maintenance; avoid repartitioning to one file.

## Q74. Why is coalesce(1) usually a bad production pattern?

It funnels all data into one partition/task and creates a single output file, destroying parallel write throughput and risking memory/time bottlenecks. Only use for genuinely tiny outputs where the single-file requirement is explicit.

## Q75. How do you optimize a write to Parquet/Delta?

- Prune columns and rows.
- Choose suitable partition columns (low/moderate cardinality, common filters).
- Control output parallelism and file size.
- Avoid one-file-per-key layouts.
- Use table-format compaction/maintenance.
- Consider compression codec and schema evolution.
- Validate stats, file count, and downstream query patterns.

**Staff/Principal:** Optimize reads, writes, concurrency, maintenance cost, and retention together.

## Q76. What is the difference between repartitioning a DataFrame and partitioning a table on write?

`repartition()` redistributes data across Spark execution partitions. `partitionBy()` on a file writer lays out output directories/files by column values. One is execution distribution; the other is storage layout.

```python
df.repartition(200, "order_date").write.partitionBy("order_date").parquet(path)
```

This may be redundant or cause multiple files per value. Decide based on output task distribution and table partition design.

## Q77. How do you inspect a physical plan?

```python
result.explain("formatted")
```

Look for scans, pushed filters, partition filters, exchanges, sort, aggregate, join strategy, Python evaluation nodes, and adaptive plan changes. Then correlate with actual SQL UI metrics.

## Q78. What is the difference between estimated and actual statistics?

Estimates guide planning; actual metrics describe runtime rows/bytes/time. Large discrepancies can cause wrong join strategy or partition decisions. Refresh table statistics where the catalog/engine supports them and use AQE when available.

## Q79. What is the best way to tune partition sizes?

There is no universal byte target; row width, format, operator, cluster, memory, and skew change it. Inspect max/median task time, input/shuffle bytes per task, spill, and number of tasks. Fix source file layout and shuffle partitioning as separate concerns.

## Q80. How do you tune Spark for cost, not just runtime?

Measure cost per successful output (compute time, DBUs/credits, bytes read/written, retries, storage, maintenance, and operator effort). Reduce repeated scans, improve incremental logic, schedule appropriately, right-size compute, and avoid caching/over-provisioning. Don't trade away correctness or SLA silently.

---

# Part 6 — Python execution, UDFs and API choices

## Q81. Why prefer built-in Spark functions over Python UDFs?

Built-in expressions are visible to Catalyst and can use JVM execution/codegen and data-source optimizations. A Python UDF introduces a Python execution boundary and limits optimizer visibility.

```python
normalized = customers.withColumn("email_norm", F.lower(F.trim("email")))
```

**Best:** Use native Spark functions first. UDF only when business logic cannot reasonably be expressed natively.

## Q82. Scalar Python UDF vs Pandas UDF vs Arrow UDF?

- Scalar Python UDF: Python function applied to column values; can involve per-row Python semantics and serialization cost.
- Pandas UDF: vectorized batches using Pandas/Arrow.
- Arrow UDF: uses Arrow columnar data representation without requiring the Pandas API in the same way.

Newer Spark releases have changed Arrow optimization/defaults; verify exact behavior in the runtime. Vectorization reduces overhead but does not fix an expensive algorithm or memory-heavy Python function.

## Q83. Implement a Pandas UDF and compare with built-in.

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf

@pandas_udf("double")
def add_tax_vectorized(amount: pd.Series) -> pd.Series:
    return amount * 1.18

taxed = order_value.withColumn("amount_with_tax", add_tax_vectorized("net_value"))
```

For this example, built-in `F.col("net_value") * F.lit(1.18)` is preferable. The UDF demonstrates the API, not the recommended solution.

## Q84. When would you use mapInPandas?

For partition/batch-level Pandas processing when the operation cannot be expressed as SQL/DataFrame functions and vectorization helps. It operates on iterators of Pandas DataFrames per partition. Ensure bounded batch memory, schema correctness, and no accidental driver collection.

## Q85. map vs mapPartitions vs foreachPartition?

- RDD `map`: function per record.
- RDD `mapPartitions`: function per partition/iterator, useful for amortizing expensive setup.
- `foreachPartition`: action with side effects per partition.

For external database/API writes, use bounded connections, idempotent upserts, retry/backoff, rate limiting, and avoid opening a connection per row. Prefer supported batch sinks/connectors.

## Q86. What is Arrow and why does it matter?

Arrow is a columnar in-memory format used for efficient JVM/Python data interchange and vectorized workloads. It can reduce serialization overhead, but batches still consume memory and Python operations still require CPU.

## Q87. Why can a UDF break predicate pushdown or query optimization?

Spark may treat UDF body as opaque; it cannot infer arbitrary Python logic to simplify/push filters or rewrite expressions. Keep filters/projections in native expressions before UDF where semantics allow.

## Q88. What is Spark Connect?

A client-server architecture where client code communicates with a Spark server using the Spark Connect protocol rather than embedding the classic driver in the client. It changes deployment and client/server compatibility considerations; APIs/features depend on Spark version.

**Principal:** Consider authentication, network latency, session isolation, remote execution, observability, and version compatibility.

---

# Part 7 — File formats, schema and table layout

## Q89. Parquet vs ORC vs CSV vs JSON?

- Parquet/ORC: columnar, typed, compressed, good for analytics.
- CSV: simple interchange, no strong embedded type system.
- JSON: flexible nested representation; can be expensive to parse and schema-manage.
- Delta/Iceberg/Hudi: table formats add transaction/metadata/evolution capabilities over data files (specific capabilities vary).

**Best:** Use columnar typed format for curated analytics. Keep raw payload where audit/replay/schema-evolution requirements justify it.

## Q90. Schema inference vs explicit schema?

Inference reads data to guess types and may be expensive/inconsistent across batches. Explicit schema improves predictability and contract enforcement.

**Best:** Use explicit schema for production ingestion, with controlled schema evolution and quarantine for incompatible changes.

## Q91. How do you handle additive and breaking schema evolution?

Classify additive vs breaking changes; validate types/nullability/meaning; version contracts; allow compatible optional additions; quarantine incompatible changes; maintain compatibility tests and lineage; coordinate rollout/deprecation. Never silently map renamed critical fields to NULL.

## Q92. What causes corrupt records in CSV/JSON ingestion?

Malformed quoting, delimiter/escape issues, invalid encoding, schema mismatch, type casts, truncated lines, or invalid JSON structures. Use permissive/fail-fast modes according to criticality; preserve corrupt payload and error reason.

## Q93. How do you read nested arrays and structs?

Use schema-aware access, `explode`/`posexplode` for array expansion, and `select("struct_field.*")` or nested column references for structs. Understand resulting grain after explosion; one input row may produce many outputs.

## Q94. How do you avoid high-cardinality partition columns?

Avoid partitioning storage by customer_id/order_id when values are numerous and per-partition data is small. Use date/month or low/moderate-cardinality dimensions aligned with filters, then cluster/sort or use file/table data skipping where supported.

---

# Part 8 — Incremental processing, CDC and SCD

## Q95. Design incremental ingestion with watermark.

```python
batch = source_df.filter(
    (F.col("source_updated_at") > F.lit(last_watermark))
    & (F.col("source_updated_at") <= F.lit(batch_cutoff))
)
```

Freeze upper cutoff and persist batch metadata. Timestamp-only watermark risks ties, late records, clock drift, and invisible deletes. Prefer source LSN/sequence or composite cursor; otherwise overlap windows plus idempotent merge and reconciliation.

## Q96. Why is timestamp-only watermark unsafe?

Multiple records can share timestamps; updates can arrive late; clocks can differ; deletes may not be represented. Use source-native ordering (LSN/offset/sequence) where possible. If using timestamp, add deterministic tie-breaker and a replay overlap strategy.

## Q97. Make an incremental PySpark pipeline idempotent.

Stable event/batch identity; deterministic de-duplication; version-aware target merge; explicit delete/tombstone semantics; atomic target/checkpoint design or recovery for partial commit; partition/key-level reconciliation; repeat same batch and prove target unchanged.

**Best:** Idempotency is about final state under retries, not merely “the job can be rerun.”

## Q98. Apply latest order updates with Delta MERGE (illustrative).

```python
from delta.tables import DeltaTable

target = DeltaTable.forPath(spark, target_path)

deduped_stage = (
    staged_orders
    .withColumn(
        "_rn",
        F.row_number().over(
            Window.partitionBy("order_id").orderBy(
                F.col("source_sequence").desc(),
                F.col("ingested_at").desc()
            )
        )
    )
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

(
    target.alias("t")
    .merge(deduped_stage.alias("s"), "t.order_id = s.order_id")
    .whenMatchedUpdateAll(condition="s.source_sequence > t.source_sequence")
    .whenNotMatchedInsertAll()
    .execute()
)
```

This is Delta Lake API, not generic Apache Spark API. Ensure source has one row per key and include tombstone handling/schema policy. Syntax may vary by Delta version.

## Q99. Explain CDC processing order.

Preserve operation type, source key, transaction/LSN/sequence, source commit time, ingestion time, and stable event identity. Deduplicate retransmissions by event ID; order state changes by source sequence; apply insert/update/delete/tombstones; make target updates idempotent; checkpoint only after durable target commit or design recovery.

## Q100. What is SCD Type 1 vs Type 2?

- Type 1: overwrite current attributes; no history.
- Type 2: preserve versions with effective start/end and current indicator.
- Type 3: preserve limited prior values in additional columns.

Choose based on analytical history and correction requirements.

## Q101. Build SCD Type 2 from daily customer snapshots.

```python
w = Window.partitionBy("customer_id").orderBy("snapshot_date")

ordered = (
    customer_snapshot
    .withColumn("prev_country", F.lag("country_code").over(w))
    .withColumn("prev_email", F.lag("email").over(w))
)

changes = ordered.filter(
    F.col("prev_country").isNull()
    | ~F.col("country_code").eqNullSafe(F.col("prev_country"))
    | ~F.col("email").eqNullSafe(F.col("prev_email"))
)

versions = (
    changes
    .withColumn("effective_from", F.col("snapshot_date"))
    .withColumn("next_from", F.lead("snapshot_date").over(w))
    .withColumn(
        "effective_to",
        F.coalesce(F.date_sub("next_from", 1), F.lit(date(9999, 12, 31)))
    )
    .withColumn("is_current", F.col("next_from").isNull())
)
```

This uses inclusive date end dates. Half-open timestamp intervals are usually safer. Daily snapshots cannot capture multiple within-day changes; late history requires interval correction.

## Q102. Resolve dimension version for a late-arriving fact.

Join fact business timestamp to dimension validity range: `fact.customer_id = dim.customer_id AND fact.event_ts >= dim.effective_from AND fact.event_ts < dim.effective_to`.

Use half-open intervals and verify exactly one dimension match. Late-arriving dimension versions can require re-resolving impacted facts.

## Q103. How do you handle deletes and tombstones?

Do not infer delete from absence in incremental extract. Capture explicit CDC delete/tombstone; retain source sequence and delete time; choose physical delete vs soft delete vs SCD history retention; ensure older events cannot resurrect deleted entities.

## Q104. What is a replay-safe backfill?

Immutable source snapshot/range; isolated compute; bounded partitions; idempotent writes; deterministic overlap precedence with live pipeline; checkpoints; partition-level reconciliation; pause/resume; and consumer-facing completeness state.

---

# Part 9 — Structured Streaming

## Q105. Batch vs streaming DataFrame?

Batch has a bounded input; streaming is an unbounded query with incremental execution and state/checkpoint concepts. DataFrame APIs look similar, but supported operations and semantics differ.

## Q106. Read a stream of events from files.

```python
stream = (
    spark.readStream
    .schema(event_schema)
    .json("/landing/events")
)
```

Use explicit schema for production file streams. Schema inference and evolving file schemas need deliberate handling.

## Q107. Write stream with checkpoint.

```python
query = (
    stream.writeStream
    .format("parquet")
    .option("path", "/lake/silver/events")
    .option("checkpointLocation", "/checkpoints/events_silver")
    .outputMode("append")
    .start()
)
```

Checkpoint location must be durable and dedicated to the query's stable identity/semantics. Do not casually reuse a checkpoint across incompatible query changes.

## Q108. Explain output modes.

- Append: newly appended result rows.
- Update: rows updated since last trigger (where supported by operation).
- Complete: entire result table each trigger (for supported aggregations).

Choose according to operator support, sink, state, and consumer contract.

## Q109. What is a watermark?

Watermark bounds how late event-time data is considered for stateful operations and allows old state to be cleaned under defined semantics.

```python
watermarked = stream.withWatermark("event_ts", "30 minutes")
```

It is not a guarantee that all data later than 30 minutes is discarded immediately in every operator. Understand event-time progress, late-data behavior, and operator semantics.

## Q110. Explain stateful vs stateless streaming operations.

Stateless filter/select/map do not need cross-record state. Stateful operations such as aggregations, stream-stream joins, deduplication, and session windows retain state across triggers.

**Production:** Monitor state size, watermark advancement, state-store latency, checkpoint size, and late data.

## Q111. Exactly-once: what can Spark guarantee?

Avoid blanket statements. End-to-end semantics depend on source replayability, checkpoint/offset management, query semantics, and sink commit/idempotency/transaction support. Some sinks are at-least-once unless the sink implementation adds transactional/idempotent guarantees.

**Best interview answer:** State the guarantees of the actual source and sink, and demonstrate failure/restart tests. “Spark exactly-once” alone is incomplete.

## Q112. What is checkpointing in Structured Streaming?

Checkpoints store query progress/offset and state required for recovery (details depend on source, sink, and stateful operators). They are not the business data archive.

Use durable storage, one checkpoint per query identity, and a compatible query evolution plan. Test restart from checkpoint and full rebuild procedure.

## Q113. How do you deduplicate streaming events?

```python
deduped = (
    stream
    .withWatermark("event_ts", "2 hours")
    .dropDuplicatesWithinWatermark(["event_id"])
)
```

`dropDuplicatesWithinWatermark` is a newer API; check Spark version/provider runtime. Older alternative is watermark + `dropDuplicates` with supported key semantics. The watermark bounds retained state and late-data behavior.

## Q114. How do you handle late events and out-of-order events?

Use event time, watermark policy, source sequence, allowed-lateness contract, and correction strategy. For stateful aggregations, late events may update prior windows within allowed bounds. For CDC entity state, source sequence controls latest state; ingestion order is not business order.

## Q115. How would you monitor a Structured Streaming job?

Track input rate, processed rate, trigger duration, processing time, batch ID, input rows, event-time watermark, state rows/bytes, state-store commit/read latency, checkpoint errors, source lag, sink commit failures, and late/dropped-event metrics. Alert on sustained backlog and freshness SLO breach.

## Q116. How do you safely change a streaming query?

Classify the change: projection/filter, source, stateful operator/schema, output schema, or checkpoint-incompatible change. Test restart, state compatibility, replay, and sink idempotency. Some changes require new checkpoint and controlled rebuild/reconciliation.

---

# Part 10 — Testing, reliability, security and observability

## Q117. How do you unit-test PySpark transformations?

Create tiny DataFrames with explicit schema covering happy path, NULL, duplicate, ties, invalid values, and boundary timestamps. Compare collected small expected output with deterministic sort/order. Keep tests independent of physical partition order.

Use local Spark for logic tests; integration-test actual table formats/connectors/permissions separately.

## Q118. How do you test data quality at scale?

Define reusable checks: schema, required columns, uniqueness, accepted values, null rates, ranges, referential integrity, volume anomaly, freshness, and source-target reconciliation. Use aggregations and partition-level controls; avoid collecting all failures to driver.

## Q119. How do you quarantine invalid records?

Split valid and invalid DataFrames with deterministic predicates; attach reason codes and batch/source metadata; persist invalid payload for remediation/replay. Decide whether batch fails or valid records proceed based on contract criticality. Publish partial completeness state.

## Q120. How do you make writes to external APIs or databases safe?

Avoid a driver-side loop and avoid one connection per row. Use partition/batch-level writes where required, connection pooling carefully, bounded parallelism, idempotency keys, retry/backoff, rate limits, and dead-letter capture. Spark may retry tasks; side effects must tolerate duplicate attempts.

## Q121. What is the small-file problem and how do you monitor it?

Track output file count, size distribution, average/median file size, partition cardinality, write task count, and planning latency. Compact with table-format-supported maintenance. Avoid excessive high-cardinality storage partitions.

## Q122. How do you design observability?

Capture pipeline run ID, source offsets, input/output rows, bytes, schema version, duration, retry count, quality metrics, rejected rows, watermark, table version, and code version. Add structured logs, traces/metrics as supported, lineage, alert ownership, and runbooks.

## Q123. How do you secure PII in PySpark pipelines?

Classify fields; least-privilege access; mask/tokenize sensitive values; avoid logging payloads; restrict temporary/staging locations; encrypt in transit/at rest; govern exports; apply retention/deletion; test access policy. A `drop("email")` in one DataFrame is not a complete privacy control.

## Q124. How do you handle multi-tenant data?

Enforce tenant isolation through platform permissions/row policies where supported, tenant-aware keys, safe join predicates, and automated cross-tenant leakage tests. Do not rely only on developers remembering a tenant filter.

## Q125. How do you upgrade a Spark runtime safely?

Check Spark/Python/Java/Scala compatibility, ANSI SQL behavior changes, connector/table-format compatibility, UDF/Arrow behavior, serialization, streaming checkpoint/state compatibility, and performance regressions. Run correctness suites and representative performance benchmarks before canary rollout.

---

# Part 11 — Architecture and Staff/Principal scenarios

## Q126. Design a 5 TB/day batch pipeline using the dataset.

**Requirements to clarify:** Batch vs micro-batch, arrival profile, SLA, source CDC capability, file format, growth, consumers, retention, PII, RPO/RTO, replay, and cost.

**Architecture:**
1. Immutable raw landing with source metadata and schema version.
2. Validated bronze ingestion with contract checks and quarantine.
3. Silver canonicalization: deterministic dedupe, CDC ordering, typed timestamps, tombstones.
4. Curated order/customer/product facts at declared grain.
5. Incremental materialization, not full scan where avoidable.
6. Reconciliation and publish gate.
7. Gold serving models for product/customer metrics.
8. Observability, lineage, security, and backfill controls.

**Best:** Use DataFrames/native expressions, columnar storage/table format appropriate to platform, partition by common access/lifecycle dimensions, manage files, and optimize using measured shuffle/skew/scan metrics.

## Q127. Design a 100K events/sec streaming pipeline.

Clarify peak vs average throughput, event size, ordering/key, allowed lateness, state horizon, latency SLO, sink semantics, retention, replay, and cost.

Use scalable ingestion, schema/version validation, durable checkpointed processing, event-time windows/watermarks, bounded state, idempotent sink writes, DLQ/quarantine, autoscaling/throughput controls, and lag/backpressure monitoring.

**Principal:** Define SLOs, failure domains, capacity headroom, replay contract, and business handling of delayed/incomplete windows.

## Q128. Design a metadata-driven PySpark framework.

Define metadata contract: source, schema, keys, incremental cursor, transforms, DQ rules, target, partition policy, owner, SLA, retry, and PII tags.

Separate orchestration/config parsing from reusable transformation libraries. Validate metadata before execution; generate declarative DataFrame plans; log run metadata; support versioning and rollback.

**Avoid:** A giant dynamic `eval`-based framework that hides logic, weakens typing, and is impossible to test. Use typed config/schema and explicit extension points.

## Q129. Design a reusable source-to-target reconciliation framework.

Layers: schema/type check; row counts and distinct business keys; duplicate/orphan checks; partition-level counts and aggregates; anti-join key differences; null-safe row-level attribute comparisons; optional canonical row hash for screening; exception store with reason/owner/run ID; publish gate and alert thresholds.

**Staff/Principal:** Define criticality tiers and reconciliation SLOs; don't treat every mismatch identically.

## Q130. A pipeline finishes successfully but revenue is wrong. What do you do?

Freeze output/run ID; reproduce against immutable inputs; confirm metric definition, currency, statuses/refunds, order grain; inspect joins/cardinality and late updates; compare aggregates and key differences; identify first divergent stage; backfill impacted partitions; reconcile; add regression test and alert.

Do not begin by increasing cluster size or blindly rerunning the job.

## Q131. A job is slow only on Mondays. Why?

Weekly volume/data distribution may differ, late batch backlog, skewed keys, upstream file layout, concurrency, cluster autoscaling, table maintenance, statistics, or external source throttling. Compare run-level input distributions, plans, task skew, cluster metrics, and competing workloads.

## Q132. How do you choose between Spark and a simpler processing engine?

Consider data volume, memory, latency, joins/shuffles, parallelism, ecosystem, operational overhead, and cost. Use single-node DataFrame engines for data that fits comfortably and has no distributed requirement; use Spark where distributed processing and ecosystem justify cluster complexity.

## Q133. How do you manage a breaking contract change across many consumers?

Version contract; dependency/lineage impact analysis; dual-write or compatibility view; consumer migration window; automated contract tests; telemetry for old-version usage; deprecation date; rollback and owner communications.

## Q134. A critical table misses its freshness SLA. What do you do?

Expose freshness/completeness; stop or mark publication according to contract; identify source lag vs compute vs sink; prioritize recovery/backfill; communicate consumer impact; reconcile before clearing incident; postmortem with preventative controls.

## Q135. How do you review a PySpark pull request at Staff level?

Check grain and correctness, schema/null semantics, join cardinality, deterministic ordering, shuffle/driver actions, UDF use, partition/file design, idempotency, tests, privacy, observability, and failure recovery. Ask author to explain expected plan and how performance will be measured.

## Q136. How do you lead a Spark optimization effort across teams?

Establish baseline metrics and workload categories; identify top cost/latency contributors; agree optimization standards; create reusable libraries/templates; train teams; use canary and regression benchmarks; publish measurable outcomes; preserve ownership and exception process.

---

# Part 12 — Current Spark/PySpark feature awareness

This section separates version-specific features from long-standing DataFrame concepts. The newest Apache Spark release should be checked before an interview; managed runtimes can lag upstream.

## Q137. What should a Spark 4.x candidate know?

Spark 4.x introduces material compatibility changes (including ANSI behavior defaults and runtime baseline changes) and newer SQL/Python capabilities. Always verify exact release/runtime matrix.

**Upgrade checklist:** ANSI mode, Java/Python/Scala versions, connector/table-format support, Arrow behavior, SQL semantics, streaming state compatibility, and test/benchmark coverage.

## Q138. What is Spark Connect?

Client-server execution protocol enabling a remote client to connect to Spark. Consider compatibility, network, authentication, session isolation, and supported API surface. Do not assume every classic Spark API works identically in Connect mode.

## Q139. What is new in Arrow-optimized Python execution?

Newer Spark 4.x releases expand Arrow-based Python execution and change defaults. Arrow can reduce JVM/Python serialization overhead, but it does not replace native expressions for simple logic. Verify defaults and UDF support in exact runtime.

## Q140. What is Spark's newer CDC support?

Newer Apache Spark versions introduce row-level change-reading capabilities in the SQL/DataFrame ecosystem. Distinguish upstream Spark capabilities from managed table-format features such as Delta Change Data Feed or provider-specific Auto CDC. Check exact release docs and source table support before designing around it.

## Q141. What are Spark Declarative Pipelines?

A declarative pipeline framework in newer Spark distributions for defining managed data flows. Understand its relation to DataFrame/SQL transformations, dependency graph, quality expectations, and runtime capabilities. Managed service packaging and operational behavior may differ.

## Q142. Why should you not blindly quote defaults from an old Spark version?

Defaults change across releases and distributions. Examples include ANSI mode, shuffle partitions, Arrow optimization, adaptive execution, and runtime compatibility. During an interview, state version, inspect effective configuration, and distinguish upstream default from managed runtime override.

---

# Part 13 — Common anti-patterns and decision guide

## 15 PySpark anti-patterns

1. `collect()` / `toPandas()` on unbounded data.
2. Python UDF for logic available natively.
3. Joining raw one-to-many facts and summing multiplied metrics.
4. `dropDuplicates(key)` when winner precedence matters.
5. Blind broadcast of a dimension.
6. Blind `repartition()` everywhere.
7. `coalesce(1)` on large output.
8. Caching data that is used once.
9. Repeated actions on expensive lineage.
10. Partitioning storage by high-cardinality IDs.
11. Ignoring skew and max-task duration.
12. Treating row count as proof of reconciliation.
13. Using Float/Double for money without policy.
14. Using ingestion time instead of source order for CDC.
15. Claiming exactly-once without source/sink semantics.

## Join decision guide

| Situation | Starting strategy | Validate |
|---|---|---|
| Small dimension, large fact | Broadcast hash | Actual in-memory build size and executor memory |
| Two large equi-join facts | Sort-merge/AQE | Shuffle, sort, skew |
| Existence only | Left semi | Right-side duplicates irrelevant |
| Absence only | Left anti | NULL/key semantics |
| Skewed heavy hitter | AQE / isolate / salt | Max vs median task metrics |
| Many-to-many facts | Aggregate to target grain first | Totals and cardinality |

## Performance diagnosis checklist

- [ ] What is the output grain?
- [ ] Are joins multiplying rows?
- [ ] Are filters and column projections pushed down?
- [ ] Is partition pruning occurring?
- [ ] How many input and shuffle partitions?
- [ ] Are task sizes/skew balanced?
- [ ] How much shuffle read/write?
- [ ] Is spill/GC significant?
- [ ] Is broadcast actually safe?
- [ ] Are Python UDFs introducing boundaries?
- [ ] Are repeated actions recomputing lineage?
- [ ] Are files too small or output partitions too many?
- [ ] Is concurrency/queueing the cause?
- [ ] Did the runtime/configuration change?
- [ ] Did the optimization improve cost and correctness, not just runtime?

---

# Part 14 — Forty hands-on coding drills

Solve from a blank editor using only the same e-commerce DataFrames:

1. Create an explicit schema and DataFrame.
2. Read Parquet and validate required columns/types.
3. Read malformed CSV into accepted and rejected records.
4. Normalize email and country codes.
5. Calculate gross and net line value with DecimalType.
6. Aggregate line values to order grain.
7. Join customer attributes without multiplying orders.
8. Find customers with no completed orders.
9. Find customers with completed orders using semi join.
10. Top three spenders by currency with ties.
11. Exactly three spenders with deterministic tie-break.
12. Above-average customer spend by currency.
13. Running order value per customer.
14. Three-order rolling average.
15. Compare each order with previous order.
16. Find three consecutive active calendar days.
17. Find longest active streak.
18. Sessionize events using a 30-minute inactivity rule.
19. Build session funnel with event ordering.
20. Explode product arrays and preserve item grain.
21. Flatten nested event struct fields.
22. Parse timestamp strings and quarantine invalid values.
23. Count NULLs by column.
24. Detect duplicate business keys.
25. Deduplicate raw CDC deterministically.
26. Find source-only keys.
27. Find target-only keys.
28. Compare source/target aggregate controls.
29. Compare rows with null-safe semantics.
30. Detect orphan order items.
31. Implement a skewed join using heavy-hitter salting.
32. Show broadcast and inspect physical plan.
33. Create balanced output partitions without `coalesce(1)`.
34. Write partitioned Parquet and inspect file layout.
35. Implement incremental watermark with overlap.
36. Build Type 2 customer history.
37. Implement idempotent Delta MERGE (where available).
38. Create file-stream reader with explicit schema/checkpoint.
39. Apply watermark and streaming deduplication.
40. Design failure/restart and reconciliation test for streaming output.

---

# Part 15 — Interview communication framework

For every non-trivial PySpark question:

1. Clarify business metric and source/output grain.
2. State schema, keys, and nullability assumptions.
3. Write native DataFrame expressions first.
4. Explain logical plan and likely physical operators.
5. Identify shuffle, skew, scan, sort, or state costs.
6. Compare alternatives and when they win.
7. Explain deterministic behavior and data correctness.
8. Cover retries, idempotency, checkpoint, replay, and backfill.
9. Explain tests and observability.
10. Quantify expected impact with measured evidence.

Useful statements when backed by evidence:

- “I want to declare the target grain before joining.”
- “The child table is one-to-many, so I aggregate before joining financial measures.”
- “The source timestamp does not guarantee source commit order; I prefer LSN/sequence for CDC.”
- “I will inspect the actual physical plan and Spark UI metrics.”
- “Broadcast is about executor memory, not merely relative table size.”
- “A few hot keys can dominate a stage even when average partition size looks healthy.”
- “A successful job status does not prove business correctness.”
- “Exactly-once requires source and sink semantics, not only a checkpoint.”
- “I will test the optimization on representative data and compare correctness, runtime, and cost.”

---

# Part 16 — What interviewers evaluate at ₹70+ LPA levels

| Signal | Weak answer | Strong answer |
|---|---|---|
| DataFrame coding | Knows API names | Correct grain, nulls, ties, schema, deterministic logic |
| Spark internals | Says “Spark is distributed” | Explains stages, tasks, shuffle, plan operators |
| Performance | “Increase workers” | Uses evidence to isolate scan/shuffle/skew/spill/concurrency |
| Reliability | “Retry job” | Idempotent writes, stable checkpoints, replay and reconciliation |
| Streaming | “Enable exactly once” | Explains event time, watermarks, state, source/sink guarantee |
| Architecture | One optimized script | Shared contracts, SLOs, cost, data ownership |
| Leadership | Solves personally | Builds reusable patterns, aligns teams, mentors and governs |

**Lead answer:** “I will aggregate line facts to order grain, use native expressions, add key and DQ checks, and validate shuffle/joins through Spark UI.”

**Staff answer:** “I will publish a tested reusable financial model with explicit grain, CDC ordering, replay safety, and reconciliation controls so multiple teams share the same trusted output.”

**Principal answer:** “I will align source ownership, metric contracts, freshness/correctness SLOs, platform cost, security, and recovery strategy across domains, then govern adoption and exceptions.”

---

# Official references and version awareness

Always verify current behavior in the official documentation for the deployed runtime.

- Apache Spark documentation: https://spark.apache.org/docs/latest/
- PySpark API reference: https://spark.apache.org/docs/latest/api/python/
- Spark SQL performance tuning: https://spark.apache.org/docs/latest/sql-performance-tuning.html
- Spark RDD programming guide: https://spark.apache.org/docs/latest/rdd-programming-guide.html
- Structured Streaming guide: https://spark.apache.org/docs/latest/streaming/index.html
- PySpark Arrow / Pandas guide: https://spark.apache.org/docs/latest/api/python/user_guide/sql/arrow_pandas.html
- PySpark UDF guide: https://spark.apache.org/docs/latest/api/python/user_guide/udfandudtf.html
- Apache Spark release news: https://spark.apache.org/news/
- Delta Lake documentation (where used): https://docs.delta.io/latest/index.html

---

# END OF TOPIC — PYSPARK

This chapter uses one connected e-commerce model throughout. Add realistic edge cases to these same DataFrames rather than switching to unrelated employee/sales/login schemas.
