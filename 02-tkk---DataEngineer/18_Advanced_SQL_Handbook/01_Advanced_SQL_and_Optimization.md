# 18 — Advanced SQL Handbook (Warehouse-grade)

> SQL is the DE lingua franca. Interviewers hand you a schema and say *"write the query."*
> This handbook is **pure SQL** (not PySpark) — deep window functions, recursive CTEs,
> gaps-and-islands, pivots, query plans, and optimization. Runs on Snowflake / BigQuery /
> Redshift / Databricks SQL / Postgres with minor dialect tweaks.

---

## 🎯 How SQL Rounds Are Graded
1. **Correctness** — right answer, edge cases (NULLs, ties, duplicates).
2. **Clarity** — CTEs over nested subqueries; readable, named steps.
3. **Performance** — you can read a plan and avoid needless scans/shuffles.
4. **Communication** — you narrate the approach before typing.

---

## 🪟 SECTION 1: Window Functions (the backbone)

```sql
SELECT
  user_id,
  order_date,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date)      AS seq,
  RANK()       OVER (PARTITION BY user_id ORDER BY amount DESC)     AS amt_rank,
  DENSE_RANK() OVER (PARTITION BY user_id ORDER BY amount DESC)     AS amt_drank,
  SUM(amount)  OVER (PARTITION BY user_id ORDER BY order_date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
  AVG(amount)  OVER (PARTITION BY user_id ORDER BY order_date
                     ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)         AS ma_7,
  LAG(amount)  OVER (PARTITION BY user_id ORDER BY order_date)         AS prev_amt,
  LEAD(amount) OVER (PARTITION BY user_id ORDER BY order_date)         AS next_amt,
  amount - LAG(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS delta
FROM orders;
```

**Must know cold:**
- `ROW_NUMBER` (no ties) vs `RANK` (gaps after ties) vs `DENSE_RANK` (no gaps).
- **Frames:** `ROWS` (physical rows) vs `RANGE` (logical value range) — a classic gotcha
  with duplicate order keys. Default frame is `RANGE UNBOUNDED PRECEDING → CURRENT ROW`.
- `NTILE(n)` for buckets/quartiles; `FIRST_VALUE`/`LAST_VALUE`/`NTH_VALUE`.
- `PERCENT_RANK`, `CUME_DIST` for distribution questions.

**Top-N per group (canonical):**
```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) rn
  FROM employees
)
SELECT * FROM ranked WHERE rn <= 3;   -- top 3 earners per department
```

---

## 🔁 SECTION 2: CTEs & Recursive CTEs

**Recursive: org hierarchy / bill-of-materials / date spine.**
```sql
WITH RECURSIVE org AS (
  SELECT employee_id, manager_id, 1 AS lvl
  FROM employees WHERE manager_id IS NULL          -- anchor
  UNION ALL
  SELECT e.employee_id, e.manager_id, o.lvl + 1    -- recursive step
  FROM employees e JOIN org o ON e.manager_id = o.employee_id
)
SELECT * FROM org;                                  -- every employee with depth
```

**Generate a date spine (fill gaps in time series):**
```sql
WITH RECURSIVE d AS (
  SELECT DATE '2024-01-01' AS dt
  UNION ALL SELECT dt + INTERVAL '1 day' FROM d WHERE dt < DATE '2024-12-31'
)
SELECT d.dt, COALESCE(s.revenue, 0) AS revenue
FROM d LEFT JOIN sales s ON s.dt = d.dt;
```
> BigQuery: use `GENERATE_DATE_ARRAY` + `UNNEST`. Snowflake: `GENERATOR`/`SEQ`.

---

## 🏝️ SECTION 3: Gaps-and-Islands (the elite pattern)

