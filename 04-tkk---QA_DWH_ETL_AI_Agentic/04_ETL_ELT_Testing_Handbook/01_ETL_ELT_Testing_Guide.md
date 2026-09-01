# 04 — ETL / ELT Testing Handbook

> Test the delivery of trusted data, not the mechanics of writing a pipeline. Senior QA owns the evidence that transformations, reruns, failures and recovery preserve business truth.

## 🎯 What must be tested

| Area | QA questions |
|---|---|
| Ingestion | Is every expected file/event received once, validated and traceable? |
| Transformation | Are mappings, joins, filters, derivations and defaults correct? |
| Incremental load | Do inserts, updates, deletes and late data behave correctly? |
| Restart/retry | Can a failure resume without loss or duplicate output? |
| Backfill | Is historical reload scoped, reconciled and safe for consumers? |
| Operations | Are SLA, alerts, lineage, rejects and audit records usable? |

## The idempotency test

Run the same logical input twice. The final target should match the approved expected state, not double in rows or amounts. Check at the target grain, not only job status.

## Failure scenarios that matter

Malformed file, empty file, partial file, late delivery, duplicate delivery, schema drift, source correction, warehouse timeout, partial write, retry, dependency outage and manual rerun.

## Senior interview answer

“I test full and incremental paths separately; reconcile source-to-target keys and aggregates; deliberately fail the pipeline at critical boundaries; validate the restart point and published state; and verify operational controls, not just data transformation.”
