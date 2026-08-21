# Databricks notebook source
# ================================================================================
# Kafka & Streaming Handbook — Chapter 2: Spark Structured Streaming
# ================================================================================
# Covers: Reading from Kafka, streaming transformations, output modes,
#         watermarking, stateful operations, and checkpointing.
#
# DATABRICKS NOTE: spark is pre-configured. All code runs on Databricks.
#                  Replace Kafka broker/topic with your actual values.
# ================================================================================

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# ==============================================================================
# Streaming vs Batch — Core Difference
# ==============================================================================
# INTERVIEW Q: "What is Spark Structured Streaming?"
#
# Structured Streaming = a streaming engine built on top of the Spark SQL engine.
# It treats a live data stream as an unbounded table that grows continuously.
# You write the same DataFrame/SQL transformations as batch — Spark handles the rest.
#
#   Batch:     fixed dataset  → transform → write once
#   Streaming: infinite dataset → micro-batch → write continuously
#
# Trigger modes:
#   default          → process new data as fast as possible (micro-batches)
#   ProcessingTime   → trigger every N seconds
#   Once             → process all available data once, then stop (like batch)
#   AvailableNow     → same as Once but smarter (respects rate limits)
#   Continuous       → ~1ms latency (experimental, limited operations)


# ==============================================================================
# Reading from Kafka
# ==============================================================================
# INTERVIEW Q: "How do you read from Kafka in Spark Structured Streaming?"

KAFKA_BROKER = "your-broker:9092"    # replace with actual
TOPIC        = "user_events"

raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", TOPIC)
    .option("startingOffsets", "latest")    # "earliest" to replay from beginning
    .option("maxOffsetsPerTrigger", 10000)  # rate limiting per micro-batch
    .load()
)

# Kafka delivers: key, value, topic, partition, offset, timestamp, timestampType
# key/value are BINARY → cast to string
raw_stream.printSchema()


# ==============================================================================
# Parsing the Value (JSON → Struct)
# ==============================================================================
# INTERVIEW Q: "How do you parse JSON messages from Kafka in Spark Streaming?"

event_schema = StructType([
    StructField("user_id",    StringType(),    True),
    StructField("event_type", StringType(),    True),
    StructField("amount",     IntegerType(),   True),
    StructField("event_time", TimestampType(), True),
])

parsed_stream = (
    raw_stream
    .select(F.col("value").cast("string").alias("raw_json"))
    .select(F.from_json("raw_json", event_schema).alias("data"))
    .select("data.*")   # flatten struct to columns
)


# ==============================================================================
# Output Modes
# ==============================================================================
# INTERVIEW Q: "What are the three output modes in Spark Structured Streaming?"
#
#   Append  → only NEW rows are written. No updates to existing output.
#             Use for: non-aggregated streams, event logs.
#
#   Update  → only CHANGED rows are written (rows whose aggregated value changed).
#             Use for: aggregations with updates (running sum, count).
#
#   Complete → ENTIRE result table is rewritten on every trigger.
#              Use for: small aggregations (must fit in memory).
#              ⚠️ Warning: rewrites everything — expensive for large results.


# ==============================================================================
# Stateless Transformations (filter, select, map)
# ==============================================================================
# Same as batch — no memory of previous rows needed.

filtered_stream = (
    parsed_stream
    .filter(F.col("event_type") == "purchase")
    .withColumn("is_high_value", F.col("amount") > 500)
    .select("user_id", "event_type", "amount", "is_high_value", "event_time")
)


# ==============================================================================
# Stateful Aggregations
# ==============================================================================
# INTERVIEW Q: "What is a stateful operation in streaming? Give an example."
#
# Stateful = operation that requires memory of past records.
# Examples: running totals, counts, joins with a lookup table, sessionization.
#
# Spark stores state in an in-memory state store (backed by checkpoint on DBFS/S3).

# Running count per event_type
agg_stream = (
    parsed_stream
    .groupBy("event_type")
    .agg(
        F.count("*").alias("event_count"),
        F.sum("amount").alias("total_amount"),
        F.approx_count_distinct("user_id").alias("unique_users"),
    )
)


# ==============================================================================
# Watermarking (Handling Late Data)
# ==============================================================================
# INTERVIEW Q: "What is watermarking in Spark Streaming? Why is it important?"
#
# Problem: Network delays mean events can arrive LATE (out of order).
#          Without watermarking, Spark must keep all state forever (OOM risk).
#
# Watermark = the maximum amount of lateness Spark will tolerate.
#   "I'll wait 10 minutes for late records. After that, ignore them."
#
# event_time watermark = max(seen event_time) - threshold
# Any record with event_time < watermark is DROPPED.
#
# Side effect: Spark can safely clean up state older than the watermark.

windowed_stream = (
    parsed_stream
    .withWatermark("event_time", "10 minutes")          # tolerate 10-min late data
    .groupBy(
        F.window("event_time", "5 minutes"),             # 5-minute tumbling window
        "event_type"
    )
    .agg(
        F.sum("amount").alias("window_total"),
        F.count("*").alias("window_count"),
    )
)

# INTERVIEW Q: "Tumbling vs sliding vs session windows?"
#
# Tumbling window: fixed size, no overlap. [0-5min] [5-10min] [10-15min]
# Sliding window:  fixed size, overlap. [0-5min] [2-7min] [4-9min] (step=2min)
# Session window:  dynamic size based on inactivity gap. Closes after N minutes of silence.

