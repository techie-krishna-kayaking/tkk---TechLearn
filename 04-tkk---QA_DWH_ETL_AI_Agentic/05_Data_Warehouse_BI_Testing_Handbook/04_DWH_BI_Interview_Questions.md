# DWH & BI Testing — Interview Q&A

**How do you validate a dashboard?** Validate metric definition and grain first, then reconcile source/fact/semantic/visual totals by business slice; test filters, RLS, cache, drill-through and export.

**What can go wrong with SCD2?** Overlapping ranges, duplicate current rows, loss of history, wrong effective date and facts linked to a current rather than historical version.

**Why is a dashboard zero risky?** It can mean a real zero, filter exclusion, stale/failed refresh or hidden error. Test and design distinguishable states.

**How do you test row-level security?** Use role/tenant/region test accounts; prove both permitted and denied data paths including export/API/drill-through.

**What is fact grain?** The business meaning of one fact row. It determines valid joins and aggregations; validate it before asserting measures.
