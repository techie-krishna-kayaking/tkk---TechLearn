"""
================================================================================
HANDBOOK 22 — RUNNABLE PRACTICE: Distributed Systems Simulations
================================================================================
Run:   python3 02_Practice_Distributed_Sims.py
Deps:  none (Python stdlib only)

Four self-checking simulations that make abstract theory concrete:
  1. Consistent hashing  — adding a node moves only ~1/N of keys
  2. Quorum consistency  — why R + W > N guarantees fresh reads
  3. Idempotent dedupe   — at-least-once delivery -> effectively-once
  4. Data skew + salting  — how salting rebalances a hot key
================================================================================
"""
import hashlib
from collections import Counter, defaultdict

# ============================================================================
# 1. CONSISTENT HASHING — minimal key movement when the cluster changes
# ============================================================================
class ConsistentHashRing:
    def __init__(self, nodes, vnodes=100):
        self.vnodes = vnodes
        self.ring = {}          # hash -> node
        self.sorted_hashes = []
        for n in nodes:
            self.add(n)

    def _h(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add(self, node):
        for i in range(self.vnodes):
            h = self._h(f"{node}#{i}")
            self.ring[h] = node
        self.sorted_hashes = sorted(self.ring)

    def get(self, key):
        h = self._h(key)
        # first vnode clockwise (binary search)
        lo, hi = 0, len(self.sorted_hashes)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.sorted_hashes[mid] < h:
                lo = mid + 1
            else:
                hi = mid
        idx = lo % len(self.sorted_hashes)
        return self.ring[self.sorted_hashes[idx]]


def naive_mod_assignment(keys, nodes):
    return {k: nodes[int(hashlib.md5(k.encode()).hexdigest(), 16) % len(nodes)]
            for k in keys}


keys = [f"user:{i}" for i in range(10_000)]

# --- Consistent hashing: 4 -> 5 nodes ---
ring4 = ConsistentHashRing(["n1", "n2", "n3", "n4"])
before = {k: ring4.get(k) for k in keys}
ring4.add("n5")
after = {k: ring4.get(k) for k in keys}
moved_ch = sum(before[k] != after[k] for k in keys)

# --- Naive mod hashing: 4 -> 5 nodes ---
b_mod = naive_mod_assignment(keys, ["n1", "n2", "n3", "n4"])
a_mod = naive_mod_assignment(keys, ["n1", "n2", "n3", "n4", "n5"])
moved_mod = sum(b_mod[k] != a_mod[k] for k in keys)

print("=== 1. CONSISTENT HASHING (add node n5 to a 4-node cluster) ===")
print(f"Consistent hashing moved: {moved_ch:5d}/{len(keys)} keys "
      f"({moved_ch/len(keys)*100:.1f}%)  ~ expected ~1/5 = 20%")
print(f"Naive  hash % N   moved: {moved_mod:5d}/{len(keys)} keys "
      f"({moved_mod/len(keys)*100:.1f}%)  ~ catastrophic reshuffle")
assert moved_ch < moved_mod          # consistent hashing moves far fewer keys
assert moved_ch / len(keys) < 0.35   # roughly ~1/N
print("[PASS] consistent hashing minimizes key movement\n")


# ============================================================================
# 2. QUORUM CONSISTENCY — R + W > N gives read-your-writes
# ============================================================================
class QuorumStore:
    """N replicas. Initial value v1 on all. A new write hits the first W
    replicas; a read queries the last R replicas and returns the newest
    version it sees. First-W and last-R overlap IFF W + R > N (pigeonhole)."""
    def __init__(self, n):
        self.n = n
        self.replicas = [(1, "v1")] * n     # all start at version 1

    def write(self, w, version, value):
        for i in range(w):                   # first W replicas
            self.replicas[i] = (version, value)

    def read(self, r):
        read_set = self.replicas[self.n - r:]  # last R replicas
        return max(read_set, key=lambda vv: vv[0])[1]


def read_sees_latest(n, w, r):
    store = QuorumStore(n)
    store.write(w, version=2, value="v2")   # newer write to first W
    return store.read(r) == "v2"            # visible only if W+R>N

print("=== 2. QUORUM (N=3): does a read always see the latest write? ===")
for (w, r) in [(1, 1), (2, 2), (3, 1), (1, 3)]:
    overlap = (w + r) > 3
    fresh = read_sees_latest(3, w, r)
    tag = "STRONG" if overlap else "stale-risk"
    print(f"W={w}, R={r}  ->  R+W>N? {str(overlap):5}  read_saw_latest={fresh}  [{tag}]")
    assert fresh == overlap             # freshness matches the R+W>N rule exactly
assert not read_sees_latest(3, 1, 1)    # W=1,R=1 CAN miss the latest write
print("[PASS] read sees latest IFF R + W > N (W=1,R=1 can go stale)\n")


# ============================================================================
# 3. IDEMPOTENT DEDUPE — at-least-once delivery becomes effectively-once
# ============================================================================
# A flaky source delivers each event at least once (some duplicated / retried).
delivered = [
    ("evt-1", 100), ("evt-2", 50), ("evt-1", 100),   # evt-1 duplicated
    ("evt-3", 25), ("evt-2", 50), ("evt-3", 25),      # more retries
]

# NON-idempotent sink: blindly sums -> WRONG (double counts)
naive_total = sum(amount for _, amount in delivered)

# Idempotent sink: MERGE/upsert keyed by event id -> correct
store = {}                       # event_id -> amount (upsert)
for eid, amount in delivered:
    store[eid] = amount          # re-applying the same key is a no-op
idempotent_total = sum(store.values())

print("=== 3. IDEMPOTENT DEDUPE (at-least-once source with retries) ===")
print(f"Naive append sink total     : {naive_total}  (WRONG - double counts)")
print(f"Idempotent upsert sink total: {idempotent_total}  (correct)")
assert idempotent_total == 175 and naive_total == 350
print("[PASS] upsert-by-key turns at-least-once into effectively-once\n")


# ============================================================================
# 4. DATA SKEW + SALTING — rebalance a hot key across reducers
# ============================================================================
# 90% of events share one hot key -> one reducer gets overloaded.
events = ["hot"] * 9000 + [f"k{i}" for i in range(1000)]
REDUCERS = 8

def reducer_of(key):
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % REDUCERS

# Without salting: the hot key all lands on ONE reducer
load_plain = Counter(reducer_of(k) for k in events)

# With salting: append a random-ish salt to spread the hot key
SALTS = 8
def salted_reducer(key, i):
    salt = i % SALTS
    return reducer_of(f"{key}#{salt}")

load_salted = Counter(salted_reducer(k, i) for i, k in enumerate(events))

def imbalance(load):
    mx, avg = max(load.values()), sum(load.values()) / REDUCERS
    return mx / avg   # 1.0 = perfectly balanced

print("=== 4. DATA SKEW + SALTING (90% of rows share one key) ===")
print(f"Max/avg reducer load WITHOUT salting: {imbalance(load_plain):.2f}x  (hotspot)")
print(f"Max/avg reducer load WITH   salting: {imbalance(load_salted):.2f}x  (balanced)")
assert imbalance(load_salted) < imbalance(load_plain)
print("[PASS] salting the hot key rebalances load across reducers\n")

print("All Handbook 22 simulations passed. ✅")
