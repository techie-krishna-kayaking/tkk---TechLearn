# Python Interview Masterbook — Lead / Staff / Principal Data Engineer

> **Target roles:** Lead Data Engineer · Staff Data Engineer · Principal Data Engineer · Data Architect  
> **Target market:** Product-based companies in India; preparation target ₹70+ LPA  
> **Scope:** Modern Python, coding interviews, data structures/algorithms, production ETL, APIs, files, memory, concurrency, Pandas, testing, reliability, security, performance, and architecture.  
> **Python baseline:** Core examples target Python 3.11+ unless version-specific behavior is explicitly called out. Use the exact interpreter/runtime supported by the production platform.
>
> This is a curated set of recurring senior Python and Data Engineering interview patterns. It is not a claim that every question was asked by a named company recently.

---

# How to use this chapter

For each problem, do not jump directly to code.

1. Clarify input size, shape, encoding, schema, and expected output.
2. Clarify correctness rules: duplicates, nulls, ordering, timezone, precision, identity, and late data.
3. State time and space complexity.
4. Write the simplest correct implementation.
5. Compare alternatives and explain when each wins.
6. Discuss tests, observability, failure/retry behavior, and operational ownership.

## What seniority means

| Dimension | Lead | Staff | Principal |
|---|---|---|---|
| Python | Correct, readable, tested code | Reusable libraries and patterns | Platform-wide engineering standards |
| Performance | Profiles and optimizes bottlenecks | Optimizes workloads and memory/concurrency | Cost/performance strategy across teams |
| Reliability | Handles failures and retries | Designs idempotency, replay, and recovery | Defines SLOs, ownership, and risk posture |
| Architecture | Builds production pipelines | Aligns multiple domains and teams | Sets technical direction and investment |
| Leadership | Mentors engineers | Influences without authority | Aligns engineering, product, security, and business |

A Principal answer is not simply a more complicated Python implementation. It demonstrates judgment about whether Python is the correct execution layer at all.

---

# Part 1 — One consistent Data Engineering dataset

## Scenario: E-commerce order ingestion and analytics

The company ingests customer, product, order, payment, and clickstream records from APIs and files. Python is used for API ingestion, validation, reconciliation, orchestration, metadata-driven transformations, and operational tooling. For data that exceeds a single machine, Python may orchestrate SQL/Spark rather than process every row itself.

All coding examples below use this same domain.

## 1.1 Canonical sample records

```python
customers = [
    {"customer_id": 1, "name": "Asha", "email": "asha@example.com", "country": "IN"},
    {"customer_id": 2, "name": "Ben", "email": "ben@example.com", "country": "US"},
    {"customer_id": 3, "name": "Chen", "email": "chen@example.com", "country": "SG"},
    {"customer_id": 4, "name": "Diya", "email": "diya@example.com", "country": "IN"},
    {"customer_id": 5, "name": "Eli", "email": None, "country": "IN"},
]

orders = [
    {"order_id": 101, "customer_id": 1, "order_ts": "2025-01-10T10:00:00Z",
     "status": "COMPLETED", "currency": "INR", "total": "1200.00"},
    {"order_id": 102, "customer_id": 1, "order_ts": "2025-01-15T12:00:00Z",
     "status": "COMPLETED", "currency": "INR", "total": "1050.00"},
    {"order_id": 103, "customer_id": 2, "order_ts": "2025-01-20T09:00:00Z",
     "status": "CANCELLED", "currency": "USD", "total": "200.00"},
    {"order_id": 104, "customer_id": 2, "order_ts": "2025-02-05T15:00:00Z",
     "status": "COMPLETED", "currency": "USD", "total": "500.00"},
    {"order_id": 105, "customer_id": 3, "order_ts": "2025-02-07T13:00:00Z",
     "status": "COMPLETED", "currency": "SGD", "total": "300.00"},
    {"order_id": 106, "customer_id": 1, "order_ts": "2025-03-01T17:00:00Z",
     "status": "COMPLETED", "currency": "INR", "total": "300.00"},
    {"order_id": 107, "customer_id": 4, "order_ts": "2025-03-03T08:00:00Z",
     "status": "PENDING", "currency": "INR", "total": "500.00"},
    {"order_id": 108, "customer_id": 5, "order_ts": "2025-03-05T19:00:00Z",
     "status": "COMPLETED", "currency": "INR", "total": "400.00"},
]

order_items = [
    {"item_id": 1001, "order_id": 101, "product_id": 10, "qty": 2, "unit_price": "500.00"},
    {"item_id": 1002, "order_id": 101, "product_id": 11, "qty": 1, "unit_price": "200.00"},
    {"item_id": 1003, "order_id": 102, "product_id": 10, "qty": 1, "unit_price": "500.00"},
    {"item_id": 1004, "order_id": 102, "product_id": 12, "qty": 2, "unit_price": "300.00"},
    {"item_id": 1005, "order_id": 103, "product_id": 11, "qty": 1, "unit_price": "200.00"},
    {"item_id": 1006, "order_id": 104, "product_id": 10, "qty": 1, "unit_price": "500.00"},
    {"item_id": 1007, "order_id": 105, "product_id": 13, "qty": 3, "unit_price": "100.00"},
]

products = [
    {"product_id": 10, "name": "Keyboard", "category": "Accessories"},
    {"product_id": 11, "name": "Mouse", "category": "Accessories"},
    {"product_id": 12, "name": "Monitor", "category": "Displays"},
    {"product_id": 13, "name": "Cable", "category": "Accessories"},
]

payments = [
    {"payment_id": 5001, "order_id": 101, "attempt": 1, "status": "SUCCESS", "amount": "1200.00"},
    {"payment_id": 5002, "order_id": 102, "attempt": 1, "status": "FAILED", "amount": "1050.00"},
    {"payment_id": 5003, "order_id": 102, "attempt": 2, "status": "SUCCESS", "amount": "1050.00"},
    {"payment_id": 5004, "order_id": 103, "attempt": 1, "status": "REFUNDED", "amount": "200.00"},
]
```

## 1.2 Common imports and type conventions

```python
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence
import csv
import hashlib
import json
import logging
import os
import random
import tempfile
import time
```

**Money rule:** use `Decimal`, not binary `float`, for financial calculations. **Time rule:** use timezone-aware datetimes (normally UTC at system boundaries). **Identity rule:** do not assume email is a globally unique customer key.

---

# Part 2 — Python language fundamentals

## Q1. Explain Python's core data structures and when to use each.

- `list`: ordered, mutable, duplicates allowed.
- `tuple`: ordered, immutable container (if all contained values are immutable/hashable, it can be a dict key).
- `set`: unique hashable elements, efficient membership.
- `dict`: key-value mapping with insertion-order preservation in modern Python.

Example: use a set for membership checks over known customer IDs; use a dict to map order_id to the order record; use a list when preserving all payment attempts and their order matters.

**Best:** Choose by semantics first, then complexity and memory. A set/dict gives average O(1) membership/lookup but uses more memory than a list and relies on hashable keys.

**Lead:** Select appropriate structure. **Staff:** Create reusable patterns for bounded/unbounded data. **Principal:** Define memory and scale boundaries for Python services so data is not accidentally materialized on one host.

## Q2. Compare time complexity of list, tuple, set, and dict.

| Operation | List/Tuple | Set | Dict |
|---|---:|---:|---:|
| Index access | O(1) | N/A | N/A |
| Membership | O(n) | O(1) average | O(1) average by key |
| Append | O(1) amortized (list) | N/A | N/A |
| Add element | N/A | O(1) average | O(1) average |
| Key lookup | N/A | N/A | O(1) average |
| Remove by value | O(n) | O(1) average | O(1) average by key |

