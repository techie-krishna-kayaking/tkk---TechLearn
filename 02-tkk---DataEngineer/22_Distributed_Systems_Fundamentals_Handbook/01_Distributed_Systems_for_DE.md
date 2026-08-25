# 22 — Distributed Systems Fundamentals for Data Engineers

> Every strong system-design answer rests on distributed-systems fundamentals. When you
> say "I'll partition by user_id" or "at-least-once with idempotent writes," the
> interviewer hears *"this person understands the machinery."* This handbook gives you the
> vocabulary and mental models behind Handbooks 06, 09, 12, and 19. Target: 80–120 LPA.

---

## 🎯 SECTION 1: Why This Matters

Data systems ARE distributed systems: Spark, Kafka, Cassandra, Snowflake, S3 all make the
same core trade-offs. Knowing them lets you *derive* the right design instead of memorizing
one. Interviewers deliberately push: *"What happens if that node dies mid-write?"*

---

## ⚖️ SECTION 2: CAP Theorem (state it precisely)

In the presence of a **network Partition (P)**, a distributed system must choose between
**Consistency (C)** and **Availability (A)**. You cannot have all three *during* a partition.

- **CP** (consistency over availability): reject/block on partition to stay correct —
  e.g. HBase, ZooKeeper, traditional RDBMS. *Banking, inventory.*
- **AP** (availability over consistency): keep serving, reconcile later (eventual
  consistency) — e.g. Cassandra, DynamoDB (tunable), Riak. *Feeds, carts, telemetry.*

**Nuance to sound senior:** CAP is only about behavior *during a partition*; the rest of
the time you also trade **latency vs consistency** — that's **PACELC** (*if Partition then
A-or-C, Else Latency-or-Consistency*). Cassandra = PA/EL, a strict RDBMS = PC/EC.

---

## 🔄 SECTION 3: Consistency Models

| Model | Guarantee | Example |
|---|---|---|
| **Strong / Linearizable** | Every read sees the latest write | Spanner, single-leader RDBMS |
| **Sequential** | All see ops in the same order | — |
| **Causal** | Causally related ops seen in order | collaborative apps |
| **Read-your-writes** | You see your own writes | session guarantees |
| **Eventual** | Replicas converge given no new writes | DynamoDB (default), S3 historically |

- **Tunable consistency (Dynamo-style)**: read/write quorums with `R + W > N` gives
  strong-ish reads; `R + W ≤ N` favors availability/latency. (N=replicas, W=write acks,
  R=read responses.)
- **S3 note:** now provides **strong read-after-write** consistency for objects.

---

## 🧩 SECTION 4: Partitioning / Sharding (core DE skill)

Split data across nodes so it scales horizontally. **Choosing the partition key is the
single most important design decision** for Spark, Kafka, and any warehouse.

**Strategies:**
- **Hash partitioning**: `hash(key) % N` → even distribution, but range queries hit all
  nodes; adding nodes reshuffles a lot (fix with **consistent hashing**).