**Consecutive login days ≥ 3** — the "row_number difference" trick:
```sql
WITH base AS (
  SELECT DISTINCT user_id, login_date FROM logins
),
grp AS (
  SELECT user_id, login_date,
         login_date - (ROW_NUMBER() OVER (PARTITION BY user_id
                                          ORDER BY login_date))::int AS island
  FROM base
)
SELECT user_id, MIN(login_date) AS streak_start,
       COUNT(*) AS streak_len
FROM grp
GROUP BY user_id, island
HAVING COUNT(*) >= 3;
```
**Why it works:** for consecutive dates, `date - row_number` is constant → groups an
"island". Sessionization (30-min gap) is the same idea with `LAG` + a new-session flag +
running `SUM`.

**Sessionization:**
```sql
WITH e AS (
  SELECT user_id, event_ts,
         CASE WHEN event_ts - LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts)
                   > INTERVAL '30 minutes'
              OR LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) IS NULL
              THEN 1 ELSE 0 END AS new_session
  FROM events
)
SELECT user_id, event_ts,
       SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_ts) AS session_id
FROM e;
```

---

## 🔀 SECTION 4: Joins, Anti-Joins, Semi-Joins

- `INNER` / `LEFT` / `FULL` — know NULL behavior of each.
- **Anti-join** (rows with no match): `LEFT JOIN ... WHERE r.key IS NULL` or `NOT EXISTS`.
- **Semi-join** (exists match, no duplication): `WHERE EXISTS (...)` — *prefer over
  `IN (subquery)`* because `NOT IN` breaks on NULLs.
- **Self-join** for pairs/adjacency; **cross join** for calendars/combinations.

**NULL trap:** `WHERE col NOT IN (SELECT x ...)` returns **zero rows** if any x is NULL.
Use `NOT EXISTS`.

---

## 🔄 SECTION 5: Pivot / Unpivot & Conditional Aggregation

```sql
-- Pivot without PIVOT syntax (portable): monthly revenue columns
SELECT
  product_id,
  SUM(CASE WHEN month = 1 THEN revenue END) AS jan,
  SUM(CASE WHEN month = 2 THEN revenue END) AS feb,
  SUM(CASE WHEN month = 3 THEN revenue END) AS mar
FROM sales GROUP BY product_id;

-- Unpivot via UNION ALL or CROSS JOIN UNNEST (dialect-specific)
```

**Median (no MEDIAN in every dialect):**
```sql
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median_salary
FROM employees;                              -- Postgres/Snowflake/Redshift
-- Fallback with window: pick middle row(s) via ROW_NUMBER + COUNT() OVER ()
```

---

## 🧮 SECTION 6: Grouping Extensions

```sql
SELECT region, product, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());   -- multi-level totals
-- ROLLUP(region, product)  → hierarchical subtotals + grand total
-- CUBE(region, product)    → all combinations
SELECT ..., GROUPING(region) AS is_region_total FROM ...;    -- flag rollup rows
```

---

## ⚙️ SECTION 7: Query Optimization & Execution Plans

**Read the plan** (`EXPLAIN` / `EXPLAIN ANALYZE`): look for full scans, the join order,
join algorithm (hash vs nested-loop vs merge), and estimated vs actual rows (bad estimates
= stale stats).

Senior habits:
1. **Filter early, project only needed columns** (columnar stores skip unused columns).
2. **Predicate pushdown / partition pruning** — filter on the partition column with a
   literal, not a function wrapping the column (`WHERE dt = '2024-01-01'`, not
   `WHERE CAST(dt AS STRING) LIKE ...`).
3. **Prefer `EXISTS`/`JOIN` over correlated subqueries** that run per-row.
4. **Avoid `SELECT *`**, avoid `DISTINCT` as a dedupe crutch (fix the join fan-out).
5. **Window function** instead of a self-join for "compare to previous/rank".
6. **`UNION ALL`** (no dedupe) over `UNION` when you know rows are distinct.
7. **Watch data skew** on join/group keys → salt or pre-aggregate.
8. **Keep statistics fresh** (`ANALYZE`) so the optimizer picks the right plan.

