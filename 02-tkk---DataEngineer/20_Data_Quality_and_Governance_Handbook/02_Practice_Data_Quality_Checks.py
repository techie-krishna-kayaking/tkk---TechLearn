"""
================================================================================
HANDBOOK 20 — RUNNABLE PRACTICE: Data Quality Checks (Great-Expectations style)
================================================================================
Run:   python3 02_Practice_Data_Quality_Checks.py
Deps:  none (Python stdlib only) — a mini expectation engine you can read end-to-end

Demonstrates a real data-quality gate a pipeline would run BEFORE publishing:
  - schema / not-null / uniqueness / range / accepted-values / regex
  - freshness SLA
  - referential integrity (relationships)
  - source-to-target reconciliation (row count + sum tolerance)
The run EXITS NON-ZERO if any critical expectation fails — exactly how you'd
wire it into CI / Airflow so bad data never reaches stakeholders.
================================================================================
"""
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta

NOW = datetime(2024, 6, 1, 12, 0, 0)   # pretend "now" for deterministic freshness


# ---- A tiny expectation engine ---------------------------------------------
@dataclass
class Result:
    name: str
    passed: bool
    detail: str = ""

@dataclass
class Suite:
    rows: list
    results: list = field(default_factory=list)

    def _add(self, name, passed, detail=""):
        self.results.append(Result(name, passed, detail))
        flag = "PASS" if passed else "FAIL"
        print(f"  [{flag}] {name}" + (f" — {detail}" if detail else ""))
        return passed

    def expect_column_to_exist(self, col):
        ok = all(col in r for r in self.rows)
        return self._add(f"column '{col}' exists", ok)

    def expect_not_null(self, col):
        bad = [r for r in self.rows if r.get(col) in (None, "")]
        return self._add(f"'{col}' not null", not bad,
                         f"{len(bad)} null(s)" if bad else "")

    def expect_unique(self, col):
        vals = [r[col] for r in self.rows]
        dups = len(vals) - len(set(vals))
        return self._add(f"'{col}' unique", dups == 0,
                         f"{dups} duplicate(s)" if dups else "")

    def expect_between(self, col, lo, hi):
        bad = [r[col] for r in self.rows if not (lo <= r[col] <= hi)]
        return self._add(f"'{col}' in [{lo},{hi}]", not bad,
                         f"{len(bad)} out of range: {bad[:3]}" if bad else "")

    def expect_accepted_values(self, col, allowed):
        bad = sorted({r[col] for r in self.rows if r[col] not in allowed})
        return self._add(f"'{col}' in {allowed}", not bad,
                         f"unexpected: {bad}" if bad else "")

    def expect_regex(self, col, pattern):
        rx = re.compile(pattern)
        bad = [r[col] for r in self.rows if not rx.match(str(r[col]))]
        return self._add(f"'{col}' matches /{pattern}/", not bad,
                         f"{len(bad)} bad: {bad[:3]}" if bad else "")

    def expect_freshness(self, col, max_age, now=NOW):
        newest = max(r[col] for r in self.rows)
        age = now - newest
        return self._add(f"freshness('{col}') < {max_age}", age <= max_age,
                         f"stale by {age - max_age}" if age > max_age else f"age={age}")

    def expect_relationship(self, col, parent_keys):
        orphans = sorted({r[col] for r in self.rows if r[col] not in parent_keys})
        return self._add(f"'{col}' FK exists in parent", not orphans,
                         f"orphans: {orphans}" if orphans else "")

    def critical_failures(self):
        return [r for r in self.results if not r.passed]


# ---- Seed data (a "clean" orders batch about to be published) ---------------
customers = {"C001", "C002", "C003"}
orders = [
    {"order_id": "O1", "customer_id": "C001", "status": "delivered",
     "amount": 200.0, "email": "a@x.com", "created_at": datetime(2024, 6, 1, 11, 30)},
    {"order_id": "O2", "customer_id": "C002", "status": "placed",
     "amount": 150.0, "email": "b@x.com", "created_at": datetime(2024, 6, 1, 10, 0)},
    {"order_id": "O3", "customer_id": "C003", "status": "cancelled",
     "amount": 0.0,   "email": "c@x.com", "created_at": datetime(2024, 6, 1, 9, 0)},
]

print("=== SUITE A: clean batch (should fully pass) ===")
a = Suite(orders)
for col in ("order_id", "customer_id", "status", "amount", "email", "created_at"):
    a.expect_column_to_exist(col)
a.expect_not_null("order_id")
a.expect_unique("order_id")
a.expect_between("amount", 0, 1_000_000)
a.expect_accepted_values("status", {"placed", "shipped", "delivered", "cancelled"})
a.expect_regex("email", r"^[^@]+@[^@]+\.[^@]+$")
a.expect_freshness("created_at", timedelta(hours=2))
a.expect_relationship("customer_id", customers)
assert not a.critical_failures(), "clean batch should pass all expectations"
print("  -> Suite A passed, batch is safe to publish.\n")


# ---- Seed data (a BAD batch that must be BLOCKED) ---------------------------
bad_orders = [
    {"order_id": "O1", "customer_id": "C001", "status": "delivered",
     "amount": 200.0, "email": "a@x.com", "created_at": datetime(2024, 6, 1, 11, 30)},
    {"order_id": "O1", "customer_id": "C999", "status": "returned",     # dup id, bad FK, bad status
     "amount": -5.0,  "email": "not-an-email", "created_at": datetime(2024, 5, 20, 9, 0)},  # neg amt, bad email, stale
    {"order_id": None, "customer_id": "C002", "status": "placed",
     "amount": 150.0, "email": "b@x.com", "created_at": datetime(2024, 6, 1, 10, 0)},        # null id
]

print("=== SUITE B: corrupted batch (should FAIL and block publish) ===")
b = Suite(bad_orders)
b.expect_not_null("order_id")
b.expect_unique("order_id")
b.expect_between("amount", 0, 1_000_000)
b.expect_accepted_values("status", {"placed", "shipped", "delivered", "cancelled"})
b.expect_regex("email", r"^[^@]+@[^@]+\.[^@]+$")
b.expect_freshness("created_at", timedelta(hours=2))
b.expect_relationship("customer_id", customers)
fails_b = b.critical_failures()
assert len(fails_b) >= 6, "corrupted batch should trip many expectations"
print(f"  -> Suite B produced {len(fails_b)} failures — publish BLOCKED.\n")


# ---- Source-to-target reconciliation ---------------------------------------
print("=== SUITE C: source -> target reconciliation ===")
source_rows, source_sum = 1_000_000, 4_523_118.55
target_rows, target_sum = 1_000_000, 4_523_118.55   # a correct load
row_ok = source_rows == target_rows
sum_ok = abs(source_sum - target_sum) <= 0.01        # penny tolerance
print(f"  [{'PASS' if row_ok else 'FAIL'}] row count match: {source_rows} == {target_rows}")
print(f"  [{'PASS' if sum_ok else 'FAIL'}] sum(amount) match within ₹0.01")
assert row_ok and sum_ok
print("  -> Reconciliation passed.\n")


# ---- CI/pipeline gate: exit non-zero on any critical failure ----------------
# (In prod this is what fails the Airflow task / CI job before publishing.)
GATE_SUITES = [a]        # only the batch we intend to publish must be clean
gate_failures = [f for s in GATE_SUITES for f in s.critical_failures()]
if gate_failures:
    print(f"DATA QUALITY GATE FAILED: {len(gate_failures)} issue(s). Blocking publish.")
    sys.exit(1)
print("All Handbook 20 data-quality checks passed. ✅  (gate is green)")
