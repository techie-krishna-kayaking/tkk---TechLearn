"""
================================================================================
HANDBOOK 19 — RUNNABLE PRACTICE: Lakehouse Table-Format Concepts (local)
================================================================================
Run:   python3 02_Practice_Lakehouse_Concepts.py
Deps:  pip install duckdb

Spark + Delta need a JVM, so this file DEMONSTRATES the table-format SEMANTICS
locally with DuckDB so you can run and verify them:
  1. MERGE upsert (the core of Delta/Iceberg/Hudi writes)
  2. Time travel  (query a table AS OF an older version/snapshot)
  3. Schema evolution (add a column without breaking old data)
  4. GDPR delete + "purge past retention" (why VACUUM breaks time travel)

For a REAL Delta Lake version (run on Databricks/Spark), see the companion
file:  03_Delta_Lake_Demo_databricks.py
================================================================================
"""
import duckdb

con = duckdb.connect()

# We simulate a versioned table by keeping every committed snapshot.
# (A real table format does this via an immutable metadata log; here we
#  materialize each version so time travel is easy to see and assert.)
snapshots = {}   # version -> table name


def commit(version, select_sql):
    """Materialize a new immutable snapshot (like an atomic metadata commit)."""
    name = f"orders_v{version}"
    con.execute(f"CREATE TABLE {name} AS {select_sql}")
    snapshots[version] = name
    print(f"  committed snapshot version {version} -> {name}")


def show(title, sql):
    print(f"\n--- {title} ---")
    print(con.sql(sql).to_df().to_string(index=False))


# ============================================================================
# VERSION 0: initial load (bronze -> silver)
# ============================================================================
print("=== 1. INITIAL LOAD (version 0) ===")
con.execute("""
CREATE TABLE staged_v0 AS SELECT * FROM (VALUES
  ('O1','C1','placed',   100.0),
  ('O2','C2','placed',   250.0),
  ('O3','C3','placed',    75.0)
) t(order_id, customer_id, status, amount);
""")
commit(0, "SELECT * FROM staged_v0")
show("orders @ v0", "SELECT * FROM orders_v0 ORDER BY order_id")


# ============================================================================
# 1. MERGE UPSERT — new + changed rows (the heart of a lakehouse write)
# ============================================================================
print("\n=== 2. MERGE UPSERT (version 1) ===")
# incoming CDC: O2 ships, O3 cancels, O4 is brand new
con.execute("""
CREATE TABLE changes AS SELECT * FROM (VALUES
  ('O2','C2','shipped',  250.0),
  ('O3','C3','cancelled',  0.0),
  ('O4','C4','placed',   500.0)
) t(order_id, customer_id, status, amount);
""")
con.execute("CREATE TABLE working AS SELECT * FROM orders_v0")
con.execute("""
MERGE INTO working t
USING changes s ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET status = s.status, amount = s.amount
WHEN NOT MATCHED THEN INSERT VALUES (s.order_id, s.customer_id, s.status, s.amount);
""")
commit(1, "SELECT * FROM working")
show("orders @ v1 (after upsert)", "SELECT * FROM orders_v1 ORDER BY order_id")

v1 = dict((r[0], r[2]) for r in con.sql("SELECT * FROM orders_v1").fetchall())
assert v1 == {"O1": "placed", "O2": "shipped", "O3": "cancelled", "O4": "placed"}
assert con.sql("SELECT COUNT(*) FROM orders_v1").fetchone()[0] == 4
print("[PASS] MERGE updated O2/O3 and inserted O4")


# ============================================================================
# 2. TIME TRAVEL — query the table AS OF an older version
# ============================================================================
print("\n=== 3. TIME TRAVEL (query AS OF older versions) ===")
def read_as_of(version):
    return con.sql(f"SELECT * FROM {snapshots[version]} ORDER BY order_id").fetchall()

show("orders VERSION AS OF 0 (before the upsert)",
     f"SELECT * FROM {snapshots[0]} ORDER BY order_id")
# O3 was 'placed' at v0, 'cancelled' at v1 — both are recoverable
o3_v0 = con.sql(f"SELECT status FROM {snapshots[0]} WHERE order_id='O3'").fetchone()[0]
o3_v1 = con.sql(f"SELECT status FROM {snapshots[1]} WHERE order_id='O3'").fetchone()[0]
print(f"O3 status: v0='{o3_v0}'  vs  v1='{o3_v1}'")
assert o3_v0 == "placed" and o3_v1 == "cancelled"
print("[PASS] time travel recovers historical state (audit / rollback)")

# RESTORE: a bad load can be undone by pointing 'current' back to an old snapshot
print("Simulating RESTORE TABLE orders TO VERSION AS OF 0 ...")
current_version = 0
assert read_as_of(current_version) == con.sql(f"SELECT * FROM {snapshots[0]} ORDER BY order_id").fetchall()
print("[PASS] rollback = repoint current to an older immutable snapshot")


# ============================================================================
# 3. SCHEMA EVOLUTION — add a column without rewriting/breaking old data
# ============================================================================
print("\n=== 4. SCHEMA EVOLUTION (add 'currency' in version 2) ===")
con.execute("CREATE TABLE working2 AS SELECT * FROM orders_v1")
con.execute("ALTER TABLE working2 ADD COLUMN currency VARCHAR DEFAULT 'INR'")
commit(2, "SELECT * FROM working2")
show("orders @ v2 (new column, old rows back-filled with default)",
     "SELECT order_id, status, amount, currency FROM orders_v2 ORDER BY order_id")
# old snapshot still has the OLD schema (3 business cols), new one has 5 cols
old_cols = len(con.sql("DESCRIBE orders_v0").fetchall())
new_cols = len(con.sql("DESCRIBE orders_v2").fetchall())
assert new_cols == old_cols + 1
print(f"[PASS] schema evolved: v0 had {old_cols} cols, v2 has {new_cols} (additive, safe)")


# ============================================================================
# 4. GDPR DELETE + PURGE PAST RETENTION (why VACUUM breaks time travel)
# ============================================================================
print("\n=== 5. GDPR ERASURE for customer C2 ===")
con.execute("CREATE TABLE working3 AS SELECT * FROM orders_v2")
con.execute("DELETE FROM working3 WHERE customer_id = 'C2'")   # rewrite affected files
commit(3, "SELECT * FROM working3")
show("orders @ v3 (C2 erased from current)",
     "SELECT order_id, customer_id, status FROM orders_v3 ORDER BY order_id")

# C2 is gone from the CURRENT version...
assert con.sql("SELECT COUNT(*) FROM orders_v3 WHERE customer_id='C2'").fetchone()[0] == 0
# ...but STILL present in older snapshots (time travel) -> not truly erased yet!
still_there = con.sql("SELECT COUNT(*) FROM orders_v2 WHERE customer_id='C2'").fetchone()[0]
print(f"C2 rows still visible via time travel (v2): {still_there}  <- must be purged")
assert still_there == 1

# VACUUM / expire_snapshots: physically drop old snapshots past retention.
print("Running VACUUM (expire snapshots older than retention) ...")
for v in (0, 1, 2):                    # purge history that still holds C2
    con.execute(f"DROP TABLE {snapshots[v]}")
    del snapshots[v]
# Now C2 is unrecoverable AND time travel to v2 no longer exists (the trade-off!)
assert 2 not in snapshots
print("[PASS] erasure complete after purging old snapshots")
print("[TEACHING] VACUUM/expire is REQUIRED for true GDPR delete, but it also")
print("           destroys time travel before the retention window — the core trade-off.")

print("\nAll Handbook 19 lakehouse-concept assertions passed. ✅")
