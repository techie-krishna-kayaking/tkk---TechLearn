# 19 — Lakehouse & Table Formats Handbook

> **The hottest DE interview topic of 2024–25.** "Delta vs Iceberg vs Hudi?" now shows up
> in nearly every senior loop at Databricks, Netflix, Apple, Uber, LinkedIn, Adobe, and
> the Indian product ecosystem. Table formats are what turn a cheap object store into a
> real warehouse. Target: 80–120 LPA.

---

## 🎯 SECTION 1: Why the Lakehouse Exists

| Era | Problem |
|---|---|
| **Data Warehouse** (Redshift, Teradata) | Fast SQL + ACID, but expensive, proprietary, poor for ML/unstructured |
| **Data Lake** (S3 + Parquet) | Cheap, open, scalable — but **no ACID, no schema enforcement, no updates/deletes, no time travel** |
| **Lakehouse** (Delta/Iceberg/Hudi on S3) | ACID + schema + updates + time travel **on cheap object storage**, one copy for BI *and* ML |

**Interview line:** *"A lakehouse adds a transactional metadata layer over open columnar
files, so I get warehouse guarantees (ACID, schema evolution, time travel) at data-lake
cost and openness — no lock-in, and BI and ML read the same tables."*

---

## 🧱 SECTION 2: The Foundation — Columnar Files

- **Parquet / ORC**: columnar, compressed, with **min/max stats per row group** →
  predicate pushdown skips blocks. This is what all three table formats sit on top of.
- **Row group / stripe**: the unit of pushdown; too-small files kill this (small-file
  problem). Columnar + stats = why you never `SELECT *` on wide tables.
- Table formats add a **transaction log / manifest** that tracks *which* files make up
  the current table version.

---

## 🔺 SECTION 3: The Big Three

### Delta Lake (Databricks)
- Transaction log = **`_delta_log/`** (ordered JSON commits + Parquet checkpoints).
- Strengths: simplest, best Spark/Databricks integration, `MERGE`, `OPTIMIZE` + `ZORDER`,
  **liquid clustering**, Photon, Unity Catalog governance.
- Protocol features: deletion vectors (merge-on-read deletes), column mapping, CDF.

### Apache Iceberg (Netflix → open, now everywhere)
- Metadata tree: **snapshot → manifest list → manifest files → data files.**
- Strengths: true **hidden partitioning** + **partition evolution** (change partition
  scheme without rewriting data or rewriting queries), **schema evolution by field ID**
  (safe rename/reorder), engine-agnostic (Spark, Flink, Trino, Snowflake, BigQuery,
  Dremio). The current industry momentum leader for open lakehouses.

### Apache Hudi (Uber)
- Built for **fast upserts + incremental streams / CDC**.
- Two table types:
  - **Copy-on-Write (CoW)**: rewrite files on write → fast reads, slower writes.
  - **Merge-on-Read (MoR)**: write delta logs, merge at read → fast writes, slower reads;
    compaction merges logs into base files.
- Strengths: record-level index, incremental pulls, streaming ingestion.

### One-line comparison
| Need | Best fit |
|---|---|
| Databricks-centric, simplest ops | **Delta** |
| Open, multi-engine, partition/schema evolution | **Iceberg** |
| Streaming CDC upserts, incremental | **Hudi** |

---

## ⚛️ SECTION 4: How ACID Works on Object Storage (know this!)

Object stores have no locks. Table formats get atomicity via **optimistic concurrency +
an atomic metadata pointer swap**:
1. Writer reads the current snapshot/version.
2. Writes new data files (immutable).
3. Attempts to **commit** a new metadata version; if another writer committed first, it
   **retries** (conflict detection on overlapping files/partitions).
4. Readers always see a consistent snapshot (snapshot isolation) — never partial files.

**Interview line:** *"Data files are immutable; a commit is an atomic swap of the metadata
pointer with optimistic concurrency and conflict checks. That's how you get ACID without
locking object storage."*

---

## 🕰️ SECTION 5: Time Travel & CDC

```sql
-- Delta
SELECT * FROM sales VERSION AS OF 42;
SELECT * FROM sales TIMESTAMP AS OF '2024-06-01T00:00:00';
RESTORE TABLE sales TO VERSION AS OF 42;         -- recover from a bad load

-- Iceberg
SELECT * FROM sales FOR SYSTEM_VERSION AS OF 3821550127947089009;
SELECT * FROM sales FOR SYSTEM_TIME AS OF '2024-06-01 00:00:00';
```
- **Change Data Feed / incremental reads**: Delta CDF, Iceberg incremental scans, Hudi
  incremental queries → feed only *changed* rows to downstream (dbt incremental, streaming).
- **Use cases:** audit, reproduce a model's training set, rollback, debugging.

---

## 🛠️ SECTION 6: Table Maintenance (the "ops" senior signal)