- **Range partitioning**: contiguous ranges (dates) → great for range scans/pruning, but
  prone to **hotspots** (today's data, sequential IDs).
- **Round-robin**: even load, no locality — for pure parallelism.

**Consistent hashing** (Cassandra, Dynamo): keys and nodes on a hash ring; adding/removing
a node moves only ~1/N of keys, not everything. **Virtual nodes** smooth out imbalance.

**Data skew** = the DE-specific killer: one key (a whale user, NULL, a hot product)
dominates a partition → one slow task/reducer stalls the whole job. **Fixes:** salting
(add a random suffix to hot keys), separate hot-key handling, AQE skew join (Spark),
pre-aggregation, better key choice.

---

## 📑 SECTION 5: Replication & Fault Tolerance

- **Why replicate:** durability + availability + read scaling.
- **Leader–follower (single-leader)**: writes to leader, replicate to followers; simple,
  strong on leader; failover needed if leader dies. (Kafka partition leader, RDBMS.)
- **Multi-leader / leaderless**: higher availability, but **conflict resolution** needed
  (last-write-wins, vector clocks, CRDTs).
- **Sync vs async replication**: sync = no data loss but slower/less available; async =
  fast but risk of losing un-replicated writes on failover.
- **Quorum:** require acks from a majority to tolerate `f` failures with `2f+1` nodes.
- **Kafka specifics:** replication factor, **ISR (in-sync replicas)**, `acks=all` +
  `min.insync.replicas` for durability; leader election on broker failure.

---

## 🗳️ SECTION 6: Consensus (know the names + purpose)

Getting nodes to agree despite failures underlies leader election, metadata, and exactly-once.
- **Paxos / Raft**: consensus protocols; Raft is the understandable one (leader election +
  replicated log). Used by etcd, Consul, CockroachDB.
- **ZooKeeper (ZAB)**: coordination/metadata; historically Kafka's controller/metadata
  (now **KRaft** — Kafka's own Raft — removes the ZooKeeper dependency).
- **Two-phase commit (2PC)**: atomic commit across systems; blocking if coordinator dies —
  why distributed transactions are avoided at scale (prefer sagas/idempotency).

---

## 📨 SECTION 7: Delivery Semantics & Idempotency (huge in DE)

| Semantic | Meaning | Cost |
|---|---|---|
| **At-most-once** | May lose, never duplicates | fire-and-forget |
| **At-least-once** | Never loses, may duplicate | **default**; needs dedupe |
| **Exactly-once** | No loss, no dup (effectively) | expensive, bounded scope |

**The senior answer:** *"True exactly-once across systems is very hard, so I aim for
**at-least-once delivery + idempotent processing**, which gives effectively-once results."*

**Idempotency techniques:**
- **Upsert/MERGE** on a natural key (rerun-safe).
- **Overwrite partition by run date** (`INSERT OVERWRITE` the day) so a rerun replaces, not
  appends.
- **Deduplicate** with a unique event id + a dedupe window / transactional sink.
- **Kafka exactly-once**: idempotent producer (`enable.idempotence`) + transactions
  (`transactional.id`) + `read_committed` consumer, within the Kafka→Kafka boundary.
- **Spark Structured Streaming**: checkpoint + idempotent/exactly-once sinks (Delta) via
  the transaction log.

---

## ⏱️ SECTION 8: Time, Ordering & Watermarks (streaming)

- **Event time** (when it happened) vs **processing time** (when we saw it). Always prefer
  **event time** for correctness.
- **Out-of-order / late data** is normal; a **watermark** = "I won't wait for events older
  than T" → bounds state and lets windows finalize.
- **Windowing**: tumbling (fixed, non-overlapping), sliding (overlapping), session (gap-based).
- **Logical clocks**: **Lamport clocks** (ordering) and **vector clocks** (detect
  concurrency/causality) — name-drop when discussing multi-leader conflict resolution.

---

## 🌊 SECTION 9: Backpressure, Flow Control & Load

- **Backpressure**: when a consumer can't keep up, signal upstream to slow down instead of
  OOM-ing. Kafka handles this naturally (pull-based, consumer lag); reactive/streaming
  frameworks propagate it.
- **Consumer lag** is the key streaming health metric → autoscale on it (KEDA, Handbook 21).
- **Load shedding / rate limiting / bulkheads / circuit breakers** protect systems under
  overload.

---

## 🛡️ SECTION 10: Failure, Retries & Resilience

- **Retries with exponential backoff + jitter** (avoid thundering herd).
- **Idempotency keys** so retries don't double-apply.
- **Dead-letter queue (DLQ)** for poison messages; alert + replay after fix.
- **Timeouts everywhere**; **circuit breaker** to stop hammering a failing dependency.
- **Graceful degradation**: serve slightly stale/partial data rather than fail hard.
- **Checkpointing** for recovery (Spark/Flink resume from last committed offset/state).

---

## ❓ SECTION 11: Rapid-Fire Q&A

**Q: Explain CAP with a data example.** During a network partition, a payments store picks
CP (reject writes to stay correct); a social feed picks AP (serve stale, reconcile later).

**Q: How do you pick a partition key?** High cardinality, even distribution, aligned with
query/join patterns, avoids hotspots. Wrong choice → skew and cross-partition scans.

**Q: How do you handle data skew in Spark?** Salt hot keys, enable AQE skew join,
broadcast the small side, pre-aggregate, or isolate the hot key.

**Q: How do you achieve exactly-once?** Usually at-least-once + idempotent writes
(MERGE/overwrite-by-partition/dedupe); within Kafka, idempotent producer + transactions.

**Q: What's a watermark?** A threshold on event time bounding how long you wait for late
data, so windows can emit and state is bounded.

**Q: Consistent hashing — why?** Adding/removing a node moves only ~1/N of keys (vs a full
reshuffle with `mod N`), enabling smooth scaling; virtual nodes balance load.

**Q: R + W > N — what does it give you?** Overlapping read/write quorums guarantee a read
sees the latest acknowledged write → strong consistency with tunable availability.

**Q: Why avoid distributed transactions (2PC)?** Blocking on coordinator failure, poor
scalability; prefer idempotency + sagas + eventual consistency.

**Q: Kafka durability config?** `acks=all` + `min.insync.replicas ≥ 2` + replication
factor ≥ 3, so a broker loss doesn't lose acknowledged data.

---

## ✅ Mastery Checklist
- [ ] State CAP precisely (and PACELC) with data examples
- [ ] Explain consistency models + quorum (R + W > N)
- [ ] Choose partition keys and diagnose/fix skew
- [ ] Explain replication, ISR, and quorum-based fault tolerance
- [ ] Name Raft/Paxos/ZAB and what consensus is for
- [ ] Reason about delivery semantics + idempotency → effectively-once
- [ ] Explain event time, watermarks, and windowing
- [ ] Discuss backpressure, retries/backoff, DLQ, circuit breakers

---

## 🧪 Hands-On Practice (runnable)

Four self-checking simulations that turn theory into numbers you can see:

```bash
python3 02_Practice_Distributed_Sims.py          # stdlib only, no deps
```
Covers: consistent hashing (minimal key movement), quorum R+W>N freshness, idempotent
dedupe (at-least-once → effectively-once), and data skew + salting rebalancing.
