# Databricks notebook source
# ================================================================================
# HANDBOOK 19 — REAL DELTA LAKE DEMO (run on Databricks or Spark + Delta)
# ================================================================================
# This is the PRODUCTION version of 02_Practice_Lakehouse_Concepts.py using a
# REAL table format. It needs a JVM + Spark + Delta, so run it on Databricks
# (where `spark` is preconfigured) or locally via:
#
#   pip install pyspark delta-spark        # and a Java 11/17 runtime installed
#   # then run with the Delta packages configured (see get_spark() below)
#
# It demonstrates, on an actual Delta table:
#   1. MERGE upsert           2. Time travel (VERSION AS OF)
#   3. Schema evolution       4. DELETE + VACUUM (GDPR)
#   5. OPTIMIZE + ZORDER      6. Change Data Feed (CDF)
# ================================================================================

from pyspark.sql import SparkSession, functions as F

PATH = "/tmp/delta_orders"          # on Databricks use e.g. "/FileStore/tables/delta_orders"


def get_spark():
    """On Databricks: just use the preconfigured `spark`. Locally: configure Delta."""
    try:
        return spark  # noqa: F821 — provided by Databricks
    except NameError:
        from delta import configure_spark_with_delta_pip
        builder = (
            SparkSession.builder.appName("delta-demo")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        )
        return configure_spark_with_delta_pip(builder).getOrCreate()


def main():
    spark = get_spark()
    from delta.tables import DeltaTable

    # ------------------------------------------------------------------
    # VERSION 0: initial write
    # ------------------------------------------------------------------
    v0 = spark.createDataFrame(
        [("O1", "C1", "placed", 100.0),
         ("O2", "C2", "placed", 250.0),
         ("O3", "C3", "placed", 75.0)],
        "order_id string, customer_id string, status string, amount double",
    )
    (v0.write.format("delta").mode("overwrite")
       .option("delta.enableChangeDataFeed", "true").save(PATH))
    print("v0 written:")
    spark.read.format("delta").load(PATH).orderBy("order_id").show()

    # ------------------------------------------------------------------
    # 1. MERGE UPSERT (version 1)
    # ------------------------------------------------------------------
    changes = spark.createDataFrame(
        [("O2", "C2", "shipped", 250.0),
         ("O3", "C3", "cancelled", 0.0),
         ("O4", "C4", "placed", 500.0)],
        "order_id string, customer_id string, status string, amount double",
    )
    dt = DeltaTable.forPath(spark, PATH)
    (dt.alias("t").merge(changes.alias("s"), "t.order_id = s.order_id")
       .whenMatchedUpdate(set={"status": "s.status", "amount": "s.amount"})
       .whenNotMatchedInsertAll()
       .execute())
    print("v1 after MERGE upsert:")
    spark.read.format("delta").load(PATH).orderBy("order_id").show()

    # ------------------------------------------------------------------
    # 2. TIME TRAVEL — read an older version
    # ------------------------------------------------------------------
    print("Time travel: VERSION AS OF 0 (before the upsert):")
    spark.read.format("delta").option("versionAsOf", 0).load(PATH) \
        .orderBy("order_id").show()
    # RESTORE a bad load:  dt.restoreToVersion(0)

    # ------------------------------------------------------------------
    # 3. SCHEMA EVOLUTION — add a column via mergeSchema
    # ------------------------------------------------------------------
    evolved = (spark.read.format("delta").load(PATH)
               .withColumn("currency", F.lit("INR")))
    (evolved.write.format("delta").mode("overwrite")
        .option("mergeSchema", "true").save(PATH))
    print("v2 after schema evolution (added 'currency'):")
    spark.read.format("delta").load(PATH).orderBy("order_id").show()

    # ------------------------------------------------------------------
    # 4. GDPR DELETE + VACUUM (physically purge past retention)
    # ------------------------------------------------------------------
    dt = DeltaTable.forPath(spark, PATH)
    dt.delete(F.col("customer_id") == "C2")     # rewrites affected files
    print("v3 after GDPR delete of C2:")
    spark.read.format("delta").load(PATH).orderBy("order_id").show()
    # WARNING: VACUUM removes old files -> breaks time travel before retention.
    # spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    # dt.vacuum(0)   # 0 hours only for demo; NEVER do this in prod

    # ------------------------------------------------------------------
    # 5. OPTIMIZE + ZORDER (compaction + data skipping) — Databricks SQL
    # ------------------------------------------------------------------
    # spark.sql(f"OPTIMIZE delta.`{PATH}` ZORDER BY (customer_id)")

    # ------------------------------------------------------------------
    # 6. CHANGE DATA FEED — read only what changed between versions
    # ------------------------------------------------------------------
    print("Change Data Feed (row-level changes from v0 -> latest):")
    (spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", 0)
        .load(PATH)
        .select("order_id", "status", "_change_type", "_commit_version")
        .orderBy("_commit_version", "order_id").show(50, truncate=False))

    print("History (each commit is an atomic metadata version):")
    dt.history().select("version", "operation").show(truncate=False)


if __name__ == "__main__":
    main()
