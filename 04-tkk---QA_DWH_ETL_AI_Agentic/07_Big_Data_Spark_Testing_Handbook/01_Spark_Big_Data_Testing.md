# 07 — Big Data & Spark Testing Handbook

## QA focus

Understand enough distributed processing to validate correctness, partition behavior, skew, shuffle impact, schema evolution, retries and recovery.

## Risks

Non-deterministic ordering, duplicate output after retry, missing partition, skewed hot key, accidental full scan, incorrect partition filter, schema evolution loss, checkpoint inconsistency and SLA breach under realistic data distribution.

## Test strategy

Validate results against a trusted small oracle, then execute scale tests with representative cardinality/skew. Check partition inventory, key/aggregate reconciliation, retry idempotency and P95 partition/runtime—not only average job duration.

## Interview probe

A job is right for a sample but fails at month end. Inspect volume, key skew, shuffle, partition count, file size, join cardinality, late data and resource/retry behavior before blaming code.
