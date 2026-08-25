# 20 — Data Quality, Governance & Observability Handbook

> At 80–120 LPA you own **trust**, not just pipelines. Senior/staff loops ask: *"A metric
> is wrong in a board deck — how did that happen and how do you prevent it?"* The answer
> is data quality, contracts, lineage, and observability. This is a top differentiator and
> is barely covered in most prep material.

---

## 🎯 SECTION 1: Why Trust Is the Product

A pipeline that runs green but ships wrong numbers is **worse** than one that fails loudly.
Senior DEs are measured on: correctness, timeliness, and the ability to **detect and
contain** bad data before it reaches stakeholders/ML.

**The 6 dimensions of data quality (name these):**
1. **Accuracy** — matches reality.
2. **Completeness** — no missing rows/columns.
3. **Consistency** — agrees across systems.
4. **Timeliness / Freshness** — arrives within SLA.
5. **Validity** — conforms to type/format/range rules.
6. **Uniqueness** — no unintended duplicates.

---

## ✅ SECTION 2: Data Quality Testing

### Layered defense
```
Schema checks → Column tests → Row/aggregate rules → Anomaly detection → Reconciliation
```

### dbt tests (most common in interviews)
```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: customer_id
        tests:
          - not_null
          - relationships: { to: ref('dim_customers'), field: customer_id }
      - name: status
        tests:
          - accepted_values: { values: ['placed','shipped','delivered','cancelled'] }
      - name: amount
        tests:
          - dbt_utils.accepted_range: { min_value: 0 }
```
`unique`, `not_null`, `relationships`, `accepted_values` catch ~90% of breakages.

### Great Expectations / Soda (declarative expectations)
```python
# Great Expectations
validator.expect_column_values_to_not_be_null("user_id")
validator.expect_column_values_to_be_between("amount", 0, 1_000_000)
validator.expect_column_values_to_be_unique("order_id")
validator.expect_table_row_count_to_be_between(1_000, 10_000_000)
```
```yaml
# Soda Checks (soda-core)
checks for fct_orders:
  - row_count > 0
  - missing_count(user_id) = 0
  - duplicate_count(order_id) = 0
  - freshness(created_at) < 2h
```

### Reconciliation (source-of-truth checks)
- Row counts source vs target; sum(amount) source vs target within tolerance.
- Financial pipelines: **penny-level** reconciliation, not just row counts.

---

## 📜 SECTION 3: Data Contracts (the modern shift-left)

A **data contract** is an enforced agreement between a **producer** (service/eng team) and
**consumers** (analytics/ML) about schema, semantics, SLAs, and ownership.

```yaml
# contract: orders.v2
owner: checkout-team
schema:
  order_id:    { type: string, required: true, unique: true }
  amount:      { type: decimal, required: true, min: 0 }
  currency:    { type: string, enum: [USD, INR, EUR] }
  created_at:  { type: timestamp, required: true }
sla:
  freshness: 15m
  availability: 99.9%
semantics:
  amount: "gross order value before refunds, in currency units"
breaking_change_policy: "new event version; 30-day deprecation"
```
- Enforced in CI and/or at ingestion (schema registry). A breaking producer change
  **fails the build**, not the board deck.
- **Interview line:** *"Contracts shift data quality LEFT — bad schema is caught at the
  source in CI, not discovered three layers downstream by a confused analyst."*

---

## 🧬 SECTION 4: Data Lineage

