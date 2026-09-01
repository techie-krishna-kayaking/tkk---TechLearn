# 02 — SQL and Data Validation

## QA focus

Validate schema, completeness, uniqueness, referential integrity, business rules, aggregates and source-to-target reconciliation.

## Core checks

`row count`, `primary-key uniqueness`, `null rate`, `domain/range`, `freshness`, `duplicate detection`, `cross-table integrity`, `aggregate/control totals`, and `record-level differences`.

## Failure modes

Join multiplication, accidental inner joins, type coercion, late-arriving dimensions, timezone shifts, decimal rounding, null handling and non-idempotent reloads.

## Practice

Use `../shared/test_data` to define SQL checks for the valid and invalid order files. State expected failures before executing them. Explain whether each issue should block release.

## Interview probe

A target has the same row count as its source but revenue is 3% higher. Describe your investigation order.
