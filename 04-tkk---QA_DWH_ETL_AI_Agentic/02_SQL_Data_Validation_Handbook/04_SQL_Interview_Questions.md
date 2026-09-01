# SQL Data QA — Interview Questions & Model Answers

## 1. How do you validate a transformation without reading all records manually?

Use independent, layered controls: schema/profile checks, key coverage, duplicate detection, business-rule queries, control totals by business slice and targeted record-level comparison. Select samples intelligently for edge cases, but never substitute a sample for a critical reconciliation.

## 2. Why can a join create a data defect without throwing an error?

The join can multiply rows when either side is not unique at the assumed grain, omit rows through inner-join semantics or map a fact to the wrong dimension version. Test input uniqueness, expected cardinality, output grain and aggregate deltas before trusting the result.

## 3. How do you test a slowly changing dimension?

Test first load, attribute change, no-change replay, late correction, effective-date boundaries, current-row flag, non-overlapping date ranges and facts linked to the correct historical version. Reconcile history and business totals, not only surrogate keys.

## 4. How do you handle data tolerance?

Tolerance is a business decision documented before execution. Ledger money can require exact agreement; delayed/counted telemetry may permit an approved percentage or timing threshold. Record cut-off, calculation, approver and expiry so tolerance does not conceal regression.

## 5. A null rate increases. Is it a defect?

It is a signal. Compare to contract and baseline, identify field criticality and affected business flow, determine whether source/business behavior changed and inspect downstream defaults/filters. For a mandatory key it is likely blocking; for an optional attribute it may be a monitored anomaly.

## 6. What is data lineage used for in QA?

Impact analysis, tracing a wrong value to origin, verifying transformations and showing ownership. Good lineage shortens incident triage and makes test coverage/scope decisions evidence-based.

## 7. How do you test late-arriving data?

Define the allowed lateness and expected correction behavior. Inject late records across the boundary; validate target partition/history/aggregate revision, consumer visibility, audit metadata, rerun behavior and reconciliation after the late load.
