"""
================================================================================
HANDBOOK 18 — RUNNABLE PRACTICE: Advanced SQL Patterns (self-checking)
================================================================================
Run:   python3 02_Practice_Advanced_SQL.py
Deps:  pip install duckdb

Each pattern is executed against seed data and validated with an assertion so
you can SEE the output AND trust it's correct. Patterns covered:
  1. Window functions (ROW_NUMBER/RANK/DENSE_RANK + running total + moving avg)
  2. Top-N per group (QUALIFY)
  3. Recursive CTE — date spine that fills gaps
  4. Gaps-and-islands — consecutive login streaks >= 3
  5. Sessionization — 30-minute inactivity windows
  6. Deduplicate keeping latest
  7. Median / percentiles per group
================================================================================
"""
import duckdb

con = duckdb.connect()


def show(title, sql):
    print(f"\n--- {title} ---")
    df = con.sql(sql).to_df()
    print(df.to_string(index=False))
    return df


# ---- Seed data --------------------------------------------------------------
con.execute("""
CREATE TABLE orders AS SELECT * FROM (VALUES
  ('U1', DATE '2024-01-01', 100.0),
  ('U1', DATE '2024-01-03', 300.0),
  ('U1', DATE '2024-01-04', 200.0),
  ('U2', DATE '2024-01-01', 500.0),
  ('U2', DATE '2024-01-02', 150.0)
) t(user_id, order_date, amount);
""")

# ============================================================================
# 1. Window functions: ranking + running total + 2-day moving average
# ============================================================================
show("Window functions per user", """
SELECT user_id, order_date, amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) AS seq,
  RANK()       OVER (PARTITION BY user_id ORDER BY amount DESC) AS amt_rank,
  SUM(amount)  OVER (PARTITION BY user_id ORDER BY order_date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
  AVG(amount)  OVER (PARTITION BY user_id ORDER BY order_date
                     ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS ma_2
FROM orders ORDER BY user_id, order_date
""")
u1_running = con.sql("""
  SELECT SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) rt
  FROM orders WHERE user_id='U1' ORDER BY order_date
""").fetchall()
assert [r[0] for r in u1_running] == [100.0, 400.0, 600.0]
print("[PASS] running total for U1 = 100, 400, 600")

# ============================================================================
# 2. Top-N per group with QUALIFY (latest order per user)
# ============================================================================
latest = show("Latest order per user (QUALIFY)", """
SELECT user_id, order_date, amount
FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) = 1
ORDER BY user_id
""")
assert set(latest["order_date"].astype(str)) == {"2024-01-04", "2024-01-02"}
print("[PASS] latest orders selected via QUALIFY")

# ============================================================================
# 3. Recursive CTE: date spine filling gaps (U1 has no order on 2024-01-02)
# ============================================================================
show("Date spine LEFT JOIN fills missing days with 0", """
WITH RECURSIVE d AS (
  SELECT DATE '2024-01-01' AS dt
  UNION ALL SELECT dt + INTERVAL 1 DAY FROM d WHERE dt < DATE '2024-01-04'
)
SELECT d.dt, COALESCE(SUM(o.amount), 0) AS revenue
FROM d LEFT JOIN orders o ON o.order_date = d.dt AND o.user_id='U1'
GROUP BY d.dt ORDER BY d.dt
""")
gapfill = con.sql("""
WITH RECURSIVE d AS (
  SELECT DATE '2024-01-01' AS dt
  UNION ALL SELECT dt + INTERVAL 1 DAY FROM d WHERE dt < DATE '2024-01-04')
SELECT COALESCE(SUM(o.amount),0) rev FROM d
LEFT JOIN orders o ON o.order_date=d.dt AND o.user_id='U1'
GROUP BY d.dt ORDER BY d.dt
""").fetchall()
assert [r[0] for r in gapfill] == [100.0, 0.0, 300.0, 200.0]
print("[PASS] gap day (2024-01-02) filled with 0")

# ============================================================================
# 4. Gaps-and-islands: users with 3+ consecutive login days
# ============================================================================
con.execute("""
CREATE TABLE logins AS SELECT * FROM (VALUES
  ('A', DATE '2024-01-01'),('A', DATE '2024-01-02'),('A', DATE '2024-01-03'),
  ('A', DATE '2024-01-05'),
  ('B', DATE '2024-01-01'),('B', DATE '2024-01-03')
) t(user_id, login_date);
""")
show("Consecutive login streaks", """
WITH base AS (SELECT DISTINCT user_id, login_date FROM logins),
grp AS (
  SELECT user_id, login_date,
         login_date - CAST(ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS INTEGER) AS island
  FROM base)
SELECT user_id, MIN(login_date) AS streak_start, COUNT(*) AS streak_len
FROM grp GROUP BY user_id, island HAVING COUNT(*) >= 3
""")
streak_users = con.sql("""
WITH base AS (SELECT DISTINCT user_id, login_date FROM logins),
grp AS (SELECT user_id, login_date,
        login_date - CAST(ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS INTEGER) AS island
        FROM base)
SELECT DISTINCT user_id FROM grp GROUP BY user_id, island HAVING COUNT(*)>=3
""").fetchall()
assert streak_users == [('A',)], streak_users
print("[PASS] only user A has a 3+ day streak")

# ============================================================================
# 5. Sessionization: new session after 30 min of inactivity
# ============================================================================
con.execute("""
CREATE TABLE events AS SELECT * FROM (VALUES
  ('U1', TIMESTAMP '2024-01-01 10:00:00'),
  ('U1', TIMESTAMP '2024-01-01 10:10:00'),   -- same session
  ('U1', TIMESTAMP '2024-01-01 11:00:00'),   -- +50 min -> new session
  ('U1', TIMESTAMP '2024-01-01 11:05:00')    -- same session
) t(user_id, event_ts);
""")
sess = show("Sessionization (30-min gap)", """
WITH e AS (
  SELECT user_id, event_ts,
    CASE WHEN event_ts - LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts)
              > INTERVAL 30 MINUTE
         OR LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) IS NULL
         THEN 1 ELSE 0 END AS new_session
  FROM events)
SELECT user_id, event_ts,
       SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_ts) AS session_id
FROM e ORDER BY event_ts
""")
assert list(sess["session_id"]) == [1, 1, 2, 2]
print("[PASS] 4 events grouped into 2 sessions")

# ============================================================================
# 6. Deduplicate keeping the latest row per key
# ============================================================================
con.execute("""
CREATE TABLE raw_cust AS SELECT * FROM (VALUES
  ('C1','old@x.com', TIMESTAMP '2024-01-01'),
  ('C1','new@x.com', TIMESTAMP '2024-02-01'),   -- keep this (latest)
  ('C2','a@x.com',   TIMESTAMP '2024-01-15')
) t(customer_id, email, updated_at);
""")
dedup = show("Dedupe keep latest", """
SELECT customer_id, email FROM raw_cust
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1
ORDER BY customer_id
""")
assert dict(zip(dedup.customer_id, dedup.email)) == {'C1':'new@x.com','C2':'a@x.com'}
print("[PASS] kept latest email per customer")

# ============================================================================
# 7. Median / percentiles per group
# ============================================================================
show("Median amount per user", """
SELECT user_id,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_amount
FROM orders GROUP BY user_id ORDER BY user_id
""")
med_u1 = con.sql("""
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) FROM orders WHERE user_id='U1'
""").fetchone()[0]
assert med_u1 == 200.0
print("[PASS] U1 median = 200")

print("\nAll Handbook 18 assertions passed. ✅")
