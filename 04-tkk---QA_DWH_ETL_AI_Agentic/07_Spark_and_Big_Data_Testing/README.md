# 07 — Spark and Big Data Testing

## QA focus

Validate distributed transformation correctness, partition behavior, data skew impact, shuffle failures, schema evolution and restart/retry outcomes.

## Risks to target

Non-deterministic ordering, incorrect partition pruning, skewed keys, duplicate output after retry, checkpoint inconsistency, data loss on executor failure and performance regression caused by shuffles.

## Practice

Design checks for a partitioned daily output: every expected partition exists, no unexpected partition exists, control totals reconcile, output is idempotent and the 95th-percentile partition runtime meets its SLA.

## Interview probe

A job is correct for a sample but times out in production. What data and runtime dimensions do you inspect before declaring a performance defect?