# Sliding window example (5-min window, slides every 2 min):
sliding_stream = (
    parsed_stream
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        F.window("event_time", "5 minutes", "2 minutes"),  # windowDuration, slideDuration
        "event_type"
    )
    .count()
)


# ==============================================================================
# Writing Output — Sink Types
# ==============================================================================
# INTERVIEW Q: "What sinks (output destinations) does Spark Structured Streaming support?"
#
# console  → print to driver (dev/debugging only)
# memory   → in-memory table (dev/testing)
# file     → S3/DBFS (Parquet, Delta, JSON, CSV)
# kafka    → back to another Kafka topic
# delta    → Delta Lake table (best for production on Databricks)
# foreach  → custom sink (write to any DB/API)

# Write to console (debug)
query_console = (
    filtered_stream
    .writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .trigger(processingTime="10 seconds")
    .start()
)

# Write to Delta Lake (production pattern on Databricks)
query_delta = (
    windowed_stream
    .writeStream
    .outputMode("update")
    .format("delta")
    .option("checkpointLocation", "/FileStore/checkpoints/windowed_events")
    .trigger(processingTime="1 minute")
    .toTable("streaming_events_agg")   # write to Delta table in catalog
)

# Write back to Kafka
query_kafka = (
    parsed_stream
    .filter(F.col("event_type") == "purchase")
    .select(
        F.col("user_id").cast("string").alias("key"),
        F.to_json(F.struct("*")).alias("value")      # serialize back to JSON
    )
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("topic", "high_value_purchases")
    .option("checkpointLocation", "/FileStore/checkpoints/purchases")
    .start()
)


# ==============================================================================
# Checkpointing
# ==============================================================================
# INTERVIEW Q: "What is checkpointing in Spark Streaming and why is it critical?"
#
# Checkpoint = periodically saves the stream state and metadata (offsets, state store)
#              to reliable storage (DBFS/S3/ADLS).
#
# If the query crashes, Spark restarts from the last checkpoint:
#   - Knows exactly which Kafka offsets were processed
#   - Restores stateful aggregation state
#   - No data loss, no duplicates (exactly-once with Kafka + Delta Lake)
#
# ⚠️ INTERVIEW TRAP: Without checkpointing, a restart reprocesses everything from
#                    startingOffsets — duplicates or data loss.
#
# Checkpoint dir must be unique per streaming query.


# ==============================================================================
# Stream-Static Joins
# ==============================================================================
# INTERVIEW Q: "Can you join a stream with a static DataFrame?"
#
# Yes! Join a streaming DF with a batch DF (e.g., enrichment lookup table).
# The static DF is loaded once and reused each micro-batch.

user_dim = spark.read.table("dim_users")   # static dimension table

enriched_stream = (
    parsed_stream
    .join(user_dim, on="user_id", how="left")   # static join — user_dim doesn't stream
    .select("user_id", "event_type", "amount", "user_dim.country", "event_time")
)


# ==============================================================================
# Monitoring & Troubleshooting
# ==============================================================================
# INTERVIEW Q: "How do you monitor a Spark Structured Streaming query?"

# query.status       → current status (is it running? what trigger?)
# query.lastProgress → metrics from last micro-batch (rows/sec, duration, lag)
# query.recentProgress → last N progress reports

# Key metrics to monitor:
#   inputRowsPerSecond  → throughput from source
#   processedRowsPerSecond → throughput processed
#   durationMs.triggerExecution → micro-batch latency
#   sources[].endOffset → latest offset seen from Kafka
#   sources[].startOffset → offset at start of micro-batch
#   (endOffset - consumer offset) = consumer lag

# print(query_delta.lastProgress)  # uncomment when query is running


# ==============================================================================
# Interview Questions Summary
# ==============================================================================

print("""
Top Interview Q&A — Spark Structured Streaming:

Q: What is the difference between Append and Update output modes?
A: Append: only new rows are written. No rows are updated or deleted in the sink.
   Use for non-aggregated streams or append-only sinks (S3, Kafka).
   Update: only rows that changed are written. Good for aggregations (count, sum).
   The sink must support updates (Delta Lake, Cassandra, JDBC).

Q: How do you handle late-arriving data?
A: withWatermark("event_time", "10 minutes") — Spark waits 10 minutes for late records.
   Records arriving after the watermark are dropped. This also bounds state store growth.

Q: What is trigger Once / AvailableNow?
A: trigger(once=True) — process all available data, then stop. Converts streaming to batch.
   trigger(availableNow=True) — same but more efficient (respects source rate limits).
   Useful for cost optimization: run on a schedule instead of continuously.

Q: How do you achieve exactly-once semantics with Kafka + Spark + Delta?
A: 1. Kafka source: Spark tracks offsets in checkpoint. Won't reprocess without restart.
   2. Delta Lake sink: uses idempotent writes + ACID transactions.
   3. Together: exactly-once end-to-end (Spark reads offset X-Y, writes to Delta atomically).

Q: What causes a streaming query to fail silently?
A: Schema mismatch (JSON field missing), malformed records (from_json returns nulls),
   Kafka consumer lag growing unchecked, state store disk full, driver OOM on large state.
""")