Worst-case hash operations can degrade due to collisions. Complexity does not capture object overhead, cache locality, hashing cost, or memory pressure.

## Q3. What does mutable vs immutable mean?

Mutable objects can be modified in place (list, dict, set). Immutable objects cannot (int, str, bytes, tuple as a container, frozenset).

```python
a = [1, 2]
b = a
b.append(3)
assert a == [1, 2, 3]  # both names reference the same list

x = "orders"
y = x.upper()
assert x == "orders" and y == "ORDERS"
```

**Best:** Understand object identity and aliasing. Use immutable value objects when shared state would otherwise be difficult to reason about.

## Q4. Shallow copy vs deep copy?

```python
import copy

source = {"order": 101, "tags": ["new", "priority"]}
shallow = copy.copy(source)
deep = copy.deepcopy(source)

shallow["tags"].append("gift")
assert "gift" in source["tags"]  # nested list is shared

deep["tags"].append("fragile")
assert "fragile" not in source["tags"]
```

Shallow copy duplicates the outer container; nested objects remain shared. Deep copy recursively copies objects where supported.

**Best:** Prefer explicit construction for known schemas; deep copy can be expensive and may fail/behave unexpectedly for file handles, connections, locks, and custom resources.

## Q5. Why are mutable default arguments dangerous?

```python
# Bug: this list is created once when the function is defined.
def add_order(order_id, order_ids=[]):
    order_ids.append(order_id)
    return order_ids

# Correct
def add_order(order_id, order_ids=None):
    if order_ids is None:
        order_ids = []
    order_ids.append(order_id)
    return order_ids
```

Default expressions are evaluated at function definition time, not every call. The issue applies to mutable dicts, sets, and custom objects too.

**Best:** Use `None` sentinel when a fresh mutable object is required. For configuration, prefer immutable defaults or explicit config objects.

## Q6. `is` vs `==`?

`==` compares values; `is` compares object identity.

```python
a = {"order_id": 101}
b = {"order_id": 101}
assert a == b
assert a is not b
if customer.get("email") is None:
    ...
```

Use `is None`/ `is not None` for sentinel checks. Do not use identity for string/number value comparisons; interning can make such code appear to work unpredictably.

## Q7. Explain hashability and why dict keys must be hashable.

A hashable object has a stable hash during its lifetime and equality behavior consistent with hashing. Immutable primitives and tuples of hashable objects are common keys; lists/dicts are mutable and unhashable.

```python
order_key = (101, "INR")
order_lookup = {order_key: orders[0]}
```

**Best:** Use immutable business-key tuples for in-memory composite lookup. Do not build keys from mutable records or assume a Python hash is a persistent cross-process identifier.

## Q8. What are `*args` and `**kwargs`?

```python
def load_orders(source, *paths, batch_size=10_000, **options):
    return {
        "source": source,
        "paths": paths,
        "batch_size": batch_size,
        "options": options,
    }
```

`*args` captures extra positional arguments; `**kwargs` captures extra keyword arguments.

**Best:** Use explicit named parameters for stable public APIs and typed configuration objects for larger frameworks. Avoid hidden, unvalidated configuration passed through unrestricted kwargs.

## Q9. Explain LEGB scope.

Python resolves names in Local, Enclosing, Global, Builtins order. Use local variables and explicit dependencies rather than mutating module globals.

```python
tax_rate = Decimal("0.18")

def amount_with_tax(net_amount: Decimal) -> Decimal:
    return net_amount * (Decimal("1") + tax_rate)
```

For production code, prefer injecting the tax policy/config instead of relying on mutable global state.

## Q10. What is a closure?

A closure is a function that retains access to variables from its enclosing scope after that scope returns.

```python
def make_currency_formatter(currency: str):
    def format_amount(amount: Decimal) -> str:
        return f"{currency} {amount:.2f}"
    return format_amount

inr_formatter = make_currency_formatter("INR")
```

Use closures for lightweight behavior configuration. For complex state or dependencies, a class/dataclass is often clearer.

## Q11. What is a decorator? Build a timing decorator.

```python
from functools import wraps
from time import perf_counter

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        started = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            logging.info("function=%s elapsed_seconds=%.4f",
                         func.__qualname__, elapsed)
    return wrapper

@timed
def build_order_index(order_rows):
    return {row["order_id"]: row for row in order_rows}
```

**Best:** Use `functools.wraps`, a monotonic high-resolution timer, structured logging, and avoid logging sensitive arguments. For async functions, write an async-aware decorator.

## Q12. What is a generator and why is it useful?

```python
def iter_order_ids(order_rows):
    for row in order_rows:
        yield row["order_id"]

for order_id in iter_order_ids(orders):
    process(order_id)
```

A generator yields values lazily and retains execution state between yields. It avoids materializing a complete output list.

**Caveat:** A generator is usually one-pass. It does not automatically make upstream source reads memory-bounded if the source itself was already loaded into memory.

## Q13. Iterable vs iterator vs generator?

An iterable can return an iterator via `iter(x)`; an iterator implements `__iter__` and `__next__`; a generator is an iterator created by a generator function/expression.

```python
rows = iter(orders)          # iterator
first = next(rows)
remaining = list(rows)       # consumes remaining iterator
```

**Best:** Use iterable interfaces for reusable APIs; document when an input iterator is consumed. Do not attempt to iterate a generator twice unless it is recreated.

## Q14. Explain `yield` vs `return`.

`return` ends a function and returns one result. `yield` suspends a generator and emits a value; subsequent iteration resumes it. A generator may yield many values.

## Q15. Why use context managers?

They guarantee cleanup around a resource scope, including exceptions.

```python
with open("orders.jsonl", encoding="utf-8") as handle:
    for line in handle:
        process_line(line)
```

Custom managers can manage database transactions, temporary directories, locks, and API sessions.

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(resource_factory, cleanup):
    resource = resource_factory()
    try:
        yield resource
    finally:
        cleanup(resource)
```

**Best:** Prefer built-in context managers; use `ExitStack` when acquiring a dynamic number of resources.

## Q16. Explain exceptions and exception chaining.

Catch errors you can handle, preserve context, and re-raise when the job cannot safely continue.

```python
class InvalidOrderError(ValueError):
    pass