| Problem | Fix |
|---|---|
| **Small files** (streaming/many writers) | Compaction: `OPTIMIZE` (Delta), `rewrite_data_files` (Iceberg), Hudi compaction/clustering |
| **Slow selective reads** | Data skipping via `ZORDER`/liquid clustering (Delta), sort order (Iceberg) |
| **Metadata/log bloat** | Checkpoints; expire old snapshots |
| **Storage growth / GDPR delete** | `VACUUM` (Delta) / `expire_snapshots` + `remove_orphan_files` (Iceberg) — but respect the time-travel retention window! |
| **Skewed/bad partitioning** | Iceberg **partition evolution**; Delta rewrite/liquid clustering |

```sql
OPTIMIZE sales ZORDER BY (customer_id, event_date);   -- Delta: co-locate for skipping
VACUUM sales RETAIN 168 HOURS;                         -- purge files older than 7 days
```
**Gotcha to mention:** `VACUUM`/`expire_snapshots` **breaks time travel** beyond the
retention window — never set retention to 0 in prod; it can corrupt concurrent readers.

---

## 🗂️ SECTION 7: Partitioning Done Right

- Partition on a **low-to-medium-cardinality column you filter by** (usually date). Never
  partition on a high-cardinality key (user_id) → millions of tiny files.
- **Iceberg hidden partitioning**: define `days(event_ts)` once; queries filtering on
  `event_ts` prune automatically — no need for a separate partition column or special
  WHERE syntax. **Partition evolution** lets you change the scheme later without rewrites.
- **Delta liquid clustering / Z-order**: alternative to rigid Hive-style partitioning;
  adapts to data and query patterns, avoids the small-file/over-partition trap.

---

## 📚 SECTION 8: Catalogs & the Metadata Layer

A table format needs a **catalog** to track table → current metadata pointer:
- **Unity Catalog** (Databricks), **AWS Glue Data Catalog**, **Hive Metastore**,
  **Iceberg REST catalog / Nessie / Polaris**, **Tabular**.
- Catalog responsibilities: namespace, current snapshot pointer, access control, lineage.
- **Nessie** adds git-like **branches/tags** for data (isolate a backfill on a branch,
  then merge) — a strong "modern DataOps" talking point.

---

## 🏗️ SECTION 9: Medallion Architecture (lakehouse layering)

```
Bronze (raw, append-only, as-ingested)
   → Silver (cleaned, deduplicated, conformed, typed)
      → Gold (business marts, aggregates, star schemas for BI/ML)
```
Maps 1:1 to dbt staging → intermediate → marts and to Handbook 17's modeling layers.
Each layer is a set of Delta/Iceberg tables with tests and expectations (Handbook 20).

---

## ❓ SECTION 10: Rapid-Fire Q&A

**Q: Why not just Parquet on S3?** No ACID, no atomic multi-file commits, no updates/
deletes, no schema enforcement, no time travel, unsafe concurrent writes. Table formats
add exactly those.

**Q: Delta vs Iceberg — pick one?** Delta if you're Databricks-centric and want simplest
ops; Iceberg if you need open multi-engine access with partition/schema evolution.

**Q: CoW vs MoR (Hudi)?** CoW rewrites files on write (fast reads, slow writes); MoR logs
deltas and merges on read (fast writes, slower reads) + async compaction. Choose by
read-heavy vs write/CDC-heavy.

**Q: How does time travel work?** Immutable data files + versioned metadata snapshots; a
query pins a snapshot/version. Retention (VACUUM/expire) bounds how far back you can go.

**Q: How is a MERGE/upsert done on a lake?** Rewrite affected files (CoW) or write delete
vectors/delta logs (MoR/deletion vectors), then atomically commit a new snapshot.

**Q: Small-file problem?** Too many tiny files → slow metadata + poor pushdown; fix with
compaction/OPTIMIZE and by not over-partitioning.

**Q: How do you GDPR-delete a user from a lake?** `DELETE` (rewrites files or deletion
vectors) **then** expire old snapshots/VACUUM past retention so tombstoned data is
physically purged.

**Q: Schema evolution safety?** Iceberg tracks columns by **field ID**, so rename/reorder
is safe; add columns is safe in all three; dropping/incompatible type changes need care.

---

## ✅ Mastery Checklist
- [ ] Explain lakehouse value vs warehouse and raw lake in 2 sentences
- [ ] Compare Delta / Iceberg / Hudi and pick per scenario
- [ ] Explain ACID via optimistic concurrency + atomic metadata swap
- [ ] Time travel, CDC/incremental reads, and rollback from memory
- [ ] Diagnose + fix small files, skew, and metadata bloat
- [ ] Explain hidden/partition evolution and Z-order/liquid clustering
- [ ] Know the catalog's role (Unity/Glue/REST/Nessie)

---

## 🧪 Hands-On Practice (runnable)

Two companion files — one runs locally (no JVM), one is the real thing:

```bash
pip install -r ../requirements_practice.txt      # duckdb
python3 02_Practice_Lakehouse_Concepts.py        # MERGE upsert, time travel,
                                                 # schema evolution, GDPR+VACUUM (DuckDB)

# Real Delta Lake version (run on Databricks, or Spark + delta-spark + Java):
python3 03_Delta_Lake_Demo_databricks.py         # MERGE, VERSION AS OF, CDF, history
```
