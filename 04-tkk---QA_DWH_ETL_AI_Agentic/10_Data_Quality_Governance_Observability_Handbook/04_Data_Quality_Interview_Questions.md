# Data Quality & Observability — Interview Q&A

**Tests versus observability?** Tests enforce known expectations; observability detects unexpected production anomalies in freshness, volume, schema, distribution and lineage. Use both.

**How do you respond to a wrong board metric?** Contain publishing, trace lineage, check data cut-off/rules/reconciliation layer by layer, correct/backfill, communicate impact and add test/monitor/contract.

**What is a data contract?** Producer-consumer agreement on schema, semantics, ownership, SLA and breaking-change policy; enforce it early to shift quality left.

**What are quality metrics?** Accuracy, completeness, consistency, timeliness, validity, uniqueness plus MTTD/MTTR, incident recurrence and gate reliability.

**How do you avoid alert fatigue?** Tier criticality, tune against baseline/seasonality, require actionable ownership/runbook and measure false-positive rate.