def parse_order_id(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidOrderError(f"Invalid order_id: {value!r}") from exc
```

Avoid `except Exception: pass`. Catch broad exceptions only at process boundaries for logging/cleanup before re-raising or returning a deliberate failure state.

## Q17. What is the difference between `finally`, `else`, and `except`?

- `except`: handles matching exceptions.
- `else`: runs only if the try block had no exception.
- `finally`: runs during cleanup regardless of success/failure (subject to process termination).

Use `else` to keep success-only code outside the protected operations and `finally` for cleanup.

## Q18. What are dataclasses and when would you use them?

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Order:
    order_id: int
    customer_id: int
    currency: str
    total: Decimal
    status: str
```

Dataclasses reduce boilerplate for data containers. `frozen=True` prevents normal attribute reassignment, but does not deep-freeze mutable fields.

**Best:** Use dataclasses for internal typed records/config; use Pydantic or equivalent validation library when runtime parsing/validation of untrusted input is required.

## Q19. TypedDict vs dataclass vs Pydantic model?

- TypedDict: static typing contract for dict-shaped data; no automatic runtime validation.
- Dataclass: Python object with generated methods; type annotations alone do not validate input.
- Pydantic: runtime parsing/validation/serialization (behavior depends on version/config).

**Best:** Choose based on boundary: TypedDict for typed dict interfaces, dataclass for internal value objects, validation model at untrusted API/file boundaries. Avoid repeated validation in every inner loop.

## Q20. Explain Python packaging and dependency isolation.

Use a project package, a pinned/locked dependency set, virtual environments, reproducible builds, and CI. Separate runtime and development dependencies. Avoid relying on a developer's global site-packages.

**Staff/Principal:** Standardize dependency policies, vulnerability scanning, artifact provenance, supported Python versions, and rollback strategy for shared libraries.

---

# Part 3 — Coding and data-structure problems using orders

## Q21. Count completed orders per customer.

```python
from collections import Counter

counts = Counter(
    row["customer_id"]
    for row in orders
    if row["status"] == "COMPLETED"
)
```

**Alternative:** A normal dict with `get(key, 0) + 1`.

**Best:** `Counter` communicates frequency aggregation clearly. Complexity O(n) time and O(k) space for k distinct customers.

## Q22. Find duplicate order IDs.

```python
from collections import Counter

id_counts = Counter(row["order_id"] for row in orders)
duplicate_ids = {key for key, count in id_counts.items() if count > 1}
```

**Best:** Counter is concise. For a streaming/unbounded source, keep only a bounded key store if possible or move exact global deduplication to a database/distributed system. A Python set/dict still grows with unique key cardinality.

## Q23. Return every duplicate record, not just duplicate IDs.

```python
from collections import defaultdict

by_id = defaultdict(list)
for row in orders:
    by_id[row["order_id"]].append(row)

duplicate_records = [
    row
    for rows in by_id.values() if len(rows) > 1
    for row in rows
]
```

This keeps all copies but uses O(n) memory. For very large data, sort/partition externally or use a distributed engine.

## Q24. Deduplicate records by order_id, keeping the latest source version.

```python
def dedupe_latest(records):
    winners = {}
    for row in records:
        key = row["order_id"]
        version = (row.get("source_sequence", -1),
                   row.get("updated_at", ""),
                   row.get("ingested_at", ""))
        previous = winners.get(key)
        if previous is None or version > previous[0]:
            winners[key] = (version, row)
    return [pair[1] for pair in winners.values()]
```

**Best:** Use source sequence/LSN as primary ordering. Timestamp alone can tie; ingestion time is only a tie-breaker, not necessarily source truth. Include tombstone/delete records in ranking before deciding final state.

## Q25. Find the top K customers by completed order value.

```python
from collections import defaultdict
from decimal import Decimal

spend = defaultdict(Decimal)
for row in orders:
    if row["status"] == "COMPLETED":
        spend[(row["customer_id"], row["currency"])] += Decimal(row["total"])

top_3 = sorted(spend.items(), key=lambda pair: (-pair[1], pair[0][0]))[:3]
```

This example ranks by `(customer_id, currency)` and does not mix currencies. Full sorting costs O(k log k); use `heapq.nlargest` when K is small relative to distinct customers. Define tie behavior.

## Q26. Implement Top K with a heap.

```python
import heapq

top_k = heapq.nlargest(
    3,
    spend.items(),
    key=lambda pair: (pair[1], -pair[0][0])
)
```

**Best:** Heap is useful when K ≪ N. Sorting is often simpler and can be competitive when K is a large fraction of N. Benchmark realistic cardinality.

## Q27. Find the first non-repeating character in an order status string.

```python
from collections import Counter

def first_unique_char(text: str) -> str | None:
    counts = Counter(text)
    return next((ch for ch in text if counts[ch] == 1), None)
```

Two-pass O(n) solution. A one-pass ordered map can also work but is less transparent for this requirement.

## Q28. Group orders by currency.

```python
from collections import defaultdict

grouped = defaultdict(list)
for row in orders:
    grouped[row["currency"]].append(row)
```

For large inputs, storing every row in groups still uses O(n) memory. If only counts/sums are required, aggregate directly rather than retaining full records.

## Q29. Flatten one level of nested order item lists.

```python
nested_items = [[1001, 1002], [1003], [], [1004, 1005]]
flat = [item for group in nested_items for item in group]
```

Time O(total elements), output memory O(total elements). For lazy processing, use `itertools.chain.from_iterable`.

## Q30. Find common product IDs between two order extracts.

```python
def product_ids(rows):
    return {row["product_id"] for row in rows}

common = product_ids(batch_a) & product_ids(batch_b)
```

Expected O(n + m) time and O(u) memory. For huge inputs, use database joins, external sort, or distributed semi-joins.

## Q31. Merge two dictionaries with explicit conflict policy.

```python
merged = {**source_record, **target_record}  # target wins on collision
```

Alternative: `source_record | target_record` in modern Python.

**Best:** Do not let merge order silently determine business precedence. Write an explicit field-level conflict policy for source/target reconciliation.

## Q32. Find the second-highest distinct order amount.

```python
amounts = sorted(
    {Decimal(row["total"]) for row in orders},
    reverse=True
)
second_highest = amounts[1] if len(amounts) >= 2 else None
```

Set handles duplicates; sort gives O(n log n). For a single pass, maintain largest and second-largest distinct values in O(n) time and O(1) extra space. Clarify “second row” vs “second distinct value.”

## Q33. Implement a single-pass second-largest distinct value.

```python
def second_largest_distinct(values):
    first = second = None
    for value in values:
        if first is None or value > first:
            if value != first:
                second = first
            first = value
        elif value != first and (second is None or value > second):
            second = value
    return second
```

This is O(n) time and O(1) space. If values may legitimately be None, use a unique sentinel rather than None for initialization.

## Q34. Find longest contiguous run of completed orders in an already ordered status list.

```python
def longest_completed_run(statuses):
    best = current = 0
    for status in statuses:
        current = current + 1 if status == "COMPLETED" else 0
        best = max(best, current)
    return best
```

O(n) time, O(1) space. Clarify that the input order is already the required chronological order; otherwise sort first using a deterministic tie-breaker.

## Q35. Implement sliding-window maximum on order totals.

```python
from collections import deque

def sliding_max(values, window_size):
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    result = []
    q = deque()  # indexes; values decrease from front to back
    for i, value in enumerate(values):
        while q and q[0] <= i - window_size:
            q.popleft()
        while q and values[q[-1]] <= value:
            q.pop()
        q.append(i)
        if i >= window_size - 1:
            result.append(values[q[0]])
    return result
```

O(n) time because each index enters/leaves deque once. Sorting each window costs more. For event streams, define event-time window semantics and late-data policy.

## Q36. Longest substring without repeating characters.

```python
def longest_unique_substring_length(text):
    last_seen = {}
    left = best = 0
    for right, char in enumerate(text):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)
    return best
```

O(n) time and O(min(n, alphabet)) space. Explain the sliding-window invariant: current window contains no repeated character.

## Q37. Implement a bounded LRU cache.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)
```

Operations are O(1) average. Production concerns: thread safety, TTL, memory size vs entry count, cache stampede, invalidation, and whether a distributed cache is more appropriate.

## Q38. Implement a bounded producer-consumer queue.

Use `queue.Queue(maxsize=N)` for thread-based producer-consumer workflows. It provides locking and blocking semantics. For asyncio use `asyncio.Queue`; for cross-process use a multiprocessing queue or broker.

**Best:** Use backpressure via bounded queues. Unbounded queues can convert a downstream slowdown into unbounded memory growth.

## Q39. When do you use recursion vs iteration?

Use recursion for naturally recursive structures when depth is bounded and code clarity improves. Python has a recursion limit and function-call overhead; for potentially deep nested files/JSON, iterative stack traversal is often safer.

## Q40. How would you implement a priority queue for order retry jobs?

Use `heapq` with tuples such as `(next_attempt_epoch, sequence_number, job)`. The sequence number gives deterministic ordering when timestamps tie. Avoid comparing arbitrary job objects directly.

---

# Part 4 — Algorithms and complexity for senior interviews

## Q41. Explain Big-O, Omega, and Theta.

- O(f(n)): asymptotic upper bound.
- Ω(f(n)): asymptotic lower bound.
- Θ(f(n)): tight asymptotic bound.

Discuss input size and worst/average/best case. For data engineering, also analyze bytes, cardinality, network, serialization, disk I/O, and memory—not just row count.

## Q42. Time complexity vs space complexity?

Time estimates growth in operations; space estimates auxiliary memory/output memory. A streaming generator may keep auxiliary state O(1) even though it processes N records; a list comprehension materializes O(N) output.

## Q43. When is a hash map better than sorting?

Hash map: expected O(n) grouping/lookup and O(k) memory. Sorting: O(n log n), but provides order, deterministic range processing, and external-sort scalability. Choose by semantics, memory, and downstream access patterns.

## Q44. Explain two-pointer technique using item IDs.

If two lists are sorted, advance the pointer with the smaller value; when equal, record the match and advance both. O(n + m) time and O(1) auxiliary space (excluding output). Sorting unsorted inputs adds O(n log n + m log m).

## Q45. Explain sliding window and its invariant.

Maintain a range [left, right] satisfying a condition (for example, no repeated event type). Extend right; while invalid, advance left and update state. The invariant is what makes the algorithm correct; amortized O(n) when each pointer advances at most N times.

## Q46. BFS vs DFS?

BFS explores level by level using a queue; shortest path in an unweighted graph. DFS explores depth-first using recursion/stack; useful for reachability, cycle detection, and topological traversal. For dependency DAGs and pipeline orchestration, detect cycles and produce topological order.

## Q47. Heap vs sorting for Top K?

Sorting all N values costs O(N log N); a bounded heap costs O(N log K) time and O(K) memory. For K near N, sorting can be simpler. Always define tie behavior.

## Q48. How do you process data too large for RAM?

Use iterators/chunks, external sort/aggregation, database pushdown, object-store scans, or distributed engines. Exact global distinct/grouping requires state or external/distributed coordination; a generator alone does not make an unbounded exact aggregation O(1) memory.

## Q49. Explain amortized complexity for list append.

A dynamic array occasionally resizes and copies elements, but appending is O(1) amortized across a sequence of operations. A single append can be O(n) during resize.

## Q50. Why can a theoretically faster algorithm be slower in practice?

Constant factors, cache locality, Python interpreter overhead, allocations, hashing, branch behavior, serialization, I/O, and vectorized native code matter. Profile real inputs instead of optimizing by Big-O alone.

---

# Part 5 — Files, formats and memory-bounded ingestion

## Q51. Process a 10 GB newline-delimited JSON file without loading it all into RAM.

```python
import json
from pathlib import Path

def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}") from exc
```

This bounds input buffering but the caller can still accumulate all yielded rows. Decide whether malformed records should fail the file or be quarantined with original payload and reason.

## Q52. Process a large CSV safely.

```python
import csv
from pathlib import Path