**What:** the map of how data flows column-by-column from source → transformation → report.
**Why:** impact analysis ("if I change this column, what breaks?"), debugging ("where did
this wrong number originate?"), compliance (where does PII live?).

- **Table & column-level lineage**: dbt exposure/docs DAG, **OpenLineage + Marquez**,
  DataHub, Amundsen, Unity Catalog, Atlan, Collibra.
- **OpenLineage** = open standard; emitters from Airflow/Spark/dbt push run-level lineage
  events to a backend (Marquez).

**Interview line:** *"Column-level lineage turns 'who owns this and what breaks?' from a
day of Slack archaeology into a 30-second graph lookup."*

---

## 🗂️ SECTION 5: Data Catalog & Discovery

- **What:** searchable inventory of datasets with schema, owner, description, freshness,
  popularity, and lineage. Tools: **DataHub, Amundsen, Unity Catalog, Glue Catalog,
  Atlan, Collibra**.
- Enables **self-serve**: consumers find and trust data without pinging the DE team.
- **Business glossary**: shared definitions ("active user") tied to physical columns.

---

## 🔐 SECTION 6: Governance, Security & Privacy

### Access control
- **RBAC** (role-based) and **ABAC** (attribute-based) — grant on roles, not individuals.
- **Column masking** & **row-level security**: analysts see hashed emails; a regional
  manager sees only their region.
- **Least privilege**, short-lived credentials, audited access.

### PII & regulation (say the right words)
- **PII/PHI** classification and tagging (tag columns as sensitive in the catalog).
- **GDPR**: right to access, **right to erasure** (delete + purge past time-travel
  retention — ties to Handbook 19), data minimization, purpose limitation.
- **CCPA / DPDP (India)** analogous obligations.
- Techniques: **tokenization, hashing, encryption at rest/in transit, differential
  privacy, k-anonymity** for analytics on sensitive data.

### The "GDPR delete on a lake" answer (a favorite)
1. `DELETE FROM table WHERE user_id = ?` (rewrites files / writes deletion vectors).
2. Propagate deletes downstream (silver/gold, backups, search indexes).
3. **Expire snapshots / VACUUM past retention** so tombstoned files are physically purged.
4. Log the erasure for audit.

---

## 🕸️ SECTION 7: Data Mesh (staff/principal talking point)

Decentralized ownership when a central DE team becomes a bottleneck. Four principles:
1. **Domain ownership** — teams own their data end-to-end.
2. **Data as a product** — discoverable, addressable, trustworthy, with SLAs.
3. **Self-serve data platform** — paved-road tooling for domains.
4. **Federated computational governance** — global standards (contracts, PII, quality)
   enforced automatically, locally applied.

**Balanced take:** *"Mesh solves org scaling, but it needs strong platform + automated
governance or it becomes chaos. I'd adopt it only past a certain org size."*

---

## 🔭 SECTION 8: Data Observability

Beyond tests — continuous monitoring of the **5 pillars**:
1. **Freshness** — is data arriving on time?
2. **Volume** — did row counts spike/drop abnormally?
3. **Schema** — did columns/types change unexpectedly (drift)?
4. **Distribution** — are values within expected ranges (null rate, cardinality, mean)?
5. **Lineage** — what's upstream/downstream of an incident?

Tools: **Monte Carlo, Bigeye, Soda, Elementary (dbt), Databand**. Approaches: threshold
rules + ML anomaly detection + SLA/SLO dashboards.

**SLA / SLO / SLI for data:** define a freshness SLO (e.g. "orders table < 30 min stale,
99.5% of days"), alert on breach, track error budget — same discipline as SRE.

**Incident response:** severity levels, on-call, **blameless postmortems**, 5-Whys root
cause (ties to Handbook 13), and a communication channel so stakeholders know when a
dashboard is *not* to be trusted.

---

## ❓ SECTION 9: Rapid-Fire Q&A

**Q: A metric is wrong in a report — how do you debug?** Use lineage to trace the column
upstream, check each layer's tests/freshness, reconcile against source, find the breaking
change, fix + add a test/contract so it can't recur.

**Q: Tests vs observability?** Tests = known rules you assert in CI/pipeline; observability
= continuous monitoring that catches *unknown/unforeseen* anomalies in prod.

**Q: How do you enforce quality without slowing everyone down?** Shift left with contracts
+ CI tests on changed models; reserve heavy checks for critical tables; tier by criticality.

**Q: How do you handle a schema change from an upstream team?** Data contract + schema
registry fails their CI on a breaking change; additive changes flow; breaking changes get
a new version + deprecation window.

**Q: What's a data SLA and how do you meet it?** A freshness/availability promise to
consumers; meet it with monitoring, retries/backfills, redundancy, and alerting on error
budget burn.

**Q: How do you prevent duplicates in a streaming pipeline?** Idempotent writes
(MERGE/upsert on a natural key), exactly-once sinks, dedupe windows (ties to Handbook 22).

---

## ✅ Mastery Checklist
- [ ] Name the 6 quality dimensions and the 5 observability pillars
- [ ] Write dbt / GE / Soda tests from memory
- [ ] Explain data contracts and shift-left enforcement in CI
- [ ] Explain table + column lineage and OpenLineage
- [ ] Answer "GDPR delete on a lakehouse" end-to-end
- [ ] Discuss RBAC, masking, tokenization, PII tagging
- [ ] Give a balanced data-mesh opinion with trade-offs
- [ ] Define a data SLO and an incident-response flow

---

## 🧪 Hands-On Practice (runnable)

A mini expectation engine that gates a publish — passes a clean batch, BLOCKS a corrupt
one, and reconciles source vs target (exits non-zero on failure, like a CI/Airflow gate):

```bash
python3 02_Practice_Data_Quality_Checks.py       # stdlib only, no deps
```
Covers: not-null, uniqueness, range, accepted-values, regex, freshness SLA, referential
integrity, and source-to-target reconciliation.
