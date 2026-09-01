# 02 — SQL & Data Validation Handbook

> SQL is a QA engineer’s most important data-proving tool. The goal is not to memorize queries; it is to produce clear evidence that data is complete, correct, valid, unique, timely and consistent.

---

## 🎯 Section 1: The validation stack

```text
Schema → column profile → key integrity → business rules → aggregate controls → record-level reconciliation
```

### Essential checks

| Check | Defect caught | Typical oracle |
|---|---|---|
| schema/type | incompatible producer or mapping | approved contract |
| `NOT NULL` | missing mandatory values | requirement |
| uniqueness | duplicate business events | natural/business key |
| referential integrity | orphan facts | dimension key set |
| domain/range | invalid status/amount | accepted values / business limit |
| freshness | late/stale delivery | data SLA |
| reconciliation | lost/changed records | independent source/control total |

## 🧪 Section 2: SQL patterns QA should know

```sql
-- Duplicate business keys
SELECT order_id, COUNT(*) AS occurrences
FROM fct_orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Source keys missing from target
SELECT s.order_id
FROM source_orders s
LEFT JOIN fct_orders t ON t.order_id = s.order_id
WHERE t.order_id IS NULL;

-- Financial control total by business date
SELECT order_date, COUNT(*) rows, SUM(amount) amount
FROM fct_orders
GROUP BY order_date;
```

### Why equal row counts are not enough

The same count can hide duplicate/missing pairs, wrong joins, changed amounts, shifted dates, incorrect filters and status mappings. Reconcile at key, attribute and aggregate levels, sliced by date/region/product/status where business risk demands it.

---

## ❓ Rapid-fire Q&A

**Q: `COUNT(*)` is equal in source and target. What next?**  
**A:** Compare key sets, duplicate rates, important attributes and aggregate control totals by business slice. Validate filters and transformation semantics.

**Q: `EXCEPT` or a join for reconciliation?**  
**A:** `EXCEPT` is concise when schemas align. Anti-joins are clearer for key-level diagnostics and allow adding source/target attributes to explain a mismatch.

**Q: How do nulls affect joins?**  
**A:** Null is not equal to null in ordinary joins. Test null business keys explicitly and confirm the intended handling rather than assuming a join covers them.

## ✅ Mastery checklist

- [ ] Build a profile for volume, nulls, distinct values and ranges.
- [ ] Prove primary/foreign-key integrity.
- [ ] Reconcile source and target by key and money/metric.
- [ ] Test date/timezone, decimals, nulls and late arrivals.
- [ ] Produce query output that a business owner can audit.