def iter_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"order_id", "customer_id", "status", "total", "currency"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        for row in reader:
            yield row
```

Use `newline=""` for the CSV module, explicit encoding, schema checks, and row-level validation. If compression or parsing complexity dominates, use a suitable library/engine rather than hand-parsing CSV.

## Q53. Process a file in chunks and aggregate revenue per currency.

```python
from collections import defaultdict
from decimal import Decimal
import pandas as pd

totals = defaultdict(Decimal)
for chunk in pd.read_csv(
    "orders.csv",
    dtype={"currency": "string", "total": "string"},
    chunksize=250_000,
    usecols=["status", "currency", "total"],
):
    completed = chunk.loc[chunk["status"].eq("COMPLETED")]
    partial = (
        completed.assign(total=completed["total"].map(Decimal))
        .groupby("currency")["total"]
        .sum()
    )
    for currency, amount in partial.items():
        totals[currency] += amount
```

Chunking bounds DataFrame size, but conversion/grouping still consumes memory per chunk. If total distinct keys are enormous, the aggregation state can also grow. Use `Decimal` when financial precision matters.

## Q54. How do you choose between csv, json, parquet, and a database connector?

- CSV: simple tabular interchange, weak typing, expensive parsing.
- JSON: flexible/nested, schema drift and parsing overhead.
- Parquet: typed columnar analytics, compression and column pruning.
- Database connector: predicate/column pushdown and source transaction/consistency concerns.

**Best:** Use a format aligned with producer/consumer and replay needs. Preserve raw source where auditability matters; curate typed columnar datasets for analytical workloads.

## Q55. What is memory amplification?

The in-memory representation can be several times larger than compressed file size due to Python object headers, strings, lists/dicts, indexes, and copies. Measure RSS/peak memory; compressed CSV size is not a reliable RAM estimate.

## Q56. How do you profile Python memory?

Use process RSS metrics (e.g. psutil), `tracemalloc` for Python allocation tracing, heap/object tools when appropriate, and workload-level metrics. `tracemalloc` may not capture every native allocation made by NumPy/Pandas/third-party extensions.

## Q57. Why is reading an entire file with read() risky?

It materializes the full file in memory. Use line iteration, chunked readers, streaming decompression, or a distributed file reader. Also consider whether downstream code retains every parsed record.

## Q58. How do you handle malformed input records?

Separate structural errors (parse/schema) from business-rule failures. Preserve source ID/file/line/offset, payload, parser version, error code, and ingestion timestamp. Quarantine vs fail batch should follow data contract criticality.

## Q59. Why should you not use pickle for untrusted data?

Unpickling can execute arbitrary code. Do not load pickle from untrusted sources. Prefer safe data formats with schema validation (JSON/Parquet/Avro/Protobuf as appropriate), and secure serialization boundaries.

## Q60. How do you write output atomically?

Write to a unique temporary/staging location, validate, then publish via atomic rename or table transaction where the storage system guarantees it. Object-store rename may be copy+delete, not atomic; use table-format commits/manifests or a pointer/manifest publish protocol appropriate to the platform.

---

# Part 6 — APIs, HTTP, retries and rate limiting

## Q61. Consume a paginated REST API safely.

```python
import requests
from collections.abc import Iterator

def iter_api_pages(base_url: str, token: str) -> Iterator[dict]:
    session = requests.Session()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 500}
    url = base_url

    while url:
        response = session.get(url, headers=headers, params=params, timeout=(5, 30))
        response.raise_for_status()
        payload = response.json()

        for record in payload["data"]:
            yield record

        url = payload.get("next")
        params = None  # next may already be a complete cursor URL
```

Production additions: retry policy for transient failures, bounded page size, response schema validation, rate-limit handling, secure token sourcing, request IDs, and durable cursor checkpoint only after records are committed.

## Q62. Implement retries with exponential backoff and jitter.

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry_call(
    operation: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 20.0,
    retryable: tuple[type[Exception], ...] = (TimeoutError, ConnectionError),
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    for attempt in range(max_attempts):
        try:
            return operation()
        except retryable:
            if attempt == max_attempts - 1:
                raise
            ceiling = min(max_delay, base_delay * (2 ** attempt))
            time.sleep(random.uniform(0, ceiling))

    raise RuntimeError("Unreachable")
```