**Indexing (OLTP/Postgres) vs warehouses:**
- OLTP: B-tree on selective filter/join columns; composite index column order matters
  (leftmost prefix). Covering indexes avoid table lookups.
- Warehouses (Snowflake/BigQuery/Redshift): **no traditional indexes** — you tune with
  partitioning, clustering/sort keys, distribution keys, and pruning (see Handbook 19).

---

## 🧠 SECTION 8: Classic Hard Problems (rehearse these)

1. **Nth highest salary** (with ties) → `DENSE_RANK`.
2. **Running / cumulative total & moving average** → window frame.
3. **Month-over-month / YoY growth** → `LAG` with date partition.
4. **Consecutive events / longest streak** → gaps-and-islands.
5. **Sessionization (30-min inactivity)** → `LAG` + flag + running `SUM`.
6. **Median / percentiles per group** → `PERCENTILE_CONT`.
7. **Top-N per group** → `ROW_NUMBER` filter.
8. **First/last event per user** → `ROW_NUMBER` or `QUALIFY` (Snowflake/BigQuery).
9. **Pivot sparse categories** → conditional aggregation.
10. **Find gaps in a sequence / missing dates** → date spine LEFT JOIN.
11. **Deduplicate keeping latest** → `ROW_NUMBER` by recency, keep `rn = 1`.
12. **Market-share / % of total** → `SUM() OVER (PARTITION BY ...)` as denominator.

**`QUALIFY` (Snowflake/BigQuery/Databricks) — filter on a window without a subquery:**
```sql
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_ts DESC) = 1;  -- latest order
```

---

## ❓ SECTION 9: Rapid-Fire Q&A

**Q: `WHERE` vs `HAVING`?** WHERE filters rows before aggregation; HAVING filters groups
after. WHERE can't reference aggregates.

**Q: `RANK` vs `DENSE_RANK` vs `ROW_NUMBER`?** Ties get same rank in RANK/DENSE_RANK;
RANK leaves gaps, DENSE_RANK doesn't; ROW_NUMBER breaks ties arbitrarily (unique).

**Q: Why is `NOT IN` dangerous?** A NULL in the subquery makes the whole predicate
UNKNOWN → zero rows. Use `NOT EXISTS`.

**Q: `ROWS` vs `RANGE` frame?** ROWS counts physical rows; RANGE groups peers with equal
ORDER BY values — different running totals when duplicates exist.

**Q: How to dedupe?** `ROW_NUMBER()` partitioned by the natural key, ordered by recency,
keep `rn = 1`. Cleaner and more controllable than `DISTINCT`.

**Q: Execution order of a SELECT?** FROM/JOIN → WHERE → GROUP BY → HAVING → window
functions → SELECT → QUALIFY → ORDER BY → LIMIT. (Explains why aliases aren't usable in
WHERE.)

**Q: Correlated subquery cost?** Runs once per outer row → often O(n²); rewrite as a JOIN
or window function.

---

## ✅ Mastery Checklist
- [ ] Any window question in < 5 min, with the correct frame
- [ ] Recursive CTE for hierarchy and date spine from memory
- [ ] Gaps-and-islands + sessionization patterns internalized
- [ ] Read an EXPLAIN plan; identify scan/join/skew issues
- [ ] Know warehouse tuning (partition/cluster/dist) vs OLTP indexing
- [ ] Use `QUALIFY`, `PERCENTILE_CONT`, `GROUPING SETS` fluently

---

## 🧪 Hands-On Practice (runnable)

Every pattern below is executed against seed data and validated with assertions:

```bash
pip install -r ../requirements_practice.txt      # duckdb
python3 02_Practice_Advanced_SQL.py
```
Covers: window functions + frames, QUALIFY top-N, recursive date spine, gaps-and-islands
streaks, sessionization, dedupe-keep-latest, and per-group medians.
