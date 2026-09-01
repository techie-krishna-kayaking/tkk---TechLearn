# 09 — Data Quality, Observability and Reconciliation

## QA focus

Build measurable controls that detect data incidents quickly: freshness, volume, distribution, schema, lineage, reconciliation and rule violations.

## Metrics

Freshness lag, completeness, uniqueness, validity, consistency, accuracy proxy, reconciliation variance, rejected-record rate, MTTD, MTTR and false-alert rate.

## Quality gate example

Block a release when a critical rule fails, source/target key coverage drops below 99.99%, reconciliation variance exceeds its approved tolerance, or quality evidence is stale.

## Practice

Draft an alert runbook that distinguishes a real source outage, delayed load, schema regression and expected business-seasonality volume shift.