**Best:** Retry only transient failures; use full jitter to reduce synchronized retries; add total deadline, request timeout, and idempotency key. Do not retry validation/authentication failures blindly.

## Q63. What is the difference between retry, timeout, and deadline?

Timeout bounds one operation/attempt. Retry repeats a failed operation. Deadline bounds total elapsed time across attempts and waits. Without a deadline, retries can exceed the orchestration SLA.

## Q64. How do you handle HTTP 429 rate limits?

Honor `Retry-After` when provided; use bounded backoff/jitter; cap concurrency; track quota headers; coordinate limits across workers; and avoid retry storms. A local sleep in each worker may still exceed a shared account-level quota.

## Q65. How do you implement a token bucket rate limiter?

Maintain a token count replenished at rate r up to capacity B; each request consumes a token. If unavailable, wait or reject. In multi-process/distributed ingestion the bucket must be coordinated centrally or partitioned deliberately; a process-local bucket does not enforce a global API quota.

## Q66. How do you make API ingestion idempotent?

Use stable source event/record IDs, idempotency keys for writes, cursor/offset checkpoints, deterministic upsert precedence, and replay-safe batches. Persist the page/cursor and output commit relationship so a crash between target commit and checkpoint does not skip or duplicate data.

## Q67. How do you prevent pagination gaps while source records change?

Prefer cursor/continuation tokens or CDC offsets with stable ordering. Offset pagination can skip/repeat records when rows are inserted/deleted between requests. Use a fixed upper watermark/snapshot where the API supports it; persist cursors only after durable output commit; reconcile overlapping windows.

## Q68. How do you safely call an external API concurrently?

Bound concurrency; reuse sessions/connections; apply shared rate limits; use per-call timeout; collect per-record outcomes; retry transient errors; preserve input identity; use circuit breaker/backpressure. Use `asyncio` only when the HTTP client is async-compatible and the workload benefits.

## Q69. What is a circuit breaker?

It temporarily stops calls to a dependency after repeated failures, allowing recovery and preventing resource exhaustion. States are usually closed (normal), open (fail fast), and half-open (probe). It complements retries; it is not a substitute for timeout or idempotency.

## Q70. How do you handle secrets and API credentials?

Use a managed secret store/environment injection/identity federation; least privilege and short-lived credentials; rotation; never commit or log secrets; scope tokens to required APIs; audit use. Environment variables are a delivery mechanism, not by themselves a full secret-management solution.

---

# Part 7 — Concurrency and asynchronous programming

## Q71. Threading vs multiprocessing vs asyncio?

| Model | Best fit | Main costs |
|---|---|---|
| Threads | Blocking I/O with sync libraries | Shared state, locks, GIL for Python CPU work |
| Processes | CPU-bound Python work | Process startup, IPC, memory duplication |
| asyncio | Many async I/O tasks | Async-compatible libraries, cancellation/state complexity |
| Distributed engine | Large-scale parallel transformations | Cluster operations, serialization, shuffle, cost |

**Best:** Identify the bottleneck first. Do not select concurrency model based on fashion.

## Q72. Explain the GIL and modern free-threaded Python.

Traditional GIL-enabled CPython allows only one thread at a time to execute Python bytecode while holding the GIL, although blocking I/O and some native extensions release it. Free-threaded CPython builds allow parallel Python execution with compatibility/performance trade-offs. Python 3.13 introduced the optional free-threaded build; later releases continue evolving it.

**Interview answer:** Check exact interpreter build and extension compatibility. Do not say “Python can never run threads in parallel” without qualification.

## Q73. Use ThreadPoolExecutor for bounded API I/O.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_order(order_id: int) -> dict:
    # Use a real HTTP client with timeouts and retry policy.
    return {"order_id": order_id, "status": "ok"}

order_ids = [101, 102, 104, 105]

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch_order, oid): oid for oid in order_ids}
    for future in as_completed(futures):
        order_id = futures[future]
        try:
            result = future.result()
        except Exception:
            logging.exception("Fetch failed for order_id=%s", order_id)
            raise
        else:
            process_result(result)
```

**Best:** Bounded workers and bounded submission for very large input. A list of millions of futures can itself exhaust memory. Consider producer/consumer queues or a semaphore.

## Q74. Use ProcessPoolExecutor for CPU-heavy pure Python work.

```python
from concurrent.futures import ProcessPoolExecutor

def compute_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

payloads = [b"order-101", b"order-102"]

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as pool:
        hashes = list(pool.map(compute_hash, payloads, chunksize=100))
```

Under spawn-based process creation, functions/arguments need to be picklable and code should be protected by the main guard. Large payload transfer can make multiprocessing slower; batch inputs or use shared memory/native libraries where appropriate.

## Q75. Explain asyncio and write a simple concurrent pattern.

```python
import asyncio

async def fetch_one(order_id: int, semaphore: asyncio.Semaphore):
    async with semaphore:
        # await an async HTTP client call with timeout
        await asyncio.sleep(0)
        return {"order_id": order_id, "status": "ok"}

async def main():
    sem = asyncio.Semaphore(20)
    tasks = [fetch_one(oid, sem) for oid in [101, 102, 104, 105]]
    return await asyncio.gather(*tasks, return_exceptions=True)

# asyncio.run(main())
```

This bounds active calls but still creates one coroutine per input. For millions of tasks, use a bounded producer/worker queue.

## Q76. What is backpressure?

A mechanism that prevents producers from overwhelming slower consumers. Use bounded queues, flow control, concurrency limits, and source pause/cursor behavior. Without backpressure, queue/memory grows until failures occur.

## Q77. What is a race condition?

A result depends on timing/interleaving of concurrent operations on shared state. Use immutability, locks, queues, transactions, atomic operations, or partition ownership. Do not assume the GIL makes multi-step business operations atomic.

## Q78. Lock vs semaphore vs queue?

- Lock: one owner at a time for a critical section.
- Semaphore: limits concurrent access to a resource.
- Queue: transfers work safely between producers/consumers and can provide backpressure.

Choose the narrowest synchronization primitive that expresses the requirement.

## Q79. How do you avoid deadlocks?

Use a consistent lock acquisition order, small critical sections, timeouts where valid, avoid waiting on a future while holding a lock needed by that future, and minimize nested locks. Capture thread dumps and wait graphs when diagnosing.

## Q80. How do you decide whether to parallelize?

Measure sequential baseline, identify CPU/I/O bottleneck, estimate parallelizable fraction, account for coordination/serialization/remote quotas, then benchmark. Amdahl's Law limits speedup when significant work remains serial.

---

# Part 8 — Pandas and single-machine analytics

## Q81. When should you use Pandas vs Python lists vs SQL vs Spark?

- Python collections: bounded, application-level records/control logic.
- Pandas: in-memory columnar analysis where data fits with headroom.
- SQL/warehouse: set-based operations close to stored data.
- Spark: distributed transformations for workloads that justify a cluster.

**Best:** Push filtering/aggregation to the system holding the data when it reduces transfer. Avoid moving multi-terabyte datasets into Pandas.

## Q82. Read only required columns and assign dtypes.

```python
import pandas as pd

