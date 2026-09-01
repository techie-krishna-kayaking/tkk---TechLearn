# 04 — Data Warehouse and BI Testing

## QA focus

Validate dimensional models, SCD behavior, facts, measures, semantic definitions, dashboards, filters and row-level security.

## High-risk areas

Grain mismatch, slowly changing dimensions, surrogate-key lookup failures, conformed-dimension drift, incorrect measure aggregation, filter-context errors and dashboard cache staleness.

## Test scenarios

Test SCD type 1/2 history, orphan facts, drill-through totals, date-boundary behavior, role-based visibility, exports and reconciliation from source to dashboard.

## Interview probe

How would you prove that a dashboard total is correct when its source fact table contains billions of records?
