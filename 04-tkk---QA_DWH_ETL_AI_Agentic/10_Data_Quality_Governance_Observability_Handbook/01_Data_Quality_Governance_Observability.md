# 10 — Data Quality, Governance & Observability Handbook

> A pipeline that finishes green but publishes false numbers is worse than one that fails loudly. QA owns the controls that make data trustworthy and incidents diagnosable.

## Six data-quality dimensions

1. **Accuracy** — matches approved reality/oracle.
2. **Completeness** — expected records and attributes are present.
3. **Consistency** — agrees across systems and definitions.
4. **Timeliness** — arrives within SLA.
5. **Validity** — meets type, format, domain and range rules.
6. **Uniqueness** — no unintended duplicate business entity/event.

## Five observability pillars

Freshness, volume, schema, distribution and lineage. Tests catch known rules; observability detects unknown or production-only anomalies. Both are required.

## Quality gates

Block when critical rules fail, source-to-target key coverage breaches threshold, reconciliation variance exceeds approved tolerance, data is stale, or evidence/lineage is insufficient for a decision.

## Interview line

“I shift quality left with contracts and CI checks, then keep production controls for freshness, volume, distribution and lineage because not every failure is predictable in a test case.”