df = pd.read_csv(
    "orders.csv",
    usecols=["order_id", "customer_id", "status", "currency", "total"],
    dtype={
        "order_id": "int64",
        "customer_id": "int64",
        "status": "string",
        "currency": "string",
        "total": "string",
    },
)
```

**Best:** Use `usecols` and explicit dtypes; parse money with Decimal or scaled integer minor units based on the financial contract. Measure memory usage rather than relying on file size.

## Q83. Why is vectorization faster than iterrows?

Vectorized Pandas/NumPy operations execute in optimized native loops and reduce Python interpreter overhead. `iterrows()` constructs row Series repeatedly and can coerce dtypes. Prefer boolean masks, groupby, merge, and vectorized string/date operations.

## Q84. Replace row-wise apply with vectorized operations.

```python
df["is_completed"] = df["status"].eq("COMPLETED")
df["normalized_email"] = df["email"].str.strip().str.lower()
```

Use `apply` only when the operation is genuinely not expressible with vectorized APIs and performance is acceptable.

## Q85. Deduplicate Pandas records by latest update.

```python
latest = (
    df.sort_values(
        ["customer_id", "source_sequence", "ingested_at"],
        ascending=[True, False, False],
        kind="stable",
    )
    .drop_duplicates("customer_id", keep="first")
)
```

The winner policy is explicit and deterministic. Do not rely on input row order or `drop_duplicates` alone when version precedence matters.

## Q86. Merge order totals to customer metadata safely.

```python
enriched = orders_df.merge(
    customers_df[["customer_id", "country"]],
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)
```

Pandas `validate` is useful for asserting join cardinality. Inspect `_merge` for unmatched customer IDs. In other tools, add explicit uniqueness checks.

## Q87. Explain groupby aggregation vs transform.

- `agg`: reduces each group to one or more summary rows.
- `transform`: returns a result aligned to original row index/shape.

Use `transform("mean")` when comparing each order to its customer's average; use `agg` for customer summary output.

## Q88. How do you reduce Pandas memory usage?

Select required columns; use suitable numeric widths only after range validation; use categorical for repeated low-cardinality strings; parse efficient datetimes; avoid copies; process chunks; use Arrow-backed dtypes where compatible; monitor peak RSS. Do not downcast identifiers blindly if precision can be lost.

## Q89. What are nullable dtypes in Pandas?

Pandas nullable integer/boolean/string types preserve missing values without forcing float/object in some cases. Be aware of `pd.NA` three-valued behavior; comparisons can produce nullable results. Test masks with missing values explicitly.

## Q90. Why can object dtype be expensive?

It often stores Python object references with per-object overhead and may prevent efficient vectorized/native operations. Prefer typed numeric, datetime, string, categorical, or Arrow-backed representations when appropriate.

---

# Part 9 — Reliability, testing and observability

## Q91. Design a production logging strategy.

Use Python `logging` with structured fields: run_id, dataset, source, target, batch_id, rows_read/written/rejected, duration, attempt, error_class, and code version. Avoid secrets/PII in logs. Use consistent correlation IDs across pipeline components.

## Q92. How do you create a custom exception hierarchy?

```python
class PipelineError(Exception):
    """Base error for pipeline failures."""

class SourceUnavailable(PipelineError):
    pass

class DataContractViolation(PipelineError):
    pass

class ReconciliationFailure(PipelineError):
    pass
```

Catch at boundaries based on recovery policy. Do not catch a base exception if you cannot decide what recovery action is safe.

## Q93. What makes a retry safe?

The operation must be idempotent or protected by idempotency key/transaction; retries must be limited to transient errors; use timeout, backoff, jitter, deadline, and observable attempt state. Retrying a non-idempotent payment/API create request can duplicate side effects.

## Q94. How do you design idempotent file ingestion?

Identify files by immutable object version/ETag plus source identity; record ingestion ledger; write output to deterministic batch/partition target or transactional table; commit manifest/state atomically; make retries detect completed commit; retain raw data and support replay.

## Q95. What is exactly-once processing in a Python ETL job?

Exactly-once effect is a system property, not a Python decorator. It requires coordination of source progress and sink commit, or idempotent deduplication at the sink. Otherwise use at-least-once delivery with idempotent writes and reconciliation.

## Q96. Unit test a transformation without external dependencies.

```python
from decimal import Decimal

def net_order_value(order: dict) -> Decimal:
    if order["status"] != "COMPLETED":
        return Decimal("0.00")
    return Decimal(order["total"])

def test_net_order_value():
    row = {"status": "COMPLETED", "total": "1200.00"}
    assert net_order_value(row) == Decimal("1200.00")
