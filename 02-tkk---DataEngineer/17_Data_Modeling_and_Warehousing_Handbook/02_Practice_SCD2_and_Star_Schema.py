"""
================================================================================
HANDBOOK 17 — RUNNABLE PRACTICE: Dimensional Modeling, SCD2 & Additivity
================================================================================
Run:   python3 02_Practice_SCD2_and_Star_Schema.py
Deps:  pip install duckdb        (pure in-process SQL engine, no server)

This file BUILDS a tiny star schema, applies a Slowly Changing Dimension
Type 2 change step-by-step, and proves point-in-time-correct joins with
assertions. Everything is executable and self-checking.
================================================================================
"""
import duckdb

con = duckdb.connect()  # in-memory


def show(title, sql):
    print(f"\n--- {title} ---")
    print(con.sql(sql).to_df().to_string(index=False))


# ============================================================================
# SECTION 1: Build a star schema (dim_customer SCD2 + fct_orders)
# ============================================================================
con.execute("""
CREATE TABLE dim_customer (
    customer_sk    INTEGER,        -- surrogate key (per version)
    customer_id    VARCHAR,        -- natural/business key (stable)
    name           VARCHAR,
    city           VARCHAR,
    effective_from TIMESTAMP,
    effective_to   TIMESTAMP,      -- 9999-12-31 = current version
    is_current     BOOLEAN
);
""")

con.execute("""
INSERT INTO dim_customer VALUES
 (1, 'C001', 'Asha',  'Bangalore', TIMESTAMP '2023-01-01', TIMESTAMP '9999-12-31', TRUE),
 (2, 'C002', 'Ravi',  'Delhi',     TIMESTAMP '2023-01-01', TIMESTAMP '9999-12-31', TRUE);
""")

con.execute("""
CREATE TABLE fct_orders (
    order_id     VARCHAR,          -- degenerate dimension
    customer_sk  INTEGER,          -- FK to the dim VERSION valid at order time
    order_ts     TIMESTAMP,
    quantity     INTEGER,          -- additive
    amount       DECIMAL(10,2),    -- additive
    unit_price   DECIMAL(10,2)     -- NON-additive (never SUM this)
);
""")
# Asha (sk=1) orders while living in Bangalore
con.execute("""
INSERT INTO fct_orders VALUES
 ('O100', 1, TIMESTAMP '2023-03-10', 2, 200.00, 100.00),
 ('O101', 2, TIMESTAMP '2023-04-05', 1, 150.00, 150.00);
""")
show("dim_customer (initial)", "SELECT * FROM dim_customer ORDER BY customer_sk")


# ============================================================================
# SECTION 2: Apply an SCD Type 2 change — Asha moves Bangalore -> Mumbai
# ============================================================================
# Step 1: close the current version (set is_current=FALSE, stamp effective_to)
CHANGE_TS = "TIMESTAMP '2023-06-01'"
con.execute(f"""
UPDATE dim_customer
   SET is_current = FALSE, effective_to = {CHANGE_TS}
 WHERE customer_id = 'C001' AND is_current = TRUE;
""")
# Step 2: insert the NEW current version with a fresh surrogate key
con.execute(f"""
INSERT INTO dim_customer VALUES
 (3, 'C001', 'Asha', 'Mumbai', {CHANGE_TS}, TIMESTAMP '9999-12-31', TRUE);
""")
show("dim_customer (after SCD2 move)", "SELECT * FROM dim_customer ORDER BY customer_sk")

# A NEW order after the move points at the new surrogate key (sk=3)
con.execute("""
INSERT INTO fct_orders VALUES
 ('O102', 3, TIMESTAMP '2023-07-20', 5, 500.00, 100.00);
""")


# ============================================================================
# SECTION 3: Point-in-time correctness — history is preserved
# ============================================================================
show("Orders joined to the dim version valid at order time",
     """
     SELECT o.order_id, o.order_ts, d.name, d.city AS city_at_order_time, o.amount
     FROM fct_orders o
     JOIN dim_customer d ON o.customer_sk = d.customer_sk
     ORDER BY o.order_ts
     """)

# Asha's pre-move order MUST still show Bangalore; post-move shows Mumbai
res = con.sql("""
    SELECT o.order_id, d.city
    FROM fct_orders o JOIN dim_customer d ON o.customer_sk = d.customer_sk
    WHERE d.name = 'Asha' ORDER BY o.order_ts
""").fetchall()
assert res == [('O100', 'Bangalore'), ('O102', 'Mumbai')], res
print("\n[PASS] SCD2 preserved history: O100=Bangalore, O102=Mumbai")

# "Current view" of customers (what a Type-1 overwrite would have shown)
show("Current customers (is_current = TRUE)",
     "SELECT customer_id, name, city FROM dim_customer WHERE is_current ORDER BY customer_id")


# ============================================================================
# SECTION 4: Additivity — why you must NOT sum a non-additive measure
# ============================================================================
# Additive: SUM(amount), SUM(quantity) across any dimension is valid.
show("Additive rollup (correct)",
     "SELECT SUM(quantity) AS total_qty, SUM(amount) AS total_amount FROM fct_orders")

# Non-additive: SUM(unit_price) is MEANINGLESS. Derive it instead.
show("Non-additive done right: derive unit price, never SUM it",
     "SELECT SUM(amount) / SUM(quantity) AS blended_unit_price FROM fct_orders")

blended = con.sql("SELECT SUM(amount)/SUM(quantity) FROM fct_orders").fetchone()[0]
naive_sum = con.sql("SELECT SUM(unit_price) FROM fct_orders").fetchone()[0]
print(f"\n[TEACHING] Correct blended unit price = {blended:.2f}  "
      f"| Naive SUM(unit_price) = {naive_sum:.2f} (WRONG, non-additive)")
assert abs(float(blended) - (850.0 / 8.0)) < 1e-6


# ============================================================================
# SECTION 5: Fan-out trap — joining to a finer grain double-counts revenue
# ============================================================================
con.execute("""
CREATE TABLE order_items AS
SELECT * FROM (VALUES
 ('O100','item_A'), ('O100','item_B'),        -- O100 has 2 line items
 ('O101','item_C'),
 ('O102','item_D'), ('O102','item_E'), ('O102','item_F')
) t(order_id, item);
""")
true_rev = con.sql("SELECT SUM(amount) FROM fct_orders").fetchone()[0]
fanned = con.sql("""
    SELECT SUM(o.amount)
    FROM fct_orders o JOIN order_items i ON o.order_id = i.order_id
""").fetchone()[0]
print(f"\n[FAN-OUT] True revenue = {true_rev} | After join to items (WRONG) = {fanned}")
assert float(fanned) > float(true_rev), "join to finer grain should inflate the sum"
# Correct fix: aggregate to the fact grain BEFORE joining, or count items separately
correct = con.sql("""
    WITH item_counts AS (SELECT order_id, COUNT(*) n FROM order_items GROUP BY order_id)
    SELECT SUM(o.amount) AS revenue, SUM(c.n) AS total_items
    FROM fct_orders o JOIN item_counts c ON o.order_id = c.order_id
""").fetchone()
print(f"[FAN-OUT FIX] revenue={correct[0]} (correct), total_items={correct[1]}")
assert float(correct[0]) == float(true_rev)
print("[PASS] Fan-out avoided by pre-aggregating to the fact grain")

print("\nAll Handbook 17 assertions passed. ✅")
