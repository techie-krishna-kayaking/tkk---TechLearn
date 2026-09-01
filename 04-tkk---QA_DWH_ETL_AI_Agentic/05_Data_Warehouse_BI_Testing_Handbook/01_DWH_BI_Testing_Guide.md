# 05 — Data Warehouse & BI Testing Handbook

> Warehouse testing proves that modeled, transformed and visualized data retains the intended business meaning. A dashboard can be technically available and still be dangerously wrong.

## 🎯 Warehouse QA focus

- Fact grain and additive/semi-additive measures.
- Dimension keys, unknown members and slowly changing history.
- Conformed dimensions and consistent business definitions.
- Source → staging → fact/dimension → semantic layer → dashboard reconciliation.
- Filters, row-level security, caching, exports and scheduled refresh.

## SCD Type 2 test matrix

| Event | Expected quality result |
|---|---|
| first dimension row | one current record, valid start/end dates |
| tracked attribute change | old row expires; new current row begins |
| unchanged replay | no extra history row |
| late effective change | documented correction behavior; no overlapping ranges |
| fact lookup | fact links to correct historical dimension version |

## BI risks

Incorrect aggregation level, many-to-many relationship, hidden filter, stale cache, timezone default, semantic metric mismatch, drill-through loss and unauthorized row visibility.

## Interview line

“I validate the metric definition and grain before validating visual totals. Then I reconcile source, warehouse and semantic-layer totals by business slice and test the dashboard’s filters, security and refresh behavior.”