```

Keep pure business logic separate from I/O. Add tests for invalid input, NULLs, duplicates, currency, and boundaries.

## Q97. Explain mock vs stub vs fake.

- Stub: returns controlled responses.
- Mock: verifies interactions/calls.
- Fake: lightweight working implementation (e.g. in-memory repository).

Use mocks for external boundaries and failure injection, but avoid asserting internal implementation details that make tests brittle.

## Q98. What is property-based testing?

Instead of testing only examples, generate many inputs and assert invariants (e.g. normalization is idempotent; dedupe output has unique keys; parsing/serialization round-trips). Tools such as Hypothesis can discover edge cases that example tests miss.

## Q99. How do you test data pipelines?

Test pure transformations; integration-test connectors/storage; contract-test schemas; test retry and partial failure; replay duplicate inputs; verify source-target reconciliation; performance-test representative volume/skew; and test disaster recovery/restore.

## Q100. What is a data contract?

A versioned agreement describing schema, semantics, keys/grain, quality, freshness, ownership, privacy, compatibility, and change process. JSON schema alone is not a complete business data contract.

## Q101. How do you handle schema drift?

Detect before transformation; classify additive/breaking; version contracts; preserve raw payload/schema version; quarantine incompatible records; coordinate consumer migration; expose schema-change alerts and lineage impact.

## Q102. What is a dead-letter queue?

A durable destination for records/messages that cannot be processed under current rules. Store original payload, key, failure reason, source offset, attempt count, and schema version. Define retention, access, replay, and ownership.

## Q103. How do you build a data-quality gate?

Validate schema, completeness, uniqueness, ranges, referential integrity, freshness, volume anomalies, and source-target controls. Publish only if critical rules pass; warnings/partial results need an explicit contract. Every rule needs owner, severity, alert, and remediation path.

## Q104. How do you make reconciliation scalable?

Start with schema, counts, distinct keys, partition controls, sums/min/max, and anti-joins; drill to row differences for affected partitions. Use canonical hashes as screening only after defining serialization and null semantics. Store run evidence and unmatched records rather than collecting everything into Python.

---

# Part 10 — Database and external-system engineering

## Q105. Why are connection pools important?

They reuse bounded database connections, avoid connection storms, and apply resource limits. Pool sizing must respect database max connections, application worker count, transaction duration, and workload concurrency.

## Q106. Why are row-by-row database inserts usually slow?

Each call adds protocol/round-trip/transaction overhead. Prefer parameterized batch inserts, COPY/bulk load, staging + merge, or warehouse-native ingestion. Tune batch size and commit boundaries; keep writes restartable.

## Q107. How do you avoid SQL injection?

Use parameterized statements for values and allowlists for dynamic identifiers (table/schema names generally cannot be bound as values). Never concatenate untrusted values into SQL.

## Q108. Explain transaction boundaries.

A transaction groups operations with ACID properties as supported by the database. Choose scope carefully: giant transactions may hold locks/logs; tiny transactions may add overhead and create partial completion. Record durable batch state and use idempotent recovery.

## Q109. How do you handle connection failure mid-batch?

Know whether transaction committed. Use stable batch ID, source offset, idempotent staging/merge, and reconciliation. Do not blindly replay unknown non-idempotent writes.

## Q110. How do you handle secrets in Python pipelines?

Use managed secrets/identity federation/short-lived tokens; least privilege; rotate; never hardcode/log. Local `.env` is for development, not a production security system.

---

# Part 11 — Architecture and Staff/Principal scenarios

## Q111. Design a metadata-driven Python ETL framework.

Metadata declares source, target, schema, key, incremental cursor, transformations, quality rules, owner, SLA, PII, retry, and retention. A typed config validator checks it before execution. Reusable connectors/adapters and explicit transformation registry keep code testable.

**Avoid:** giant `eval`/reflection framework where business logic is hidden in arbitrary strings. Keep an escape hatch for specialized workloads and version metadata.

## Q112. Design a source-to-target reconciliation framework.

Layers: schema/type check → row/key counts → duplicate/orphan checks → partition-level aggregates → source-only/target-only keys → null-safe row diffs → optional canonical hashes → exception store → publish gate. Persist run ID, batch, rule, expected/actual, severity, evidence, owner.

**Staff:** Reusable engine and contracts. **Principal:** Reconciliation SLOs, domain ownership, audit/financial controls, and exception governance.

## Q113. Design a reusable connector framework.

Define stable interfaces (read/write/health/checkpoint/schema), connector capabilities, typed configuration, common retry/timeout/metrics, secrets integration, and contract tests. Keep connector-specific pagination/transaction semantics explicit; do not pretend all sources support the same guarantees.

## Q114. How would you process 100 GB of CSV?

First challenge whether CSV and pure Python are necessary. If single-machine is viable, chunk with explicit dtypes/schema, vectorize, aggregate incrementally, and monitor RSS. If the operation is join-heavy/distributed or exceeds single-host capacity, push to SQL/Spark/Polars/DuckDB depending on workload. Do not claim chunking makes every global operation bounded-memory.

## Q115. How do you design a backfill?

Use immutable source range/snapshot, bounded batches, deterministic ordering, idempotent output, checkpoints, overlap precedence with live traffic, partition-level reconciliation, pause/resume, and consumer-visible completeness. Backfill must not silently overwrite newer CDC state.

## Q116. A pipeline meets its runtime SLA but data is wrong. What do you do?

Freeze run/output; reproduce from immutable input; confirm metric contract and grain; compare source and target at partition/key level; identify first divergent transform; correct logic; replay impacted scope; reconcile; add regression test/alert; communicate consumer impact. Job success is not data correctness.

## Q117. How do you decide between Python, Pandas, SQL, and Spark?

Assess data size/cardinality, memory headroom, operation shape, latency, concurrency, ecosystem, and operational cost. Use SQL where data resides; Pandas for bounded in-memory analytics; Python for orchestration/API/control logic; Spark for distributed transformations. Prefer the simplest system that meets SLO and growth needs.

## Q118. How do you lead a Python library used by many data teams?

Define API/versioning, semantic compatibility, typed contracts, observability, docs, tests, deprecation policy, release automation, security scanning, support ownership, and adoption metrics. Keep core stable, plugins explicit, and breaking changes managed.

## Q119. A 1,000-worker API ingestion job exceeds provider quota. What do you do?

Implement shared quota coordination, bounded concurrency, token bucket/leaky bucket, Retry-After honoring, jitter, request prioritization, circuit breaker, and adaptive throughput. Per-process limits are insufficient if quota is account-wide. Consider source-side export/bulk APIs instead of per-record calls.

## Q120. Your Python service leaks memory after several hours. Debug it.

Reproduce with representative load; monitor RSS and Python allocations; use tracemalloc/object profiling; inspect caches, references, queue growth, unclosed resources, native allocations, and DataFrame copies; add bounded queues/eviction; verify memory returns after workload. Distinguish a leak from allocator-retained memory/high-water behavior.

## Q121. A dependency upgrade breaks a pipeline. How do you prevent recurrence?

Lock dependencies; maintain compatibility matrix; build reproducible artifacts; unit/integration/contract tests; canary; compare row counts/schema/business controls/runtime; pin rollback artifact. Staff/Principal standardize dependency governance and ownership of shared runtime.

## Q122. How do you design a multi-tenant Python data service?

Tenant identity established from authenticated context, tenant-aware storage/query boundaries, authorization on every request, per-tenant quotas, secret isolation, audit, noisy-neighbor control, and cross-tenant tests. Do not trust a caller-supplied tenant_id without authorization.

## Q123. How do you handle PII and privacy requests?

Data classification, least privilege, tokenization/masking, retention schedules, access logs, safe diagnostics, approved deletion/anonymization, propagation to derived systems, and restore-time reapplication. Python `del` only removes a local reference; it is not a data deletion guarantee.

## Q124. How would you design operational SLOs for a Python ingestion platform?

Define freshness, completeness, correctness, availability, recovery time, and consumer impact. Measure latency distributions, success/partial rates, retries, backlogs, rejected rows, reconciliation mismatch, and restore tests. Tie alerts to an owner/runbook/error budget.

## Q125. How do you prioritize optimization across multiple pipelines?

Rank by business criticality, incident frequency, cost, SLA breaches, user impact, and engineering effort. Establish baselines; optimize dominant workloads; canary; prove correctness and cost improvement; publish reusable patterns. Avoid optimizing a low-impact microbenchmark while core data products miss SLAs.

---

# Part 12 — Modern Python and version awareness

## Q126. Which Python version is current, and what should senior engineers know?

As of November 3, 2026, **Python 3.15 is the latest stable feature release**, first released October 9, 2026. Python 3.14 and 3.13 remain supported maintenance branches; Python 3.16 is in development. Production runtimes may deliberately stay on earlier supported versions because libraries, vendors, and deployment images have their own compatibility matrix.

**Best interview response:** Know important release changes, but state the version used in the actual production environment. Do not upgrade a data platform only because a new interpreter was released.

Official sources:
- https://www.python.org/doc/versions/
- https://docs.python.org/3.15/whatsnew/3.15.html

## Q127. What are free-threaded CPython builds?

Free-threaded builds allow Python threads to execute Python code in parallel without the traditional global interpreter lock, with compatibility and performance trade-offs. This capability was introduced as an optional build in Python 3.13 and continues to evolve.

**Caveats:** Some C extensions may not support free-threaded execution or may re-enable the GIL; thread safety of application/shared state still matters; single-thread performance can differ.

**Best:** Benchmark the actual workload and package ecosystem. Do not assume free-threading makes every threaded ETL faster.

Reference: https://docs.python.org/3.15/howto/free-threading-python.html

## Q128. What are lazy imports in newer Python?

Python 3.15 introduces lazy-import-related language/runtime support. Lazy imports can defer module loading and reduce startup work in suitable applications, but can move import errors/side effects to later execution points and complicate debugging.

**Best:** Treat it as a startup optimization, not an ETL throughput solution. Verify import semantics and compatibility before adopting in production.

Reference: https://docs.python.org/3.15/whatsnew/3.15.html

## Q129. What is a sentinel value?

A sentinel is a unique marker representing a state distinct from valid domain values (including None where None is valid data).

```python
MISSING = object()

def read_config(config, key):
    value = config.get(key, MISSING)
    if value is MISSING:
        raise KeyError(key)
    return value
