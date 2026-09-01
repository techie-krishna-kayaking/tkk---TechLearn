# ETL / ELT Testing — Interview Questions & Model Answers

## 1. Full load versus incremental load: how does testing differ?

A full load proves complete baseline population. Incremental QA proves change detection, watermarks/cut-offs, inserts, updates, deletes, late records, duplicate delivery and rerun safety. Test both; a passing full load does not prove CDC correctness.

## 2. How do you prove idempotency?

Process the same logical batch twice and compare final target state with the approved one-run state at business-key and aggregate levels. Check audit records too: an idempotent target with misleading duplicate audit/publish events may still be operationally unsafe.

## 3. What do you test after a partial pipeline failure?

The durable checkpoint/transaction boundary, rollback/cleanup, retry scope, duplicate protection, data publication state, alerting and final reconciliation. Job success after retry is insufficient if consumers could see partial or stale data.

## 4. How do you test a backfill?

Confirm scope/cut-off, isolate it from normal incrementals, protect consumers from partial history, reconcile every affected business slice, validate downstream refresh/caches and retain audit/release evidence. Test failure and restart because backfills are high-volume/high-impact.

## 5. What are common ETL defects?

Wrong filter, type/rounding change, null default, join multiplication, schema drift, watermark error, time-zone shift, duplicate delivery, delete handling, wrong SCD logic, partial write and non-idempotent retry.

## 6. How do you test source-file ingestion?

Valid/empty/malformed/duplicate/late files; header/order/type/schema changes; encoding; checksum/completeness; filename/date convention; quarantine/reject behavior; traceability; and safe rerun. Verify source receipt does not equal successful publish.
