# Test Design Techniques for Data and AI QA

## Equivalence, boundary and decision-table testing

Partition inputs by behavior, then test the edges. For an `amount` rule of `0 <= amount <= 1,000,000`, test `-0.01`, `0`, `0.01`, `999,999.99`, `1,000,000`, `1,000,000.01`, null and non-numeric text. Do not sample arbitrary valid values only.

## State-transition testing

Pipelines and agents have state. Test legal and illegal transitions:

```text
RECEIVED → VALIDATED → LOADED → PUBLISHED
                   ↘ REJECTED
LOADED → FAILED → RETRIED → LOADED       (must not duplicate output)
```

## Pairwise and combinatorial testing

Use pairwise coverage when dimensions multiply: input source × load type × schema version × region × role. Reserve exhaustive coverage for critical, small state spaces.

## Exploratory testing charter

“Explore incremental rerun behavior when a source sends duplicate records and a dimension arrives late. Focus on source-to-target keys, revenue, rejects, retries and published dashboard totals.” Capture observations, data versions and trace IDs—not just pass/fail.

## Defect report quality

A defect is reproducible evidence: environment/build/data version, exact input, steps, expected oracle, actual result, impact, trace/query/log evidence, severity and regression scope.