```

A unique object avoids confusing absent keys with present keys whose value is None. Newer Python releases may offer built-in sentinel facilities; use based on runtime compatibility.

## Q130. Why do type hints matter at senior level?

Type hints support static checking, IDEs, API clarity, and safer refactoring. They do not validate runtime input by themselves. Use mypy/pyright or equivalent in CI for static guarantees, and runtime validation at untrusted boundaries.

---

# Part 13 — Alternatives and design decision tables

## 13.1 Choose the right execution tool

| Requirement | Good starting point | Why | Watch out |
|---|---|---|---|
| Small in-memory lookup | dict/set | Simple, fast average lookup | Memory grows with unique keys |
| Huge line-oriented file | iterator/generator | Bounded read buffer | Downstream may still accumulate |
| CSV analysis fits RAM | Pandas | Convenient typed/vectorized operations | Memory amplification |
| Database-resident data | SQL | Push computation to data | Network/transaction semantics |
| Large distributed joins | Spark | Distributed shuffle/parallel compute | Cluster and shuffle overhead |
| Many async HTTP requests | asyncio client | Efficient I/O multiplexing | Async library and backpressure |
| Sync I/O calls | ThreadPoolExecutor | Simple bounded concurrency | API quota and thread safety |
| CPU-heavy pure Python | ProcessPoolExecutor | Separate processes/cores | Serialization/startup overhead |

## 13.2 Choose retry strategy

| Error | Retry? | Typical handling |
|---|---|---|
| Connect timeout | Usually | Bounded retry/backoff |
| Temporary 5xx | Usually | Backoff/jitter |
| HTTP 429 | Yes, policy-aware | Honor Retry-After/global quota |
| Invalid schema | No blind retry | Quarantine/fail contract |
| Authentication 401/403 | Usually no | Refresh/repair credentials, alert |
| Unique constraint violation | Depends | Idempotency/reconciliation |
| Unknown commit outcome | Do not blindly repeat | Inspect batch/transaction state |

## 13.3 Code review checklist

- [ ] Clear function/API contract and type hints
- [ ] No mutable default arguments
- [ ] No unbounded file/DataFrame materialization
- [ ] Decimal/timezone semantics are explicit
- [ ] Exceptions are observable and re-raised correctly
- [ ] Retry only transient failures
- [ ] Timeout and total deadline exist
- [ ] Idempotency for external side effects
- [ ] Concurrency is bounded and has backpressure
- [ ] Secrets and PII do not leak
- [ ] Unit, integration, contract and failure tests
- [ ] Metrics, logs, run IDs and runbooks
- [ ] Dependencies are pinned and reproducible
- [ ] Performance measured on representative input

---

# Part 14 — 50 hands-on coding drills

Solve from a blank editor using the same e-commerce data:

1. Count completed orders per customer.
2. Find duplicate order IDs.
3. Return all duplicate records.
4. Keep latest CDC version per order.
5. Top 3 customer spenders by currency.
6. Implement Top K with heap.
7. First non-repeating character in a status string.
8. Group orders by currency without storing unnecessary rows.
9. Flatten nested item lists.
10. Find common product IDs in two extracts.
11. Merge dictionaries with explicit conflict policy.
12. Second-highest distinct order amount in one pass.
13. Longest completed-order streak.
14. Sliding-window maximum of order values.
15. Longest substring without repeated event names.
16. Implement bounded LRU cache.
17. Implement bounded producer-consumer queue.
18. Priority queue for retry jobs.
19. Stream a large JSONL file.
20. Stream a large CSV with schema checks.
21. Chunked Pandas aggregation by currency.
22. Quarantine malformed JSON lines.
23. Validate required columns/types.
24. Parse currency safely with Decimal.
25. Paginate a REST API.
26. Implement retry with exponential backoff and jitter.
27. Honor HTTP Retry-After.
28. Implement token bucket rate limiter.
29. Use ThreadPoolExecutor for bounded I/O.
30. Use ProcessPoolExecutor for CPU tasks.
31. Use asyncio semaphore to bound requests.
32. Implement a circuit breaker.
33. Implement a context manager for a resource.
34. Write a timing decorator.
35. Unit-test order normalization.
36. Property-test deduplication idempotence.
37. Reconcile source and target keys.
38. Reconcile source/target totals by date/currency.
39. Use Pandas merge validation to enforce many-to-one.
40. Replace iterrows with vectorized Pandas logic.
41. Write output atomically using a staging protocol.
42. Implement idempotent API ingestion with durable cursor.
43. Design dead-letter record format.
44. Build metadata validation for an ETL config.
45. Implement safe SQL parameterization.
46. Design database batch insert and checkpoint.
47. Profile a memory growth issue.
48. Build a typed connector interface.
49. Design a multi-tenant API ingestion service.
50. Design an SLO and incident dashboard for the pipeline.

---

# Part 15 — Interview communication framework

For every non-trivial Python question:

1. Clarify the contract and input boundaries.
2. State algorithm and data structure.
3. Give time and space complexity.
4. Write clean code and handle edge cases.
5. Discuss bounded memory and streaming.
6. Discuss concurrency and external quotas.
7. Explain retries, idempotency, and partial commits.
8. Add tests and observability.
9. Compare alternative tools (Python/Pandas/SQL/Spark).
10. State what changes at larger scale and what operational owner is needed.

Strong statements when backed by reasoning:

- “Before selecting a concurrency model, I identify whether this is CPU-, I/O-, memory-, or database-bound.”
- “A generator bounds materialization only if downstream code also avoids accumulation.”
- “Retry is safe only when the operation is idempotent or protected by an idempotency key.”
- “I will use Decimal or scaled integers for financial values.”
- “A successful process exit does not prove the dataset is complete or correct.”
- “For large data, Python should orchestrate the right compute engine rather than force all transformations into one process.”
- “A process-local rate limiter cannot enforce an account-wide API quota.”
- “I will validate the source/sink commit relationship before replaying an uncertain batch.”

---

# Part 16 — What interviewers evaluate at ₹70+ LPA level

| Signal | Weak | Strong |
|---|---|---|
| Python fundamentals | Memorized definitions | Object model, iteration, typing, error semantics |
| Coding | Happy path | Correctness, complexity, edge cases, clarity |
| Performance | “Use multiprocessing” | Profile, identify bottleneck, choose execution model |
| Data Engineering | Script that loads data | Streaming, idempotency, checkpoint, reconciliation |
| Reliability | Retry all exceptions | Classified failures, deadlines, safe replay |
| Architecture | One Python file | Contracts, modularity, ownership, security, SLOs |
| Leadership | Solves alone | Reusable standards, cross-team influence, mentoring |
| Business judgment | More code | Correct tool and risk/cost trade-off |

**Lead:** “I will process the input in bounded chunks, use Decimal for monetary fields, validate records, and make each batch retry-safe.”

**Staff:** “I will turn this into a reusable ingestion/reconciliation library with explicit contracts, idempotent checkpoints, bounded concurrency, and operational metrics.”

**Principal:** “I will align domain owners on data contracts and SLOs, establish security and replay standards, choose the right execution platform, and govern cost, adoption, and exceptions across teams.”

---

# Official references

- Python documentation/version index: https://www.python.org/doc/versions/
- Python 3.15 What's New: https://docs.python.org/3.15/whatsnew/3.15.html
- Python language reference: https://docs.python.org/3/reference/
- Python data model: https://docs.python.org/3/reference/datamodel.html
- Python typing: https://docs.python.org/3/library/typing.html
- Python concurrent.futures: https://docs.python.org/3/library/concurrent.futures.html
- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Python multiprocessing: https://docs.python.org/3/library/multiprocessing.html
- Python free-threading: https://docs.python.org/3.15/howto/free-threading-python.html
- Python decimal: https://docs.python.org/3/library/decimal.html
- Python logging: https://docs.python.org/3/library/logging.html
- Pandas user guide: https://pandas.pydata.org/docs/user_guide/

---

# END OF TOPIC 04 — PYTHON

This chapter uses one connected e-commerce domain throughout. Extend these same records with realistic duplicate, null, late, malformed, and high-volume edge cases instead of switching to unrelated toy schemas.