# 03 — ETL and ELT Testing

## QA focus

Test ingestion, transformations, orchestration, retries, backfills, idempotency, lineage and failure recovery—not how to build the pipeline.

## Test scenarios

- Full load versus incremental load; inserts, updates, deletes and late arrivals.
- Restart after a partial write; retry after a transient dependency failure.
- Schema change, malformed input, empty input, duplicate delivery and replay.
- Reconciliation at row, key, attribute and aggregate levels.

## Quality gates

Define thresholds for source availability, reconciliation variance, reject rate, duplicate rate, SLA completion and unresolved severity-one defects.

## Practice

Write test cases for a daily orders pipeline that must handle a rerun without double-counting revenue. Include the oracle and evidence for each case.
